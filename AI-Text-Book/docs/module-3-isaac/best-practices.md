---
sidebar_position: 6
---

# Best Practices & Production Patterns

This section covers real-world patterns, optimization techniques, and safety practices used by companies shipping production robotics systems.

---

## 1. Performance Optimization

### GPU Memory Management

**Problem**: Deep learning models can consume gigabytes of GPU memory, limiting what else can run.

**Solution: Optimize Memory Usage**

```python
# ❌ BAD: Large batch sizes
detections = model(images_batch_of_100)  # 100 images = 3GB

# ✅ GOOD: Stream-based processing
for image in image_stream:
    detection = model(image)  # One at a time, ~30MB per frame
    process(detection)
```

**Best Practice**:
- For robotics: Process one frame at a time (stream-based)
- For data analysis: Batch process offline
- Monitor GPU memory: `nvidia-smi --loop=1`

### Model Quantization

Reduce model size and inference time by 3-10x:

```python
import torch

# Original FP32 model: 350 MB, 45ms inference
model = YOLO("yolov8m.pt")

# Quantized INT8 model: 90 MB, 12ms inference (3.75x speedup)
model_int8 = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)

# Export to ONNX for maximum compatibility
model.export(format="onnx")
```

**Impact**:
```
Model Size:          350 MB → 90 MB (75% smaller)
Inference Time:      45 ms → 12 ms (3.75x faster)
GPU Memory:          800 MB → 200 MB (4x less)
Battery Life (edge): +150% longer runtime
```

### Model Selection for Robotics

```
CRITERIA FOR MODEL SELECTION:
┌─────────────────────────────────────────────────────┐
│                                                     │
│ Task                Model          Inference Time   │
│ ────────────────────────────────────────────────────│
│ Detection           YOLOv8n         12ms  ✓ GOOD   │
│                     YOLOv8s         18ms  ✓ OK     │
│                     YOLOv8m         35ms  ✗ TOO SLOW
│                                                     │
│ Segmentation        Segformer-Tiny  40ms  ✓ GOOD   │
│                     DeepLabV3       60ms  ~ OK     │
│                     Panoptic         >100ms ✗ SLOW  │
│                                                     │
│ Pose Estimation     MobileNet       20ms  ✓ GOOD   │
│                     ResNet50        50ms  ~ OK     │
│                     ResNet101       100ms ✗ SLOW    │
│                                                     │
└─────────────────────────────────────────────────────┘

Rule: Target <50ms per inference on Jetson for real-time control
```

---

## 2. Real-Time Guarantees

### Meeting Hard Deadlines

Robotics requires deterministic timing. Missing a deadline can crash the robot.

**Implementation Pattern**:

```python
import time
from threading import Thread

class RealtimeControlLoop:
    def __init__(self, frequency_hz=200):
        """
        Guarantee consistent control frequency

        Args:
            frequency_hz: Target control frequency (Hz)
        """
        self.period = 1.0 / frequency_hz
        self.last_time = time.time()

    def wait_until_next_cycle(self):
        """
        Sleep until next cycle time

        Handles: unexpected delays, clock skips, system jitter
        """
        elapsed = time.time() - self.last_time

        if elapsed < self.period:
            # Sleep for remaining time
            time.sleep(self.period - elapsed)
        elif elapsed > self.period * 1.1:  # 10% overrun
            print(f"⚠ DEADLINE MISS: {elapsed*1000:.1f}ms (target: {self.period*1000:.1f}ms)")
            # Log but don't crash—keep going
        else:
            print(f"🟡 SLIGHT OVERRUN: {elapsed*1000:.1f}ms")

        self.last_time = time.time()

# Usage
controller = RealtimeControlLoop(frequency_hz=200)

while True:
    # Do control work
    t_start = time.time()
    command = compute_control()
    apply_command(command)
    t_elapsed = (time.time() - t_start) * 1000

    # Wait until next cycle
    controller.wait_until_next_cycle()

    # At this point, elapsed time ≈ 5ms consistently
```

**Key Points**:
- Use `time.perf_counter()` for accurate timing
- Never use `time.sleep(period)` alone—won't be accurate
- Log overruns for debugging
- Use dedicated real-time OS features if available (PREEMPT_RT on Linux)

### Resource Allocation

```
THREAD SCHEDULING (Linux):

Priority Level    Use Case                    Policy
──────────────────────────────────────────────────────
99 (Highest)      Safety Monitor (watchdog)   FIFO
90                Motor Control Loop          RR
80                Sensor Reading              RR
70                Perception (AI)             NORMAL
60                Planning                    NORMAL
50                Logging                     NORMAL
0  (Lowest)       UI/Visualization            NORMAL

Command to set thread priority:
chrt -f -p 90 <PID>  # Real-time FIFO, priority 90
```

---

## 3. Safety & Fault Tolerance

### Emergency Stop (E-Stop)

Every production robot needs a hardware E-stop. Here's how to implement software support:

```python
import signal
from threading import Event

class EmergencyStop:
    def __init__(self):
        self.triggered = Event()

        # Register Ctrl+C as emergency stop
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum, frame):
        """Handle Ctrl+C as emergency stop"""
        print("\n🚨 EMERGENCY STOP TRIGGERED")
        self.triggered.set()

    def check(self):
        """Check if e-stop is active"""
        return self.triggered.is_set()

    def assert_safe(self):
        """Raise exception if e-stop triggered"""
        if self.triggered.is_set():
            raise RuntimeError("Emergency stop active")

# Usage in control loop
estop = EmergencyStop()

try:
    while not estop.check():
        estop.assert_safe()

        # Compute and apply control
        command = compute_control()
        apply_command(command)

finally:
    # Always execute cleanup
    stop_motors()
    release_gripper()
    print("✓ Safe shutdown complete")
```

### Watchdog Timer

Detect and recover from unexpected delays:

```python
import time
from threading import Thread

class Watchdog:
    def __init__(self, timeout_sec=1.0, on_timeout=None):
        """
        Monitor for failures

        Args:
            timeout_sec: Time before timeout
            on_timeout: Callback if timeout occurs
        """
        self.timeout = timeout_sec
        self.on_timeout = on_timeout
        self.last_reset = time.time()

    def reset(self):
        """Signal system is healthy"""
        self.last_reset = time.time()

    def check(self):
        """Check if timeout occurred"""
        elapsed = time.time() - self.last_reset

        if elapsed > self.timeout:
            print(f"🚨 WATCHDOG TIMEOUT: No heartbeat for {elapsed:.1f}s")
            if self.on_timeout:
                self.on_timeout()
            return True  # Timeout occurred
        return False

# Usage
watchdog = Watchdog(timeout_sec=1.0, on_timeout=stop_motors)

while True:
    if watchdog.check():
        break  # Exit control loop, execute emergency stop

    try:
        command = compute_control()
        apply_command(command)
    except Exception as e:
        print(f"Error: {e}")
        break

    watchdog.reset()  # Signal heartbeat
```

---

## 4. Debugging & Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime

# Configure logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('robot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('robotics')

# Structured logging (machine-readable)
def log_event(event_type, **kwargs):
    """Log events as JSON for analysis"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event': event_type,
        **kwargs
    }
    logger.info(json.dumps(log_entry))

# Usage
log_event('object_detected', confidence=0.95, x=0.2, y=0.3, z=0.5)
log_event('trajectory_planned', waypoints=20, duration=2.0)
log_event('error', type='position_tracking', error=0.05)
```

### Performance Profiling

```python
import cProfile
import pstats

def profile_code(func):
    """Decorator to profile function performance"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 slowest

        return result
    return wrapper

# Usage
@profile_code
def perception_node():
    # Your perception code
    pass

# Output shows:
# ncalls  tottime  cumtime
# 1       0.050   0.150    model.inference()  <- where time is spent
# 100     0.025   0.040    post_processing()
```

### Visualization with Isaac Sight

```python
# Publish data for visualization
from isaac_common.common import Isaac

class Visualizer:
    def __init__(self):
        self.isaac = Isaac()

    def publish_detection(self, detections):
        """Publish for visualization in Isaac Sight"""
        for det in detections:
            self.isaac.publish('/detections', {
                'bbox': det['bbox'],
                'class': det['class_name'],
                'confidence': det['confidence']
            })

    def publish_trajectory(self, trajectory):
        """Visualize motion trajectory"""
        self.isaac.publish('/trajectory', {
            'waypoints': trajectory['joint_angles'],
            'times': trajectory['times']
        })

# Isaac Sight automatically shows:
# - Bounding boxes overlay on camera
# - Robot trajectory in 3D
# - Sensor data streams
# - Real-time performance metrics
```

---

## 5. Handling Sensor Failures

### Graceful Degradation

When sensors fail, don't crash—degrade gracefully:

```python
class RobustPerception:
    def __init__(self):
        self.camera_available = True
        self.lidar_available = True

    def get_object_position(self):
        """
        Get object position using available sensors

        Strategy:
        1. Try camera + depth
        2. Fall back to LiDAR
        3. Fall back to last known position
        """
        try:
            if self.camera_available:
                return self.detect_from_camera()
        except CameraError:
            print("⚠ Camera failed, switching to LiDAR")
            self.camera_available = False

        try:
            if self.lidar_available:
                return self.detect_from_lidar()
        except LiDARError:
            print("⚠ LiDAR failed, using last known position")
            self.lidar_available = False

        # Last resort: use predicted position from motion model
        return self.predicted_position

    def detect_from_camera(self):
        """Camera-based detection"""
        raise CameraError("Camera read failed")

    def detect_from_lidar(self):
        """LiDAR-based detection"""
        raise LiDARError("LiDAR read failed")
```

### Timeout Handling

```python
import time

def read_sensor_with_timeout(sensor, timeout=1.0):
    """
    Read sensor with timeout

    Args:
        sensor: Sensor object
        timeout: Maximum wait time (seconds)

    Returns:
        data or None if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            data = sensor.read_nonblocking()
            if data is not None:
                return data
        except Exception as e:
            print(f"Sensor error: {e}")

        time.sleep(0.001)  # 1ms

    print("⚠ Sensor read timeout")
    return None
```

---

## 6. Testing & Validation

### Unit Tests for Perception

```python
import unittest
import numpy as np

class TestPerception(unittest.TestCase):
    def setUp(self):
        self.detector = ObjectDetector()

    def test_detection_confidence_filtering(self):
        """Verify low-confidence detections are filtered"""
        # Create fake low-confidence detection
        fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        detections = self.detector.detect(fake_frame)

        # All detections should have confidence > threshold
        for det in detections:
            self.assertGreater(det['confidence'], self.detector.confidence_threshold)

    def test_no_false_positives(self):
        """Test on blank image"""
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = self.detector.detect(blank_frame)
        self.assertEqual(len(detections), 0, "Should detect no objects in blank image")

    def test_inference_speed(self):
        """Verify inference meets latency requirements"""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        import time
        start = time.time()
        detections = self.detector.detect(frame)
        elapsed = time.time() - start

        self.assertLess(elapsed, 0.050, f"Inference took {elapsed*1000:.1f}ms, should be <50ms")
```

### Integration Tests

```python
def test_end_to_end_bin_picking():
    """Test complete picking pipeline"""
    # Setup
    sim = IsaacSim()
    sim.load_scene("bin_picking.usd")

    # Run pipeline
    detection = sim.get_camera_frame()
    objects = detector.detect(detection)

    assert len(objects) > 0, "Should detect objects in bin"

    # Plan trajectory
    target = objects[0]
    trajectory = planner.plan_to(target)

    assert trajectory is not None, "Should generate valid trajectory"
    assert len(trajectory.points) > 0, "Trajectory should have waypoints"

    # Execute and verify
    controller.execute(trajectory)
    gripper_closed = sim.get_gripper_state()

    assert gripper_closed, "Gripper should be closed after pick"
```

---

## 7. Optimization Checklist

Before deploying a robot system, use this checklist:

```
PERFORMANCE OPTIMIZATION CHECKLIST
──────────────────────────────────────────────────────

Perception:
  ☐ Model quantized (INT8 or FP16)
  ☐ Batch size = 1 (stream processing)
  ☐ GPU memory < 1GB
  ☐ Inference time < 50ms
  ☐ FPS ≥ real-time requirement (typically 30 FPS)

Planning:
  ☐ Cycle time < 500ms for motion planning
  ☐ IK solver converges in <100 iterations
  ☐ No planning failures (>99% success rate)
  ☐ Handles collisions gracefully

Control:
  ☐ Control frequency: 200+ Hz
  ☐ Latency < 10ms jitter
  ☐ Position tracking error: < 5°
  ☐ E-stop responds in < 100ms

Robustness:
  ☐ Handles sensor failure (graceful degradation)
  ☐ Watchdog timer active
  ☐ Logging enabled for debugging
  ☐ Unit tests: >80% code coverage
  ☐ Integration tests passing

Deployment:
  ☐ Models optimized for target hardware
  ☐ Dependency versions frozen
  ☐ Config files externalized (not hardcoded)
  ☐ Documentation complete
  ☐ Team trained
```

---

## 8. Common Pitfalls & How to Avoid Them

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| **GPU OOM (Out of Memory)** | CUDA memory error during inference | Use quantization, stream processing, smaller models |
| **Missed control deadlines** | Jerky robot motion, crashes | Use real-time OS, dedicated thread, lower priority for other tasks |
| **Sensor data corruption** | Random failures, segfaults | Add checksum, timeout detection, redundant sensors |
| **Inference latency spike** | Occasional 500ms delays | Profile code, use consistent batch sizes, pin threads |
| **No graceful shutdown** | Robot keeps moving after stop | Use e-stop handler, finally blocks, watchdog |
| **Hardcoded parameters** | Can't tune for new robot | Use config files, ROS parameters |

---

## 9. Production Deployment Pattern

```
DEVELOPMENT → TESTING → STAGING → PRODUCTION
    ↓           ↓          ↓          ↓
Simulation    Unit Tests  Real HW   Customers
GPU Testing   Integration Hardening Safety
             Full Stack   Thermal   Compliance
```

**Key Stages**:

1. **Development** (Laptop)
   - Code locally in simulation
   - Profile performance
   - Optimize models

2. **Testing** (Lab)
   - Run unit & integration tests
   - Test on real Jetson hardware
   - Validate sensor integration

3. **Staging** (Pre-production Robot)
   - Full system test with real mechanics
   - Long-duration stress tests
   - Thermal envelope testing

4. **Production** (Customer Deployment)
   - Frozen code version
   - Telemetry/logging enabled
   - Support team trained

---

## Summary

**Best Practices in Robotics**:

✅ Optimize for real-time performance (GPU, quantization, stream processing)
✅ Guarantee deadlines (deterministic timing, watchdogs)
✅ Fail safely (e-stop, graceful degradation, health monitoring)
✅ Debug effectively (structured logging, profiling, visualization)
✅ Test thoroughly (unit tests, integration tests, real hardware)
✅ Deploy systematically (stages: dev → test → staging → production)

These patterns are used by companies shipping millions of robots. Follow them, and your systems will be reliable, performant, and safe.

---

**Next Section**: Summary & Key Takeaways
**Time to Read**: 10 minutes
**Prerequisites**: All previous sections

*Last Updated: 2026-01-20*

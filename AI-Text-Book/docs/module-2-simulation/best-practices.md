---
sidebar_position: 14
---

# Best Practices & Professional Patterns for Simulation

This section covers best practices from production robotics teams that use simulation for development and validation.

---

## 1. Physics Tuning for Sim-to-Real Transfer

The biggest challenge in simulation is making the virtual world behave like the real world.

### Physics Parameters from Hardware Datasheets

**Always use real specifications**, not defaults:

```python
# Load robot parameters from YAML (not hardcoded)
# config/robot_params.yaml
robot:
  mass: 25.0  # kg from CAD
  gravity: 9.81  # m/s²

joints:
  - name: "shoulder_joint"
    friction: 0.15  # From bearing spec
    damping: 0.01   # Measured in lab
    effort_limit: 150  # Nm from motor datasheet
    velocity_limit: 1.57  # rad/s (max speed)
```

### Joint Friction Modeling

Real joints have friction that's missing in basic simulation:

**Good practice**:
```xml
<!-- In URDF/SDF -->
<dynamics>
  <friction>0.15</friction>
  <damping>0.01</damping>
  <spring_reference>0</spring_reference>
  <spring_stiffness>1000</spring_stiffness>
</dynamics>
```

**Why**:
- Friction affects achievable speed and torque
- Damping stabilizes simulation (prevents oscillation)
- Spring constants model joint compliance
- These parameters should match hardware measurements

### Contact Properties

Surfaces interact differently in reality:

```xml
<surface>
  <!-- Friction -->
  <friction>
    <ode>
      <mu>0.5</mu>      <!-- Static friction -->
      <mu2>0.5</mu2>    <!-- Sliding friction -->
      <fdir1>1 0 0</fdir1>
      <slip1>0.0</slip1>
      <slip2>0.0</slip2>
    </ode>
  </friction>

  <!-- Bounce/Elasticity -->
  <bounce>
    <restitution_coefficient>0.2</restitution_coefficient>
    <threshold>0.05</threshold>
  </bounce>

  <!-- Soft contact -->
  <contact>
    <collide_bitmask>0xffff</collide_bitmask>
  </contact>
</surface>
```

### Domain Randomization

Train robust algorithms by intentionally varying physics:

```python
def randomize_physics():
    """
    Vary simulation parameters to create robust policies
    that work across manufacturing tolerances
    """
    import random

    # Vary mass by ±10%
    mass_factor = random.uniform(0.9, 1.1)

    # Vary friction by ±20%
    friction_factor = random.uniform(0.8, 1.2)

    # Vary damping
    damping_factor = random.uniform(0.9, 1.1)

    # Apply to simulation
    apply_robot_parameters(
        mass=nominal_mass * mass_factor,
        friction=nominal_friction * friction_factor,
        damping=nominal_damping * damping_factor
    )
```

**Result**: Algorithm trained on varied physics generalizes better to real hardware.

---

## 2. Realistic Sensor Simulation

Simulated sensors must reproduce real sensor characteristics, not perfect measurements.

### Camera Simulation with Noise

Real cameras have lens distortion, noise, motion blur:

```python
class RealisticCameraSimulator:
    """
    Simulate real camera imperfections
    """

    def __init__(self):
        self.gaussian_noise_std = 0.005  # 0.5% noise
        self.focal_length = 525.0  # pixels
        self.cx, self.cy = 320, 240  # principal point
        self.distortion_k1 = 0.1  # Radial distortion

    def add_noise_to_image(self, image):
        """Add Gaussian noise (simulates photon noise)"""
        import numpy as np
        noise = np.random.normal(0, self.gaussian_noise_std, image.shape)
        noisy_image = np.clip(image + noise, 0, 1)
        return noisy_image

    def apply_lens_distortion(self, image):
        """Simulate barrel/pincushion distortion"""
        # In real cameras, straight lines appear curved
        # This affects localization accuracy
        # (Would use OpenCV undistort in reverse)
        pass

    def add_motion_blur(self, image, velocity):
        """Simulate motion blur from fast movement"""
        if np.linalg.norm(velocity) > 0.5:  # Moving fast
            # Blur in direction of motion
            pass
```

### LiDAR Noise Modeling

Real LiDAR has unique characteristics:

```python
class RealisticLiDARSimulator:
    """
    Simulate LiDAR imperfections
    """

    def __init__(self):
        self.angular_noise = 0.02  # radians
        self.range_noise_std = 0.02  # 2cm per 100m
        self.max_range = 100  # meters
        self.min_range = 0.1  # minimum measurable

    def add_realistic_noise(self, ranges):
        """
        Add noise that matches real LiDAR
        - Noise increases with distance
        - Random dropouts
        - Phase discontinuities at edges
        """
        import numpy as np

        noisy_ranges = ranges.copy()

        # Distance-dependent noise
        noise_magnitude = 0.02 + 0.0001 * ranges  # Increases with distance
        noise = np.random.normal(0, noise_magnitude)
        noisy_ranges += noise

        # Random dropouts (missing returns)
        dropout_mask = np.random.random(len(ranges)) < 0.01  # 1% dropout
        noisy_ranges[dropout_mask] = self.max_range

        # Clamp to valid range
        noisy_ranges = np.clip(noisy_ranges, self.min_range, self.max_range)

        return noisy_ranges
```

### IMU Simulation with Bias & Drift

Real IMU sensors have bias, scale factor errors, and temperature drift:

```python
class RealisticIMUSimulator:
    """
    Simulate real IMU characteristics
    """

    def __init__(self):
        # Accelerometer parameters
        self.accel_bias = np.array([0.02, 0.01, 0.03])  # m/s²
        self.accel_noise_std = 0.001  # m/s²
        self.accel_scale_factor = 1.01  # 1% scale error

        # Gyroscope parameters
        self.gyro_bias = np.array([0.001, -0.002, 0.0015])  # rad/s
        self.gyro_noise_std = 0.0001
        self.gyro_drift_rate = 0.0001  # rad/s per hour

        # Initialization
        self.gyro_bias_random_walk = np.zeros(3)
        self.time_step = 0.01

    def simulate_accelerometer(self, true_accel):
        """Simulate realistic accelerometer output"""
        import numpy as np

        # Add bias (DC offset that drifts)
        biased = true_accel + self.accel_bias

        # Add scale factor error
        scaled = biased * self.accel_scale_factor

        # Add white noise
        noise = np.random.normal(0, self.accel_noise_std, 3)
        measured = scaled + noise

        return measured

    def simulate_gyroscope(self, true_angular_vel):
        """Simulate realistic gyroscope output"""
        import numpy as np

        # Add bias and bias drift
        self.gyro_bias_random_walk += np.random.normal(
            0, self.gyro_drift_rate * self.time_step, 3
        )

        biased = true_angular_vel + self.gyro_bias + self.gyro_bias_random_walk

        # Add white noise
        noise = np.random.normal(0, self.gyro_noise_std, 3)
        measured = biased + noise

        return measured
```

---

## 3. Performance Optimization

Simulations can be slow. Here's how to speed them up:

### Physics Step Size Tuning

```yaml
# config/gazebo_physics.yaml
physics:
  # Smaller step = more accurate but slower
  # Typical: 0.001s (1000 Hz) for good stability
  # Can reduce to 0.01s (100 Hz) for speed
  max_step_size: 0.001

  # Real-time factor: 1.0 = real-time, 2.0 = 2x speed
  real_time_factor: 1.0

  # More iterations = more accurate
  # Diminishing returns after 50
  solver_iterations: 50
```

### Collision Mesh Simplification

```python
# Good practice: Simple collision, detailed visual
<link name="arm_link">
  <!-- Simplified collision (fast) -->
  <collision name="collision">
    <geometry>
      <cylinder radius="0.05" length="0.4"/>
    </geometry>
  </collision>

  <!-- Detailed visual (slow, but only for rendering) -->
  <visual name="visual">
    <geometry>
      <mesh filename="models/arm_link_detailed.stl"/>
    </geometry>
  </visual>
</link>
```

### Sensor Update Rate Management

Not all sensors need high frequency:

```python
# config/sensor_rates.yaml
sensors:
  camera:
    update_rate: 30  # Hz (30 FPS typical for cameras)

  lidar:
    update_rate: 10  # Hz (10 Hz is often enough)
    # Benefit: 3x faster than 30 Hz

  imu:
    update_rate: 100  # Hz (IMU can be high frequency)

  force_torque:
    update_rate: 1000  # Hz (joint sensors, high precision)
```

### GPU Acceleration

```bash
# Enable GPU physics if available
export GAZEBO_FORCE_SINGLE_THREAD=0  # Use multiple cores
export GAZEBO_LOG_COMMAND_OPTION=disable  # Disable logging

# Run with optimized settings
gazebo --verbose --server-only  # Headless for speed
```

---

## 4. Debugging Simulation Problems

### Physics Instability Detection

**Problem**: Robot vibrates, sinks, or flies apart

```python
# Monitor for instability
def check_simulation_health(robot_state):
    """Check for common simulation problems"""

    # Check for NaN values
    for joint in robot_state.joint_angles:
        if math.isnan(joint):
            logger.error("NaN detected in joint angles!")
            return False

    # Check for excessive acceleration
    max_accel = max(robot_state.accelerations)
    if max_accel > 100:  # m/s²
        logger.warn(f"Excessive acceleration: {max_accel}")
        return False

    # Check robot hasn't fallen through ground
    if robot_state.position.z < -1:
        logger.error("Robot below ground!")
        return False

    return True
```

### Sensor Data Validation

```python
def validate_sensor_data(lidar_scan):
    """Check if sensor data looks reasonable"""

    # Check range limits
    if min(lidar_scan) < 0.1 or max(lidar_scan) > 100:
        logger.warn("LiDAR readings out of expected range")

    # Check for too many dropouts
    dropouts = sum(1 for r in lidar_scan if r > 99.9)
    dropout_percent = 100 * dropouts / len(lidar_scan)
    if dropout_percent > 50:
        logger.error(f"High dropout rate: {dropout_percent}%")
        return False

    # Check for suddenly jumping values
    diffs = [abs(lidar_scan[i] - lidar_scan[i-1])
             for i in range(1, len(lidar_scan))]
    max_diff = max(diffs)
    if max_diff > 10:  # Big jump between adjacent rays suspicious
        logger.warn(f"Large gap in LiDAR: {max_diff}m")

    return True
```

### Visual Inspection Tools

```bash
# Open Gazebo with visualization
gazebo --verbose  # Verbose logging

# Monitor topics in separate terminal
watch -n 0.1 "ros2 topic hz /scan /odom /camera/image_raw"

# Use rqt for visualization
rqt_plot /joint_states/effort[0]  # Plot joint torques
rqt_image_view /camera/image_raw  # View camera
```

---

## 5. Testing Strategies for Simulation

### Unit Test a Simulation Component

```python
import unittest
import rclpy
from robot_system.obstacle_detector import ObstacleDetectorNode

class TestObstacleDetector(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = ObstacleDetectorNode()

    def tearDown(self):
        self.node.destroy_node()

    def test_detects_close_obstacle(self):
        """Obstacle at 0.2m should trigger danger"""
        from sensor_msgs.msg import LaserScan

        # Create fake scan with obstacle at 0.2m
        scan = LaserScan()
        scan.ranges = [10.0] * 360  # All far
        scan.ranges[0] = 0.2  # One close at angle 0
        scan.angle_min = -3.14159
        scan.angle_max = 3.14159
        scan.range_min = 0.1
        scan.range_max = 10.0

        # Call callback directly
        self.node.lidar_callback(scan)

        # Verify danger was handled
        # (Implementation-specific verification)
```

### Integration Test: Simulation + Algorithm

```bash
#!/bin/bash
# test_sim_integration.sh

# Start Gazebo in background
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py &
GAZEBO_PID=$!

sleep 5  # Wait for Gazebo to start

# Run algorithm
ros2 run robot_system trajectory_tracker

# Clean up
kill $GAZEBO_PID
wait
```

---

## 6. Common Mistakes to Avoid

### ❌ Mistake 1: Over-Tuning to Simulation

**Problem**: Algorithm works perfectly in sim but fails on hardware

**Solution**:
- Add noise and uncertainty intentionally
- Test with multiple random seeds
- Use domain randomization
- Validate early on real hardware

### ❌ Mistake 2: Ignoring Actuation Dynamics

**Problem**: Commands execute instantly in simulation but have lag in reality

**Solution**:
```python
# Model actuator response
class ActuatorModel:
    def __init__(self, tau=0.05):  # 50ms response time
        self.tau = tau
        self.current_value = 0.0

    def update(self, target, dt):
        # First-order response model
        self.current_value += (target - self.current_value) * (dt / self.tau)
        return self.current_value
```

### ❌ Mistake 3: Perfect Sensor Synchronization

**Problem**: In simulation, all sensor callbacks happen at same time

**Solution**:
```python
# Add jitter to sensor updates
update_time = self.get_clock().now()
jitter = random.uniform(-0.001, 0.001)  # ±1ms
effective_time = update_time + jitter
```

### ❌ Mistake 4: No Error Recovery

**Problem**: Algorithm crashes if sensor is missing

**Solution**:
```python
def sensor_callback(self, msg):
    try:
        process_data(msg)
    except Exception as e:
        logger.error(f"Sensor error: {e}")
        # Fall back to safe behavior
        self.enter_safe_state()
```

---

## 7. Production Readiness Checklist

Before deploying simulation-trained models to real hardware:

### Simulation Fidelity
- [ ] Physics parameters match hardware specs
- [ ] Sensor noise models validated against real sensors
- [ ] Actuator dynamics modeled (not ideal)
- [ ] Friction and contact properties measured
- [ ] Domain randomization applied (10-20% variation)

### Algorithm Robustness
- [ ] Works with degraded sensors (60% of LiDAR returns)
- [ ] Handles latency (add 50-100ms delay)
- [ ] Tolerates ±10% parameter variation
- [ ] Recovers from momentary sensor failure
- [ ] Safe defaults when uncertain

### Sim-to-Real Validation
- [ ] Recorded 1+ hours of real sensor data
- [ ] Replayed real data in simulation
- [ ] Algorithm behaves similarly in both
- [ ] Discrepancies identified and addressed
- [ ] A/B test on subset of real hardware

### Code Quality
- [ ] All sensor callbacks have error handling
- [ ] Logging at appropriate levels
- [ ] No hardcoded parameters (all in YAML)
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests with simulation

### Documentation
- [ ] Physics tuning documented
- [ ] Sensor noise model explained
- [ ] Known limitations listed
- [ ] Failure modes identified
- [ ] Fallback behaviors described

---

## Summary of Best Practices

| Practice | Benefit | Priority |
|----------|---------|----------|
| **Use hardware specs** | Accurate sim-to-real | 🔴 Critical |
| **Model sensor noise** | Robust algorithms | 🔴 Critical |
| **Add domain randomization** | Works with variation | 🟠 High |
| **Validate sim vs real** | Catch discrepancies | 🔴 Critical |
| **Performance optimization** | Faster iteration | 🟢 Medium |
| **Comprehensive testing** | Fewer bugs in real | 🟠 High |
| **Error recovery** | Safe failures | 🔴 Critical |

---

**Next Section**: Summary & Key Takeaways
**Time to Read**: 30 minutes

---

*Last Updated: 2026-01-20*
*Module Version: 1.0*

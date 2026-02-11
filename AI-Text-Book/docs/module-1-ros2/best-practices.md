---
sidebar_position: 6
---

# Best Practices & Professional Patterns

This section covers proven patterns from production ROS 2 systems used at companies like Boston Dynamics, Tesla, TIER IV, and leading robotics research institutions.

---

## 1. Node Design Principles

### Single Responsibility Principle

**Good** ✅:
```
- SensorNode: Only reads sensor, publishes data
- ProcessorNode: Only processes data, publishes results
- ControlNode: Only controls actuators
```

**Bad** ❌:
```
- MegaNode: Reads sensors, processes data, AND controls actuators
```

**Why**: Each node should have one clear purpose. This makes:
- ✅ Testing easier (single responsibility = easy to test)
- ✅ Reusability better (can use sensor node in other projects)
- ✅ Debugging simpler (know exactly what each node does)
- ✅ Maintenance cleaner (changes isolated to one node)

### Node Lifecycle Management

**Always** implement proper shutdown:

```python
def main(args=None):
    rclpy.init(args=args)
    node = MyNode()

    try:
        rclpy.spin(node)  # Run until interrupted
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down gracefully...')
    finally:
        node.destroy_node()  # Clean up resources
        rclpy.shutdown()     # Shutdown ROS 2
```

**Why**:
- Prevents resource leaks (unclosed files, sockets)
- Allows proper cleanup (stop motors, close grippers)
- Enables graceful multi-node shutdown

---

## 2. Communication Best Practices

### QoS Profile Selection

**For sensor streams** (camera, lidar, IMU):
```python
QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,  # Ok to lose frames
    durability=DurabilityPolicy.VOLATILE,       # Don't need old data
    history=HistoryPolicy.KEEP_LAST,
    depth=5  # Keep last 5 messages
)
```

**For critical commands** (motor, safety):
```python
QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,      # Don't lose commands
    durability=DurabilityPolicy.TRANSIENT_LOCAL, # New nodes get last value
    history=HistoryPolicy.KEEP_LAST,
    depth=10  # Keep last 10 messages
)
```

### Topic Naming Convention

Use hierarchical naming:
```
/robot/sensors/camera/rgb/image
/robot/sensors/imu/acceleration
/robot/control/motors/left_wheel/speed
/robot/status/battery/voltage
```

**NOT**:
```
/camera_image
/imu
/motor_speed
```

**Why**: Hierarchy makes it easier to understand system organization and filter topics.

### Avoid Message Deadlocks

**Bad pattern** ⚠️:
```python
# Publisher blocks until subscriber processes
# If subscriber is slow, publisher waits
```

**Good pattern** ✅:
```python
# Use async publish
# Publisher never blocks
# Messages queued by middleware
self.publisher.publish(msg)  # Returns immediately
```

---

## 3. Error Handling & Robustness

### Wrap All Callbacks in Try-Except

```python
def sensor_callback(self, msg):
    try:
        value = msg.data
        # Process...
        return result
    except Exception as e:
        self.get_logger().error(f'Sensor error: {e}')
        # Return safe default or skip processing
```

**Why**: A crash in one callback shouldn't crash the entire node.

### Implement Timeouts

```python
# If no messages for 5 seconds, assume sensor failure
self.sensor_timeout = 5.0
self.last_message_time = self.get_clock().now()

def check_sensor_health(self):
    elapsed = (self.get_clock().now() - self.last_message_time).nanoseconds / 1e9
    if elapsed > self.sensor_timeout:
        self.get_logger().error('Sensor timeout!')
        self.disable_motors()  # Safe state
```

### Validate Input Data

```python
def process_command(self, msg):
    # Check bounds
    if msg.speed > self.MAX_SPEED:
        self.get_logger().warn(
            f'Speed {msg.speed} exceeds limit {self.MAX_SPEED}'
        )
        msg.speed = self.MAX_SPEED  # Clamp to safe value

    # Check for NaN/Inf
    if math.isnan(msg.speed) or math.isinf(msg.speed):
        self.get_logger().error('Invalid speed value')
        return
```

---

## 4. Debugging Techniques

### Essential ROS 2 Debugging Commands

```bash
# List active nodes
ros2 node list

# View node info
ros2 node info /my_node

# List topics
ros2 topic list

# Listen to topic messages
ros2 topic echo /my_topic

# Publish test message
ros2 topic pub /my_topic geometry_msgs/msg/Twist \
  "{linear: {x: 1.0}}"

# List services
ros2 service list

# Call service
ros2 service call /my_service std_srvs/srv/Trigger

# View parameters
ros2 param list
ros2 param get /my_node param_name
ros2 param set /my_node param_name value

# Record messages
ros2 bag record -a  # Record all topics

# Replay messages
ros2 bag play rosbag2_2026_01_20

# Graph visualization
rqt_graph

# Topic monitor GUI
rqt_topic
```

### Add Debug Logging

```python
# Different logging levels
self.get_logger().debug('Detailed info')     # Development
self.get_logger().info('Important info')     # General
self.get_logger().warn('Warning condition')  # Alerts
self.get_logger().error('Error occurred')    # Errors
self.get_logger().fatal('Fatal error')       # System down
```

Set log level:
```bash
# View all debug messages
export ROS_LOG_DIR=/tmp/ros2_logs
ros2 run --log-level DEBUG my_package my_node
```

### Use Ros 2 Introspection Tools

```bash
# Install tools
sudo apt-get install ros-jazzy-rqt-*

# Network monitoring
rqt_graph  # See node connections

# Message inspection
rqt_topic  # View message values

# Service debugging
rqt_service_caller  # Call services from GUI
```

---

## 5. Performance Optimization

### Measure Before Optimizing

```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.callback_times = []

    def monitor_callback(self, msg):
        start = time.time()

        # Your code here
        result = self.expensive_computation(msg)

        elapsed = (time.time() - start) * 1000  # ms
        self.callback_times.append(elapsed)

        # Log stats every 100 callbacks
        if len(self.callback_times) % 100 == 0:
            avg = sum(self.callback_times) / len(self.callback_times)
            max_time = max(self.callback_times)
            self.get_logger().info(
                f'Callback performance: '
                f'avg={avg:.2f}ms, max={max_time:.2f}ms'
            )
```

### Optimization Techniques

**1. Use Appropriate Message Types**
```python
# Bad: Publishing entire point cloud for simple distance
# Good: Publish only the extracted distance value
```

**2. Downsample High-Frequency Data**
```python
self.frame_skip = 5  # Process every 5th frame
self.frame_counter = 0

def image_callback(self, msg):
    self.frame_counter += 1
    if self.frame_counter % self.frame_skip != 0:
        return  # Skip this frame
    # Process only 1 in 5 frames
```

**3. Use Lazy Evaluation**
```python
# Only compute complex value when needed
@property
def computed_value(self):
    if not hasattr(self, '_cached_value'):
        self._cached_value = expensive_computation()
    return self._cached_value
```

---

## 6. Testing Best Practices

### Unit Test a ROS 2 Node

```python
# tests/test_my_node.py
import unittest
import rclpy
from my_package.my_node import MyNode

class TestMyNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = MyNode()

    def tearDown(self):
        self.node.destroy_node()

    def test_initialization(self):
        """Node initializes without errors"""
        self.assertIsNotNone(self.node)

    def test_publisher_exists(self):
        """Publisher is created"""
        self.assertGreater(len(self.node.publishers_), 0)

    def test_callback_handles_message(self):
        """Callback processes message correctly"""
        from std_msgs.msg import Float64
        msg = Float64(data=42.0)
        # Call callback directly
        self.node.process_callback(msg)
        # Assert expected behavior

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```bash
# Launch all nodes
ros2 launch my_package system.launch.py

# Record system behavior
ros2 bag record -a

# Run tests
ros2 test /path/to/test.py

# Analyze results
python3 analyze_results.py
```

---

## 7. Common Mistakes to Avoid

### ❌ Mistake 1: Blocking Operations in Callbacks

```python
# BAD: Blocks entire node
def callback(self, msg):
    time.sleep(5)  # WRONG! Blocks other callbacks
    process(msg)

# GOOD: Use threading or separate node
def callback(self, msg):
    threading.Thread(target=slow_process, args=(msg,)).start()
```

### ❌ Mistake 2: Global Shared State

```python
# BAD: Global state, race conditions
global_value = 0
def update():
    global global_value
    global_value = 42  # Race condition!

# GOOD: Instance variables, thread-safe
class MyNode:
    def __init__(self):
        self.value = 0
    def update(self):
        self.value = 42  # Safe in ROS callbacks
```

### ❌ Mistake 3: Ignoring Message Ordering

```python
# BAD: Assumes messages arrive in order
self.last_id = 0
def callback(self, msg):
    assert msg.id > self.last_id  # Might fail

# GOOD: Handle out-of-order messages
def callback(self, msg):
    if msg.id <= self.last_id:
        self.get_logger().warn(f'Out of order message {msg.id}')
        return
```

### ❌ Mistake 4: Not Handling ROS Shutdown

```python
# BAD: Resource leak
class MyNode:
    def __init__(self):
        self.file = open('/tmp/data.txt', 'w')

# GOOD: Clean up resources
class MyNode:
    def __init__(self):
        self.file = open('/tmp/data.txt', 'w')

    def on_shutdown(self):
        self.file.close()  # Called during shutdown
```

---

## 8. Production Checklist

Before deploying your ROS 2 system to a real robot:

- [ ] All nodes handle shutdown gracefully
- [ ] Appropriate QoS profiles configured
- [ ] Error handling in all callbacks
- [ ] Timeouts implemented for all sensor inputs
- [ ] Input validation on all received messages
- [ ] Logging at INFO level (not debug)
- [ ] Unit tests for core functionality
- [ ] Integration tests for node communication
- [ ] Performance profiled and acceptable
- [ ] Documentation complete
- [ ] Known issues documented

---

## Summary

**Professional ROS 2 systems follow these patterns:**

✅ Single responsibility per node
✅ Appropriate QoS profiles
✅ Robust error handling
✅ Proper lifecycle management
✅ Performance monitoring
✅ Comprehensive testing
✅ Clear debugging capabilities

Master these practices, and your ROS 2 systems will be production-ready.

---

**Next Section**: Summary & Key Takeaways
**Time to Read**: 20-30 minutes

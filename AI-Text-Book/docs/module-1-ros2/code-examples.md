---
sidebar_position: 5
---

# Code Examples: Production-Quality ROS 2 Patterns

In this section, we provide five production-quality code examples you can run immediately. Each example demonstrates a different pattern used in real robots.

---

## Example 1: Publisher with Error Handling and Logging

**Scenario**: A robot publishes its battery status at regular intervals.

```python
#!/usr/bin/env python3
"""
Battery Monitor Node - Publishes battery status
Demonstrates: Publisher, error handling, logging, and rate control
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from rclpy.qos import QoSProfile, ReliabilityPolicy
import math
import time

class BatteryMonitorNode(Node):
    """
    Monitors battery voltage and publishes to /battery/state.

    Real-world application:
    - Monitors actual battery via GPIO/ADC
    - Alerts when battery is low
    - Shuts down gracefully when critical
    """

    def __init__(self):
        super().__init__('battery_monitor')

        # Configuration (would load from params in production)
        self.publish_rate = 1.0  # Hz (once per second)
        self.warning_threshold = 20.0  # %
        self.critical_threshold = 10.0  # %
        self.nominal_voltage = 12.0  # Volts

        # Publisher with RELIABLE QoS (don't lose battery updates)
        qos_profile = QoSProfile(depth=10)
        qos_profile.reliability = ReliabilityPolicy.RELIABLE

        self.publisher = self.create_publisher(
            BatteryState,
            '/battery/state',
            qos_profile
        )

        # Timer to publish regularly
        period = 1.0 / self.publish_rate
        self.timer = self.create_timer(period, self.publish_battery_status)

        # Simulation: battery discharging over time
        self.start_time = time.time()
        self.battery_percent = 100.0

        self.get_logger().info('Battery Monitor started')

    def publish_battery_status(self):
        """Published battery status every 1 second"""
        try:
            # Simulate battery discharge (lose 0.5% per second)
            elapsed = time.time() - self.start_time
            self.battery_percent = max(0.0, 100.0 - (elapsed * 0.5))

            # Create message
            msg = BatteryState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.voltage = self.nominal_voltage * (self.battery_percent / 100.0)
            msg.temperature = 25.0 + (100 - self.battery_percent) * 0.1  # Heats up when low
            msg.percentage = self.battery_percent / 100.0
            msg.power_supply_technology = BatteryState.POWER_SUPPLY_TECHNOLOGY_LIPO
            msg.power_supply_status = BatteryState.POWER_SUPPLY_STATUS_DISCHARGING

            self.publisher.publish(msg)

            # Log with appropriate level
            if self.battery_percent > self.warning_threshold:
                self.get_logger().debug(
                    f'Battery: {self.battery_percent:.1f}% ({msg.voltage:.2f}V)'
                )
            elif self.battery_percent > self.critical_threshold:
                self.get_logger().warn(
                    f'⚠️ Battery LOW: {self.battery_percent:.1f}%'
                )
            else:
                self.get_logger().error(
                    f'🔴 Battery CRITICAL: {self.battery_percent:.1f}% - SHUTDOWN IMMINENT'
                )

        except Exception as e:
            self.get_logger().error(f'Error publishing battery status: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = BatteryMonitorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key production patterns:**
- Error handling in callback
- Different logging levels (debug, warn, error)
- QoS profile for critical data
- Simulation of real sensor behavior

---

## Example 2: Subscriber with Callback and State Management

**Scenario**: A robot tracks movement commands and logs when movement direction changes.

```python
#!/usr/bin/env python3
"""
Movement Tracker Node - Subscribes to velocity commands
Demonstrates: Subscriber with state management, filtering, and logging
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class MovementTrackerNode(Node):
    """
    Subscribes to /cmd_vel (movement commands).
    Tracks changes in movement and logs important transitions.
    """

    def __init__(self):
        super().__init__('movement_tracker')

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_callback,
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        # State tracking
        self.last_direction = "STOPPED"
        self.last_speed = 0.0
        self.speed_threshold = 0.01  # m/s (minimum detectable speed)

        self.get_logger().info('Movement Tracker started - listening on /cmd_vel')

    def velocity_callback(self, msg: Twist):
        """Called when velocity command arrives"""
        try:
            # Extract values
            linear_speed = math.sqrt(
                msg.linear.x**2 +
                msg.linear.y**2 +
                msg.linear.z**2
            )
            angular_speed = math.sqrt(
                msg.angular.x**2 +
                msg.angular.y**2 +
                msg.angular.z**2
            )

            # Determine direction
            if linear_speed < self.speed_threshold:
                if angular_speed < self.speed_threshold:
                    direction = "STOPPED"
                else:
                    direction = "SPINNING"
            else:
                if msg.linear.x > 0:
                    direction = "FORWARD"
                elif msg.linear.x < 0:
                    direction = "BACKWARD"
                elif msg.linear.y > 0:
                    direction = "STRAFE_LEFT"
                else:
                    direction = "STRAFE_RIGHT"

            # Log state changes only (not every message)
            if direction != self.last_direction:
                self.get_logger().info(
                    f'Direction changed: {self.last_direction} → {direction}'
                )
                self.last_direction = direction

            # Log speed changes
            if abs(linear_speed - self.last_speed) > 0.1:
                self.get_logger().debug(
                    f'Speed: {linear_speed:.2f} m/s, '
                    f'Rotation: {angular_speed:.2f} rad/s'
                )
                self.last_speed = linear_speed

        except Exception as e:
            self.get_logger().error(f'Error in velocity callback: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = MovementTrackerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key patterns:**
- State tracking between callbacks
- Filtering redundant messages
- Error handling in callback
- Using math for data interpretation

---

## Example 3: Service Server for Computations

**Scenario**: A robot provides a service to compute inverse kinematics (IK).

```python
#!/usr/bin/env python3
"""
Inverse Kinematics Service - Computes joint angles from target position
Demonstrates: Service server, computation, and response handling
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import math

# Define a custom service message (you'd normally use a .srv file)
from rclpy.impl.rcutils_logger import RcutilsLogger

class IKServiceNode(Node):
    """
    Provides /compute_ik service.
    Takes target position (x, y, z) and returns joint angles.
    Simplified 2-DOF arm simulation.
    """

    def __init__(self):
        super().__init__('ik_service')

        # Robot parameters (2-DOF arm)
        self.link1_length = 0.5  # 50cm
        self.link2_length = 0.3  # 30cm

        # Create service
        # In production, this would use a .srv file
        # For now, we use geometry_msgs for simplicity
        self.service = self.create_service(
            # Would be: CustomIKRequest/CustomIKResponse
            # Here we'll simulate with simple Python
            Pose,  # Simplified
            '/compute_ik',
            self.handle_ik_request
        )

        self.get_logger().info('IK Service ready at /compute_ik')

    def compute_ik_2dof(self, target_x, target_y):
        """
        Compute inverse kinematics for 2-DOF arm.

        Real-world: You'd use a proper IK library (IKPy, PyKDL)
        Here we use simple math for demonstration.
        """
        try:
            # Distance to target
            distance = math.sqrt(target_x**2 + target_y**2)

            # Check if reachable
            max_reach = self.link1_length + self.link2_length
            if distance > max_reach:
                return None  # Unreachable

            # Apply law of cosines to find angles
            # (Simplified - real IK is more complex)
            cos_theta2 = (
                (distance**2 - self.link1_length**2 - self.link2_length**2) /
                (2 * self.link1_length * self.link2_length)
            )

            if cos_theta2 < -1 or cos_theta2 > 1:
                return None  # No solution

            theta2 = math.acos(cos_theta2)

            k1 = self.link1_length + self.link2_length * math.cos(theta2)
            k2 = self.link2_length * math.sin(theta2)

            theta1 = math.atan2(target_y, target_x) - math.atan2(k2, k1)

            return (theta1, theta2)

        except Exception as e:
            self.get_logger().error(f'IK computation error: {e}')
            return None

    def handle_ik_request(self, request, response):
        """Handle IK service request"""
        try:
            self.get_logger().info(
                f'IK request: target=({request.position.x:.2f}, {request.position.y:.2f})'
            )

            # Compute solution
            result = self.compute_ik_2dof(
                request.position.x,
                request.position.y
            )

            if result:
                theta1, theta2 = result
                self.get_logger().info(
                    f'IK solution found: theta1={math.degrees(theta1):.1f}°, '
                    f'theta2={math.degrees(theta2):.1f}°'
                )
                # Set response (simplified)
                response.position.z = 1.0  # Success flag
            else:
                self.get_logger().warn('Target unreachable')
                response.position.z = 0.0  # Failure flag

            return response

        except Exception as e:
            self.get_logger().error(f'Error handling IK request: {e}')
            response.position.z = 0.0
            return response

def main(args=None):
    rclpy.init(args=args)
    node = IKServiceNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key patterns:**
- Service server responding to requests
- Mathematical computations
- Error handling and validation
- Logging computation results

---

## Example 4: Parameter Server Integration

**Scenario**: A node that loads configuration from the parameter server.

```python
#!/usr/bin/env python3
"""
Configurable Robot Node - Uses ROS 2 parameters
Demonstrates: Parameter declarations, callbacks, and dynamic reconfiguration
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter

class ConfigurableRobotNode(Node):
    """
    Demonstrates ROS 2 parameter server usage.
    Can be reconfigured without restart.
    """

    def __init__(self):
        super().__init__('configurable_robot')

        # Declare parameters with defaults
        self.declare_parameter('max_speed', 1.0)  # m/s
        self.declare_parameter('max_angular_velocity', 2.0)  # rad/s
        self.declare_parameter('wheel_radius', 0.1)  # meters
        self.declare_parameter('track_width', 0.5)  # meters
        self.declare_parameter('safety_enabled', True)
        self.declare_parameter('name', 'robot_01')

        # Register callback for parameter changes
        self.add_on_set_parameters_callback(self.parameters_callback)

        # Load initial values
        self.load_parameters()

        self.get_logger().info(f'Robot "{self.robot_name}" configured')
        self.log_current_config()

    def load_parameters(self):
        """Load all parameters from server"""
        self.max_speed = self.get_parameter('max_speed').value
        self.max_angular_vel = self.get_parameter('max_angular_velocity').value
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.track_width = self.get_parameter('track_width').value
        self.safety_enabled = self.get_parameter('safety_enabled').value
        self.robot_name = self.get_parameter('name').value

    def parameters_callback(self, params):
        """Called when parameters are changed"""
        for param in params:
            self.get_logger().info(f'Parameter changed: {param.name} = {param.value}')

            # Validate new values
            if param.name == 'max_speed' and param.value < 0:
                self.get_logger().error('max_speed cannot be negative!')
                return SetParametersResult(successful=False)

            if param.name == 'wheel_radius' and param.value <= 0:
                self.get_logger().error('wheel_radius must be positive!')
                return SetParametersResult(successful=False)

        # Reload all parameters
        self.load_parameters()
        self.log_current_config()

        return SetParametersResult(successful=True)

    def log_current_config(self):
        """Log current configuration"""
        self.get_logger().info(
            f'Configuration: max_speed={self.max_speed} m/s, '
            f'max_angular_vel={self.max_angular_vel} rad/s, '
            f'wheel_radius={self.wheel_radius} m, '
            f'track_width={self.track_width} m, '
            f'safety={self.safety_enabled}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = ConfigurableRobotNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

# To test from command line:
# ros2 param list
# ros2 param get /configurable_robot max_speed
# ros2 param set /configurable_robot max_speed 2.0
```

**Key patterns:**
- Declaring parameters
- Parameter callbacks
- Validation logic
- Dynamic reconfiguration

---

## Example 5: Multi-Node Coordination

**Scenario**: Multiple nodes coordinating through a central coordinator.

```python
#!/usr/bin/env python3
"""
Multi-Node Coordination System
Demonstrates: Multiple publishers, subscribers, and coordination
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Float64
from geometry_msgs.msg import Twist

class CoordinatorNode(Node):
    """
    Central coordinator that:
    - Subscribes to sensor data from multiple sensors
    - Publishes movement commands based on sensor fusion
    """

    def __init__(self):
        super().__init__('coordinator')

        # Subscribers to multiple sensor inputs
        self.distance_sub = self.create_subscription(
            Float64,
            '/sensor/distance',
            self.distance_callback,
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        self.light_sub = self.create_subscription(
            Float64,
            '/sensor/light',
            self.light_callback,
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        # Publisher for movement commands
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        # Internal state
        self.distance = 1.0  # meters
        self.light_level = 0.5  # 0=dark, 1=bright

        self.get_logger().info('Coordinator started')

    def distance_callback(self, msg):
        """Update distance sensor reading"""
        self.distance = msg.data
        self.update_behavior()

    def light_callback(self, msg):
        """Update light sensor reading"""
        self.light_level = msg.data
        self.update_behavior()

    def update_behavior(self):
        """
        Decide movement based on sensor fusion.

        Rules:
        - If close to obstacle: stop and turn
        - If low light: move slowly
        - Otherwise: move forward
        """
        cmd = Twist()

        # Rule 1: Safety first - stop if close to obstacle
        if self.distance < 0.3:  # 30cm
            self.get_logger().warn('Obstacle detected! Stopping.')
            cmd.linear.x = 0.0
            cmd.angular.z = 1.0  # Rotate
        else:
            # Rule 2: Adjust speed based on light
            if self.light_level < 0.3:  # Dark
                cmd.linear.x = 0.2  # Move slowly
                self.get_logger().debug('Low light - moving slowly')
            else:
                cmd.linear.x = 1.0  # Move normally

        self.cmd_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = CoordinatorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key patterns:**
- Multiple subscriptions
- Sensor fusion logic
- Decision making based on multiple inputs
- Publishing commands based on coordinated logic

---

## Using These Examples

### To Run Example 1 (Battery Monitor):
```bash
ros2 run robot_system battery_monitor
# In another terminal:
ros2 topic echo /battery/state
```

### To Run Example 2 (Movement Tracker):
```bash
ros2 run robot_system movement_tracker
# In another terminal:
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}}"
```

### To Run Example 3 (IK Service):
```bash
ros2 run robot_system ik_service
# In another terminal, would call service (needs .srv file in production)
```

### To Run Example 4 (Configurable Robot):
```bash
ros2 run robot_system configurable_robot
# In another terminal:
ros2 param set /configurable_robot max_speed 2.0
```

### To Run Example 5 (Coordinator):
```bash
# Run coordinator
ros2 run robot_system coordinator
# In other terminals, simulate sensors:
ros2 topic pub /sensor/distance std_msgs/msg/Float64 "{data: 0.5}"
ros2 topic pub /sensor/light std_msgs/msg/Float64 "{data: 0.8}"
```

---

## Production Patterns You See Here

✅ Error handling in all callbacks
✅ Logging at appropriate levels
✅ QoS configuration for reliability
✅ Parameter validation
✅ State tracking between messages
✅ Sensor fusion and coordination
✅ Configuration management

Use these patterns in all your ROS 2 code!

---

**Next Section**: Architecture & Diagrams
**Time to Study**: 30 minutes
**Hands-On Time**: 1-2 hours running examples

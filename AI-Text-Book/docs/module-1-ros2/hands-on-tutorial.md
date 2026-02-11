---
sidebar_position: 4
---

# Hands-On Tutorial: Build Your First ROS 2 System

## Goal

In this tutorial, you'll build a complete robot simulation system with:
- ✅ A sensor emulator (publishing fake sensor data)
- ✅ A data processor (subscribing to sensor data)
- ✅ A command interface (using services)
- ✅ A task coordinator (using actions)

By the end, you'll have built a realistic ROS 2 system from scratch.

## Prerequisites

Before starting, ensure you have:
- Ubuntu 22.04 LTS (or similar Linux)
- ROS 2 Jazzy installed
- Python 3.10+
- A text editor (VS Code recommended)
- 1-2 hours of time

### Quick Install Check

```bash
# Verify ROS 2 is installed
ros2 --version

# You should see: ROS 2 Jazzy Jalisco (version X.X.X)
```

## Step 1: Create a ROS 2 Workspace

A workspace is a directory where you organize your ROS 2 packages.

```bash
# Create workspace directory
mkdir -p ~/ros2_textbook_ws/src
cd ~/ros2_textbook_ws

# Create a ROS 2 package
ros2 pkg create --build-type ament_python robot_system

# Navigate into package
cd ~/ros2_textbook_ws/src/robot_system
```

### Workspace Structure

Your workspace should look like:

```
ros2_textbook_ws/
├── src/
│   └── robot_system/
│       ├── robot_system/          # Python package
│       │   ├── __init__.py
│       │   ├── sensor_node.py     # We'll create these
│       │   ├── processor_node.py
│       │   ├── command_server.py
│       │   └── coordinator_node.py
│       ├── setup.py
│       ├── setup.cfg
│       ├── package.xml
│       └── resource/
├── build/                          # Auto-generated
├── install/                        # Auto-generated
└── log/                            # Auto-generated
```

## Step 2: Create the Sensor Node

This node publishes fake sensor data (simulating a temperature sensor).

**File: `robot_system/sensor_node.py`**

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import random
import time

class TemperatureSensorNode(Node):
    """
    Simulates a temperature sensor.
    Publishes temperature readings to /sensor/temperature
    """

    def __init__(self):
        super().__init__('temperature_sensor_node')

        # Create publisher
        self.publisher = self.create_publisher(
            Float64,
            '/sensor/temperature',
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        # Create timer to publish every 500ms
        self.timer = self.create_timer(0.5, self.timer_callback)

        # Base temperature and noise
        self.base_temperature = 25.0  # 25°C
        self.noise_level = 2.0  # ±2°C

        self.get_logger().info('Temperature Sensor Node started')

    def timer_callback(self):
        """Called every 500ms to publish sensor data"""
        # Simulate realistic sensor readings with noise
        temperature = self.base_temperature + random.uniform(
            -self.noise_level,
            self.noise_level
        )

        msg = Float64()
        msg.data = temperature

        self.publisher.publish(msg)
        self.get_logger().debug(f'Publishing temperature: {temperature:.2f}°C')

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureSensorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key concepts here:**
- `create_publisher()`: Creates a publisher on topic `/sensor/temperature`
- `create_timer()`: Calls function every 500ms
- `publish()`: Sends message
- `rclpy.spin()`: Keeps node running

## Step 3: Create the Processor Node

This node subscribes to sensor data and processes it.

**File: `robot_system/processor_node.py`**

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

class TemperatureProcessorNode(Node):
    """
    Subscribes to temperature readings.
    Processes and logs them.
    """

    def __init__(self):
        super().__init__('temperature_processor_node')

        # Create subscriber
        self.subscription = self.create_subscription(
            Float64,
            '/sensor/temperature',
            self.listener_callback,
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        # Track statistics
        self.measurements = []
        self.max_measurements = 20

        self.get_logger().info('Temperature Processor Node started')

    def listener_callback(self, msg):
        """Called when new temperature message arrives"""
        temperature = msg.data

        # Track measurements
        self.measurements.append(temperature)
        if len(self.measurements) > self.max_measurements:
            self.measurements.pop(0)

        # Calculate statistics
        avg_temp = sum(self.measurements) / len(self.measurements)
        max_temp = max(self.measurements)
        min_temp = min(self.measurements)

        # Log results
        self.get_logger().info(
            f'Temperature: {temperature:.2f}°C | '
            f'Avg: {avg_temp:.2f} | '
            f'Min: {min_temp:.2f} | '
            f'Max: {max_temp:.2f}'
        )

        # Alert if temperature is too high
        if temperature > 35.0:
            self.get_logger().warn(f'⚠️  HIGH TEMPERATURE: {temperature:.2f}°C')
        elif temperature < 15.0:
            self.get_logger().warn(f'❄️  LOW TEMPERATURE: {temperature:.2f}°C')

def main(args=None):
    rclpy.init(args=args)
    node = TemperatureProcessorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key concepts:**
- `create_subscription()`: Subscribes to `/sensor/temperature`
- `listener_callback()`: Called when new message arrives
- Maintains moving average of measurements

## Step 4: Create the Command Service

This node provides a service to reset the sensor.

**File: `robot_system/command_server.py`**

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger  # Empty request, bool response

class CommandServerNode(Node):
    """
    Provides services for system commands.
    Service: /reset_sensor - resets the sensor state
    """

    def __init__(self):
        super().__init__('command_server_node')

        # Create service
        self.service = self.create_service(
            Trigger,  # Trigger is an empty request
            '/reset_sensor',
            self.handle_reset_sensor
        )

        # Internal state
        self.sensor_resets = 0

        self.get_logger().info('Command Server started')
        self.get_logger().info('Service /reset_sensor is available')

    def handle_reset_sensor(self, request, response):
        """Handle reset sensor service call"""
        self.sensor_resets += 1

        self.get_logger().info(f'Sensor reset #{self.sensor_resets}')

        # Set response
        response.success = True
        response.message = f'Sensor reset successfully (reset #{self.sensor_resets})'

        return response

def main(args=None):
    rclpy.init(args=args)
    node = CommandServerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**Key concepts:**
- `create_service()`: Creates service endpoint
- `Trigger`: Built-in ROS message type (no parameters)
- Service handler receives request, returns response

## Step 5: Update setup.py

Configure your package to install the nodes:

**File: `setup.py`**

```python
from setuptools import setup, find_packages

setup(
    name='robot_system',
    version='1.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_cmake_core/cmake/ament_cmake_export_libraries', []),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Your Name',
    author_email='your.email@example.com',
    maintainer='Your Name',
    description='ROS 2 Textbook - Robot System Example',
    license='MIT',
    entry_points={
        'console_scripts': [
            'sensor_node = robot_system.sensor_node:main',
            'processor_node = robot_system.processor_node:main',
            'command_server = robot_system.command_server:main',
        ],
    },
)
```

## Step 6: Build Your Workspace

```bash
# Navigate to workspace root
cd ~/ros2_textbook_ws

# Build the package
colcon build

# Source the installation
source install/setup.bash

# Verify everything compiled
ls install/robot_system/lib/python*/site-packages/robot_system/
```

## Step 7: Run the System

Open three terminal windows. In each, source the workspace first:

```bash
cd ~/ros2_textbook_ws
source install/setup.bash
```

**Terminal 1: Run the Sensor Node**
```bash
ros2 run robot_system sensor_node
```

**Terminal 2: Run the Processor Node**
```bash
ros2 run robot_system processor_node
```

**Terminal 3: Run the Command Server**
```bash
ros2 run robot_system command_server
```

### Expected Output

**Terminal 1 (Sensor):**
```
[INFO] Temperature Sensor Node started
[DEBUG] Publishing temperature: 24.32°C
[DEBUG] Publishing temperature: 25.78°C
...
```

**Terminal 2 (Processor):**
```
[INFO] Temperature Processor Node started
[INFO] Temperature: 24.32°C | Avg: 24.32 | Min: 24.32 | Max: 24.32
[INFO] Temperature: 25.78°C | Avg: 25.05 | Min: 24.32 | Max: 25.78
```

**Terminal 3 (Command Server):**
```
[INFO] Command Server started
[INFO] Service /reset_sensor is available
```

## Step 8: Interact with the System

Open a fourth terminal to call the service and inspect the system:

```bash
cd ~/ros2_textbook_ws
source install/setup.bash

# Call the reset service
ros2 service call /reset_sensor std_srvs/srv/Trigger

# View active nodes
ros2 node list

# View active topics
ros2 topic list

# Listen to temperature messages
ros2 topic echo /sensor/temperature

# View services
ros2 service list
```

## Step 9: Visualize with RQT

RQT is a graphical tool for ROS 2:

```bash
# View the system graph
rqt_graph

# View message data
rqt_topic

# View node information
rqt_node_graph
```

---

## What You've Built

Congratulations! You've created a real ROS 2 system with:

✅ **Publisher Node** - Generates sensor data
✅ **Subscriber Node** - Processes sensor data
✅ **Service Server** - Responds to commands
✅ **Communication** - Nodes communicating via ROS 2 middleware

This is the same architecture used in real robots, just simpler for learning.

---

## Common Errors and Solutions

### Error: "Cannot find module 'robot_system'"
**Solution**: Make sure you sourced the setup:
```bash
source ~/ros2_textbook_ws/install/setup.bash
```

### Error: "Node does not exist"
**Solution**: Make sure you built the package:
```bash
cd ~/ros2_textbook_ws
colcon build
```

### Error: "Topic not found"
**Solution**: Make sure all nodes are running:
```bash
ros2 node list  # Should show all three nodes
```

---

## Next Steps

Now that you understand the basics:
1. Modify the sensor to publish different data
2. Add a second sensor to your system
3. Create a new processor that subscribes to both sensors
4. Add more services

---

**Next Section**: Code Examples
**Time to Complete**: 1-2 hours hands-on
**Key Skill**: You can now build basic ROS 2 systems from scratch

---

## Summary

You've gone from zero to building a working ROS 2 system:
- ✅ Created nodes in Python
- ✅ Implemented pub-sub communication
- ✅ Built a service endpoint
- ✅ Compiled and ran the system
- ✅ Interacted with running nodes

This is the foundation for everything more complex in ROS 2.

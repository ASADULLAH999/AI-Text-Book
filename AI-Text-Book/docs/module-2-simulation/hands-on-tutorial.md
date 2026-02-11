---
sidebar_position: 12
---

# Hands-On Tutorial: Your First Gazebo Simulation

## Goal

In this tutorial, you'll:
1. ✅ Install Gazebo on your system
2. ✅ Load a pre-built robot model (TurtleBot3)
3. ✅ Create a simple world with obstacles
4. ✅ Add sensors to the robot
5. ✅ Connect Gazebo to ROS 2
6. ✅ Subscribe to simulated sensor data
7. ✅ Control the robot from ROS 2

By the end, you'll have a fully functional simulation that publishes sensor data on ROS 2 topics—just like Module 1, but with simulated data instead of real hardware.

---

## Prerequisites

Before starting, verify you have:

```bash
# Check ROS 2 is installed
ros2 --version
# Expected: ROS 2 Jazzy Jalisco (or similar)

# Check Python 3
python3 --version
# Expected: Python 3.10+

# Check colcon (build system)
colcon --version
# Expected: colcon command-line tool X.X.X
```

If any of these are missing, refer to the ROS 2 Jazzy installation guide.

---

## Step 1: Install Gazebo

### Ubuntu/Linux Installation

```bash
# Add Gazebo repository
sudo apt-get update
sudo apt-get install -y wget lsb-release gnupg

# Get latest Gazebo (version 8+)
sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# Install Gazebo
sudo apt-get update
sudo apt-get install -y gazebo-8

# Install Gazebo ROS 2 packages
sudo apt-get install -y ros-jazzy-gazebo-ros
sudo apt-get install -y ros-jazzy-gazebo-ros-pkgs
sudo apt-get install -y ros-jazzy-gazebo-ros2-control

# Verify installation
gazebo --version
```

### macOS Installation

```bash
# Using Homebrew
brew tap osrf/simulation
brew install gazebo8 gazebo-8
```

### Verification

```bash
# Launch Gazebo
gazebo

# You should see the Gazebo GUI open with an empty world
# Close Gazebo (Ctrl+C in terminal)
```

---

## Step 2: Install TurtleBot3 Package

We'll use TurtleBot3 (a popular mobile robot) as our simulation platform.

```bash
# Install TurtleBot3 packages
sudo apt-get install -y ros-jazzy-turtlebot3*

# Install TurtleBot3 models (robot descriptions)
sudo apt-get install -y ros-jazzy-turtlebot3-msgs
sudo apt-get install -y ros-jazzy-turtlebot3-simulations

# Set the TurtleBot3 model (we'll use waffle)
export TURTLEBOT3_MODEL=waffle

# Verify installation
ros2 pkg find turtlebot3_gazebo
# Expected: /opt/ros/jazzy/share/turtlebot3_gazebo
```

---

## Step 3: Launch Gazebo with TurtleBot3

### Terminal 1: Gazebo Server

Source ROS 2 and launch Gazebo with TurtleBot3:

```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle

# Launch Gazebo with TurtleBot3 in empty world
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Expected output**:
```
[INFO] Launching: /opt/ros/jazzy/share/turtlebot3_gazebo/launch/turtlebot3_world.launch.py
[INFO] [launch]: Starting Gazebo server...
[INFO] [launch]: Spawning robot...
```

You should see:
- Gazebo window opens with a room/warehouse environment
- TurtleBot3 robot (yellow rectangular robot) in the center
- Walls, tables, and obstacles around

**Keep this terminal running** (it's the Gazebo server).

### Terminal 2: Gazebo Client (Visualization)

In a new terminal, open the Gazebo GUI client:

```bash
source /opt/ros/jazzy/setup.bash
gzclient
```

Now you can see the 3D visualization and interact with the simulation (rotate view, zoom, etc.).

---

## Step 4: Verify ROS 2 Topics from Gazebo

### Terminal 3: List ROS 2 Topics

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```

**Expected output**:
```
/camera/image_raw
/camera/camera_info
/imu
/joint_states
/odom
/scan
/tf
/tf_static
/cmd_vel
```

These are the topics Gazebo is publishing! Let's examine a few:

### View Joint States

```bash
ros2 topic echo /joint_states --once
```

**Output**:
```yaml
header:
  stamp:
    sec: 10
    nsec: 123456789
  frame_id: ''
name:
- wheel_left_joint
- wheel_right_joint
- caster_back_joint
- caster_front_joint
position: [-0.1, 0.1, 0.05, -0.05]
velocity: [0.0, 0.0, 0.0, 0.0]
effort: [0.0, 0.0, 0.0, 0.0]
```

This shows the current joint positions and velocities!

### View Odometry

```bash
ros2 topic echo /odom --once
```

**Output**:
```yaml
header:
  frame_id: odom
pose:
  pose:
    position: [0.0, 0.0, 0.0]
    orientation: [0.0, 0.0, 0.0, 1.0]
```

The robot's estimated position from odometry (initially at origin).

### View LiDAR Scan

```bash
ros2 topic echo /scan --once
```

Shows 360° LiDAR scan (360 distance measurements around the robot).

---

## Step 5: Control the Robot via ROS 2

The robot responds to velocity commands on `/cmd_vel` topic.

### Send Movement Command

```bash
# Move forward (linear velocity: 0.5 m/s, no rotation)
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

**In Gazebo**, you should see:
- TurtleBot3 moves forward
- Continues moving while command is published
- Stops when you stop publishing

### Rotate in Place

```bash
# Rotate counter-clockwise (angular velocity: 0.5 rad/s)
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"
```

The robot should spin in place.

### Stop the Robot

Press `Ctrl+C` to stop publishing commands, or publish zero velocity:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

---

## Step 6: Visualize with RViz

RViz is a visualization tool that shows the robot's perception of the world.

### Terminal 4: Launch RViz

```bash
source /opt/ros/jazzy/setup.bash
rviz2
```

**Configure RViz**:
1. In the "Fixed Frame" dropdown, select `odom`
2. Click "Add" button (bottom-left)
3. Select `RobotModel` to see the robot
4. Click "Add" again
5. Select `LaserScan` to visualize LiDAR
6. Set LaserScan topic to `/scan`

Now you should see:
- The robot model (yellow box with wheels)
- The LiDAR point cloud (red dots showing walls and obstacles)

As the robot moves, the point cloud updates in real-time!

---

## Step 7: Record Sensor Data with rosbag

Now let's record the simulation sensor data to a file (like in Module 1).

### Terminal 5: Record All Topics

```bash
source /opt/ros/jazzy/setup.bash

# Create directory for recordings
mkdir -p ~/gazebo_bags

# Record all topics
cd ~/gazebo_bags
ros2 bag record -a

# Let it record for 10 seconds
# (make the robot move during recording for interesting data)
```

**In Terminal 3**, while recording, send movement commands:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.1}}"
```

After 10 seconds, press `Ctrl+C` in the recording terminal.

### Playback Recording

```bash
cd ~/gazebo_bags

# List recorded files
ls -la

# Play back (this replays all published topics)
ros2 bag play rosbag2_*
```

Now in RViz, you'll see the **recorded** robot trajectory playing back!

---

## Step 8: Create Your Own World

Create a custom Gazebo world file with obstacles.

**File**: `~/my_world.sdf`

```xml
<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="my_warehouse">
    <!-- Physics engine -->
    <physics name="default_physics" default="true" type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
    </physics>

    <!-- Lighting -->
    <light name="sun" type="directional">
      <cast_shadows>true</cast_shadows>
      <pose>5 10 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <linear>0.01</linear>
        <constant>0.1</constant>
        <quadratic>0.0</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

    <!-- Simple wall obstacle -->
    <model name="wall_1">
      <static>true</static>
      <pose>2 0 0 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.1 2 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.1 2 1</size>
            </box>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Wood</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

    <!-- Table model -->
    <model name="table">
      <static>true</static>
      <pose>-1 1 0 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 0.7</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 0.7</size>
            </box>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

### Launch with Your World

```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle

# Create launch file
cat > /tmp/my_sim.launch.py << 'EOF'
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import ThisLaunchFileDir
import os

def generate_launch_description():
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            '/opt/ros/jazzy/share/gazebo_ros/launch/gazebo.launch.py'
        ),
        launch_arguments=[('world', os.path.expanduser('~/my_world.sdf'))]
    )

    return LaunchDescription([gazebo])
EOF

# Run it
ros2 launch /tmp/my_sim.launch.py
```

Now Gazebo opens with your custom world!

---

## Step 9: Integrate with Your Module 1 Code

Remember the processor node from Module 1? Let's feed it simulated data instead of real sensors!

**File**: `~/ros2_ws/src/robot_system/robot_system/simulation_processor.py`

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import math

class SimulationProcessorNode(Node):
    """
    Process simulated sensor data from Gazebo.
    Subscribes to:
    - /scan (LiDAR from Gazebo)
    - /odom (Odometry from Gazebo)
    """

    def __init__(self):
        super().__init__('simulation_processor_node')

        # Subscribe to simulated LiDAR
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        # Subscribe to simulated odometry
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            qos_profile=rclpy.qos.QoSProfile(depth=10)
        )

        self.get_logger().info('Simulation Processor started')

    def lidar_callback(self, msg):
        """Process simulated LiDAR data"""
        # Find closest obstacle
        min_distance = float('inf')
        for i, distance in enumerate(msg.ranges):
            if distance > msg.range_min and distance < msg.range_max:
                if distance < min_distance:
                    min_distance = distance

        if min_distance < float('inf'):
            self.get_logger().info(f'Closest obstacle: {min_distance:.2f}m')

            if min_distance < 0.3:
                self.get_logger().warn('⚠️ OBSTACLE VERY CLOSE!')
        else:
            self.get_logger().info('No obstacles detected')

    def odom_callback(self, msg):
        """Process simulated odometry"""
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        # Extract orientation (quaternion to angle)
        quat = msg.pose.pose.orientation
        # Simple heading from quaternion
        heading = 2 * math.atan2(quat.z, quat.w)

        self.get_logger().info(
            f'Robot pose: x={x:.2f}, y={y:.2f}, θ={heading:.2f}rad'
        )

def main(args=None):
    rclpy.init(args=args)
    node = SimulationProcessorNode()

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

### Run Both Together

**Terminal 5**: Launch simulation
```bash
source /opt/ros/jazzy/setup.bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Terminal 6**: Run your processor node
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 run robot_system simulation_processor
```

**Expected output**:
```
[INFO] Simulation Processor started
[INFO] Robot pose: x=0.00, y=0.00, θ=0.00rad
[INFO] Closest obstacle: 1.23m
[INFO] Closest obstacle: 1.22m
...
```

You're now processing **simulated sensor data** with your **Module 1 ROS 2 code**!

---

## Step 10: Common Errors & Solutions

### Error: "gazebo: command not found"

**Solution**: Gazebo not installed or not in PATH
```bash
which gazebo
# If empty, reinstall: sudo apt-get install gazebo-8
```

### Error: "Could not load world" (SDF file error)

**Solution**: Check SDF syntax
```bash
# Validate SDF file
gz sdf --check ~/my_world.sdf
```

### Error: "/scan topic not found"

**Solution**: Gazebo hasn't initialized yet
- Wait 5 seconds for Gazebo to start
- Check if `gzclient` is running: `ros2 node list`

### Error: "TurtleBot3 doesn't move when I publish to /cmd_vel"

**Solution**: Controller might not be active
```bash
# Check if controller is running
ros2 node list | grep controller

# If missing, the gazebo_ros2_control plugin didn't load
# Verify: ros2 topic list should show many turtlebot topics
```

### Gazebo Runs Slowly

**Solution**: Disable graphics or reduce physics frequency
```bash
# Run with server only (no visualization)
gazebo --verbose --server-only

# Or use gzclient on separate machine
```

---

## What You've Accomplished

✅ Installed Gazebo and ROS 2 simulation packages
✅ Launched TurtleBot3 in a pre-made world
✅ Controlled the robot with ROS 2 commands
✅ Subscribed to simulated sensor topics
✅ Visualized sensor data with RViz
✅ Recorded and played back sensor data
✅ Created a custom simulation world
✅ Integrated simulated sensors with your Module 1 code

You now have the **core skill for simulation development**: connecting physical algorithms (your ROS 2 code) to virtual sensors (Gazebo).

---

## Next Steps

1. **Experiment**: Try different Gazebo worlds from ros-simulations package
2. **Customize**: Create your own world with different obstacles
3. **Add Sensors**: Add RGB-D camera, additional LiDARs, force sensors
4. **Learn Models**: Download humanoid robot models and simulate them
5. **Advanced**: Study the code examples in the next section

---

**Next Section**: Code Examples - Advanced Simulation Integration
**Time to Read**: 90 minutes
**Hands-On Setup Time**: 1-2 hours

---

*Last Updated: 2026-01-20*
*Module Version: 1.0*

---
sidebar_position: 4
---

# Hands-On Tutorial: Building the Capstone System

## Overview: Building "Humanoid Kitchen Assistant"

In this tutorial, you'll build a complete voice-controlled humanoid robot system. The project has four main phases:

1. **Voice Recognition** - Listen and transcribe
2. **Command Parsing** - Understand intent
3. **Motion Execution** - Execute on simulated humanoid
4. **Integration & Testing** - Full system end-to-end

### Architecture

```
SYSTEM ARCHITECTURE:

User → Microphone → [Whisper STT] → Text
                         ↓
                    [NLP Parser]
                         ↓
User Feedback ← [LLM Reasoning] ← World State
                         ↓
              [Motion Planning] (Isaac)
                         ↓
          [Humanoid Control] (ROS 2 + Isaac)
                         ↓
          Simulated Robot Executes Task
```

---

## Phase 1: Setup (0-1 hour)

### Step 1: Install Dependencies

```bash
# Core dependencies
pip install openai-whisper transformers torch torchaudio
pip install rclpy ros2-numpy rosgraph

# Audio processing
pip install numpy scipy librosa pyaudio

# Humanoid simulation
pip install isaacgym pybullet urdf_parser_py

# LLM (using Ollama for local LLMs)
# Install from https://ollama.ai or use API

# Verification
python3 << 'EOF'
import whisper
import torch
print(f"PyTorch: {torch.__version__}")
print(f"GPU available: {torch.cuda.is_available()}")
print("✓ All dependencies installed")
EOF
```

### Step 2: Download Models

```bash
# Whisper model (base size = 74MB, ~100ms inference)
python3 << 'EOF'
import whisper
model = whisper.load_model("base")
print("✓ Whisper model downloaded")
EOF

# Humanoid URDF (UR10e + humanoid torso)
mkdir -p ~/.local/robots
wget -O ~/.local/robots/humanoid.urdf \
  https://raw.githubusercontent.com/humanoids-io/models/main/humanoid.urdf
```

### Step 3: Verify Setup

```bash
# Test voice input
python3 << 'EOF'
import pyaudio
import numpy as np

p = pyaudio.PyAudio()
print(f"Default audio device: {p.get_default_input_device_info()['name']}")

# Test Whisper
import whisper
model = whisper.load_model("base")
print("✓ Whisper model loaded and ready")

# Test ROS 2
import rclpy
rclpy.init()
print("✓ ROS 2 initialized")
EOF
```

---

## Phase 2: Voice Recognition (1-2 hours)

### Create Speech Recognizer Node

```python
#!/usr/bin/env python3
"""
SpeechRecognizer: Real-time voice-to-text
Captures audio and transcribes using Whisper
"""

import queue
import threading
import numpy as np
import whisper
import pyaudio
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SpeechRecognizer(Node):
    def __init__(self):
        super().__init__('speech_recognizer')

        # Whisper model
        self.model = whisper.load_model("base")
        self.get_logger().info("✓ Whisper model loaded")

        # Audio recording parameters
        self.CHUNK = 1024  # Samples per frame
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1  # Mono
        self.RATE = 16000  # Hz

        # Audio buffer
        self.audio_queue = queue.Queue()

        # ROS 2 publisher
        self.command_pub = self.create_publisher(
            String,
            '/speech/transcription',
            10
        )

        # Start recording thread
        self.is_recording = True
        self.record_thread = threading.Thread(target=self._record_audio)
        self.record_thread.daemon = True
        self.record_thread.start()

        # Start transcription thread
        self.transcribe_thread = threading.Thread(target=self._transcribe_audio)
        self.transcribe_thread.daemon = True
        self.transcribe_thread.start()

        self.get_logger().info("✓ Speech recognizer started")

    def _record_audio(self):
        """Continuously record audio in background"""
        p = pyaudio.PyAudio()

        stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )

        self.get_logger().info("🎤 Listening...")

        try:
            while self.is_recording:
                data = stream.read(self.CHUNK)
                audio_data = np.frombuffer(data, dtype=np.float32)
                self.audio_queue.put(audio_data)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def _transcribe_audio(self):
        """Transcribe audio when user stops speaking"""
        audio_buffer = []
        silence_count = 0
        silence_threshold = 5  # Frames of silence to trigger transcription

        while self.is_recording:
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)

                # Detect silence (RMS energy)
                rms = np.sqrt(np.mean(audio_chunk**2))

                if rms < 0.01:  # Silent frame
                    silence_count += 1
                else:  # Sound detected
                    silence_count = 0
                    audio_buffer.append(audio_chunk)

                # Trigger transcription after 5 frames of silence
                if silence_count > silence_threshold and len(audio_buffer) > 0:
                    audio_data = np.concatenate(audio_buffer)

                    # Transcribe
                    result = self.model.transcribe(audio_data)
                    transcription = result["text"]

                    # Publish
                    msg = String()
                    msg.data = transcription
                    self.command_pub.publish(msg)

                    self.get_logger().info(f"🗣️  {transcription}")

                    # Reset buffers
                    audio_buffer = []
                    silence_count = 0

            except queue.Empty:
                continue

def main(args=None):
    rclpy.init(args=args)
    node = SpeechRecognizer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.is_recording = False
        node.get_logger().info("Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Test Voice Recognition

```bash
# Terminal 1: Run speech recognizer
python3 speech_recognizer.py

# Terminal 2: Monitor output
ros2 topic echo /speech/transcription

# Say something: "Make a sandwich"
# Expected output: "make a sandwich"
```

---

## Phase 3: Command Parsing (2-3 hours)

### Create NLP Command Parser

```python
#!/usr/bin/env python3
"""
CommandParser: Extract intent and entities from text
"""

import json
import re
from typing import Dict, List
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import JSON  # (use custom message in real code)

class CommandParser(Node):
    def __init__(self):
        super().__init__('command_parser')

        # Define intents and extraction patterns
        self.intent_patterns = {
            'RETRIEVE': {
                'patterns': ['get', 'bring', 'fetch', 'grab'],
                'entities': ['object', 'location']
            },
            'PREPARE': {
                'patterns': ['make', 'prepare', 'cook'],
                'entities': ['object', 'ingredients']
            },
            'PLACE': {
                'patterns': ['put', 'place', 'set down'],
                'entities': ['object', 'location']
            },
            'NAVIGATE': {
                'patterns': ['go to', 'move to', 'navigate'],
                'entities': ['location']
            },
            'QUESTION': {
                'patterns': ['where', 'what', 'how', 'which'],
                'entities': ['subject']
            }
        }

        # Known objects and locations
        self.known_objects = ['sandwich', 'coffee', 'cup', 'bread', 'cheese', 'water']
        self.known_locations = ['kitchen', 'table', 'counter', 'fridge', 'sink']

        # Subscriber
        self.create_subscription(
            String,
            '/speech/transcription',
            self.parse_command,
            10
        )

        # Publisher
        self.command_pub = self.create_publisher(
            String,  # Should be custom message
            '/commands/parsed',
            10
        )

        self.get_logger().info("✓ Command parser started")

    def parse_command(self, msg):
        """Parse transcribed text into structured command"""
        text = msg.data.lower()

        # Detect intent
        intent = self._detect_intent(text)

        # Extract entities
        entities = self._extract_entities(text)

        # Create command
        command = {
            'text': text,
            'intent': intent,
            'entities': entities,
            'confidence': 0.85  # Placeholder
        }

        self.get_logger().info(f"Parsed: {json.dumps(command)}")

        # Publish
        cmd_msg = String()
        cmd_msg.data = json.dumps(command)
        self.command_pub.publish(cmd_msg)

    def _detect_intent(self, text: str) -> str:
        """Identify command intent"""
        for intent, config in self.intent_patterns.items():
            for pattern in config['patterns']:
                if pattern in text:
                    return intent
        return 'UNKNOWN'

    def _extract_entities(self, text: str) -> Dict:
        """Extract named entities"""
        entities = {}

        # Find objects
        for obj in self.known_objects:
            if obj in text:
                entities['object'] = obj
                break

        # Find locations
        for loc in self.known_locations:
            if loc in text:
                entities['location'] = loc
                break

        return entities

def main(args=None):
    rclpy.init(args=args)
    node = CommandParser()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Test Command Parsing

```bash
# Terminal 1: Run speech recognizer
python3 speech_recognizer.py

# Terminal 2: Run command parser
python3 command_parser.py

# Terminal 3: Monitor output
ros2 topic echo /commands/parsed

# Say: "Bring me coffee from the kitchen"
# Expected:
# intent: RETRIEVE
# object: coffee
# location: kitchen
```

---

## Phase 4: Motion Execution (3-4 hours)

### Create Humanoid Motion Controller

```python
#!/usr/bin/env python3
"""
HumanoidController: Execute commands on humanoid robot
"""

import json
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from sensor_msgs.msg import JointState
import pybullet as p
import pybullet_data

class HumanoidController(Node):
    def __init__(self):
        super().__init__('humanoid_controller')

        # Physics simulation
        self.client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

        # Load humanoid
        self.humanoid_id = p.loadURDF(
            "humanoid.urdf",
            [0, 0, 0]
        )

        self.get_logger().info("✓ Humanoid loaded in simulation")

        # Robot state
        self.num_joints = p.getNumJoints(self.humanoid_id)
        self.current_positions = np.zeros(self.num_joints)

        # Command subscriber
        self.create_subscription(
            String,
            '/commands/parsed',
            self.execute_command,
            10
        )

        # Joint state publisher
        self.state_pub = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        # Control loop timer
        self.create_timer(0.01, self.control_loop)  # 100Hz

        self.get_logger().info("✓ Humanoid controller ready")

    def execute_command(self, msg):
        """Execute parsed command on humanoid"""
        try:
            command = json.loads(msg.data)
            intent = command.get('intent')
            entities = command.get('entities', {})

            self.get_logger().info(f"Executing: {intent} {entities}")

            if intent == 'RETRIEVE':
                self._execute_retrieve(entities)
            elif intent == 'PREPARE':
                self._execute_prepare(entities)
            elif intent == 'NAVIGATE':
                self._execute_navigate(entities)
            # ... other intents

        except Exception as e:
            self.get_logger().error(f"Execution error: {e}")

    def _execute_retrieve(self, entities):
        """Execute retrieve task (grasp and bring object)"""
        object_name = entities.get('object', 'unknown')
        self.get_logger().info(f"Retrieving {object_name}...")

        # Simplified example: raise arm
        # In production: full manipulation pipeline (Module 3)
        target_angles = {
            'shoulder_pan': 0.0,
            'shoulder_lift': -1.57,
            'elbow': -1.57,
            'wrist': 0.0
        }

        # Apply target angles
        for joint_name, angle in target_angles.items():
            # Find joint index
            for i in range(self.num_joints):
                info = p.getJointInfo(self.humanoid_id, i)
                if joint_name.encode() in info[1]:
                    p.setJointMotorControl2(
                        self.humanoid_id, i,
                        p.POSITION_CONTROL,
                        targetPosition=angle,
                        force=500
                    )
                    break

    def _execute_prepare(self, entities):
        """Execute prepare task (e.g., make sandwich)"""
        object_name = entities.get('object', 'unknown')
        self.get_logger().info(f"Preparing {object_name}...")
        # Complex manipulation sequence

    def _execute_navigate(self, entities):
        """Execute navigation task"""
        location = entities.get('location', 'unknown')
        self.get_logger().info(f"Navigating to {location}...")
        # Use Isaac motion planning (Module 3)

    def control_loop(self):
        """100Hz control loop"""
        # Step simulation
        p.stepSimulation()

        # Publish joint states
        self._publish_joint_states()

    def _publish_joint_states(self):
        """Publish current joint states"""
        msg = JointState()
        msg.name = []
        msg.position = []
        msg.velocity = []

        for i in range(self.num_joints):
            state = p.getJointState(self.humanoid_id, i)
            msg.position.append(state[0])
            msg.velocity.append(state[1])
            msg.name.append(f"joint_{i}")

        self.state_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = HumanoidController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        p.disconnect()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## Phase 5: Integration & Testing (4-5 hours)

### Launch Full System

```python
# capstone_launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='capstone',
            executable='speech_recognizer.py',
            name='speech_recognizer',
            output='screen'
        ),
        Node(
            package='capstone',
            executable='command_parser.py',
            name='command_parser',
            output='screen'
        ),
        Node(
            package='capstone',
            executable='humanoid_controller.py',
            name='humanoid_controller',
            output='screen'
        ),
    ])
```

### End-to-End Testing

```bash
# Launch entire system
ros2 launch capstone capstone_launch.py

# Test flow
echo "Say: 'Bring me coffee'"
# Should see:
#  1. Speech recognized
#  2. Command parsed
#  3. Robot executes motion
#  4. Success feedback
```

---

## Capstone Milestones Checklist

- [ ] **Phase 1** (1h): All dependencies installed, models downloaded
- [ ] **Phase 2** (1h): Voice recognition working, transcriptions accurate
- [ ] **Phase 3** (1h): Command parsing extracting intents and entities
- [ ] **Phase 4** (1h): Humanoid responding to simple commands
- [ ] **Phase 5** (2h): Full system integrated and tested
- [ ] **Final** (2h): Performance optimized, safety tested, demo video created

---

**Next Section**: Code Examples
**Time**: 3-5 hours
**Difficulty**: Advanced

*Last Updated: 2026-01-20*

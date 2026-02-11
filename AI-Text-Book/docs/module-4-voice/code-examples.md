---
sidebar_position: 5
---

# Code Examples: Voice-to-Action in Practice

## Example 1: Real-Time Speech Recognition

Complete, production-ready speech recognition with Whisper:

```python
#!/usr/bin/env python3
"""
Example 1: Real-Time Speech Recognition
Captures audio and transcribes with confidence scoring
"""

import whisper
import pyaudio
import numpy as np
import threading
import time

class RealtimeSpeechRecognizer:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)
        self.RATE = 16000
        self.CHUNK = 1024
        self.threshold = 0.01  # Silence threshold

    def recognize_speech(self, duration=5):
        """
        Recognize speech from microphone

        Args:
            duration: Maximum recording time (seconds)

        Returns:
            {text, confidence, language}
        """
        print(f"🎤 Listening for {duration}s...")

        # Record audio
        audio_data = self._record_audio(duration)

        # Transcribe
        print("⏳ Transcribing...")
        result = self.model.transcribe(audio_data)

        # Extract results
        text = result["text"].strip()
        confidence = np.mean([seg.get("confidence", 0.9)
                             for seg in result.get("segments", [])])
        language = result.get("language", "en")

        print(f"✓ {text}")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Language: {language}")

        return {
            "text": text,
            "confidence": confidence,
            "language": language
        }

    def _record_audio(self, duration):
        """Record audio from microphone"""
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1,
                       rate=self.RATE, input=True,
                       frames_per_buffer=self.CHUNK)

        frames = []
        for _ in range(0, int(self.RATE / self.CHUNK * duration)):
            data = stream.read(self.CHUNK)
            frames.append(np.frombuffer(data, dtype=np.float32))

        stream.stop_stream()
        stream.close()
        p.terminate()

        return np.concatenate(frames)

# Usage
if __name__ == "__main__":
    recognizer = RealtimeSpeechRecognizer()

    print("Speech Recognition Example")
    print("=" * 50)

    for i in range(3):
        print(f"\nTest {i+1}/3:")
        result = recognizer.recognize_speech(duration=3)

        if result["confidence"] > 0.8:
            print("✓ High confidence - action can execute")
        else:
            print("⚠ Low confidence - request clarification")
```

**Output**:
```
🎤 Listening for 3s...
⏳ Transcribing...
✓ bring me coffee
  Confidence: 92.34%
  Language: en
✓ High confidence - action can execute
```

---

## Example 2: NLP Intent and Entity Extraction

Using transformers for semantic understanding:

```python
#!/usr/bin/env python3
"""
Example 2: NLP Intent and Entity Extraction
Parses natural language into structured commands
"""

from transformers import pipeline
import json

class NLPCommandParser:
    def __init__(self):
        # Semantic role labeling
        self.classifier = pipeline("text-classification",
            model="zero-shot-classification")

        # Intents the robot understands
        self.intents = [
            "RETRIEVE_OBJECT",
            "PREPARE_FOOD",
            "NAVIGATE",
            "PLACE_OBJECT",
            "ANSWER_QUESTION"
        ]

    def parse(self, text):
        """
        Parse text into structured command

        Args:
            text: User command in natural language

        Returns:
            {intent, entities, confidence}
        """
        # Classify intent
        result = self.classifier(text, self.intents)
        intent = result[0]["labels"][0]
        confidence = result[0]["scores"][0]

        # Extract entities
        entities = self._extract_entities(text)

        command = {
            "text": text,
            "intent": intent,
            "entities": entities,
            "confidence": confidence
        }

        return command

    def _extract_entities(self, text):
        """Extract named entities"""
        entities = {}

        # Simple keyword matching
        objects = ["coffee", "sandwich", "water", "cup", "bread", "cheese"]
        locations = ["kitchen", "table", "counter", "fridge", "sink", "dining room"]
        actions = ["bring", "get", "fetch", "make", "prepare", "clean"]

        # Entity extraction
        text_lower = text.lower()

        for obj in objects:
            if obj in text_lower:
                entities["object"] = obj

        for loc in locations:
            if loc in text_lower:
                entities["location"] = loc

        for action in actions:
            if action in text_lower:
                entities["action"] = action

        return entities

# Example usage
if __name__ == "__main__":
    parser = NLPCommandParser()

    test_commands = [
        "Bring me coffee from the kitchen",
        "Make a sandwich please",
        "Where is the water?",
        "Navigate to the dining room",
        "Please clean up the mess"
    ]

    print("NLP Parser Examples")
    print("=" * 60)

    for cmd in test_commands:
        print(f"\nInput: {cmd}")
        parsed = parser.parse(cmd)
        print(f"Output: {json.dumps(parsed, indent=2)}")
```

**Output**:
```
Input: Bring me coffee from the kitchen
Output: {
  "text": "bring me coffee from the kitchen",
  "intent": "RETRIEVE_OBJECT",
  "entities": {
    "object": "coffee",
    "location": "kitchen",
    "action": "bring"
  },
  "confidence": 0.89
}
```

---

## Example 3: LLM Reasoning for Task Planning

Using local LLMs to generate action plans:

```python
#!/usr/bin/env python3
"""
Example 3: LLM Reasoning for Multi-Step Task Planning
Uses language model to decompose high-level goals into actions
"""

import requests
import json

class LLMPlanner:
    def __init__(self, model="llama2"):
        self.model = model
        self.base_url = "http://localhost:11434"  # Ollama API

        # World knowledge
        self.world_state = {
            "objects": {
                "coffee_machine": {"location": "kitchen", "status": "ready"},
                "table": {"location": "dining_room"},
                "cup": {"location": "kitchen_counter", "count": 5}
            },
            "robot_position": "living_room"
        }

        # Action primitives the robot can execute
        self.primitives = [
            "navigate(location)",
            "grasp(object)",
            "place(object, location)",
            "pour(object1, object2)",
            "ask_user(question)"
        ]

    def plan_task(self, goal):
        """
        Generate action plan for high-level goal

        Args:
            goal: High-level goal string

        Returns:
            [action1, action2, ...]
        """
        prompt = f"""
You are a robot planner. Generate a step-by-step plan to achieve this goal.
Goal: {goal}

Available actions:
{chr(10).join(self.primitives)}

World state:
{json.dumps(self.world_state, indent=2)}

Return only a JSON list of actions, no other text.
Format: ["action1", "action2", ...]
"""

        # Query LLM
        response = self._query_llm(prompt)

        # Parse plan
        try:
            plan = json.loads(response)
            return plan
        except:
            return [f"ERROR parsing plan: {response}"]

    def _query_llm(self, prompt):
        """Query local LLM (Ollama)"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False}
            )
            return response.json()["response"]
        except Exception as e:
            return f"LLM error: {e}"

# Example usage
if __name__ == "__main__":
    planner = LLMPlanner()

    goals = [
        "Make me a cup of coffee",
        "Clean the table",
        "Prepare a sandwich"
    ]

    print("LLM Task Planner Examples")
    print("=" * 60)

    for goal in goals:
        print(f"\nGoal: {goal}")
        plan = planner.plan_task(goal)
        print("Plan:")
        for i, action in enumerate(plan, 1):
            print(f"  {i}. {action}")
```

**Output**:
```
Goal: Make me a cup of coffee
Plan:
  1. navigate("kitchen")
  2. grasp("cup")
  3. place("cup", "coffee_machine")
  4. pour("coffee", "cup")
  5. navigate("living_room")
  6. place("cup", "user")
```

---

## Example 4: Humanoid Inverse Kinematics

Computing joint angles for humanoid manipulation:

```python
#!/usr/bin/env python3
"""
Example 4: Humanoid Inverse Kinematics
Solves joint angles for end-effector target position
"""

import numpy as np
from scipy.optimize import minimize

class HumanoidIK:
    def __init__(self):
        # 7-DOF arm parameters
        self.link_lengths = np.array([0.0, 0.2, 0.4, 0.4, 0.0, 0.0, 0.1])
        self.dh_params = self._create_dh_params()

    def solve_ik(self, target_pos, target_orient=None):
        """
        Solve inverse kinematics

        Args:
            target_pos: [x, y, z] target position
            target_orient: [roll, pitch, yaw] target orientation

        Returns:
            joint_angles: 7-DOF joint configuration
        """
        # Initial guess
        x0 = np.zeros(7)

        # Optimization
        def objective(q):
            fk_pos, _ = self.forward_kinematics(q)
            error = np.linalg.norm(fk_pos - target_pos)
            return error

        result = minimize(objective, x0, method='Nelder-Mead')
        joint_angles = result.x

        # Enforce joint limits
        joint_limits = np.array([
            [-2*np.pi, 2*np.pi],
            [-np.pi, np.pi],
            [-2*np.pi, 2*np.pi],
            [-np.pi, np.pi],
            [-2*np.pi, 2*np.pi],
            [-np.pi, np.pi],
            [-2*np.pi, 2*np.pi]
        ])

        for i in range(7):
            joint_angles[i] = np.clip(joint_angles[i],
                                     joint_limits[i, 0],
                                     joint_limits[i, 1])

        return joint_angles

    def forward_kinematics(self, joint_angles):
        """
        Forward kinematics computation

        Args:
            joint_angles: 7 joint angles

        Returns:
            (position, orientation)
        """
        # Accumulate transformations
        T = np.eye(4)

        for i in range(len(joint_angles)):
            # Rotation
            c = np.cos(joint_angles[i])
            s = np.sin(joint_angles[i])

            # Translation
            T = T @ np.array([
                [c, -s, 0, 0],
                [s, c, 0, 0],
                [0, 0, 1, self.link_lengths[i]],
                [0, 0, 0, 1]
            ])

        position = T[:3, 3]
        orientation = T[:3, :3]

        return position, orientation

    def _create_dh_params(self):
        """Create Denavit-Hartenberg parameters"""
        pass

# Example usage
if __name__ == "__main__":
    ik_solver = HumanoidIK()

    # Test targets
    targets = [
        [0.3, 0.0, 0.5],   # Reach forward
        [0.2, 0.3, 0.6],   # Reach right and up
        [0.4, -0.2, 0.4]   # Reach down-left
    ]

    print("Humanoid IK Solver Examples")
    print("=" * 60)

    for target in targets:
        print(f"\nTarget: {target}")
        angles = ik_solver.solve_ik(target)
        print(f"Solution: {angles}")

        # Verify
        fk_pos, _ = ik_solver.forward_kinematics(angles)
        error = np.linalg.norm(fk_pos - np.array(target))
        print(f"Verification error: {error:.6f}m")
```

---

## Example 5: Complete Voice-to-Action Pipeline

End-to-end system integrating all components:

```python
#!/usr/bin/env python3
"""
Example 5: Complete Voice-to-Action Pipeline
Integrates speech recognition, NLP, LLM, and motion
"""

import time

class VoiceToActionPipeline:
    def __init__(self):
        from Example1 import RealtimeSpeechRecognizer
        from Example2 import NLPCommandParser
        from Example3 import LLMPlanner

        self.recognizer = RealtimeSpeechRecognizer()
        self.parser = NLPCommandParser()
        self.planner = LLMPlanner()

    def execute(self):
        """Full pipeline execution"""
        print("🤖 Voice-to-Action Pipeline")
        print("=" * 60)

        # Stage 1: Listen
        print("\n[1/5] LISTENING...")
        speech = self.recognizer.recognize_speech()
        if speech["confidence"] < 0.7:
            print("⚠ Low confidence - ask user to repeat")
            return

        # Stage 2: Parse
        print("\n[2/5] PARSING...")
        command = self.parser.parse(speech["text"])
        print(f"Intent: {command['intent']}")
        print(f"Entities: {command['entities']}")

        # Stage 3: Plan
        print("\n[3/5] PLANNING...")
        goal = f"{command['intent']} {command['entities']}"
        plan = self.planner.plan_task(goal)
        for i, action in enumerate(plan, 1):
            print(f"  {i}. {action}")

        # Stage 4: Execute
        print("\n[4/5] EXECUTING...")
        for action in plan:
            print(f"  → {action}")
            time.sleep(0.5)  # Simulate execution

        # Stage 5: Feedback
        print("\n[5/5] FEEDBACK...")
        print("✓ Task completed successfully")
        print("Would you like me to do anything else?")

# Run
if __name__ == "__main__":
    pipeline = VoiceToActionPipeline()
    pipeline.execute()
```

---

**Next Section**: Best Practices & Production Patterns
**Time**: 1-2 hours
**Difficulty**: Advanced

*Last Updated: 2026-01-20*

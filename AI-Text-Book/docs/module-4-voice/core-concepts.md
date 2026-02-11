---
sidebar_position: 3
---

# Core Concepts & Theory

## The Five Components of Voice-to-Action

```
USER COMMAND
    ↓
[1. SPEECH RECOGNITION] → Transcribe audio to text
    ↓
[2. NLP PARSING] → Extract intent and entities
    ↓
[3. LLM REASONING] → Generate action plan
    ↓
[4. MOTION PLANNING] → Create collision-free trajectories
    ↓
[5. REAL-TIME CONTROL] → Execute on robot hardware
    ↓
ACTION + FEEDBACK
```

Let's explore each layer.

---

## 1. Speech Recognition

### How It Works

Modern speech recognition uses deep neural networks:

```
AUDIO SIGNAL → FEATURE EXTRACTION → NEURAL NETWORK → TRANSCRIPTION

Example:
Input: Human says "Please make a sandwich"
  ↓
Audio: Waveform (48kHz sampling, mono/stereo)
  ↓
Features: Mel-Frequency Cepstral Coefficients (MFCC)
  └─ Compress audio into perceptually-relevant features
  └─ ~13 features per 10ms frame = ~1,300 features/second
  ↓
NN Processing: Transformer or RNN
  └─ Detect phonemes (smallest units of sound)
  └─ Combine phonemes into words
  └─ Add language model (what words are likely together)
  ↓
Output: "please make a sandwich" (with confidence scores)
```

### Key Models for Robotics

**Whisper (OpenAI)**
```
Model Size:    tiny (39M) → base (74M) → small (244M) → medium (769M) → large (1.5B)
Latency:       tiny: 100ms, large: 500ms on Jetson Orin
Accuracy:      tiny: 80%, large: 95%
Deployment:    All models run locally (no cloud needed)
Recommended:   "base" model for robotics (fast + accurate)
```

**Key Properties**:
- Multi-lingual (97 languages)
- Robust to background noise and accents
- No fine-tuning needed for deployment
- Available open-source

### Handling Noisy Environments

Robots operate in real-world environments (kitchen, factory, street) with background noise.

```
NOISE ROBUSTNESS TECHNIQUES:

1. Microphone Selection
   ├─ Directional microphone (beamforming)
   ├─ Multiple mics (array) for noise cancellation
   └─ Optimal: 4-8 mic array with beam steering

2. Pre-Processing
   ├─ Noise gate (silence detection)
   ├─ High-pass filter (remove rumble <100Hz)
   └─ Spectral subtraction (estimate noise, subtract it)

3. Model Robustness
   ├─ Whisper trained on 680,000 hours (including noisy)
   └─ Inherently robust to reverberation, accents

4. Post-Processing
   ├─ Language model scoring (reject unlikely transcriptions)
   ├─ Confidence thresholding (reject if <0.7 confidence)
   └─ User confirmation for ambiguous cases
```

### Latency Budget

```
TARGET: <500ms from voice input to first robot action

Speech Recognition Breakdown:
├─ Audio buffering: 0-100ms (collect audio)
├─ Transcription: 100-500ms (depends on model size)
└─ Total: 100-600ms

OPTIMIZATION:
- Use "base" or "small" model (not "large")
- Stream audio in chunks (don't wait for silence)
- Parallelize: start NLP parsing as audio streams
→ Result: <300ms by the time transcription finishes
```

---

## 2. NLP Semantic Parsing

### Extracting Intent and Entities

NLP converts raw text into structured commands:

```
INPUT TEXT:
"Please bring me the blue cup from the kitchen counter"

OUTPUT (Structured):
{
  "intent": "RETRIEVE_OBJECT",
  "object": {
    "name": "cup",
    "color": "blue",
    "count": 1
  },
  "location_from": "kitchen counter",
  "location_to": "user",
  "modifiers": ["please"],
  "confidence": 0.94
}

Now robot can:
1. Navigate to kitchen counter
2. Find blue cup (vision)
3. Pick it up (manipulation)
4. Return to user
5. Place in user's location
```

### Semantic Role Labeling

Maps words to semantic roles:

```
SENTENCE: "Robot, bring me water from the fridge"

Semantic Roles:
├─ Agent: Robot (who does the action)
├─ Verb: bring (action to perform)
├─ Patient: water (what to move)
├─ Source: fridge (where to get it from)
└─ Recipient: me/user (where to bring it to)

This allows robot to understand:
- Why it's moving water (for user to drink)
- Where to get it (fridge, not counter)
- Where to deliver (user's hand, not floor)
```

### Handling Ambiguity

Not all commands are clear:

```
AMBIGUOUS COMMAND:
"Get me something to eat"

LLM + Clarification Strategy:
Step 1: Detect ambiguity ("something" is vague)
Step 2: Query world state (what food is available?)
Step 3: Ask user: "I found apple, sandwich, and cookies. Which would you like?"
Step 4: Parse response: "Sandwich, please."
Step 5: Execute retrieval

This is key to usability—robots must ask for help!
```

---

## 3. LLM Reasoning & Planning

### Grounding Language Models to Robotics

Large Language Models are trained on internet text, not robot tasks. The challenge is **grounding**: connecting words to physical actions.

```
GROUNDING EXAMPLE:

LLM Reasoning:
Q: "User asked to make a sandwich. What should I do?"
A: "I need to: 1) Get bread, 2) Get toppings, 3) Assemble, 4) Serve"

Grounding (Mapping to Robots):
  1. "Get bread" → navigate kitchen → find bread
    ├─ Use vision to locate bread
    ├─ Navigate collision-free to bread
    ├─ Grasp bread (use Isaac manipulation primitives)
    ├─ Carry to counter

  2. "Get toppings" → Similar process

  3. "Assemble" → Place bread, add toppings, press
    ├─ Requires two-hand coordination
    ├─ Force control to not squish sandwich

  4. "Serve" → Place on plate, set in front of user
```

### Action Primitives

Robots should break tasks into primitives:

```
HIGH-LEVEL PRIMITIVES:
├─ Navigate(location): Go to location with collision avoidance
├─ Grasp(object): Pick up object (use vision + manipulation)
├─ Place(object, location): Put object down at location
├─ Pour(liquid, destination): Pour from container to destination
├─ Push(object, direction): Apply force to move object
├─ Ask(question): Ask user for clarification
└─ Wait(seconds): Pause for user input

MID-LEVEL PRIMITIVES:
├─ GetObject(name): Locate + navigate + grasp
├─ DeliverObject(object, person): Grasp + navigate + hand over
└─ PrepareFood(ingredients): Complex multi-step food prep

Example Task Decomposition:
"Make a sandwich" →
  1. GetObject(bread)
  2. Place(bread, counter)
  3. GetObject(cheese)
  4. Place(cheese, bread)
  5. GetObject(spreads)
  6. Spread(spreads, bread)
  7. DeliverObject(sandwich, user)
```

### LLM Context and Memory

```
CONTEXT FOR DECISION MAKING:

Robot maintains understanding of:
├─ WORLD STATE: What objects are where
├─ USER PREFERENCES: Likes/dislikes, dietary restrictions
├─ TASK HISTORY: What was done recently
└─ SAFETY CONSTRAINTS: Don't spill hot liquid, don't drop fragile items

Example:
User: "Make me something to eat"
Robot context:
  └─ Knows user is vegetarian (from preferences)
  └─ Knows there's no fresh vegetables (from inventory)
  └─ Suggests: "I can make you an egg sandwich. Is that okay?"

This context is crucial for useful suggestions.
```

---

## 4. Humanoid Kinematics & Dynamics

### Understanding Humanoid Robots

A humanoid robot has 50+ degrees of freedom (DOF):

```
JOINT BREAKDOWN (Example: 50 DOF humanoid):

Head: 3 DOF
  ├─ Pan (left-right)
  ├─ Tilt (up-down)
  └─ Roll (tilt side-to-side)

Torso: 3 DOF
  ├─ Pitch (forward-back)
  ├─ Roll (left-right)
  └─ Yaw (spin)

Left Arm: 7 DOF
  ├─ Shoulder pitch, roll, yaw
  ├─ Elbow pitch
  ├─ Wrist pitch, roll, yaw

Right Arm: 7 DOF (same as left)

Left Leg: 6 DOF
  ├─ Hip pitch, roll, yaw
  ├─ Knee pitch
  └─ Ankle pitch, roll

Right Leg: 6 DOF (same as left)

Hands: 2×15 DOF = 30 DOF (if high-fidelity hands)
  └─ 5 fingers × 3 joints each

TOTAL: 50+ DOF
```

### Forward & Inverse Kinematics

**Forward Kinematics (FK)**: Joint angles → 3D position

```
EXAMPLE:
Joint angles: [0°, 45°, 90°, 0°, 0°, 0°, 0°] (arm angles)
  ↓
FK Computation: Multiply transformation matrices
  ↓
Result: Hand position = (x=0.5m, y=0.0m, z=0.7m)
        Hand orientation = (roll=0°, pitch=45°, yaw=0°)

Used for: Forward simulation, validation
```

**Inverse Kinematics (IK)**: 3D target → Joint angles

```
EXAMPLE:
Goal: Move hand to grasp mug at (x=0.6m, y=0.2m, z=0.5m)
  ↓
IK Solver: Solve 7 equations with 7 unknowns
  ↓
Result: Joint angles = [angle1, angle2, ..., angle7]

Challenge: 7+ DOF systems have INFINITE solutions
  ├─ Could reach target with arm stretched
  ├─ Could reach target with arm bent
  └─ Could reach target with various intermediate poses

Solution: Choose solution that:
  ├─ Minimizes motion (closest to current pose)
  ├─ Avoids obstacles
  ├─ Is physically feasible (within joint limits)
  ├─ Looks natural (human-like pose)
  └─ Is most stable for the task
```

### Balance and Stability

Critical for bipedal humanoids:

```
BALANCE CONTROL:

Main Principle: Keep center of mass (COM) within support base

For Bipedal Standing:
└─ Support base = area between feet
└─ COM must be above this area
└─ If COM moves outside, robot falls

Real-time Balance:
├─ Measure: IMU sensors (accelerometers, gyroscopes)
├─ Compute: Desired ankle torques to keep COM stable
├─ Execute: Ankle torque commands continuously
└─ Frequency: 200+ Hz (must be fast!)

During Task Execution:
└─ Lower body: Maintain balance
└─ Upper body: Execute task (grasp, manipulate)
└─ Both run simultaneously without interference
```

---

## 5. Real-Time Coordination

### The Full Pipeline Under Real-Time Constraints

```
TIME BUDGET FOR COMPLETE CYCLE:

0ms:   Voice command captured
0-200ms: Speech recognition running
0-50ms: NLP parsing ready to run (parallel)
200ms: Transcription complete
250ms: Intent parsed, entities extracted
300ms: LLM generates action plan
400ms: Motion planning generates trajectory
450ms: First trajectory point sent to control
500ms: ROBOT MOVES! ← User perceives response

Total: 500ms from speech input to visible motion
(Humans perceive response latency; <500ms feels immediate)
```

### Parallel Processing Architecture

To meet real-time deadlines, run everything in parallel:

```
THREAD 1: Speech Recognition
├─ Listens to audio stream
├─ Buffers data
└─ Transcribes when complete

THREAD 2: NLP Parsing (starts when transcription begins)
├─ Receives transcribed text
├─ Extracts entities
└─ Publishes intent

THREAD 3: LLM Reasoning
├─ Receives parsed command
├─ Generates action plan
└─ Publishes plan steps

THREAD 4: Motion Planning
├─ Receives first plan step
├─ Generates trajectory
├─ Publishes trajectory points

THREAD 5: Control (highest priority)
├─ Real-time loop (200+ Hz)
├─ Receives trajectory points
├─ Executes with feedback
└─ Guarantees deadlines (can't miss)

Result: Latency minimized by parallelism
```

### Error Recovery

Real systems fail. Handle it gracefully:

```
FAILURE SCENARIOS:

1. "Speech recognition very uncertain"
   └─ Ask user to repeat
   └─ Don't execute ambiguous command

2. "Object not found by vision"
   └─ Ask user location
   └─ Navigate to location and search

3. "Path blocked by obstacle"
   └─ Replan around obstacle
   └─ If no path exists, ask for help

4. "Grasp failed"
   └─ Retry with different grasp
   └─ If repeated failures, report to user

5. "Falling (balance loss)"
   └─ Execute emergency recovery (bend legs, extend arms)
   └─ Stop all upper-body motion
   └─ Recover balance first

Key Principle: Never leave the system in unknown state
Always either: 1) Succeed, 2) Ask for help, 3) Enter safe state
```

---

## System Integration (Modules 1-4)

### How Everything Connects

```
MODULE INTEGRATION:

Module 1: ROS 2
  └─ Node orchestration, message passing
  └─ Used for: Inter-node communication

Module 2: Simulation
  └─ Digital twins, physics simulation
  └─ Used for: Testing without hardware

Module 3: Isaac SDK
  └─ Perception, motion planning, control
  └─ Used for: Core robot manipulation

Module 4: Voice-to-Action
  └─ Speech recognition, LLM reasoning
  └─ Adds: Natural language interface

EXAMPLE DATA FLOW:

User: "Bring me coffee"
  ↓
[Whisper]: Transcribe to text "Bring me coffee"
  ↓
[NLP]: Extract intent=RETRIEVE, object=COFFEE
  ↓
[LLM]: Generate plan [Navigate kitchen, Find coffee machine, ...]
  ↓
[Isaac Planning]: Generate collision-free trajectory for each step
  ↓
[Isaac Control]: Execute trajectory on robot
  ↓
[ROS 2]: All data flows through topics/services
  ↓
Robot brings coffee to user
```

---

## Summary: The Five Concepts

| Component | Input | Output | Technology | Latency |
|-----------|-------|--------|------------|---------|
| **Speech Recognition** | Audio | Transcribed text | Whisper | 100-500ms |
| **NLP Parsing** | Text | Intent + entities | Custom NLP | 50ms |
| **LLM Reasoning** | Intent | Action plan | LLM (Llama, etc.) | 100-300ms |
| **Motion Planning** | Action step | Trajectory | RMP-Flow (Isaac) | 50-100ms |
| **Real-Time Control** | Trajectory | Motor commands | PID (Isaac) | 5ms cycle |

---

**Next Section**: Hands-On Tutorial
**Time to Read**: 20-25 minutes
**Difficulty**: Advanced

*Last Updated: 2026-01-20*

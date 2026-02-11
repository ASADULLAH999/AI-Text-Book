---
sidebar_position: 8
---

# Module 4 Quiz: Test Your Understanding

## Quiz Instructions

- **Total Questions**: 10
- **Question Types**: Multiple choice and true/false
- **Passing Score**: 70% (7/10 correct)
- **Time Limit**: 30 minutes
- **Retakes**: Available (different questions each time)

---

## Question 1: Voice-to-Action Pipeline (Multiple Choice)

**Question**: In a complete voice-to-action system, which component has the LONGEST typical latency?

A) Speech recognition (Whisper base model)
B) NLP semantic parsing
C) LLM reasoning for task planning
D) Motion planning (RMP-Flow)

**Correct Answer**: **C**

**Explanation**: Latency breakdown:
- Speech recognition: ~150ms (fast)
- NLP parsing: ~50ms (very fast)
- LLM reasoning: 100-300ms (slowest) ← must generate text
- Motion planning: ~50-100ms (fast)

LLM inference is inherently slow because it generates tokens sequentially. This is why optimizing the LLM (quantization, smaller models) is critical for real-time systems.

---

## Question 2: Whisper Speech Recognition (True/False)

**Question**: Using Whisper's "large" model instead of "base" will always result in better voice-controlled robot performance.

**Correct Answer**: **False**

**Explanation**: While "large" has higher accuracy (95% vs 92%), it has worse latency (500ms vs 150ms). For robots, latency matters more than absolute accuracy:

```
Large model: 95% accuracy, 500ms latency
  → Feels slow to user, delayed response

Base model: 92% accuracy, 150ms latency
  → Feels responsive, occasional misunderstanding

For robots: Base model is better choice
Tradeoff: Sacrifice 3% accuracy for 3.3x faster response
```

---

## Question 3: NLP Intent Extraction (Multiple Choice)

**Question**: You have this command: "I want something cold to drink, maybe water."

What should an NLP parser output?

A) Intent: RETRIEVE, Object: water, Confidence: 0.95
B) Intent: RETRIEVE, Object: uncertain (water or juice or soda), Confidence: 0.65
C) Intent: RETRIEVE, Object: "something cold to drink", Confidence: 0.75
D) The system should ask for clarification before parsing

**Correct Answer**: **D**

**Explanation**: The command is ambiguous ("something cold" could be many things). Best practice is:

```
Robot: "I can provide water, juice, or soda. Which would you prefer?"
User: "Water, please."
Robot: Executes retrieval with high confidence
```

Asking for clarification is better than:
- Guessing wrong (choosing juice when user wanted water)
- Forcing low confidence (0.65) into the system
- Overspecifying (treating entire phrase as object name)

This is **supervised autonomy**: user confirms ambiguous plans before execution.

---

## Question 4: LLM Grounding (Multiple Choice)

**Question**: An LLM generates this action plan:
```
1. Go to kitchen
2. Take coffee maker
3. Brew coffee
4. Serve to user
```

What is the main challenge for a real robot to execute this plan?

A) The instructions are too detailed
B) The instructions are too vague (missing kinematic details)
C) The LLM used wrong grammar
D) The plan requires too many steps

**Correct Answer**: **B**

**Explanation**: The LLM plan is intentionally high-level. Robots need specific details:

```
What LLM provides:   "Take coffee maker"

What robot needs:
  ├─ Where is coffee maker? (navigation target)
  ├─ How to grasp it? (grasp pose, force)
  ├─ How to carry? (balance while holding)
  └─ How to avoid obstacles? (collision checking)

This is called GROUNDING:
Mapping high-level language to low-level robot actions
```

This is the core challenge in robotics+LLMs: bridging the semantic gap.

---

## Question 5: Real-Time Constraints (True/False)

**Question**: If LLM reasoning takes 200ms and motion planning takes 100ms, the robot should wait for both to complete before starting motion.

**Correct Answer**: **False**

**Explanation**: With parallel processing:

```
SEQUENTIAL (slow):
  Voice (150ms) → NLP (50ms) → LLM (200ms) → Plan (100ms)
  → Total: 500ms ← Still within budget but inefficient

PARALLEL (fast):
  Voice (150ms)
  ├─ While voice transcribing:
  │  ├─ NLP ready to parse
  │  └─ Pre-load motion models
  └─ By time voice finishes:
     ├─ NLP immediately parses
     ├─ LLM starts
     └─ By time LLM finishes: planning starts immediately
  → Total: ~400ms ← Better response

Lesson: Overlap processing stages
```

This is why production systems use thread pools and queues.

---

## Question 6: Humanoid Balance Control (Multiple Choice)

**Question**: A humanoid is executing an upper-body manipulation task (grasping an object) while maintaining bipedal balance. How should these be controlled?

A) Sequentially: first maintain balance, then manipulate
B) Single control loop coordinating both
C) Hierarchical: lower body maintains balance automatically, upper body executes task
D) Lower priority—if balance is lost, the task takes precedence

**Correct Answer**: **C**

**Explanation**: Hierarchical control is critical for humanoids:

```
LEVEL 1: Balance Control (Lower Body) [200 Hz]
  └─ Continuous ankle torque to keep COM over base

LEVEL 2: Task Execution (Upper Body) [200 Hz]
  └─ Execute gripper motion, grasping

Both run simultaneously:
  - Lower body: "Maintaining balance—adjust ankles"
  - Upper body: "Grasping object—move arm"
  - Result: Stable, natural humanoid motion

If sequentially (wrong):
  - Robot would sway or fall during manipulation

If single loop (inefficient):
  - Would be too slow, robot would fall
```

This hierarchy is what makes humanoid motion smooth and natural.

---

## Question 7: Error Recovery (True/False)

**Question**: If a robot hears "bring me something" but the speech confidence is 0.65 (below 0.7 threshold), it should ignore the command and not respond to the user.

**Correct Answer**: **False**

**Explanation**: Correct error recovery:

```
Low confidence (0.65):

WRONG: Ignore silently
  └─ User thinks robot broke
  └─ Confusing experience

RIGHT: Ask for clarification
  └─ Robot: "I didn't quite catch that. Can you repeat?"
  └─ User: "Bring me coffee"
  └─ Robot: Recognizes with higher confidence

Principle: Never fail silently
Always either: 1) succeed, 2) ask for help, or 3) give feedback
```

This is **supervised autonomy**: robot maintains communication with user.

---

## Question 8: Performance Optimization (Multiple Choice)

**Question**: Your voice-to-action system achieves 450ms latency (listening to first motion). You want to improve to 300ms. What's the MOST impactful optimization?

A) Use speech model "tiny" instead of "base"
B) Implement parallel processing (speech → NLP → planning simultaneously)
C) Reduce humanoid DOF from 50 to 30
D) Use faster microphone hardware

**Correct Answer**: **B**

**Explanation**: Impact analysis:

```
Option A: Switch to "tiny"
  ├─ Saves: 50ms
  ├─ Cost: 7% lower accuracy
  └─ Result: 400ms (not good enough)

Option B: Parallel processing ← BEST
  ├─ Saves: 100-150ms (overlap stages)
  ├─ Cost: Complexity, but high ROI
  └─ Result: 300ms ← Target achieved!

Option C: Fewer DOF
  ├─ Saves: Minimal (planning isn't bottleneck)
  └─ Cost: Reduced capability

Option D: Faster microphone
  ├─ Saves: <10ms
  └─ Not significant
```

Parallelism has highest ROI. This is why production systems use thread pools.

---

## Question 9: Model Deployment (Multiple Choice)

**Question**: You want to deploy a voice-controlled humanoid to a Jetson Orin with 8GB RAM. Current LLM model is Llama 13B (takes 6GB GPU memory). What's the best approach?

A) Use Llama 13B anyway (it's the most accurate)
B) Quantize to INT8, use cloud API fallback
C) Switch to 7B quantized model locally
D) Remove the LLM entirely, use hard-coded responses

**Correct Answer**: **C**

**Explanation**:
```
Constraints: 8GB total, need headroom for other processes

Option A: 13B FP32 = 6GB + OS + ROS 2 = OOM (Out of Memory)

Option B: Quantized ✓ + Cloud fallback
  ├─ Quantized: 2GB ✓
  ├─ Cloud fallback: Needs internet (not always available)
  └─ Better than A, but imperfect

Option C: 7B quantized (BEST) ✓
  ├─ Size: ~2GB
  ├─ Fits comfortably on Jetson
  ├─ Performance: 90% of 13B
  ├─ Latency: Lower (7B is faster)
  └─ No internet dependency

Option D: Hard-coded
  ├─ No reasoning capability
  ├─ Defeats purpose of LLM
  └─ Last resort only
```

Quantized 7B is the sweet spot for edge deployment.

---

## Question 10: End-to-End System Integration (Multiple Choice)

**Question**: You've built voice, NLP, LLM, planning, and control subsystems separately. They work perfectly in isolation. But end-to-end testing shows only 70% success rate (vs expected 95%). What's the MOST likely cause?

A) One of the subsystems has a latent bug
B) Integration issues: timing mismatches, state synchronization failures
C) The humanoid simulation is too different from real hardware
D) The microphone is positioned wrong

**Correct Answer**: **B**

**Explanation**: Classic systems integration problem:

```
Expected: 95% × 95% × 95% × 95% × 95% = 77%
Observed: 70%
Gap: Compound failures + integration issues

Individual Success Rates (isolated):
  └─ Each: ~95%

System Success Rate (integrated):
  └─ 70% ← 7% worse than expected

Causes of integration failures:
✓ Timing mismatches:
  └─ LLM slow, planning reads stale state
✓ State sync issues:
  └─ Different threads have different view of world
✓ Error propagation:
  └─ Small errors in each layer compound
✓ Boundary cases:
  └─ Edge cases don't appear individually but in combinations

Solution: Integration testing (test components together)
```

This is why production systems emphasize end-to-end testing.

---

## Answer Key & Scoring

| Q# | Answer | Type | Difficulty |
|----|--------|------|-----------|
| 1 | C | MCQ | Intermediate |
| 2 | False | T/F | Intermediate |
| 3 | D | MCQ | Important |
| 4 | B | MCQ | Important |
| 5 | False | T/F | Advanced |
| 6 | C | MCQ | Important |
| 7 | False | T/F | Intermediate |
| 8 | B | MCQ | Advanced |
| 9 | C | MCQ | Intermediate |
| 10 | B | MCQ | Advanced |

**Scoring**:
- 9-10 correct: **Excellent** ⭐⭐⭐ (Mastered capstone concepts!)
- 7-8 correct: **Good** ⭐⭐ (Solid understanding, review weak areas)
- 6 correct: **Passing** ⭐ (You pass! Review core concepts)
- Less than 6 correct: **Not Yet** (Review module and retake)

---

## Feedback by Score

### If you scored 9-10 ⭐⭐⭐
Excellent! You've mastered voice-to-action and capstone integration. Ready to:
- Deploy to real Jetson Orin humanoid
- Optimize for production performance
- Contribute to robotics industry/research
- Build your own robotics products

### If you scored 7-8 ⭐⭐
Strong foundation! Review:
- Real-time system architecture (Questions 5, 8)
- Integration issues (Question 10)
- Run code examples and experiments
- Then deploy capstone project

### If you scored 6 ⭐
Passing! But review:
- Voice-to-action pipeline architecture
- Error recovery and robustness
- Performance optimization strategies
- Complete hands-on tutorial again

### If you scored less than 6 🔄
Not ready for production deployment. Recommend:
1. Re-read Core Concepts section
2. Run all 5 code examples
3. Complete hands-on tutorial thoroughly
4. Study integration patterns in Best Practices
5. Retake quiz after review

---

## Capstone Completion Checklist

Your capstone project must include:

- ☐ **Speech Recognition**: >90% accuracy on test commands
- ☐ **NLP Parsing**: Correctly extracts intent + entities
- ☐ **LLM Integration**: Generates sensible multi-step plans
- ☐ **Motion Execution**: Smooth humanoid motion
- ☐ **Balance Control**: Maintains stability during tasks
- ☐ **Safety Mechanisms**: E-stop, watchdog, constraints
- ☐ **Error Recovery**: Asks for help when stuck
- ☐ **Real Hardware**: Code runs on Jetson Orin
- ☐ **Performance**: Less than 500ms listening-to-action latency
- ☐ **Demo Video**: Shows system working end-to-end

---

## Resources for Review

**If questions 5, 8 were hard** (Real-time & performance):
- Re-read: Best Practices section
- Run: Code Example 5 (complete pipeline)
- Focus: Multi-threading, parallel processing

**If questions 3, 7 were hard** (Error handling):
- Re-read: Core Concepts Layer 2 (NLP) and Layer 3 (LLM)
- Run: Code Example 2 (NLP parsing)
- Focus: Ambiguity handling, supervised autonomy

**If question 10 was hard** (Integration):
- Re-read: Summary section (how layers connect)
- Run: Code Example 5 (complete system)
- Focus: Testing complete systems

---

## Congratulations! 🎓

**You've completed Module 4: Voice-to-Action & Capstone!**

This means you've now completed the entire Physical AI & Humanoid Robotics textbook:

✅ Module 1: ROS 2 Fundamentals
✅ Module 2: Digital Twins & Simulation
✅ Module 3: Isaac SDK & AI Robot Programming
✅ Module 4: Voice-to-Action & Capstone Project

You are now qualified to:
- Build autonomous robots from scratch
- Deploy AI systems to edge hardware
- Integrate voice interfaces with robotics
- Work in the physical AI industry

---

## Next Steps

### Immediate
1. Deploy capstone to real Jetson Orin robot
2. Create demo video showing system
3. Document your implementation
4. Share on GitHub/portfolio

### Short Term
1. Specialize in area of interest (vision, control, learning)
2. Join robotics communities
3. Apply to robotics companies/labs

### Long Term
1. Contribute to open-source robotics
2. Publish research or technical blog
3. Build robotics products/startups
4. Mentor others learning robotics

---

**You're ready to build the future of robotics.**

*Last Updated: 2026-01-20*
*Module 4 Complete: Capstone project finished*
*Textbook Complete: All 4 modules done!*

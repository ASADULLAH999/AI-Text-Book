---
sidebar_position: 8
---

# Module 1 Quiz: Test Your Understanding

## Quiz Instructions

- **Total Questions**: 10
- **Question Types**: Multiple choice and true/false
- **Passing Score**: 70% (7/10 correct)
- **Time Limit**: 30 minutes
- **Retakes**: Available (different question order each time)

---

## Question 1: ROS 2 Architecture (Multiple Choice)

**Question**: Which of the following best describes how ROS 2 differs from ROS 1?

A) ROS 2 uses a central Master node while ROS 1 is fully distributed
B) ROS 2 uses distributed DDS middleware without a central Master
C) ROS 2 doesn't support multiple nodes on different computers
D) ROS 2 only works with Python, not C++

**Correct Answer**: **B**

**Explanation**: ROS 1 relied on a central ROS Master for node coordination, which was a single point of failure. ROS 2 uses a standardized DDS middleware that enables nodes to discover each other directly without a central authority, making it more reliable and scalable.

---

## Question 2: Topic vs Service (Multiple Choice)

**Question**: You need to request a robot to compute the inverse kinematics (joint angles) for a target position and wait for the result. Which communication pattern should you use?

A) Publish the target position on a topic
B) Use a service to request the computation
C) Use an action for the computation
D) Store the target in a parameter

**Correct Answer**: **B**

**Explanation**: Services are designed for synchronous request-response patterns where the client waits for a result. While actions could work for complex computations with feedback, a simple IK computation is best served by a service. Topics are for one-way streaming, and parameters are for configuration.

---

## Question 3: Publisher-Subscriber Pattern (True/False)

**Question**: In ROS 2's publish-subscribe pattern, the publisher must know the address of all subscribers.

**Correct Answer**: **False**

**Explanation**: One of the key advantages of ROS 2's pub-sub pattern is that publishers and subscribers are completely decoupled. The publisher simply sends messages to a topic; the middleware (DDS) handles routing to all interested subscribers. Neither party needs to know about the other.

---

## Question 4: QoS Profiles (Multiple Choice)

**Question**: You're publishing raw camera frames at 30 Hz over a network with occasional packet loss. What QoS profile should you use?

A) Reliability: RELIABLE, Durability: TRANSIENT_LOCAL
B) Reliability: BEST_EFFORT, Durability: VOLATILE
C) Reliability: RELIABLE, Durability: VOLATILE
D) Reliability: BEST_EFFORT, Durability: TRANSIENT_LOCAL

**Correct Answer**: **B**

**Explanation**: For high-frequency sensor streams like camera frames, losing an occasional frame is acceptable and actually preferred to reduce latency. Therefore, BEST_EFFORT (ok to lose) and VOLATILE (don't keep old data) is the right choice. RELIABLE would introduce unnecessary latency.

---

## Question 5: Parameters (True/False)

**Question**: Parameters in ROS 2 can only be set at node startup and cannot be changed while the node is running.

**Correct Answer**: **False**

**Explanation**: One of the key features of ROS 2 parameters is that they can be changed dynamically while the node is running using `ros2 param set` or through callbacks. Nodes can register callbacks to be notified when parameters change.

---

## Question 6: Actions vs Services (Multiple Choice)

**Question**: A robot needs to navigate to a target waypoint. The client wants to receive periodic updates (e.g., "45% complete") and be able to cancel the navigation mid-way. What should you use?

A) Service
B) Topic
C) Action
D) Parameter

**Correct Answer**: **C**

**Explanation**: Actions are specifically designed for long-running tasks that need progress feedback and cancellation capability. Services are synchronous but don't provide feedback. Topics are one-way. Parameters are for configuration.

---

## Question 7: Middleware (Multiple Choice)

**Question**: ROS 2 runs on top of which standardized middleware technology?

A) MQTT
B) Apache Kafka
C) DDS (Data Distribution Service)
D) HTTP/REST

**Correct Answer**: **C**

**Explanation**: ROS 2 uses DDS, an industry-standard middleware for real-time distributed systems. This allows ROS 2 to benefit from enterprise-grade reliability, security, and performance characteristics.

---

## Question 8: Node Independence (True/False)

**Question**: If one ROS 2 node crashes, all other nodes in the system will automatically crash.

**Correct Answer**: **False**

**Explanation**: One of ROS 2's key advantages is that nodes are independent. If one node crashes, others continue running unaffected. This is much different from systems with a central coordinator that would cause total system failure if it crashed.

---

## Question 9: Message Types (Multiple Choice)

**Question**: In ROS 2, which of the following is true about message types?

A) All messages must be defined in .msg files; you cannot use Python dict or objects
B) ROS 2 only supports a fixed set of message types defined by ROS
C) You can define custom message types by creating .msg interface files
D) Message types are only used for topics, not services

**Correct Answer**: **C**

**Explanation**: ROS 2 allows you to define custom message types in interface files (.msg for messages, .srv for services, .action for actions). This enables you to create application-specific data structures for your system.

---

## Question 10: System Design (Multiple Choice)

**Question**: You're designing a robot control system. Which of the following is the best architecture?

A) One large node that handles sensors, processing, and actuators
B) Separate nodes for sensors, processors, and actuators with clear responsibilities
C) All logic in a single node but with multiple threads
D) No communication between nodes to avoid overhead

**Correct Answer**: **B**

**Explanation**: Following the single-responsibility principle, separate nodes for different tasks is the best design. This enables reusability, testability, debuggability, and maintainability. Large monolithic nodes are harder to test and reuse.

---

## Answer Key & Scoring

| Q# | Correct Answer | Difficulty |
|----|---|---|
| 1 | B | Foundational |
| 2 | B | Important |
| 3 | False | Foundational |
| 4 | B | Intermediate |
| 5 | False | Intermediate |
| 6 | C | Important |
| 7 | C | Foundational |
| 8 | False | Important |
| 9 | C | Intermediate |
| 10 | B | Important |

**Scoring**:
- 9-10 correct: **Excellent** ⭐⭐⭐ (You mastered ROS 2 fundamentals!)
- 7-8 correct: **Good** ⭐⭐ (Solid understanding, review weak areas)
- 6 correct: **Passing** ⭐ (You pass! Consider reviewing core concepts)
- Less than 6 correct: **Not Yet** (Review the module and retake the quiz)

---

## Feedback for Each Score Range

### If you scored 9-10 ⭐⭐⭐
Excellent work! You've thoroughly understood ROS 2 fundamentals. You're ready to:
- Start Module 2 (Digital Twins & Simulation)
- Begin building your own multi-node systems
- Explore advanced ROS 2 features (real-time, security, middleware)

### If you scored 7-8 ⭐⭐
Good foundation! Review:
- Any questions you marked uncertain about
- The relevant section in this module
- Run the code examples to solidify understanding
- Then proceed to Module 2

### If you scored 6 ⭐
Passing, but consider:
- Reviewing the Introduction section for context
- Re-reading Core Concepts (especially topics vs services)
- Running the hands-on tutorial again
- Retaking the quiz after review

### If you scored less than 6 🔄
Not yet ready for Module 2. I recommend:
- **Retake the quiz** (You'll see different questions)
- **Review weak areas** based on your answers
- **Re-run the hands-on tutorial** and modify it
- **Study the code examples** and experiment with them
- **Join the community** for questions: discourse.ros.org

---

## Common Quiz Mistakes

### Misconception 1: "ROS 2 has a central Master"
**Correct Understanding**: ROS 2 uses distributed DDS, not a central Master. This is a major improvement over ROS 1.

### Misconception 2: "Topics are reliable by default"
**Correct Understanding**: Topics are BEST_EFFORT by default. You must specify RELIABLE QoS if needed.

### Misconception 3: "All nodes must run on the same computer"
**Correct Understanding**: Nodes can run anywhere and communicate over network using DDS.

### Misconception 4: "Services are always faster than topics"
**Correct Understanding**: Services are synchronous (block until response); topics are asynchronous. Each has trade-offs.

---

## Study Tips for Next Time

If you didn't pass or want to score higher:

1. **Focus on the five core concepts** - If you understand nodes, topics, services, actions, and parameters deeply, most questions become obvious
2. **Understand the trade-offs** - ROS 2 choices involve trade-offs: sync vs async, reliability vs speed, etc.
3. **Think about real-world examples** - Ask yourself: "In a real robot, when would I use this?"
4. **Don't memorize, understand** - This quiz tests understanding, not memorization

---

## After the Quiz

### If You Passed (7+/10)
Congratulations! You're ready for:
- ✅ Module 2: Digital Twins & Simulation
- ✅ Building real multi-node robot systems
- ✅ Moving to intermediate ROS 2 topics

### If You Didn't Pass (6/10)
- 🔄 Retake the quiz (you'll get different questions)
- 📖 Review the module sections you struggled with
- 🛠️ Run the hands-on tutorial and experiment
- 💬 Ask questions in the ROS 2 community

---

## Certificate & Badge

**Upon passing this module (quiz score 7+/10):**
- ✅ You'll receive a Digital Certificate of Completion
- 🏅 Badge: "ROS 2 Fundamentals Master"
- 📊 Your score will be recorded in your learning profile
- 🔓 You'll unlock access to Module 2

---

## Additional Practice

Want more practice with ROS 2 concepts?

- **Mini-Challenges**:
  1. Create a 3-node system (sensor, processor, actuator)
  2. Implement error handling in a subscriber
  3. Build a custom service server

- **Reading**:
  1. ROS 2 Design Document
  2. DDS Specification (executive summary)
  3. Real-world ROS 2 examples on GitHub

- **Community**:
  1. Post your systems on ROS Discourse
  2. Help others understand concepts
  3. Join ROS 2 study groups

---

## Ready to Continue?

🎉 **If you passed**: Proceed to **Module 2: Digital Twins & Simulation** (Gazebo, Unity)
🔄 **If you want to retake**: Select "Retake Quiz" above
📖 **Need to review**: Go back to specific section in Module 1

---

**You've completed Module 1: ROS 2 Fundamentals!**

*Module 1 Total: 8,000+ words, 5 code examples, 10 quiz questions*

*Next Stop: Module 2 - Digital Twins & Simulation*

---

*Last Updated: 2026-01-20*
*Module Version: 1.0*

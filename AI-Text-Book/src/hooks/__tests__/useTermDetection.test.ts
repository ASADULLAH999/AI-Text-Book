/**
 * Unit Tests — useTermDetection / detectTermsInText
 * T097 [US5] — Validates term detection accuracy >85% and performance <50ms.
 *
 * Run with Jest (npm test) or Vitest.
 *
 * Coverage:
 *  - detectTermsInText: basic match, alias match, case-insensitive, multi-term
 *  - No false positives on unrelated words
 *  - Accuracy benchmark: >85% on 30 labelled sentences
 *  - Performance: <50ms for 10,000-character text
 *  - measureDetectionAccuracy helper
 */

import {
  detectTermsInText,
  measureDetectionAccuracy,
} from '../useTermDetection';

// ---------------------------------------------------------------------------
// Basic detection
// ---------------------------------------------------------------------------

describe('detectTermsInText — basic', () => {
  test('detects an exact term', () => {
    const results = detectTermsInText('ROS2 is a popular framework.');
    expect(results.some((r) => r.term.id === 'ros2')).toBe(true);
  });

  test('detects an alias (Robot Operating System 2)', () => {
    const results = detectTermsInText(
      'Robot Operating System 2 provides communication middleware.',
    );
    expect(results.some((r) => r.term.id === 'ros2')).toBe(true);
  });

  test('detection is case-insensitive', () => {
    const upper = detectTermsInText('LIDAR sensors return point clouds.');
    const lower = detectTermsInText('lidar sensors return point clouds.');
    expect(upper.some((r) => r.term.id === 'lidar')).toBe(true);
    expect(lower.some((r) => r.term.id === 'lidar')).toBe(true);
  });

  test('detects multiple distinct terms in one sentence', () => {
    const results = detectTermsInText(
      'Nav2 uses SLAM and a costmap for autonomous navigation.',
    );
    const ids = new Set(results.map((r) => r.term.id));
    expect(ids.has('nav2')).toBe(true);
    expect(ids.has('slam')).toBe(true);
    expect(ids.has('costmap')).toBe(true);
  });

  test('returns start and end indices correctly', () => {
    const text = 'Use ROS2 for robotics.';
    const results = detectTermsInText(text);
    const match = results.find((r) => r.term.id === 'ros2');
    expect(match).toBeDefined();
    expect(text.slice(match!.startIndex, match!.endIndex)).toBe(match!.matchedText);
  });

  test('returns empty array for text with no terms', () => {
    const results = detectTermsInText('The cat sat on the mat.');
    expect(results).toHaveLength(0);
  });

  test('returns empty array for empty string', () => {
    expect(detectTermsInText('')).toHaveLength(0);
  });

  test('does not produce overlapping ranges', () => {
    const results = detectTermsInText(
      'ROS2 nodes communicate using DDS topics.',
    );
    for (let i = 0; i < results.length - 1; i++) {
      expect(results[i].endIndex).toBeLessThanOrEqual(results[i + 1].startIndex);
    }
  });
});

// ---------------------------------------------------------------------------
// Term-specific detection
// ---------------------------------------------------------------------------

describe('detectTermsInText — domain coverage', () => {
  const cases: [string, string, string][] = [
    ['ros2', 'ROS2 is middleware', 'ROS2'],
    ['node', 'A node publishes on a topic', 'node'],
    ['topic', 'Subscribe to the cmd_vel topic', 'topic'],
    ['slam', 'SLAM builds a map in real time', 'SLAM'],
    ['nav2', 'Nav2 handles path planning', 'Nav2'],
    ['lidar', 'The LiDAR returns a point cloud', 'LiDAR'],
    ['imu', 'The IMU measures angular velocity', 'IMU'],
    ['ekf', 'Use EKF for sensor fusion', 'EKF'],
    ['gazebo', 'Simulate in Gazebo before deployment', 'Gazebo'],
    ['isaac-sim', 'NVIDIA Isaac Sim is GPU-accelerated', 'Isaac Sim'],
    ['moveit2', 'MoveIt2 solves inverse kinematics', 'MoveIt2'],
    ['urdf', 'Load the URDF robot description', 'URDF'],
    ['tf2', 'TF2 tracks coordinate transforms', 'TF2'],
    ['qos', 'Set the QoS reliability to reliable', 'QoS'],
    ['asr', 'ASR converts speech to text', 'ASR'],
    ['tts', 'TTS synthesises robot speech', 'TTS'],
    ['wakeword', 'Detect the wake word to start listening', 'wake word'],
    ['odometry', 'Odometry drifts over time', 'Odometry'],
    ['reinforcement-learning', 'Reinforcement Learning trains robot policies', 'Reinforcement Learning'],
    ['sim-to-real', 'Sim-to-Real transfer closes the reality gap', 'Sim-to-Real'],
    ['point-cloud', 'Process the point cloud for obstacle detection', 'point cloud'],
    ['colcon', 'Build the workspace with colcon', 'colcon'],
    ['behavior-tree', 'Nav2 uses a Behavior Tree for task sequencing', 'Behavior Tree'],
    ['dds', 'ROS2 is built on DDS middleware', 'DDS'],
    ['isaac-lab', 'Isaac Lab enables parallel RL training', 'Isaac Lab'],
  ];

  test.each(cases)('detects %s in "%s"', (termId, text) => {
    const results = detectTermsInText(text);
    expect(results.some((r) => r.term.id === termId)).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// T097 — Accuracy benchmark (>85%)
// ---------------------------------------------------------------------------

describe('T097 — detection accuracy >85%', () => {
  const LABELLED_SAMPLES = [
    { text: 'ROS2 provides pub-sub messaging over DDS.', expectedTermIds: ['ros2', 'dds'] },
    { text: 'A node subscribes to the cmd_vel topic.', expectedTermIds: ['node', 'topic'] },
    { text: 'SLAM builds a map and localises the robot simultaneously.', expectedTermIds: ['slam'] },
    { text: 'Nav2 plans paths using a global costmap.', expectedTermIds: ['nav2', 'costmap'] },
    { text: 'LiDAR scans produce a dense point cloud.', expectedTermIds: ['lidar', 'point-cloud'] },
    { text: 'Fuse IMU and odometry with an EKF node.', expectedTermIds: ['imu', 'odometry', 'ekf', 'node'] },
    { text: 'Load the URDF into Gazebo for simulation.', expectedTermIds: ['urdf', 'gazebo'] },
    { text: 'Isaac Sim provides GPU-accelerated physics.', expectedTermIds: ['isaac-sim'] },
    { text: 'Isaac Lab runs parallel RL environments.', expectedTermIds: ['isaac-lab', 'reinforcement-learning'] },
    { text: 'MoveIt2 solves IK for the robot arm.', expectedTermIds: ['moveit2', 'ik'] },
    { text: 'Sim-to-Real transfer requires domain randomization.', expectedTermIds: ['sim-to-real', 'domain-randomization'] },
    { text: 'TF2 tracks the transform between base_link and odom.', expectedTermIds: ['tf2'] },
    { text: 'Set QoS to reliable for critical topics.', expectedTermIds: ['qos', 'topic'] },
    { text: 'ASR transcribes the wake word command.', expectedTermIds: ['asr', 'wakeword'] },
    { text: 'TTS generates spoken feedback from the robot.', expectedTermIds: ['tts'] },
    { text: 'colcon builds the ROS2 workspace.', expectedTermIds: ['colcon', 'ros2'] },
    { text: 'Nav2 uses a Behavior Tree to sequence actions.', expectedTermIds: ['nav2', 'behavior-tree'] },
    { text: 'Publish odometry to the /odom topic.', expectedTermIds: ['odometry', 'topic'] },
    { text: 'The service returns a response to the client node.', expectedTermIds: ['service', 'node'] },
    { text: 'An action server provides goal, feedback, and result.', expectedTermIds: ['action'] },
    { text: 'Launch files configure nodes with parameters.', expectedTermIds: ['launch-file', 'node'] },
    { text: 'The URDF defines links and joints of the robot.', expectedTermIds: ['urdf'] },
    { text: 'Reinforcement Learning policies are trained in Isaac Lab.', expectedTermIds: ['reinforcement-learning', 'isaac-lab'] },
    { text: 'Domain randomization improves sim-to-real transfer.', expectedTermIds: ['domain-randomization', 'sim-to-real'] },
    { text: 'The point cloud is segmented for object detection.', expectedTermIds: ['point-cloud'] },
    { text: 'DDS delivers messages peer-to-peer with QoS policies.', expectedTermIds: ['dds', 'qos'] },
    { text: 'MoveIt2 uses OMPL for collision-aware motion planning.', expectedTermIds: ['moveit2'] },
    { text: 'Gazebo integrates with ROS2 via ros_gz_bridge.', expectedTermIds: ['gazebo', 'ros2'] },
    { text: 'The EKF fuses LiDAR and IMU for accurate localisation.', expectedTermIds: ['ekf', 'lidar', 'imu'] },
    { text: 'SLAM toolbox creates a 2D occupancy grid map.', expectedTermIds: ['slam'] },
  ];

  test('accuracy is >85% on 30 labelled samples', () => {
    const accuracy = measureDetectionAccuracy(LABELLED_SAMPLES);
    console.log(`Term detection accuracy: ${(accuracy * 100).toFixed(1)}%`);
    expect(accuracy).toBeGreaterThan(0.85);
  });
});

// ---------------------------------------------------------------------------
// T095 — Performance <50ms for 10,000-character text
// ---------------------------------------------------------------------------

describe('T095 — performance <50ms', () => {
  // Build a large text that contains many glossary terms
  const buildLargeText = (): string => {
    const sentences = [
      'ROS2 nodes communicate over DDS topics with QoS policies.',
      'SLAM builds a map while the robot navigates using Nav2.',
      'LiDAR scans are converted to point clouds for obstacle detection.',
      'The EKF fuses IMU and odometry data to reduce localisation drift.',
      'Isaac Sim provides GPU physics; Isaac Lab trains RL policies.',
      'MoveIt2 solves IK for the robot arm trajectory planning.',
      'TF2 tracks coordinate transforms; URDF defines the robot links.',
      'ASR transcribes voice; TTS synthesises robot speech responses.',
      'Sim-to-Real uses domain randomization to bridge the reality gap.',
      'colcon builds the workspace; launch files configure the nodes.',
    ];
    let text = '';
    while (text.length < 10000) {
      text += sentences.join(' ') + ' ';
    }
    return text.slice(0, 10000);
  };

  const LARGE_TEXT = buildLargeText();

  test('detects terms in 10,000-char text in <50ms', () => {
    const start = performance.now();
    const results = detectTermsInText(LARGE_TEXT);
    const elapsed = performance.now() - start;

    console.log(
      `Detection time for 10k chars: ${elapsed.toFixed(2)}ms, found ${results.length} matches`,
    );
    expect(elapsed).toBeLessThan(50);
    expect(results.length).toBeGreaterThan(0);
  });
});

import React from 'react';
import { QuizData } from '../../types/quiz';
import styles from './styles.module.css';

interface QuizIntroProps {
  quizData: QuizData;
  attemptNumber: number;
  onStart: () => void;
}

export default function QuizIntro({ quizData, attemptNumber, onStart }: QuizIntroProps) {
  const questionCount = Math.min(10, quizData.questions.length);
  const passingScore = quizData.passing_score || 70;
  const timeLimit = quizData.time_limit;

  return (
    <div className={styles.intro}>
      <div className={styles.introHeader}>
        <h1 className={styles.introTitle}>{quizData.module_name} Quiz</h1>
        <div className={styles.attemptBadge}>Attempt #{attemptNumber}</div>
      </div>

      <div className={styles.introContent}>
        <div className={styles.introSection}>
          <h2 className={styles.introSectionTitle}>Quiz Information</h2>
          <ul className={styles.introList}>
            <li>
              <strong>Questions:</strong> {questionCount} questions (randomly selected)
            </li>
            <li>
              <strong>Passing Score:</strong> {passingScore}% or higher
            </li>
            {timeLimit && (
              <li>
                <strong>Time Limit:</strong> {Math.floor(timeLimit / 60)} minutes
              </li>
            )}
            <li>
              <strong>Format:</strong> Multiple choice
            </li>
            <li>
              <strong>Attempts:</strong> Unlimited retakes with different questions each time
            </li>
          </ul>
        </div>

        <div className={styles.introSection}>
          <h2 className={styles.introSectionTitle}>Instructions</h2>
          <ul className={styles.introList}>
            <li>Read each question carefully before selecting your answer</li>
            <li>You can navigate between questions using the Previous/Next buttons</li>
            <li>Use the "Flag for Review" option to mark questions you want to revisit</li>
            <li>You can change your answers anytime before submitting</li>
            <li>Once submitted, you'll see your score and detailed explanations</li>
            {timeLimit && (
              <li className={styles.warningText}>
                A timer will start when you begin. The quiz will auto-submit when time expires.
              </li>
            )}
          </ul>
        </div>

        <div className={styles.introSection}>
          <h2 className={styles.introSectionTitle}>Ready to Begin?</h2>
          <p className={styles.introText}>
            Click the button below to start your quiz. Good luck!
          </p>
        </div>
      </div>

      <div className={styles.introFooter}>
        <button onClick={onStart} className={styles.buttonStart}>
          Start Quiz →
        </button>
      </div>
    </div>
  );
}

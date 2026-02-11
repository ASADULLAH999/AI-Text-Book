import React, { useState } from 'react';
import { QuizQuestion as QuizQuestionType } from '../../types/quiz';
import QuizQuestion from './QuizQuestion';
import styles from './styles.module.css';

interface QuizResultsProps {
  result: any; // QuizResult type from service
  questions: QuizQuestionType[];
  onRetake: () => void;
  moduleId: string;
}

export default function QuizResults({ result, questions, onRetake, moduleId }: QuizResultsProps) {
  const [showReview, setShowReview] = useState(false);

  const passed = result.passed;
  const percentage = result.percentage;
  const correct = result.correct;
  const incorrect = result.incorrect;
  const skipped = result.skipped;
  const timeSpentMs = result.time_spent_ms;

  // Format time spent
  const timeSpentMinutes = Math.floor(timeSpentMs / 60000);
  const timeSpentSeconds = Math.floor((timeSpentMs % 60000) / 1000);

  // Get answers map from result
  const answersMap: Record<string, number> = {};
  result.question_results.forEach((qr: any) => {
    if (qr.user_answer !== null) {
      answersMap[qr.question_id] = qr.user_answer;
    }
  });

  return (
    <div className={styles.resultsContainer}>
      {/* Score Display */}
      <div className={`${styles.scoreDisplay} ${passed ? styles.scorePassed : styles.scoreFailed}`}>
        <div className={styles.scoreIcon}>{passed ? '✓' : '✗'}</div>
        <div className={styles.scorePercentage}>{percentage}%</div>
        <div className={styles.scoreStatus}>{passed ? 'PASSED' : 'FAILED'}</div>
        <div className={styles.scoreMessage}>
          {passed
            ? 'Congratulations! You passed the quiz.'
            : `You need ${result.passing_score || 70}% to pass. Try again!`}
        </div>
      </div>

      {/* Stats Breakdown */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{correct}</div>
          <div className={styles.statLabel}>Correct</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{incorrect}</div>
          <div className={styles.statLabel}>Incorrect</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>{skipped}</div>
          <div className={styles.statLabel}>Skipped</div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {timeSpentMinutes}:{String(timeSpentSeconds).padStart(2, '0')}
          </div>
          <div className={styles.statLabel}>Time</div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className={styles.resultsActions}>
        <button onClick={() => setShowReview(!showReview)} className={styles.buttonSecondary}>
          {showReview ? 'Hide Review' : 'Review Answers'}
        </button>
        <button onClick={onRetake} className={styles.buttonPrimary}>
          Retake Quiz
        </button>
        <a href={`/docs/module-${moduleId}`} className={styles.buttonOutline}>
          Back to Module
        </a>
      </div>

      {/* Confetti on Pass (Optional - can be implemented with CSS animation) */}
      {passed && (
        <div className={styles.confetti} aria-hidden="true">
          🎉
        </div>
      )}

      {/* Question Review */}
      {showReview && (
        <div className={styles.reviewSection}>
          <h2 className={styles.reviewTitle}>Question Review</h2>
          <div className={styles.reviewQuestions}>
            {questions.map((question, index) => {
              const questionResult = result.question_results.find(
                (qr: any) => qr.question_id === question.id
              );

              return (
                <div key={question.id} className={styles.reviewQuestionWrapper}>
                  <div className={styles.reviewQuestionNumber}>
                    <span>Question {index + 1}</span>
                    {questionResult?.correct && (
                      <span className={styles.reviewStatusCorrect}>✓ Correct</span>
                    )}
                    {!questionResult?.correct && questionResult?.user_answer !== null && (
                      <span className={styles.reviewStatusIncorrect}>✗ Incorrect</span>
                    )}
                    {questionResult?.user_answer === null && (
                      <span className={styles.reviewStatusSkipped}>Skipped</span>
                    )}
                  </div>
                  <QuizQuestion
                    question={question}
                    selectedAnswer={answersMap[question.id]}
                    isFlagged={false}
                    onAnswerSelect={() => {}}
                    onFlagToggle={() => {}}
                    showCorrectAnswer={true}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

import React from 'react';
import { QuizQuestion as QuizQuestionType } from '../../types/quiz';
import styles from './styles.module.css';

interface QuizQuestionProps {
  question: QuizQuestionType;
  selectedAnswer?: number;
  isFlagged: boolean;
  onAnswerSelect: (optionIndex: number) => void;
  onFlagToggle: () => void;
  showCorrectAnswer?: boolean;
}

export default function QuizQuestion({
  question,
  selectedAnswer,
  isFlagged,
  onAnswerSelect,
  onFlagToggle,
  showCorrectAnswer = false,
}: QuizQuestionProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return styles.difficultyEasy;
      case 'medium':
        return styles.difficultyMedium;
      case 'hard':
        return styles.difficultyHard;
      default:
        return '';
    }
  };

  return (
    <div className={styles.questionContainer}>
      {/* Question Header */}
      <div className={styles.questionHeader}>
        <div className={styles.questionMeta}>
          <span className={`${styles.difficultyBadge} ${getDifficultyColor(question.difficulty)}`}>
            {question.difficulty}
          </span>
          {question.category && (
            <span className={styles.categoryBadge}>{question.category}</span>
          )}
        </div>
        <button
          onClick={onFlagToggle}
          className={`${styles.flagButton} ${isFlagged ? styles.flagButtonActive : ''}`}
          aria-label={isFlagged ? 'Unflag question' : 'Flag for review'}
        >
          {isFlagged ? '🚩 Flagged' : '⚑ Flag for Review'}
        </button>
      </div>

      {/* Question Text */}
      <div className={styles.questionText}>
        <h3>{question.question}</h3>
      </div>

      {/* Options */}
      <div className={styles.optionsContainer}>
        {question.options.map((option, index) => {
          const isSelected = selectedAnswer === index;
          const isCorrect = showCorrectAnswer && index === question.correct_answer;
          const isIncorrect = showCorrectAnswer && isSelected && !isCorrect;

          return (
            <button
              key={index}
              onClick={() => !showCorrectAnswer && onAnswerSelect(index)}
              disabled={showCorrectAnswer}
              className={`${styles.option} ${isSelected ? styles.optionSelected : ''} ${
                isCorrect ? styles.optionCorrect : ''
              } ${isIncorrect ? styles.optionIncorrect : ''}`}
              aria-label={`Option ${index + 1}: ${option}`}
            >
              <span className={styles.optionLetter}>
                {String.fromCharCode(65 + index)}
              </span>
              <span className={styles.optionText}>{option}</span>
              {isCorrect && <span className={styles.optionIcon}>✓</span>}
              {isIncorrect && <span className={styles.optionIcon}>✗</span>}
            </button>
          );
        })}
      </div>

      {/* Explanation (shown in review mode) */}
      {showCorrectAnswer && question.explanation && (
        <div className={styles.explanation}>
          <div className={styles.explanationHeader}>
            <span className={styles.explanationIcon}>💡</span>
            <strong>Explanation</strong>
          </div>
          <p className={styles.explanationText}>{question.explanation}</p>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { quizService } from '../../services/quiz-service';
import { QuizData, QuizQuestion as QuizQuestionType, QuizAttempt } from '../../types/quiz';
import QuizIntro from './QuizIntro';
import QuizQuestion from './QuizQuestion';
import QuizResults from './QuizResults';
import styles from './styles.module.css';

interface QuizProps {
  moduleId: string;
  userId?: string;
}

type QuizStatus = 'intro' | 'in_progress' | 'results';

export default function Quiz({ moduleId, userId = 'anonymous' }: QuizProps) {
  const [status, setStatus] = useState<QuizStatus>('intro');
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [selectedQuestions, setSelectedQuestions] = useState<QuizQuestionType[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<string>>(new Set());
  const [startTime, setStartTime] = useState<number>(0);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [attemptNumber, setAttemptNumber] = useState(1);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load quiz data on mount
  useEffect(() => {
    const loadQuizData = async () => {
      try {
        setLoading(true);
        const data = await quizService.loadQuiz(moduleId);
        setQuizData(data);

        // Get attempt history to determine attempt number
        const history = await quizService.getAttemptHistory(userId, moduleId);
        setAttemptNumber(history.length + 1);

        setLoading(false);
      } catch (err) {
        setError('Failed to load quiz. Please try again.');
        setLoading(false);
      }
    };

    loadQuizData();
  }, [moduleId, userId]);

  // Timer countdown
  useEffect(() => {
    if (status === 'in_progress' && timeRemaining !== null && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev === null || prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [status, timeRemaining]);

  const handleStart = () => {
    if (!quizData) return;

    // Select questions for this attempt
    const questions = quizService.selectQuestions(
      quizData.questions,
      10, // Select 10 questions
      attemptNumber
    );
    setSelectedQuestions(questions);
    setStartTime(Date.now());
    setStatus('in_progress');

    // Set timer if time limit exists
    if (quizData.time_limit) {
      setTimeRemaining(quizData.time_limit);
    }
  };

  const handleAnswerSelect = (questionId: string, optionIndex: number) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleFlagToggle = (questionId: string) => {
    setFlaggedQuestions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const handleNext = () => {
    if (currentQuestionIndex < selectedQuestions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (!quizData) return;

    const endTime = Date.now();
    const attempt: QuizAttempt = {
      id: `attempt_${userId}_${moduleId}_${Date.now()}`,
      module_id: moduleId,
      user_id: userId,
      answers,
      score: 0,
      percentage: 0,
      passed: false,
      time_spent: endTime - startTime,
      timestamp: endTime,
      skipped: selectedQuestions
        .filter((q) => !(q.id in answers))
        .map((q) => q.id),
      start_time: startTime,
      end_time: endTime,
    };

    // Score the quiz
    const quizResult = quizService.scoreQuiz(attempt, selectedQuestions);

    // Update attempt with score
    attempt.score = quizResult.correct_count || 0;
    attempt.percentage = quizResult.percentage;
    attempt.passed = quizResult.passed;

    // Save attempt
    await quizService.saveAttempt(attempt);

    // Show results
    setResult(quizResult);
    setStatus('results');
  };

  const handleRetake = () => {
    setAnswers({});
    setFlaggedQuestions(new Set());
    setCurrentQuestionIndex(0);
    setTimeRemaining(null);
    setResult(null);
    setAttemptNumber((prev) => prev + 1);
    setStatus('intro');
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading quiz...</div>
      </div>
    );
  }

  if (error || !quizData) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || 'Quiz not found'}</div>
      </div>
    );
  }

  if (status === 'intro') {
    return (
      <QuizIntro
        quizData={quizData}
        attemptNumber={attemptNumber}
        onStart={handleStart}
      />
    );
  }

  if (status === 'results' && result) {
    return (
      <QuizResults
        result={result}
        questions={selectedQuestions}
        onRetake={handleRetake}
        moduleId={moduleId}
      />
    );
  }

  // In progress
  const currentQuestion = selectedQuestions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / selectedQuestions.length) * 100;

  return (
    <div className={styles.container}>
      {/* Progress Bar */}
      <div className={styles.progressBar}>
        <div className={styles.progressFill} style={{ width: `${progress}%` }} />
      </div>

      {/* Timer */}
      {timeRemaining !== null && (
        <div className={`${styles.timer} ${timeRemaining < 60 ? styles.timerWarning : ''}`}>
          Time Remaining: {Math.floor(timeRemaining / 60)}:
          {String(timeRemaining % 60).padStart(2, '0')}
        </div>
      )}

      {/* Question Counter */}
      <div className={styles.questionCounter}>
        Question {currentQuestionIndex + 1} of {selectedQuestions.length}
      </div>

      {/* Question */}
      <QuizQuestion
        question={currentQuestion}
        selectedAnswer={answers[currentQuestion.id]}
        isFlagged={flaggedQuestions.has(currentQuestion.id)}
        onAnswerSelect={(optionIndex) => handleAnswerSelect(currentQuestion.id, optionIndex)}
        onFlagToggle={() => handleFlagToggle(currentQuestion.id)}
      />

      {/* Navigation */}
      <div className={styles.navigation}>
        <button
          onClick={handlePrevious}
          disabled={currentQuestionIndex === 0}
          className={styles.buttonSecondary}
        >
          ← Previous
        </button>

        {currentQuestionIndex < selectedQuestions.length - 1 ? (
          <button onClick={handleNext} className={styles.buttonPrimary}>
            Next →
          </button>
        ) : (
          <button onClick={handleSubmit} className={styles.buttonSubmit}>
            Submit Quiz
          </button>
        )}
      </div>

      {/* Question Navigator */}
      <div className={styles.questionNavigator}>
        {selectedQuestions.map((q, index) => (
          <button
            key={q.id}
            onClick={() => setCurrentQuestionIndex(index)}
            className={`${styles.questionDot} ${
              index === currentQuestionIndex ? styles.questionDotActive : ''
            } ${answers[q.id] !== undefined ? styles.questionDotAnswered : ''} ${
              flaggedQuestions.has(q.id) ? styles.questionDotFlagged : ''
            }`}
            aria-label={`Question ${index + 1}`}
          >
            {index + 1}
          </button>
        ))}
      </div>
    </div>
  );
}

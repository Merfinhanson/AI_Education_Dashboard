import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import FileUpload from '../components/FileUpload';
import { runEvaluation } from '../services/api';
import '../styles/studentDashboard.css';

const navItems = [
  { label: 'Overview', to: '/student/dashboard', meta: 'Dashboard home' },
  { label: 'Upload Sheet', href: '#upload-section', meta: 'Answer uploads' },
  { label: 'AI Feedback', href: '#feedback-section', meta: 'Suggestions' },
  { label: 'Progress', href: '#progress-section', meta: 'Performance charts' },
  { label: 'Teacher View', to: '/teacher/dashboard', meta: 'Preview teacher UI' },
];

const defaultSummaryCards = [
  {
    title: 'Assignments Submitted',
    value: '24',
    trend: '+03',
    caption: 'Completed answer sheets submitted this month.',
  },
  {
    title: 'Average AI Score',
    value: '89%',
    trend: '+6%',
    caption: 'Consistency is improving across recent uploads.',
  },
  {
    title: 'Study Streak',
    value: '16 Days',
    trend: 'On track',
    caption: 'Continuous practice keeps your feedback sharp.',
  },
];

const defaultPerformanceCards = [
  { label: 'Mathematics', value: '92%', tone: 'student-metric--blue' },
  { label: 'Physics', value: '87%', tone: 'student-metric--teal' },
  { label: 'Writing Quality', value: '81%', tone: 'student-metric--violet' },
];

const progressBars = [
  { label: 'Week 1', valueClass: 'student-progress__bar--one' },
  { label: 'Week 2', valueClass: 'student-progress__bar--two' },
  { label: 'Week 3', valueClass: 'student-progress__bar--three' },
  { label: 'Week 4', valueClass: 'student-progress__bar--four' },
];

const metricTones = [
  'student-metric--blue',
  'student-metric--teal',
  'student-metric--violet',
];

function StudentDashboard() {
  const [formValues, setFormValues] = useState({
    studentName: 'Jordan',
    studentId: 'STD-104',
    questionPaperTitle: 'Science Assessment',
    questionPaperFile: null,
    answerSheetFile: null,
    markingSchemeFile: null,
  });
  const [report, setReport] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const summaryCards = !report
    ? defaultSummaryCards
    : [
        {
          title: 'Total Score',
          value: `${report.summary.total_marks_obtained}/${report.summary.total_marks_possible}`,
          trend: report.summary.grade,
          caption: 'Marks awarded by the evaluation engine for this submission.',
        },
        {
          title: 'Final Percentage',
          value: `${report.summary.percentage}%`,
          trend: report.plagiarism_report.is_flagged ? 'Review' : 'Clear',
          caption: report.plagiarism_report.is_flagged
            ? 'Similarity checks found a submission that needs review.'
            : 'Submission passed similarity checks without a flag.',
        },
        {
          title: 'Evaluated Questions',
          value: String(report.question_results.length),
          trend: `${report.question_results.filter((item) => item.awarded_marks > 0).length} scored`,
          caption: 'Questions parsed, mapped, and graded from the uploaded files.',
        },
      ];

  const performanceCards = !report?.question_results?.length
    ? defaultPerformanceCards
    : report.question_results.slice(0, 3).map((result, index) => ({
        label: `Question ${result.question_number}`,
        value: `${result.awarded_marks}/${result.max_marks}`,
        tone: metricTones[index % metricTones.length],
      }));

  const latestFeedback = report?.question_results?.[0] ?? null;
  const plagiarismMatches = report?.plagiarism_report?.matches ?? [];

  const handleTextChange = (event) => {
    const { name, value } = event.target;
    setFormValues((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleFileSelect = (fieldName) => (file) => {
    setFormValues((current) => ({
      ...current,
      [fieldName]: file,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!formValues.questionPaperFile || !formValues.answerSheetFile) {
      setErrorMessage('Please upload both the question paper and the answer sheet.');
      return;
    }

    setIsSubmitting(true);
    setErrorMessage('');

    try {
      const nextReport = await runEvaluation(formValues);
      setReport(nextReport);
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'Unable to evaluate this submission right now.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="student-page">
      <div className="dashboard-shell">
        <Sidebar
          brand="AstraLearn"
          navItems={navItems}
          footerText="Keep submissions, AI feedback, and performance summaries in a calm, student-friendly learning hub."
        />

        <main className="dashboard-content">
          <Navbar
            title="Student Dashboard"
            subtitle="Upload your question paper and answer sheet, trigger AI evaluation, and review the returned score report from FastAPI."
            actionLabel="Run Evaluation"
            profileName="Jordan"
            profileRole="Grade 10 Student"
          />

          <section className="student-hero">
            <div className="student-hero__content">
              <p className="student-hero__eyebrow">Connected Evaluation Flow</p>
              <h2>Send answer sheets to the backend and review real score reports.</h2>
              <p>
                This dashboard is now wired to the FastAPI evaluation endpoint.
                Upload the required files below, submit the form, and the report
                card updates with marks, grade, and plagiarism results.
              </p>
            </div>

            <div className="student-hero__panel">
              <div className="student-hero__panel-head">
                <h3>Integration Snapshot</h3>
                <span>Live API Flow</span>
              </div>

              <div className="student-hero__panel-grid">
                <div className="student-hero__panel-card">
                  <span>Frontend</span>
                  <strong>Vite + React</strong>
                </div>
                <div className="student-hero__panel-card">
                  <span>Backend</span>
                  <strong>FastAPI</strong>
                </div>
                <div className="student-hero__panel-card">
                  <span>Upload Mode</span>
                  <strong>Multipart Form</strong>
                </div>
              </div>
            </div>
          </section>

          <section className="student-summary-grid">
            {summaryCards.map((card) => (
              <Card key={card.title} {...card} />
            ))}
          </section>

          <section className="student-main-grid">
            <div id="upload-section" className="student-section">
              <div className="student-section__heading">
                <div>
                  <p className="student-section__eyebrow">Evaluation Upload</p>
                  <h3>Connect the UI to the FastAPI evaluation endpoint</h3>
                </div>
                <span className="student-section__pill">API Connected</span>
              </div>

              <form className="student-evaluation-form" onSubmit={handleSubmit}>
                <div className="student-form-grid">
                  <label className="student-form-field">
                    <span>Student Name</span>
                    <input
                      name="studentName"
                      value={formValues.studentName}
                      onChange={handleTextChange}
                      placeholder="Enter student name"
                      required
                    />
                  </label>

                  <label className="student-form-field">
                    <span>Student ID</span>
                    <input
                      name="studentId"
                      value={formValues.studentId}
                      onChange={handleTextChange}
                      placeholder="Enter student ID"
                    />
                  </label>

                  <label className="student-form-field student-form-field--full">
                    <span>Question Paper Title</span>
                    <input
                      name="questionPaperTitle"
                      value={formValues.questionPaperTitle}
                      onChange={handleTextChange}
                      placeholder="Assessment title"
                    />
                  </label>
                </div>

                <div className="student-upload-stack">
                  <FileUpload
                    title="Upload question paper"
                    description="The current backend endpoint evaluates against a supplied question paper for each run."
                    buttonLabel="Select Question Paper"
                    helperText="Choose the question paper file used for this evaluation."
                    acceptedText="Accepted formats: PDF, TXT, PNG, JPG"
                    accept=".pdf,.txt,.png,.jpg,.jpeg"
                    required
                    selectedFileName={formValues.questionPaperFile?.name}
                    onFileSelect={handleFileSelect('questionPaperFile')}
                  />

                  <FileUpload
                    title="Upload answer sheet"
                    description="Submit the answer sheet that should be graded against the uploaded paper."
                    buttonLabel="Select Answer Sheet"
                    helperText="Choose the student's answer sheet to send to the backend."
                    acceptedText="Accepted formats: PDF, TXT, PNG, JPG"
                    accept=".pdf,.txt,.png,.jpg,.jpeg"
                    required
                    selectedFileName={formValues.answerSheetFile?.name}
                    onFileSelect={handleFileSelect('answerSheetFile')}
                  />

                  <FileUpload
                    title="Upload marking scheme"
                    description="Optional, but recommended for better rubric coverage and missing-point suggestions."
                    buttonLabel="Select Marking Scheme"
                    helperText="You can leave this empty if no marking scheme is available."
                    acceptedText="Accepted formats: PDF, TXT"
                    accept=".pdf,.txt"
                    selectedFileName={formValues.markingSchemeFile?.name}
                    onFileSelect={handleFileSelect('markingSchemeFile')}
                  />
                </div>

                {errorMessage ? (
                  <div className="student-status-banner student-status-banner--error">
                    {errorMessage}
                  </div>
                ) : null}

                {report ? (
                  <div className="student-status-banner student-status-banner--success">
                    Evaluation completed for {report.student_name}. Submission ID:{' '}
                    {report.submission_id}
                  </div>
                ) : null}

                <div className="student-form-actions">
                  <button
                    type="submit"
                    className="student-submit"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? 'Evaluating...' : 'Submit For Evaluation'}
                  </button>
                  <p>
                    The form posts to `POST /api/v1/evaluations/run` and returns
                    marks, grade, suggestions, and plagiarism checks.
                  </p>
                </div>
              </form>
            </div>

            <div id="feedback-section" className="student-section">
              <div className="student-section__heading">
                <div>
                  <p className="student-section__eyebrow">AI Feedback</p>
                  <h3>Latest feedback summary</h3>
                </div>
                <span className="student-section__pill">
                  {report ? 'Live Report' : 'Awaiting Upload'}
                </span>
              </div>

              <article className="student-feedback-card">
                <div className="student-feedback-card__head">
                  <span className="student-feedback-card__score">
                    {report ? `${report.summary.percentage}%` : '89%'}
                  </span>
                  <span className="student-feedback-card__badge">
                    {report ? `Grade ${report.summary.grade}` : 'Strong Progress'}
                  </span>
                </div>
                <h4>
                  {report
                    ? report.summary.summary
                    : 'Algebraic reasoning is becoming more structured.'}
                </h4>
                <p>
                  {latestFeedback
                    ? latestFeedback.justification
                    : 'Your last submission showed cleaner step-by-step logic and fewer skipped workings. Focus next on concise explanations for final answers.'}
                </p>

                <div className="student-feedback-card__list">
                  <div>
                    <strong>What improved</strong>
                    <span>
                      {latestFeedback?.strengths?.[0] ||
                        'Better method clarity in multi-step equations.'}
                    </span>
                  </div>
                  <div>
                    <strong>What to practice</strong>
                    <span>
                      {report?.summary?.suggestions?.[0] ||
                        latestFeedback?.missing_key_points?.[0] ||
                        'Shorten final summaries without losing accuracy.'}
                    </span>
                  </div>
                </div>
              </article>

              {plagiarismMatches.length ? (
                <div className="student-plagiarism-panel">
                  <div className="student-plagiarism-panel__head">
                    <strong>Plagiarism Review</strong>
                    <span>Flagged for teacher verification</span>
                  </div>

                  <div className="student-plagiarism-list">
                    {plagiarismMatches.map((match) => (
                      <article
                        key={match.matched_submission_id}
                        className="student-plagiarism-item"
                      >
                        <div>
                          <h4>{match.matched_student_name}</h4>
                          <p>Matched submission: {match.matched_submission_id}</p>
                        </div>
                        <strong>{Math.round(match.overall_similarity * 100)}%</strong>
                      </article>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </section>

          <section id="progress-section" className="student-progress-grid">
            <div className="student-section">
              <div className="student-section__heading">
                <div>
                  <p className="student-section__eyebrow">Progress Placeholder</p>
                  <h3>Monthly performance trend</h3>
                </div>
                <span className="student-section__pill">Last 4 Weeks</span>
              </div>

              <div className="student-progress">
                {progressBars.map((bar) => (
                  <div key={bar.label} className="student-progress__item">
                    <span className={`student-progress__bar ${bar.valueClass}`} />
                    <small>{bar.label}</small>
                  </div>
                ))}
              </div>
            </div>

            <div className="student-section">
              <div className="student-section__heading">
                <div>
                  <p className="student-section__eyebrow">Performance Summary</p>
                  <h3>Question strength cards</h3>
                </div>
                <span className="student-section__pill">
                  {report ? 'From API Report' : 'AI Snapshot'}
                </span>
              </div>

              <div className="student-metrics-grid">
                {performanceCards.map((metric) => (
                  <div key={metric.label} className={`student-metric ${metric.tone}`}>
                    <span>{metric.label}</span>
                    <strong>{metric.value}</strong>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {report ? (
            <section className="student-section student-results-section">
              <div className="student-section__heading">
                <div>
                  <p className="student-section__eyebrow">Question Results</p>
                  <h3>Marks and feedback returned from the backend</h3>
                </div>
                <span className="student-section__pill">Submission Report</span>
              </div>

              <div className="student-results-grid">
                {report.question_results.map((result) => (
                  <article key={result.question_number} className="student-result-card">
                    <div className="student-result-card__head">
                      <div>
                        <h4>Question {result.question_number}</h4>
                        <p>{result.question_text}</p>
                      </div>
                      <span className="student-result-card__score">
                        {result.awarded_marks}/{result.max_marks}
                      </span>
                    </div>

                    <p className="student-result-card__copy">{result.justification}</p>

                    <div className="student-result-card__tags">
                      {(result.missing_key_points.length
                        ? result.missing_key_points
                        : result.strengths
                      )
                        .slice(0, 3)
                        .map((item) => (
                          <span key={item}>{item}</span>
                        ))}
                    </div>
                  </article>
                ))}
              </div>
            </section>
          ) : null}
        </main>
      </div>
    </div>
  );
}

export default StudentDashboard;

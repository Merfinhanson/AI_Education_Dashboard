import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import FileUpload from '../components/FileUpload';
import '../styles/studentDashboard.css';

const navItems = [
  { label: 'Overview', to: '/student/dashboard', meta: 'Dashboard home' },
  { label: 'Upload Sheet', href: '#upload-section', meta: 'Answer uploads' },
  { label: 'AI Feedback', href: '#feedback-section', meta: 'Suggestions' },
  { label: 'Progress', href: '#progress-section', meta: 'Performance charts' },
  { label: 'Teacher View', to: '/teacher/dashboard', meta: 'Preview teacher UI' },
];

const summaryCards = [
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

const performanceCards = [
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

function StudentDashboard() {
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
            subtitle="Upload answer sheets, receive AI feedback, and stay motivated with a polished progress experience."
            actionLabel="Open Study Plan"
            profileName="Jordan"
            profileRole="Grade 10 Student"
          />

          <section className="student-hero">
            <div className="student-hero__content">
              <p className="student-hero__eyebrow">Learning Command Center</p>
              <h2>Understand your performance with faster, clearer feedback.</h2>
              <p>
                Submit answer sheets, check AI feedback highlights, and monitor
                your learning curve in a premium student workspace.
              </p>
            </div>

            <div className="student-hero__panel">
              <div className="student-hero__panel-head">
                <h3>Momentum Snapshot</h3>
                <span>Weekly Growth</span>
              </div>

              <div className="student-hero__panel-grid">
                <div className="student-hero__panel-card">
                  <span>Feedback Accuracy</span>
                  <strong>89%</strong>
                </div>
                <div className="student-hero__panel-card">
                  <span>Practice Completion</span>
                  <strong>94%</strong>
                </div>
                <div className="student-hero__panel-card">
                  <span>Improvement Rate</span>
                  <strong>+11%</strong>
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
                  <p className="student-section__eyebrow">Answer Sheet Upload</p>
                  <h3>Submit your latest response sheet</h3>
                </div>
                <span className="student-section__pill">Secure Upload</span>
              </div>

              <FileUpload
                title="Upload answer sheet"
                description="Share your latest submission to unlock a cleaner feedback loop and progress view."
                buttonLabel="Select Answer Sheet"
                helperText="Drag and drop your response sheet here or browse your files."
                acceptedText="Accepted formats: PDF, PNG, JPG up to 15MB"
              />
            </div>

            <div id="feedback-section" className="student-section">
              <div className="student-section__heading">
                <div>
                  <p className="student-section__eyebrow">AI Feedback</p>
                  <h3>Latest feedback summary</h3>
                </div>
                <span className="student-section__pill">Updated Today</span>
              </div>

              <article className="student-feedback-card">
                <div className="student-feedback-card__head">
                  <span className="student-feedback-card__score">89%</span>
                  <span className="student-feedback-card__badge">Strong Progress</span>
                </div>
                <h4>Algebraic reasoning is becoming more structured.</h4>
                <p>
                  Your last submission showed cleaner step-by-step logic and
                  fewer skipped workings. Focus next on concise explanations for
                  final answers.
                </p>

                <div className="student-feedback-card__list">
                  <div>
                    <strong>What improved</strong>
                    <span>Better method clarity in multi-step equations.</span>
                  </div>
                  <div>
                    <strong>What to practice</strong>
                    <span>Shorten final summaries without losing accuracy.</span>
                  </div>
                </div>
              </article>
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
                  <h3>Subject strength cards</h3>
                </div>
                <span className="student-section__pill">AI Snapshot</span>
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
        </main>
      </div>
    </div>
  );
}

export default StudentDashboard;

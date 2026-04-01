import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import FileUpload from '../components/FileUpload';
import '../styles/teacherDashboard.css';

const navItems = [
  { label: 'Overview', to: '/teacher/dashboard', meta: 'Dashboard home' },
  { label: 'Paper Upload', href: '#upload-section', meta: 'Question bank' },
  { label: 'Answer Scripts', href: '#scripts-section', meta: 'Review queue' },
  { label: 'Analytics', href: '#analytics-section', meta: 'Class insights' },
  { label: 'Student View', to: '/student/dashboard', meta: 'Preview student UI' },
];

const statCards = [
  {
    title: 'Total Students',
    value: '1,284',
    trend: '+12%',
    caption: 'Active across all current classes and sections.',
  },
  {
    title: 'Uploaded Papers',
    value: '86',
    trend: '+08',
    caption: 'Question papers ready for AI-assisted evaluation.',
  },
  {
    title: 'Evaluations Done',
    value: '642',
    trend: '+34%',
    caption: 'Completed review cycles during this academic term.',
  },
];

const answerScripts = [
  {
    student: 'Ava Patel',
    exam: 'Mathematics Midterm',
    status: 'Pending Review',
    submitted: '10:30 AM',
    score: '88/100',
  },
  {
    student: 'Noah Carter',
    exam: 'Physics Weekly Test',
    status: 'AI Scored',
    submitted: '09:15 AM',
    score: '91/100',
  },
  {
    student: 'Mia Thompson',
    exam: 'Chemistry Practice Set',
    status: 'Ready to Publish',
    submitted: 'Yesterday',
    score: '84/100',
  },
];

const reviewStages = [
  { title: 'Uploads in Queue', value: '14', detail: 'Awaiting normalization' },
  { title: 'AI Review Time', value: '12 min', detail: 'Average turnaround' },
  { title: 'Top Class', value: 'Grade 10A', detail: 'Highest completion rate' },
];

const barItems = [
  { label: 'Mon', valueClass: 'teacher-bars__bar--one', value: '68%' },
  { label: 'Tue', valueClass: 'teacher-bars__bar--two', value: '78%' },
  { label: 'Wed', valueClass: 'teacher-bars__bar--three', value: '82%' },
  { label: 'Thu', valueClass: 'teacher-bars__bar--four', value: '74%' },
  { label: 'Fri', valueClass: 'teacher-bars__bar--five', value: '91%' },
];

function TeacherDashboard() {
  return (
    <div className="teacher-page">
      <div className="dashboard-shell">
        <Sidebar
          brand="AstraLearn"
          navItems={navItems}
          footerText="Stay on top of paper uploads, script reviews, and classroom insights in one polished command center."
        />

        <main className="dashboard-content">
          <Navbar
            title="Teacher Dashboard"
            subtitle="Upload papers, review answer scripts, and track assessment performance with clarity."
            actionLabel="Create Evaluation"
            profileName="Dr. Sarah"
            profileRole="Math Faculty Lead"
          />

          <section className="teacher-hero">
            <div className="teacher-hero__content">
              <p className="teacher-hero__eyebrow">Faculty Control Center</p>
              <h2>Run every assessment flow from a single premium workspace.</h2>
              <p>
                Coordinate question paper intake, review answer scripts faster,
                and surface class-wide trends without losing visual clarity.
              </p>

              <div className="teacher-hero__actions">
                <a href="#upload-section" className="teacher-hero__button">
                  Upload Question Paper
                </a>
                <a
                  href="#analytics-section"
                  className="teacher-hero__button teacher-hero__button--ghost"
                >
                  Explore Analytics
                </a>
              </div>
            </div>

            <div className="teacher-hero__panel">
              <div className="teacher-hero__panel-head">
                <h3>Today&apos;s Snapshot</h3>
                <span>Updated 4 mins ago</span>
              </div>

              <div className="teacher-hero__panel-grid">
                {reviewStages.map((item) => (
                  <div key={item.title} className="teacher-hero__panel-card">
                    <span>{item.title}</span>
                    <strong>{item.value}</strong>
                    <p>{item.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="teacher-stats">
            {statCards.map((card) => (
              <Card key={card.title} {...card} />
            ))}
          </section>

          <section className="teacher-main-grid">
            <div id="upload-section" className="teacher-section">
              <div className="teacher-section__heading">
                <div>
                  <p className="teacher-section__eyebrow">Question Paper Intake</p>
                  <h3>Upload new papers for evaluation pipelines</h3>
                </div>
                <span className="teacher-section__pill">Encrypted Intake</span>
              </div>

              <FileUpload
                title="Upload question papers"
                description="Bring in PDFs or editable documents to prepare them for AI-assisted review workflows."
                buttonLabel="Select Question Paper"
                helperText="Drag and drop files here or browse from your device."
                acceptedText="Accepted formats: PDF, DOCX, JPG up to 20MB"
              />
            </div>

            <div className="teacher-section">
              <div className="teacher-section__heading">
                <div>
                  <p className="teacher-section__eyebrow">Review Pipeline</p>
                  <h3>Current evaluation activity</h3>
                </div>
                <span className="teacher-section__pill">Live Queue</span>
              </div>

              <div className="teacher-activity-list">
                <div className="teacher-activity-item">
                  <strong>Batch 04 normalized</strong>
                  <span>26 scripts prepared for model review.</span>
                </div>
                <div className="teacher-activity-item">
                  <strong>Rubric update applied</strong>
                  <span>Scoring logic refreshed for Physics Weekly Test.</span>
                </div>
                <div className="teacher-activity-item">
                  <strong>Feedback pack published</strong>
                  <span>Grade 9A can now view annotated summaries.</span>
                </div>
              </div>
            </div>
          </section>

          <section id="scripts-section" className="teacher-section">
            <div className="teacher-section__heading">
              <div>
                <p className="teacher-section__eyebrow">Answer Scripts</p>
                <h3>View answer script review cards</h3>
              </div>
              <button type="button" className="teacher-section__action">
                Open All Scripts
              </button>
            </div>

            <div className="teacher-script-grid">
              {answerScripts.map((script) => (
                <article key={script.student} className="teacher-script-card">
                  <div className="teacher-script-card__head">
                    <div>
                      <h4>{script.student}</h4>
                      <p>{script.exam}</p>
                    </div>
                    <span className="teacher-script-card__status">{script.status}</span>
                  </div>

                  <div className="teacher-script-card__meta">
                    <span>Submitted {script.submitted}</span>
                    <strong>{script.score}</strong>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section id="analytics-section" className="teacher-chart-grid">
            <div className="teacher-chart-panel">
              <div className="teacher-section__heading">
                <div>
                  <p className="teacher-section__eyebrow">Analytics Placeholder</p>
                  <h3>Submission throughput</h3>
                </div>
                <span className="teacher-section__pill">This Week</span>
              </div>

              <div className="teacher-bars">
                {barItems.map((bar) => (
                  <div key={bar.label} className="teacher-bars__item">
                    <span className={`teacher-bars__bar ${bar.valueClass}`} />
                    <strong>{bar.value}</strong>
                    <small>{bar.label}</small>
                  </div>
                ))}
              </div>
            </div>

            <div className="teacher-chart-panel">
              <div className="teacher-section__heading">
                <div>
                  <p className="teacher-section__eyebrow">Analytics Placeholder</p>
                  <h3>Class mastery distribution</h3>
                </div>
                <span className="teacher-section__pill">AI Summary</span>
              </div>

              <div className="teacher-distribution">
                <div className="teacher-distribution__ring">
                  <div className="teacher-distribution__ring-inner">84%</div>
                </div>

                <div className="teacher-distribution__legend">
                  <div>
                    <span className="teacher-distribution__dot teacher-distribution__dot--primary" />
                    Mastered Concepts
                  </div>
                  <div>
                    <span className="teacher-distribution__dot teacher-distribution__dot--accent" />
                    Needs Review
                  </div>
                  <div>
                    <span className="teacher-distribution__dot teacher-distribution__dot--muted" />
                    Yet to Evaluate
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default TeacherDashboard;

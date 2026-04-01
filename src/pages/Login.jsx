import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/login.css';

const roleOptions = [
  {
    id: 'teacher',
    title: 'Teacher',
    description: 'Upload papers, review scripts, and monitor analytics.',
  },
  {
    id: 'student',
    title: 'Student',
    description: 'Submit answer sheets, review AI feedback, and track growth.',
  },
];

const platformMetrics = [
  { value: '12k+', label: 'Scripts Processed' },
  { value: '98%', label: 'Review Accuracy' },
  { value: '24/7', label: 'AI Assistance' },
];

const workflowItems = [
  'Upload question papers and answer sheets with structured review queues.',
  'Track classroom performance using smart insights and dashboard summaries.',
  'Give students premium feedback experiences with clear progression visuals.',
];

function Login() {
  const [role, setRole] = useState('teacher');
  const navigate = useNavigate();

  const handleSubmit = (event) => {
    event.preventDefault();
    navigate(role === 'teacher' ? '/teacher/dashboard' : '/student/dashboard');
  };

  return (
    <div className="login-page">
      <section className="login-showcase">
        <div className="login-showcase__badge">AstraLearn AI Suite</div>
        <h1>Premium assessment workflows for modern classrooms.</h1>
        <p className="login-showcase__lead">
          Centralize evaluation, feedback, and student performance into one calm,
          polished interface built for educators and learners.
        </p>

        <div className="login-showcase__metrics">
          {platformMetrics.map((metric) => (
            <div key={metric.label} className="login-showcase__metric">
              <strong>{metric.value}</strong>
              <span>{metric.label}</span>
            </div>
          ))}
        </div>

        <div className="login-showcase__panel">
          <div className="login-showcase__panel-head">
            <h2>Why teams love this workspace</h2>
            <span>Built for focus</span>
          </div>

          <div className="login-showcase__timeline">
            {workflowItems.map((item, index) => (
              <div key={item} className="login-showcase__timeline-item">
                <span className="login-showcase__timeline-index">
                  0{index + 1}
                </span>
                <p>{item}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-panel__header">
          <p className="login-panel__eyebrow">Welcome Back</p>
          <h2>Sign in to your dashboard</h2>
          <p>
            Choose your role to preview the tailored workspace experience for
            teachers and students.
          </p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="login-form__role-switch">
            {roleOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`login-form__role ${
                  role === option.id ? 'is-active' : ''
                }`}
                onClick={() => setRole(option.id)}
              >
                <span>{option.title}</span>
                <small>{option.description}</small>
              </button>
            ))}
          </div>

          <label className="login-form__field">
            <span>Email Address</span>
            <input type="email" placeholder="you@school.edu" required />
          </label>

          <label className="login-form__field">
            <span>Password</span>
            <input type="password" placeholder="Enter your password" required />
          </label>

          <div className="login-form__meta">
            <label className="login-form__checkbox">
              <input type="checkbox" defaultChecked />
              <span>Keep me signed in</span>
            </label>
            <a href="/login">Need help?</a>
          </div>

          <button type="submit" className="login-form__submit">
            Continue as {role === 'teacher' ? 'Teacher' : 'Student'}
          </button>
        </form>
      </section>
    </div>
  );
}

export default Login;

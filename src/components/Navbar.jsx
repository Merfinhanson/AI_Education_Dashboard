import '../styles/navbar.css';

function Navbar({ title, subtitle, actionLabel, profileName, profileRole }) {
  return (
    <header className="navbar">
      <div className="navbar__copy">
        <p className="navbar__eyebrow">Premium Dashboard</p>
        <h1>{title}</h1>
        <p className="navbar__subtitle">{subtitle}</p>
      </div>

      <div className="navbar__actions">
        <div className="navbar__status">
          <span className="navbar__status-dot" />
          AI Workspace Live
        </div>

        {actionLabel ? (
          <button type="button" className="navbar__button">
            {actionLabel}
          </button>
        ) : null}

        <div className="navbar__profile">
          <div className="navbar__avatar">{profileName.charAt(0)}</div>
          <div>
            <span className="navbar__profile-name">{profileName}</span>
            <span className="navbar__profile-role">{profileRole}</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;

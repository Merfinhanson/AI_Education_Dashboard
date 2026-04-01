import { NavLink } from 'react-router-dom';
import '../styles/sidebar.css';

function Sidebar({ brand, navItems, footerText }) {
  return (
    <aside className="sidebar">
      <div className="sidebar__brand">
        <div className="sidebar__brand-mark">A</div>
        <div>
          <p className="sidebar__eyebrow">AI Education Platform</p>
          <h2>{brand}</h2>
        </div>
      </div>

      <nav className="sidebar__nav" aria-label="Dashboard navigation">
        {navItems.map((item) =>
          item.to ? (
            <NavLink
              key={item.label}
              to={item.to}
              className={({ isActive }) =>
                `sidebar__link ${isActive ? 'is-active' : ''}`
              }
            >
              <div>
                <span className="sidebar__link-title">{item.label}</span>
                <span className="sidebar__link-meta">{item.meta}</span>
              </div>
              <span className="sidebar__link-indicator" />
            </NavLink>
          ) : (
            <a key={item.label} href={item.href} className="sidebar__link">
              <div>
                <span className="sidebar__link-title">{item.label}</span>
                <span className="sidebar__link-meta">{item.meta}</span>
              </div>
              <span className="sidebar__link-indicator" />
            </a>
          ),
        )}
      </nav>

      <div className="sidebar__footer">
        <p className="sidebar__footer-label">Workspace Note</p>
        <p className="sidebar__footer-copy">{footerText}</p>
      </div>
    </aside>
  );
}

export default Sidebar;

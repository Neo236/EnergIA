import { NavLink } from 'react-router-dom'

export function Navbar() {
  return (
    <header className="topbar">
      <div className="topbar__inner">
        <NavLink to="/" className="brand">EnergiAI</NavLink>
        <nav className="nav" aria-label="Principal">
          <NavLink
            to="/"
            end
            className={({ isActive }) => (isActive ? 'nav__link is-active' : 'nav__link')}
          >
            Analizar
          </NavLink>
        </nav>
      </div>
    </header>
  )
}

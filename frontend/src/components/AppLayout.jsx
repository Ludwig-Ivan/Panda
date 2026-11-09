import { Link, NavLink, Outlet } from 'react-router-dom'
import HelpChat from './HelpChat.jsx'
import '../app.css'

// ready=false: pantalla aún no construida (se muestra deshabilitada).
const NAV = [
  { to: '/inicio', label: 'Inicio', icon: '🏠', ready: true },
  { to: '/comidas/nueva', label: 'Registrar comida', icon: '➕', ready: true },
  { to: '/historial', label: 'Historial', icon: '🕘', ready: true },
  { to: '/progreso', label: 'Progreso', icon: '📊', ready: false },
  { to: '/ajustes', label: 'Ajustes', icon: '⚙️', ready: false },
]

const Item = ({ n, cls }) => n.ready
  ? <NavLink to={n.to} className={({ isActive }) => `${cls}${isActive ? ' active' : ''}`}><span aria-hidden="true">{n.icon}</span>{n.label}</NavLink>
  : <span className={`${cls} off`} aria-disabled="true"><span aria-hidden="true">{n.icon}</span>{n.label}<em className="soon">Pronto</em></span>

export default function AppLayout() {
  const [inicio, nueva, ...resto] = NAV
  return (
    <div className="app-shell">
      <aside className="side">
        <Link to="/inicio" className="brand"><span className="logo">🐼</span>PANDA</Link>
        <nav aria-label="Principal">{NAV.map((n) => <Item key={n.to} n={n} cls="nav-i" />)}</nav>
      </aside>
      <div className="app-main">
        <header className="app-top"><Link to="/inicio" className="brand"><span className="logo">🐼</span>PANDA</Link></header>
        <Outlet />
      </div>
      <nav className="tabbar" aria-label="Principal móvil">
        <Item n={inicio} cls="tab" />
        <Item n={resto[0]} cls="tab" />
        <NavLink to={nueva.to} className="tab-fab" aria-label="Registrar comida">＋</NavLink>
        <Item n={resto[1]} cls="tab" />
        <Item n={resto[2]} cls="tab" />
      </nav>
      <HelpChat />
    </div>
  )
}

import { Link, NavLink, Outlet } from 'react-router-dom'
import HelpChat from './HelpChat.jsx'
import ImgSlot from './ImgSlot.jsx'
import { IMG } from '../data/imagenes.js'
import s from './AppLayout.module.css'
import '../app.css' // estilos de las demás pantallas (se irán migrando a módulos)
import { House, Plus, History, ChartColumn, Settings, Bell } from 'lucide-react'

// ready=false: pantalla aún no construida (se muestra deshabilitada).
const NAV = [
  { to: '/inicio', label: 'Inicio', icon: <House size={20} aria-hidden="true" />, ready: true },
  { to: '/comidas/nueva', label: 'Registrar comida', icon: <Plus size={20} aria-hidden="true" />, ready: true },
  { to: '/historial', label: 'Historial', icon: <History size={20} aria-hidden="true" />, ready: true },
  { to: '/progreso', label: 'Progreso', icon: <ChartColumn size={20} aria-hidden="true" />, ready: false },
  { to: '/ajustes', label: 'Ajustes', icon: <Settings size={20} aria-hidden="true" />, ready: false },
]

function Item({ n, base }) {
  return n.ready
    ? <NavLink to={n.to} className={({ isActive }) => `${base}${isActive ? ` ${s.active}` : ''}`}><span aria-hidden="true">{n.icon}</span>{n.label}</NavLink>
    : <span className={`${base} ${s.off}`} aria-disabled="true"><span aria-hidden="true">{n.icon}</span>{n.label}<em className={s.soon}>Pronto</em></span>
}

const Brand = () => (
  <Link to="/inicio" className={s.brand}>
    <ImgSlot src={IMG.logo} w={52} h={52} round label="Logo" alt="Panda" />
    <span><b>PANDA</b><small>Come mejor, avanza más</small></span>
  </Link>
)

export default function AppLayout() {
  return (
    <div className={s.shell}>
      <aside className={s.side}>
        <Brand />
        <nav className={s.nav} aria-label="Principal">{NAV.map((n) => <Item key={n.to} n={n} base={s.navItem} />)}</nav>
        <div className={s.sideFoot}>
          <ImgSlot src={IMG.hojasMenu} w={200} h={160} label="Hojas decorativas" />
          <p>Pequeños cambios, grandes resultados.</p>
        </div>
      </aside>

      <div className={s.main}>
        <header className={s.top}>
          <Link to="/inicio" className={s.topBrand}><ImgSlot src={IMG.logo} w={36} h={36} round label="Logo" alt="Panda" /><b>PANDA</b></Link>
          <input className={s.search} type="search" placeholder="Buscar alimentos, recetas y más… (próximamente)" disabled aria-label="Buscar (próximamente)" />
          <button type="button" className={s.iconBtn} disabled aria-label="Notificaciones (próximamente)"><Bell size={20} aria-hidden="true" /></button>
          <div className={s.user}><ImgSlot src={IMG.avatar} w={36} h={36} round label="Foto" alt="Tu foto" /><span>Mi cuenta</span></div>
        </header>
        <Outlet />
      </div>

      <nav className={s.tabbar} aria-label="Principal móvil">
        <Item n={NAV[0]} base={s.tab} />
        <Item n={NAV[2]} base={s.tab} />
        <NavLink to={NAV[1].to} className={s.tabFab} aria-label="Registrar comida"><Plus size={20} aria-hidden="true" /></NavLink>
        <Item n={NAV[3]} base={s.tab} />
        <Item n={NAV[4]} base={s.tab} />
      </nav>
      <HelpChat />
    </div>
  )
}

import { Link, Outlet, useLocation } from 'react-router-dom'
import logo from "../assets/logo.png"

export default function PublicLayout() {
  const { pathname } = useLocation()
  const home = pathname === '/'
  return (
    <>
      <header className="top">
        <div className="wrap row">
          <Link to="/" className="brand"><img className="logo" src = {logo}/>Panda</Link>
          {home && (
            <nav className="links">
              <a href="#funciones">Funciones</a><a href="#calculadora">Calculadora</a><a href="#como">Cómo funciona</a>
            </nav>
          )}
          <span className="grow" />
          <Link to="/acceso" className="btn hide-sm">Iniciar sesión</Link>
          <Link to="/registro" className="btn p">Crear cuenta</Link>
        </div>
      </header>
      <Outlet />
      <footer className="foot-bar">
        <div className="wrap row wrapx">
          <span>Bamboo · Pequeños cambios, grandes resultados.</span>
          <span className="legal-links">
            <Link to="/avisos/privacidad">Privacidad</Link>
            <Link to="/avisos/avisos-salud">Avisos de salud</Link>
            <Link to="/avisos/procesamiento-terceros">Terceros</Link>
          </span>
        </div>
      </footer>
    </>
  )
}

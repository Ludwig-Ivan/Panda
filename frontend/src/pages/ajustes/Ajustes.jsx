import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { userApi } from '../../lib/userApi.js'
import s from './Ajustes.module.css'

const Row = ({ to, title, sub, danger }) => (
  <Link className={`${s.row} ${danger ? s.danger : ''}`} to={to}>
    <span>{title}{sub && <small>{sub}</small>}</span><span className={s.chev} aria-hidden="true">›</span>
  </Link>
)

export default function Ajustes() {
  const nav = useNavigate()
  const [cuenta, setCuenta] = useState(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  useEffect(() => { userApi.getCuenta().then(setCuenta).catch(() => {}) }, [])

  async function logout() {
    setBusy(true); setErr('')
    try { await userApi.logout(); nav('/acceso', { replace: true }) }
    catch { setErr('No pudimos cerrar la sesión. Inténtalo de nuevo.'); setBusy(false) }
  }

  return (
    <main className={s.page}>
      <header><h1>Ajustes</h1></header>

      <section className={`${s.card} ${s.account}`} aria-label="Tu cuenta">
        <span className={s.avatar} aria-hidden="true">{cuenta ? cuenta.email[0].toUpperCase() : ''}</span>
        <div><b>Mi cuenta</b><small>{cuenta ? cuenta.email : 'Cargando…'}</small></div>
      </section>

      <section className={s.group}>
        <h2 className={s.groupTitle}>Tu perfil</h2>
        <div className={s.list}>
          <Row to="/ajustes/perfil" title="Perfil físico" sub="Edad, sexo, peso, estatura y actividad" />
          <Row to="/ajustes/actividades" title="Actividades preferidas" sub="Se priorizan en tus recomendaciones" />
        </div>
      </section>

      <section className={s.group}>
        <h2 className={s.groupTitle}>Privacidad</h2>
        <div className={s.list}>
          <Row to="/ajustes/privacidad" title="Privacidad y datos" sub="Fotos y avisos aceptados" />
          <Row to="/avisos/privacidad" title="Avisos legales" />
        </div>
      </section>

      <section className={s.group}>
        <h2 className={s.groupTitle}>Sesión</h2>
        <div className={s.list}>
          <button type="button" className={s.row} onClick={logout} disabled={busy}><span>{busy ? 'Cerrando sesión…' : 'Cerrar sesión'}</span></button>
        </div>
        {err && <p className={s.msgErr} role="alert">{err}</p>}
      </section>

      <section className={s.group}>
        <h2 className={s.groupTitle}>Zona de riesgo</h2>
        <div className={s.list}>
          <Row to="/ajustes/historial" title="Eliminar historial" sub="Borra todas tus comidas y fotos" danger />
          <Row to="/ajustes/cuenta" title="Eliminar cuenta" sub="Borra tu cuenta y todos tus datos" danger />
        </div>
      </section>
    </main>
  )
}

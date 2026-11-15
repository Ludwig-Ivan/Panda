import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { userApi } from '../../lib/userApi.js'
import SubPage from './SubPage.jsx'
import s from './Ajustes.module.css'

export default function EliminarCuenta() {
  const nav = useNavigate()
  const [pwd, setPwd] = useState('')
  const [ok, setOk] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  async function del(e) {
    e.preventDefault()
    if (!pwd) return setErr('Escribe tu contraseña para continuar.')
    setBusy(true); setErr('')
    try { await userApi.deleteCuenta(pwd); nav('/', { replace: true }) }
    catch (x) { setErr(x.status === 400 || x.status === 403 ? 'La contraseña no es correcta.' : 'No pudimos eliminar tu cuenta. Inténtalo de nuevo.'); setBusy(false) }
  }

  return (
    <SubPage title="Eliminar cuenta" desc="Se borrarán tu cuenta y todos tus datos.">
      <section className={s.warnBox}>
        <b>Se eliminará de inmediato:</b>
        <ul>
          <li>Tu cuenta, tu perfil y tus preferencias.</li>
          <li>Todas tus comidas y sus fotos.</li>
          <li>El registro de los avisos que aceptaste.</li>
        </ul>
        <span>Tus datos también desaparecen de los respaldos cuando vence su retención de 7 días. Esta acción no se puede deshacer.</span>
      </section>
      <form className={s.card} onSubmit={del} noValidate>
        <label className={s.field}>Tu contraseña
          <input className={s.input} type="password" autoComplete="current-password" value={pwd} onChange={(e) => setPwd(e.target.value)} aria-invalid={!!err} />
        </label>
        <label className={s.opt}><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} /><span>Entiendo que mi cuenta se eliminará de forma permanente.</span></label>
        {err && <p className={s.msgErr} role="alert">{err}</p>}
        <div className={s.actions}>
          <Link className={s.btn} to="/ajustes">Cancelar</Link>
          <button className={`${s.btn} ${s.btnDanger}`} disabled={!ok || !pwd || busy}>{busy ? 'Eliminando…' : 'Eliminar mi cuenta'}</button>
        </div>
      </form>
    </SubPage>
  )
}

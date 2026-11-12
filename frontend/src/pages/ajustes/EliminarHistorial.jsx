import { useState } from 'react'
import { Link } from 'react-router-dom'
import { userApi } from '../../lib/userApi.js'
import SubPage from './SubPage.jsx'
import s from './Ajustes.module.css'

export default function EliminarHistorial() {
  const [ok, setOk] = useState(false)
  const [busy, setBusy] = useState(false)
  const [done, setDone] = useState(false)
  const [err, setErr] = useState('')

  async function del() {
    setBusy(true); setErr('')
    try { await userApi.deleteHistorial(); setDone(true) }
    catch { setErr('No pudimos eliminar tu historial. Inténtalo de nuevo.') } finally { setBusy(false) }
  }

  if (done) return (
    <SubPage title="Historial eliminado">
      <p className={s.msgOk} role="status">Tus comidas y sus fotos se eliminaron.</p>
      <Link className={`${s.btn} ${s.btnP}`} to="/inicio">Volver al inicio</Link>
    </SubPage>
  )

  return (
    <SubPage title="Eliminar historial" desc="Borra todo lo que registraste, pero conserva tu cuenta y tu perfil.">
      <section className={s.warnBox}>
        <b>Se eliminará de inmediato:</b>
        <ul><li>Todas tus comidas, con sus alimentos y correcciones.</li><li>Las recomendaciones de actividad asociadas.</li><li>Las fotos de tus comidas.</li></ul>
        <span>Esta acción no se puede deshacer.</span>
      </section>
      <label className={s.opt}><input type="checkbox" checked={ok} onChange={(e) => setOk(e.target.checked)} /><span>Entiendo que se borrará todo mi historial.</span></label>
      {err && <p className={s.msgErr} role="alert">{err}</p>}
      <div className={s.actions}>
        <Link className={s.btn} to="/ajustes">Cancelar</Link>
        <button type="button" className={`${s.btn} ${s.btnDanger}`} disabled={!ok || busy} onClick={del}>{busy ? 'Eliminando…' : 'Eliminar historial'}</button>
      </div>
    </SubPage>
  )
}

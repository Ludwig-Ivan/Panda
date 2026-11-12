import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { userApi } from '../../lib/userApi.js'
import { AVISOS } from '../../data/avisos.js'
import SubPage from './SubPage.jsx'
import s from './Ajustes.module.css'

const aviso = (tipo) => Object.entries(AVISOS).find(([, a]) => a.tipo === tipo)

export default function Privacidad() {
  const [fotos, setFotos] = useState(null)
  const [cons, setCons] = useState([])
  const [state, setState] = useState('loading')
  const [err, setErr] = useState('')

  useEffect(() => {
    Promise.all([userApi.getCuenta(), userApi.getConsentimientos()])
      .then(([c, k]) => { setFotos(c.guardar_fotos); setCons(k); setState('ok') })
      .catch(() => setState('error'))
  }, [])

  async function toggle() {
    const next = !fotos
    setFotos(next); setErr('')
    try { await userApi.saveFotos(next) } catch { setFotos(!next); setErr('No pudimos guardar el cambio. Inténtalo de nuevo.') }
  }

  return (
    <SubPage title="Privacidad y datos" desc="Decide qué se conserva y revisa los avisos que aceptaste.">
      {state === 'loading' && <p className={s.hint} role="status">Cargando…</p>}
      {state === 'error' && <p className={s.msgErr} role="alert">No pudimos cargar esta información.</p>}
      {state === 'ok' && (
        <>
          <section className={s.card}>
            <div className={s.switchRow}>
              <div><b>Guardar mis fotos en el historial</b><small>Se aplica a las próximas comidas que registres.</small></div>
              <button type="button" role="switch" aria-checked={fotos} aria-label="Guardar mis fotos en el historial" className={s.switch} onClick={toggle} />
            </div>
            {err && <p className={s.msgErr} role="alert">{err}</p>}
          </section>

          <section className={s.card}>
            <h2 className={s.sectionTitle}>Avisos aceptados</h2>
            <ul className={s.recap}>
              {cons.map((c) => {
                const a = aviso(c.tipo)
                return (
                  <li key={`${c.tipo}-${c.version}`}>
                    <span>{a ? a[1].titulo : c.tipo}<small> Versión {c.version}. Aceptado el {new Date(c.aceptado_at).toLocaleDateString('es-MX', { dateStyle: 'long' })}.</small></span>
                    {a && <Link to={`/avisos/${a[0]}`}>Leer</Link>}
                  </li>
                )
              })}
            </ul>
            <p className={s.hint}>Los tres avisos son necesarios para registrar comidas. Si quieres retirarlos, puedes <Link to="/ajustes/cuenta" style={{ color: 'var(--or)' }}>eliminar tu cuenta</Link>.</p>
          </section>
        </>
      )}
    </SubPage>
  )
}

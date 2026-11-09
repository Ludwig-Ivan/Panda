import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { mealsApi } from '../lib/mealsApi.js'
import '../app2.css'

export default function ComidaDetalle() {
  const { id } = useParams()
  const nav = useNavigate()
  const [m, setM] = useState(null)
  const [rec, setRec] = useState(null)
  const [state, setState] = useState('loading') // loading | ok | notfound | error
  const [ask, setAsk] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    let alive = true
    setState('loading')
    mealsApi.getComida(id).then((r) => { if (alive) { setM(r); setState('ok') } }).catch((e) => alive && setState(e.status === 404 ? 'notfound' : 'error'))
    mealsApi.getRecomendacion(id).then((r) => alive && setRec(r)).catch(() => {}) // no bloquea la pantalla
    return () => { alive = false }
  }, [id])

  async function del() {
    setBusy(true); setErr('')
    try { await mealsApi.deleteComida(id); nav('/inicio', { replace: true }) }
    catch { setErr('No pudimos eliminar la comida. Inténtalo de nuevo.'); setBusy(false) }
  }

  if (state === 'loading') return <main className="page narrow"><p className="hint" role="status">Cargando…</p></main>
  if (state !== 'ok') return (
    <main className="page narrow">
      <p className={state === 'error' ? 'err box' : 'ok box'} role="alert">{state === 'notfound' ? 'No encontramos esta comida.' : 'No pudimos cargar la comida.'}</p>
      <Link className="btn" to="/inicio">Volver al inicio</Link>
    </main>
  )

  return (
    <main className="page narrow">
      <header>
        <p className="hint">{new Date(m.consumida_at).toLocaleString('es-MX', { dateStyle: 'long', timeStyle: 'short' })}</p>
        <h1>Detalle de la comida</h1>
      </header>
      <section className="card form-card">
        {m.foto && <img className="thumb-l" src={m.foto} alt="Foto de la comida" />}
        <div className="preview"><span>Total aproximado</span><b>{m.kcal_total} kcal</b></div>
        {m.kcal_min !== m.kcal_max && <small className="hint">Rango estimado: {m.kcal_min} a {m.kcal_max} kcal</small>}
        <ul className="recap">
          {m.items.map((x, i) => (
            <li key={i}><span>{x.nombre}<small> · {x.porcion_g} g</small>{x.origen === 'usuario' && <> <span className="pill">Agregado por ti</span></>}</span><b>{x.kcal} kcal</b></li>
          ))}
        </ul>
      </section>

      {rec && (
        <section className="card">
          <h2>Para equilibrar esta comida</h2>
          <ul className="recap">
            {rec.items.slice(0, 3).map((r) => (
              <li key={r.actividad.id}><span>{r.actividad.nombre}</span><b>{r.duracion_min} min</b></li>
            ))}
          </ul>
          <Link className="btn full" to={`/comidas/${id}/actividad`}>Ver todas las opciones</Link>
        </section>
      )}

      {!ask ? (
        <button type="button" className="link-btn danger" onClick={() => setAsk(true)}>Eliminar comida</button>
      ) : (
        <div className="confirm-del" role="alertdialog" aria-label="Confirmar eliminación">
          <p>Se eliminará esta comida y su foto. Esta acción no se puede deshacer.</p>
          {err && <small className="err" role="alert">{err}</small>}
          <div className="row-btns">
            <button type="button" className="btn" onClick={() => setAsk(false)} disabled={busy}>Cancelar</button>
            <button type="button" className="btn p" onClick={del} disabled={busy}>{busy ? 'Eliminando…' : 'Eliminar'}</button>
          </div>
        </div>
      )}
      <Link className="hint center" to="/inicio">Volver al inicio</Link>
    </main>
  )
}

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { mealsApi } from '../lib/mealsApi.js'
import '../app2.css'

const dayLabel = (iso) => {
  const d = new Date(iso), today = new Date(), y = new Date(); y.setDate(today.getDate() - 1)
  if (d.toDateString() === today.toDateString()) return 'Hoy'
  if (d.toDateString() === y.toDateString()) return 'Ayer'
  return d.toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long' })
}

export default function Historial() {
  const [list, setList] = useState([])
  const [next, setNext] = useState(null)
  const [state, setState] = useState('loading') // loading | ok | error
  const [more, setMore] = useState(false)

  async function load(cursor) {
    try {
      const r = await mealsApi.getHistorial(cursor)
      setList((l) => (cursor ? [...l, ...r.results] : r.results)); setNext(r.next); setState('ok')
    } catch { setState('error') } finally { setMore(false) }
  }
  useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const groups = list.reduce((m, c) => {
    const k = new Date(c.consumida_at).toDateString()
    if (!m.has(k)) m.set(k, { label: dayLabel(c.consumida_at), items: [] })
    m.get(k).items.push(c); return m
  }, new Map())

  return (
    <main className="page">
      <header><h1>Historial</h1><p className="hint">Tus comidas confirmadas, de la más reciente a la más antigua.</p></header>
      {state === 'loading' && <p className="hint" role="status">Cargando…</p>}
      {state === 'error' && <p className="err box" role="alert">No pudimos cargar tu historial.</p>}
      {state === 'ok' && list.length === 0 && (
        <section className="card"><p className="hint">Aún no hay comidas guardadas.</p><Link className="btn p" to="/comidas/nueva">Registrar mi primera comida</Link></section>
      )}
      {[...groups.values()].map((g) => (
        <section className="card day" key={g.label}>
          <h2 style={{ textTransform: 'capitalize' }}>{g.label}<span>{g.items.reduce((a, c) => a + c.kcal, 0)} kcal</span></h2>
          <ul className="meals">
            {g.items.map((c) => (
              <li key={c.id}><Link className="meal-row" to={`/comidas/${c.id}`}><time>{c.hora}</time><span>{c.nombre}</span><b>{c.kcal} kcal</b></Link></li>
            ))}
          </ul>
        </section>
      ))}
      {next && <button type="button" className="btn" disabled={more} onClick={() => { setMore(true); load(next) }}>{more ? 'Cargando…' : 'Cargar más'}</button>}
    </main>
  )
}

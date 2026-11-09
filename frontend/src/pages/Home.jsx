import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { mealsApi } from '../lib/mealsApi.js'

export default function Home() {
  const [h, setH] = useState(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => { mealsApi.getHoy().then(setH).catch(() => setFailed(true)) }, [])

  const fecha = new Date().toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long' })
  const total = h ? h.comidas.reduce((a, c) => a + c.kcal, 0) : 0
  const meta = h?.meta_kcal || 1
  const left = h ? meta - total : 0

  return (
    <main className="page">
      <header><p className="hint cap">{fecha}</p><h1>¡Hola!</h1></header>
      {failed && <p className="err box" role="alert">No pudimos cargar tu resumen. Inténtalo de nuevo más tarde.</p>}

      <section className="card kcal-card" aria-label="Calorías de hoy">
        <div className="ring">
          <svg viewBox="0 0 120 120" aria-hidden="true">
            <circle className="trk" cx="60" cy="60" r="52" />
            <circle className="fill" cx="60" cy="60" r="52" style={{ strokeDashoffset: 326.7 * (1 - Math.min(total / meta, 1)) }} />
          </svg>
          <div className="ring-txt"><b>{total}</b><small>de {h ? h.meta_kcal : '…'} kcal</small></div>
        </div>
        <div>
          <h2>Calorías de hoy</h2>
          <p className="hint">{!h ? 'Cargando…' : left >= 0 ? `Te quedan ${left} kcal.` : `Superaste tu meta por ${-left} kcal.`}</p>
          <Link to="/comidas/nueva" className="btn p">Registrar comida</Link>
        </div>
      </section>

      <section className="card">
        <h2>Comidas de hoy</h2>
        {h && h.comidas.length === 0 && <p className="hint">Aún no registras comidas hoy. Empieza con una foto.</p>}
        <ul className="meals">
          {h?.comidas.map((c) => (
            <li key={c.id}><Link className="meal-row" to={`/comidas/${c.id}`}><time>{c.hora}</time><span>{c.nombre}</span><b>{c.kcal} kcal</b></Link></li>
          ))}
        </ul>
      </section>
    </main>
  )
}

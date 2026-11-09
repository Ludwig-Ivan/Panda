import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { mealsApi } from '../lib/mealsApi.js'
import '../app2.css'

export default function Recomendacion() {
  const { id } = useParams()
  const [r, setR] = useState(null)
  const [state, setState] = useState('loading')

  useEffect(() => {
    let alive = true
    mealsApi.getRecomendacion(id).then((x) => { if (alive) { setR(x); setState('ok') } }).catch(() => alive && setState('error'))
    return () => { alive = false }
  }, [id])

  return (
    <main className="page narrow">
      <header>
        <h1>Actividad recomendada</h1>
        {r && <p className="hint">Para equilibrar unas {r.kcal_objetivo} kcal. Elige una de estas opciones: cada una equilibra la comida por sí sola.</p>}
      </header>
      {state === 'loading' && <p className="hint" role="status">Calculando opciones…</p>}
      {state === 'error' && <p className="err box" role="alert">No pudimos cargar las recomendaciones.</p>}
      {r && (
        <>
          <div className="rec">
            {r.items.map((x) => (
              <article className="card rec-card" key={x.actividad.id}>
                <div>
                  <b>{x.actividad.nombre}</b>
                  <small>{x.actividad.intensidad} · ≈ {x.kcal_estimadas} kcal</small>
                  {x.es_preferida && <span className="pill fav">Una de tus favoritas</span>}
                </div>
                <div className="rec-min">{x.duracion_min} min<small>{x.sesiones > 1 ? `en ${x.sesiones} sesiones` : 'en una sesión'}</small></div>
              </article>
            ))}
          </div>
          <small className="hint">Calculado con un peso de {r.peso_kg_usado} kg (fórmula {r.formula_version}). Son estimaciones orientativas y no sustituyen la guía de un profesional del deporte o de la salud.</small>
        </>
      )}
      <Link className="btn" to={`/comidas/${id}`}>Volver a la comida</Link>
    </main>
  )
}

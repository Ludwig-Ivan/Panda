import { Link } from 'react-router-dom'
import { AVISOS, VERSION } from '../../data/avisos.js'

export default function StepConsent({ d, setD, errors }) {
  const c = d.consents
  const all = Object.values(c).every(Boolean)
  const toggle = (t) => setD((p) => ({ ...p, consents: { ...p.consents, [t]: !p.consents[t] } }))
  const setAll = (v) => setD((p) => ({ ...p, consents: Object.fromEntries(Object.keys(p.consents).map((k) => [k, v])) }))

  return (
    <fieldset className="onb-step">
      <legend>Avisos y consentimientos</legend>
      <p className="sub">Necesitamos tu aceptación para analizar tus comidas. Cada aviso se abre en otra pestaña para que no pierdas tu avance.</p>
      <label className="opt">
        <input type="checkbox" checked={all} onChange={(e) => setAll(e.target.checked)} />
        <span><b>Aceptar todos</b></span>
      </label>
      {Object.entries(AVISOS).map(([slug, a]) => (
        <label className="opt" key={slug}>
          <input type="checkbox" checked={c[a.tipo]} onChange={() => toggle(a.tipo)} />
          <span>
            <b>{a.titulo}</b>
            <small>Versión {VERSION}. <Link to={`/avisos/${slug}`} target="_blank" rel="noopener noreferrer">Leer aviso</Link></small>
          </span>
        </label>
      ))}
      {errors.consents && <small className="err" role="alert">{errors.consents}</small>}
    </fieldset>
  )
}

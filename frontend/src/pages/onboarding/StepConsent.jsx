import { Link } from 'react-router-dom'
import { AVISOS, VERSION } from '../../data/avisos.js'

export default function StepConsent({ d, setD, errors }) {
  const consents = d.consents
  const allAccepted = Object.values(consents).every(Boolean)

  const toggleConsent = (type) => {
    setD((prev) => ({
      ...prev,
      consents: { ...prev.consents, [type]: !prev.consents[type] },
    }))
  }

  const setAllConsents = (checked) => {
    setD((prev) => ({
      ...prev,
      consents: Object.fromEntries(Object.keys(prev.consents).map((key) => [key, checked])),
    }))
  }

  return (
    <fieldset className="onb-step">
      <legend>Avisos y consentimientos</legend>
      <p className="sub">
        Necesitamos tu aceptación para analizar tus comidas. Cada aviso se abre en otra pestaña para que no pierdas tu avance.
      </p>
      
      <label className="opt">
        <input 
          type="checkbox" 
          checked={allAccepted} 
          onChange={(e) => setAllConsents(e.target.checked)} 
        />
        <span><b>Aceptar todos</b></span>
      </label>

      {Object.entries(AVISOS).map(([slug, aviso]) => (
        <label className="opt" key={slug}>
          <input 
            type="checkbox" 
            checked={consents[aviso.tipo]} 
            onChange={() => toggleConsent(aviso.tipo)} 
          />
          <span>
            <b>{aviso.titulo}</b>
            <small>
              Versión {VERSION}.{' '}
              <Link to={`/avisos/${slug}`} target="_blank" rel="noopener noreferrer">
                Leer aviso
              </Link>
            </small>
          </span>
        </label>
      ))}

      {errors.consents && <small className="err" role="alert">{errors.consents}</small>}
    </fieldset>
  )
}
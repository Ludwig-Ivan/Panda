import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Orb from '../components/Orb.jsx'
import StepConsent from './onboarding/StepConsent.jsx'
import StepPerfil from './onboarding/StepPerfil.jsx'
import StepActividades from './onboarding/StepActividades.jsx'
import StepFotos from './onboarding/StepFotos.jsx'
import { api } from '../lib/api.js'
import { AVISOS, VERSION } from '../data/avisos.js'
import '../onboarding.css'

const TITLES = ['Antes de empezar', 'Cuéntanos sobre ti', 'Tus actividades favoritas', 'Tus fotos']

// Rangos tomados de las restricciones CHECK de la tabla perfiles.
const validators = [
  (d) => (Object.values(d.consents).every(Boolean) ? {} : { consents: 'Para continuar debes aceptar los tres avisos.' }),
  ({ perfil: p }) => {
    const e = {}
    const n = (k) => Number(p[k])
    if (!Number.isInteger(n('edad')) || n('edad') < 18 || n('edad') > 100) e.edad = 'Ingresa una edad entre 18 y 100 años.'
    if (!p.sexo) e.sexo = 'Selecciona una opción.'
    if (!(n('peso_kg') >= 30 && n('peso_kg') <= 300)) e.peso_kg = 'Ingresa un peso entre 30 y 300 kg.'
    if (!(n('estatura_cm') >= 120 && n('estatura_cm') <= 230)) e.estatura_cm = 'Ingresa una estatura entre 120 y 230 cm.'
    if (!p.nivel_actividad) e.nivel_actividad = 'Elige tu nivel de actividad.'
    return e
  },
  () => ({}), // opcional
  () => ({}),
]

export default function Onboarding() {
  const nav = useNavigate()
  const [step, setStep] = useState(0)
  const [errs, setErrs] = useState({})
  const [busy, setBusy] = useState(false)
  const [server, setServer] = useState('')
  const [d, setD] = useState({
    consents: { privacidad: false, avisos_salud: false, procesamiento_terceros: false },
    perfil: { edad: '', sexo: '', peso_kg: '', estatura_cm: '', nivel_actividad: '' },
    actividades: [],
    guardar_fotos: true, // mismo valor por defecto que usuarios.guardar_fotos
  })
  const head = useRef(null)
  useEffect(() => { head.current?.focus() }, [step])

  const last = step === TITLES.length - 1
  const Step = [StepConsent, StepPerfil, StepActividades, StepFotos][step]

  async function next() {
    const e = validators[step](d)
    setErrs(e); setServer('')
    if (Object.keys(e).length) return
    if (!last) return setStep((s) => s + 1)
    setBusy(true)
    try {
      const p = d.perfil
      await api.completeOnboarding({
        consentimientos: Object.values(AVISOS).map((a) => ({ tipo: a.tipo, version: VERSION })),
        perfil: { edad: +p.edad, sexo: p.sexo, peso_kg: +p.peso_kg, estatura_cm: +p.estatura_cm, nivel_actividad: p.nivel_actividad },
        actividades: d.actividades,
        guardar_fotos: d.guardar_fotos,
      })
      nav('/inicio')
    } catch {
      setServer('No pudimos guardar tu información. Inténtalo de nuevo.')
    } finally { setBusy(false) }
  }

  return (
    <main className="auth onb-wrap">
      <div className="onb-top"><span className="brand"><span className="logo">🐼</span>PANDA</span></div>
      <div className="auth-card onb">
        <div className="onb-head">
          <Orb size={36} />
          <div>
            <small>Paso {step + 1} de {TITLES.length}</small>
            <h1 ref={head} tabIndex={-1}>{TITLES[step]}</h1>
          </div>
        </div>
        <div className="prog" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={((step + 1) / TITLES.length) * 100}>
          <i style={{ width: `${((step + 1) / TITLES.length) * 100}%` }} />
        </div>

        <Step d={d} setD={setD} errors={errs} />

        {server && <p className="err box" role="alert">{server}</p>}
        <div className="nav-row">
          {step > 0 && <button type="button" className="btn" onClick={() => { setErrs({}); setStep((s) => s - 1) }} disabled={busy}>Atrás</button>}
          <button type="button" className="btn p" onClick={next} disabled={busy}>{busy ? 'Guardando…' : last ? 'Finalizar' : 'Continuar'}</button>
        </div>
      </div>
    </main>
  )
}

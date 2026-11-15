import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Orb from '../../components/Orb.jsx'
import StepConsent from './StepConsent.jsx'
import StepPerfil from './StepPerfil.jsx'
import StepActividades from './StepActividades.jsx'
import StepFotos from './StepFotos.jsx'
import { api } from '../../lib/api.js'
import { AVISOS, VERSION } from '../../data/avisos.js'
import logo from '../../assets/logo.png'
import "./onboarding.css"

const TITLES = ['Antes de empezar', 'Cuéntanos sobre ti', 'Tus actividades favoritas', 'Tus fotos']
const STEP_COMPONENTS = [StepConsent, StepPerfil, StepActividades, StepFotos]

// Rangos tomados de las restricciones CHECK de la tabla perfiles.
const VALIDATORS = [
  (data) => (Object.values(data.consents).every(Boolean) ? {} : { consents: 'Para continuar debes aceptar los tres avisos.' }),
  ({ perfil }) => {
    const errors = {}
    const num = (k) => Number(perfil[k])
    if (!Number.isInteger(num('edad')) || num('edad') < 18 || num('edad') > 100) errors.edad = 'Ingresa una edad entre 18 y 100 años.'
    if (!perfil.sexo) errors.sexo = 'Selecciona una opción.'
    if (!(num('peso_kg') >= 30 && num('peso_kg') <= 300)) errors.peso_kg = 'Ingresa un peso entre 30 y 300 kg.'
    if (!(num('estatura_cm') >= 120 && num('estatura_cm') <= 230)) errors.estatura_cm = 'Ingresa una estatura entre 120 y 230 cm.'
    if (!perfil.nivel_actividad) errors.nivel_actividad = 'Elige tu nivel de actividad.'
    return errors
  },
  () => ({}), // Paso opcional
  () => ({}), // Paso opcional
]

export default function Onboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)
  const [serverError, setServerError] = useState('')
  const [formData, setFormData] = useState({
    consents: { privacidad: false, avisos_salud: false, procesamiento_terceros: false },
    perfil: { edad: '', sexo: '', peso_kg: '', estatura_cm: '', nivel_actividad: '' },
    actividades: [],
    guardar_fotos: true, // Mismo valor por defecto que usuarios.guardar_fotos
  })

  const headRef = useRef(null)
  
  // Enfocar el título cada vez que cambia el paso para accesibilidad
  useEffect(() => { 
    headRef.current?.focus() 
  }, [step])

  const isLastStep = step === TITLES.length - 1
  const CurrentStepComponent = STEP_COMPONENTS[step]

  async function handleNext() {
    const stepErrors = VALIDATORS[step](formData)
    setErrors(stepErrors)
    setServerError('')

    if (Object.keys(stepErrors).length > 0) return
    if (!isLastStep) return setStep((prev) => prev + 1)

    setBusy(true)
    try {
      const perfil = formData.perfil
      await api.completeOnboarding({
        consentimientos: Object.values(AVISOS).map((a) => ({ tipo: a.tipo, version: VERSION })),
        perfil: { 
          edad: Number(perfil.edad), 
          sexo: perfil.sexo, 
          peso_kg: Number(perfil.peso_kg), 
          estatura_cm: Number(perfil.estatura_cm), 
          nivel_actividad: perfil.nivel_actividad 
        },
        actividades: formData.actividades,
        guardar_fotos: formData.guardar_fotos,
      })
      navigate('/inicio')
    } catch {
      setServerError('No pudimos guardar tu información. Inténtalo de nuevo.')
    } finally { 
      setBusy(false) 
    }
  }

  return (
    <main className="auth onb-wrap">
      <div className="onb-top">
        <span className="brand">
          <img src={logo} className="logo" alt="Logo Panda" />
          <b>PANDA</b>
        </span>
      </div>
      
      <div className="auth-card onb">
        <div className="onb-head">
          <Orb size={36} />
          <div>
            <small>Paso {step + 1} de {TITLES.length}</small>
            <h1 ref={headRef} tabIndex={-1}>{TITLES[step]}</h1>
          </div>
        </div>

        <div 
          className="prog" 
          role="progressbar" 
          aria-valuemin={0} 
          aria-valuemax={100} 
          aria-valuenow={((step + 1) / TITLES.length) * 100}
        >
          <i style={{ width: `${((step + 1) / TITLES.length) * 100}%` }} />
        </div>

        <CurrentStepComponent d={formData} setD={setFormData} errors={errors} />

        {serverError && <p className="err box" role="alert">{serverError}</p>}
        
        <div className="nav-row">
          {step > 0 && (
            <button 
              type="button" 
              className="btn" 
              onClick={() => { setErrors({}); setStep((s) => s - 1) }} 
              disabled={busy}
            >
              Atrás
            </button>
          )}
          <button 
            type="button" 
            className="btn p" 
            onClick={handleNext} 
            disabled={busy}
          >
            {busy ? 'Guardando…' : isLastStep ? 'Finalizar' : 'Continuar'}
          </button>
        </div>
      </div>
    </main>
  )
}
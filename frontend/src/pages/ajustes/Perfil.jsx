import { useEffect, useState } from 'react'
import { userApi } from '../../lib/userApi.js'
import SubPage from './SubPage.jsx'
import s from './Ajustes.module.css'

const NIVELES = [
  ['sedentario', 'Sedentario', 'Poco o nada de ejercicio'],
  ['ligero', 'Ligero', 'Ejercicio de 1 a 3 días por semana'],
  ['moderado', 'Moderado', 'Ejercicio de 3 a 5 días por semana'],
  ['alto', 'Alto', 'Ejercicio de 6 a 7 días por semana'],
]

// Rangos tomados de las restricciones CHECK de la tabla perfiles.
function validar(f) {
  const e = {}, n = (k) => Number(f[k])
  if (!Number.isInteger(n('edad')) || n('edad') < 18 || n('edad') > 100) e.edad = 'Ingresa una edad entre 18 y 100 años.'
  if (!f.sexo) e.sexo = 'Selecciona una opción.'
  if (!(n('peso_kg') >= 30 && n('peso_kg') <= 300)) e.peso_kg = 'Ingresa un peso entre 30 y 300 kg.'
  if (!(n('estatura_cm') >= 120 && n('estatura_cm') <= 230)) e.estatura_cm = 'Ingresa una estatura entre 120 y 230 cm.'
  if (!f.nivel_actividad) e.nivel_actividad = 'Elige tu nivel de actividad.'
  return e
}

export default function Perfil() {
  const [f, setF] = useState(null)
  const [errs, setErrs] = useState({})
  const [state, setState] = useState('loading')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    userApi.getPerfil()
      .then((p) => { setF({ edad: String(p.edad), sexo: p.sexo, peso_kg: String(Number(p.peso_kg)), estatura_cm: String(Number(p.estatura_cm)), nivel_actividad: p.nivel_actividad }); setState('ok') })
      .catch(() => setState('error'))
  }, [])

  const set = (k) => (e) => { setMsg(''); setF((p) => ({ ...p, [k]: e.target.value })) }

  async function save(e) {
    e.preventDefault()
    const er = validar(f)
    setErrs(er); setMsg('')
    if (Object.keys(er).length) return
    setBusy(true)
    try {
      await userApi.savePerfil({ edad: +f.edad, sexo: f.sexo, peso_kg: +f.peso_kg, estatura_cm: +f.estatura_cm, nivel_actividad: f.nivel_actividad })
      setMsg('ok')
    } catch { setMsg('error') } finally { setBusy(false) }
  }

  return (
    <SubPage title="Perfil físico" desc="Usamos estos datos para personalizar tus recomendaciones de actividad.">
      {state === 'loading' && <p className={s.hint} role="status">Cargando…</p>}
      {state === 'error' && <p className={s.msgErr} role="alert">No pudimos cargar tu perfil.</p>}
      {f && (
        <form className={s.card} onSubmit={save} noValidate>
          <div className={s.grid2}>
            <label className={s.field}>Edad
              <input className={s.input} type="number" inputMode="numeric" value={f.edad} onChange={set('edad')} aria-invalid={!!errs.edad} />
              {errs.edad && <small className={s.err} role="alert">{errs.edad}</small>}
            </label>
            <label className={s.field}>Sexo
              <select className={s.input} value={f.sexo} onChange={set('sexo')} aria-invalid={!!errs.sexo}>
                <option value="">Selecciona</option>
                <option value="femenino">Femenino</option>
                <option value="masculino">Masculino</option>
                <option value="no_indica">Prefiero no indicarlo</option>
              </select>
              {errs.sexo && <small className={s.err} role="alert">{errs.sexo}</small>}
            </label>
            <label className={s.field}>Peso (kg)
              <input className={s.input} type="number" inputMode="decimal" step="0.1" value={f.peso_kg} onChange={set('peso_kg')} aria-invalid={!!errs.peso_kg} />
              {errs.peso_kg && <small className={s.err} role="alert">{errs.peso_kg}</small>}
            </label>
            <label className={s.field}>Estatura (cm)
              <input className={s.input} type="number" inputMode="decimal" step="0.1" value={f.estatura_cm} onChange={set('estatura_cm')} aria-invalid={!!errs.estatura_cm} />
              {errs.estatura_cm && <small className={s.err} role="alert">{errs.estatura_cm}</small>}
            </label>
          </div>
          <div role="radiogroup" aria-label="Nivel de actividad" style={{ display: 'grid', gap: 8 }}>
            <span className={s.sectionTitle}>Nivel de actividad</span>
            {NIVELES.map(([v, t, d]) => (
              <label className={s.opt} key={v}>
                <input type="radio" name="nivel" value={v} checked={f.nivel_actividad === v} onChange={set('nivel_actividad')} />
                <span><b>{t}</b><small>{d}</small></span>
              </label>
            ))}
            {errs.nivel_actividad && <small className={s.err} role="alert">{errs.nivel_actividad}</small>}
          </div>
          <p className={s.hint}>Si cambias tu peso, las recomendaciones de comidas anteriores no se modifican: se quedan con el peso que se usó al calcularlas.</p>
          {msg === 'ok' && <p className={s.msgOk} role="status">Cambios guardados.</p>}
          {msg === 'error' && <p className={s.msgErr} role="alert">No pudimos guardar los cambios. Inténtalo de nuevo.</p>}
          <button className={`${s.btn} ${s.btnP}`} disabled={busy}>{busy ? 'Guardando…' : 'Guardar cambios'}</button>
        </form>
      )}
    </SubPage>
  )
}

import Field from '../../components/Field.jsx'

const NIVELES = [
  ['sedentario', 'Sedentario', 'Poco o nada de ejercicio'],
  ['ligero', 'Ligero', 'Ejercicio de 1 a 3 días por semana'],
  ['moderado', 'Moderado', 'Ejercicio de 3 a 5 días por semana'],
  ['alto', 'Alto', 'Ejercicio de 6 a 7 días por semana'],
]

export default function StepPerfil({ d, setD, errors }) {
  const p = d.perfil
  const set = (k) => (e) => setD((s) => ({ ...s, perfil: { ...s.perfil, [k]: e.target.value } }))

  return (
    <fieldset className="onb-step">
      <legend>Perfil físico</legend>
      <p className="sub">Usamos estos datos para personalizar tus recomendaciones. Puedes cambiarlos después en Ajustes.</p>
      <div className="grid2">
        <Field id="edad" label="Edad" type="number" inputMode="numeric" min="18" max="100" value={p.edad} onChange={set('edad')} error={errors.edad} />
        <div className="field">
          <label htmlFor="sexo">Sexo</label>
          <select id="sexo" value={p.sexo} onChange={set('sexo')} aria-invalid={!!errors.sexo}>
            <option value="">Selecciona</option>
            <option value="femenino">Femenino</option>
            <option value="masculino">Masculino</option>
            <option value="no_indica">Prefiero no indicarlo</option>
          </select>
          {errors.sexo && <small className="err" role="alert">{errors.sexo}</small>}
        </div>
        <Field id="peso" label="Peso (kg)" type="number" inputMode="decimal" step="0.1" value={p.peso_kg} onChange={set('peso_kg')} error={errors.peso_kg} />
        <Field id="estatura" label="Estatura (cm)" type="number" inputMode="decimal" step="0.1" value={p.estatura_cm} onChange={set('estatura_cm')} error={errors.estatura_cm} />
      </div>
      <div className="group" role="radiogroup" aria-label="Nivel de actividad">
        <h2>Nivel de actividad</h2>
        {NIVELES.map(([v, t, s]) => (
          <label className="opt" key={v}>
            <input type="radio" name="nivel" value={v} checked={p.nivel_actividad === v} onChange={set('nivel_actividad')} />
            <span><b>{t}</b><small>{s}</small></span>
          </label>
        ))}
        {errors.nivel_actividad && <small className="err" role="alert">{errors.nivel_actividad}</small>}
      </div>
    </fieldset>
  )
}

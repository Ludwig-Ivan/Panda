import { Camera, Flame, Footprints } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import Orb from '../../components/Orb.jsx'

// Constantes estáticas fuera del componente para evitar recrearlas en cada render
const FEATURES = [
  { icon: <Flame size={20} aria-hidden="true" />, title: 'Calorías y macros', desc: 'Registra lo que comes y ve cuánto te queda en el día.' },
  { icon: <Camera size={20} aria-hidden="true" />, title: 'Registro con foto', desc: 'Fotografía tu plato y revisa la estimación antes de confirmarla.' },
  { icon: <Footprints size={20} aria-hidden="true" />, title: 'Actividad recomendada', desc: 'Sugerencias para equilibrar cada comida según tus preferencias.' },
]

const STEPS = [
  { title: 'Define tu perfil', desc: 'Indica tu edad, peso, estatura y nivel de actividad.' },
  { title: 'Registra tus comidas', desc: 'Con foto o de forma manual; corriges lo que no sea exacto.' },
  { title: 'Sigue tu progreso', desc: 'Consulta tu historial y las recomendaciones de cada comida.' },
]

export default function Landing() {
  const [form, setForm] = useState({ sex: 'm', age: 25, w: 108, h: 175, act: 1.375, def: 20 })

  // Manejador genérico de cambios para el formulario
  const handleChange = (field) => (e) => {
    const value = e.target.value
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  // Conversión numérica y cálculo de calorías (BMR usando la fórmula de Mifflin-St Jeor)
  const weight = Number(form.w)
  const height = Number(form.h)
  const age = Number(form.age)
  const activity = Number(form.act)
  const deficit = Number(form.def)

  const bmr = 10 * weight + 6.25 * height - 5 * age + (form.sex === 'm' ? 5 : -161)
  const kcal = weight && height && age 
    ? Math.max(Math.round((bmr * activity * (1 - deficit / 100)) / 10) * 10, 1200) 
    : 0

  return (
    <main>
      {/* Sección Hero */}
      <section className="hero wrap">
        <h1>Come mejor.<em>Pierde grasa sin adivinar.</em></h1>
        <div>
          <p>Panda cuenta tus calorías y te muestra cuánto te falta cada día para llegar a tu meta.</p>
          <div className="cta">
            <Link className="btn p lg" to="/registro">Crear cuenta</Link>
            <a className="btn lg" href="#calculadora">Calcular mi meta</a>
          </div>
        </div>
      </section>

      {/* Sección de Características / Funciones */}
      <section className="wrap cards" id="funciones">
        {FEATURES.map(({ icon, title, desc }) => (
          <article className="card" key={title}>
            <span className="ico">{icon}</span>
            <h3>{title}</h3>
            <p>{desc}</p>
          </article>
        ))}
        <article className="card ai">
          <Orb size={40} />
          <h3>Asistente de IA</h3>
          <p>Pregúntale cómo equilibrar tu día o qué comer para llegar a tu meta.</p>
          <div className="bubble">¿Qué ceno si ya comí 1,400 kcal?</div>
          <div className="bubble bot">Una opción ligera con proteína, como yogur griego con fruta.</div>
        </article>
      </section>

      {/* Sección de Calculadora Interactiva */}
      <section className="wrap" id="calculadora">
        <h2>Calcula tu meta diaria</h2>
        <p className="lead">Una estimación con déficit moderado para empezar.</p>
        <div className="calc">
          <form className="panel f" onSubmit={(e) => e.preventDefault()}>
            <label>
              Sexo
              <select value={form.sex} onChange={handleChange('sex')}>
                <option value="m">Hombre</option>
                <option value="f">Mujer</option>
              </select>
            </label>
            <label>
              Edad
              <input type="number" min="18" max="100" value={form.age} onChange={handleChange('age')} />
            </label>
            <label>
              Peso (kg)
              <input type="number" min="30" max="300" value={form.w} onChange={handleChange('w')} />
            </label>
            <label>
              Estatura (cm)
              <input type="number" min="120" max="230" value={form.h} onChange={handleChange('h')} />
            </label>
            <label className="full">
              Actividad
              <select value={form.act} onChange={handleChange('act')}>
                <option value="1.2">Sedentaria</option>
                <option value="1.375">Ligera</option>
                <option value="1.55">Moderada</option>
                <option value="1.725">Alta</option>
              </select>
            </label>
            <label className="full">
              Déficit: {form.def}%
              <input type="range" min="10" max="25" value={form.def} onChange={handleChange('def')} />
            </label>
          </form>
          
          <div className="panel res">
            <small>Tu meta de calorías al día</small>
            <div className="big">{kcal.toLocaleString('es-MX')}</div>
            <small>Estimación general; no sustituye la guía de un profesional de la salud.</small>
          </div>
        </div>
      </section>

      {/* Sección de Pasos */}
      <section className="wrap" id="como">
        <h2>Empieza en tres pasos</h2>
        <div className="steps">
          {STEPS.map(({ title, desc }) => (
            <div className="step" key={title}>
              <h3>{title}</h3>
              <p>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Sección Final / CTA */}
      <section className="wrap">
        <div className="join">
          <h2>Empieza hoy con Panda</h2>
          <p>Crea tu cuenta y registra tu primera comida en minutos.</p>
          <Link className="btn p lg" to="/registro">Crear cuenta</Link>
        </div>
      </section>
    </main>
  )
}
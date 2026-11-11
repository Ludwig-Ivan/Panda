import { useState } from 'react'
import { Link } from 'react-router-dom'
import Orb from '../components/Orb.jsx'
import { Camera, Flame, Footprints } from 'lucide-react'

const features = [
  [<Flame size={20} aria-hidden="true"/>, 'Calorías y macros', 'Registra lo que comes y ve cuánto te queda en el día.'],
  [<Camera size={20} aria-hidden="true"/>, 'Registro con foto', 'Fotografía tu plato y revisa la estimación antes de confirmarla.'],
  [<Footprints size={20} aria-hidden="true"/>, 'Actividad recomendada', 'Sugerencias para equilibrar cada comida según tus preferencias.'],
]
const steps = [
  ['Define tu perfil', 'Indica tu edad, peso, estatura y nivel de actividad.'],
  ['Registra tus comidas', 'Con foto o de forma manual; corriges lo que no sea exacto.'],
  ['Sigue tu progreso', 'Consulta tu historial y las recomendaciones de cada comida.'],
]

export default function Landing() {
  const [f, setF] = useState({ sex: 'm', age: 25, w: 108, h: 175, act: 1.375, def: 20 })
  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))
  const w = +f.w, h = +f.h, a = +f.age
  const bmr = 10 * w + 6.25 * h - 5 * a + (f.sex === 'm' ? 5 : -161)
  const kcal = w && h && a ? Math.max(Math.round((bmr * f.act * (1 - f.def / 100)) / 10) * 10, 1200) : 0

  return (
    <main>
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

      <section className="wrap cards" id="funciones">
        {features.map(([i, t, d]) => (
          <article className="card" key={t}><span className="ico">{i}</span><h3>{t}</h3><p>{d}</p></article>
        ))}
        <article className="card ai">
          <Orb size={40} /><h3>Asistente de IA</h3>
          <p>Pregúntale cómo equilibrar tu día o qué comer para llegar a tu meta.</p>
          <div className="bubble">¿Qué ceno si ya comí 1,400 kcal?</div>
          <div className="bubble bot">Una opción ligera con proteína, como yogur griego con fruta.</div>
        </article>
      </section>

      <section className="wrap" id="calculadora">
        <h2>Calcula tu meta diaria</h2>
        <p className="lead">Una estimación con déficit moderado para empezar.</p>
        <div className="calc">
          <form className="panel f" onSubmit={(e) => e.preventDefault()}>
            <label>Sexo<select value={f.sex} onChange={set('sex')}><option value="m">Hombre</option><option value="f">Mujer</option></select></label>
            <label>Edad<input type="number" min="18" max="100" value={f.age} onChange={set('age')} /></label>
            <label>Peso (kg)<input type="number" min="30" max="300" value={f.w} onChange={set('w')} /></label>
            <label>Estatura (cm)<input type="number" min="120" max="230" value={f.h} onChange={set('h')} /></label>
            <label className="full">Actividad
              <select value={f.act} onChange={set('act')}>
                <option value="1.2">Sedentaria</option><option value="1.375">Ligera</option>
                <option value="1.55">Moderada</option><option value="1.725">Alta</option>
              </select>
            </label>
            <label className="full">Déficit: {f.def}%<input type="range" min="10" max="25" value={f.def} onChange={set('def')} /></label>
          </form>
          <div className="panel res">
            <small>Tu meta de calorías al día</small>
            <div className="big">{kcal.toLocaleString('es-MX')}</div>
            <small>Estimación general; no sustituye la guía de un profesional de la salud.</small>
          </div>
        </div>
      </section>

      <section className="wrap" id="como">
        <h2>Empieza en tres pasos</h2>
        <div className="steps">
          {steps.map(([t, d]) => (<div className="step" key={t}><h3>{t}</h3><p>{d}</p></div>))}
        </div>
      </section>

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

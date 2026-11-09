import { useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { useMealDraft, calc } from '../../context/MealDraft.jsx'
import '../../app2.css'

const inRange = (v, a, b) => v !== '' && Number(v) >= a && Number(v) <= b

export default function EditarItem() {
  const { id } = useParams()
  const nav = useNavigate()
  const { items, setItems } = useMealDraft()
  const it = items.find((x) => x.id === id)
  const [f, setF] = useState(() => ({ nombre: it?.nombre ?? '', porcion_g: it?.porcion_g ?? '', kcal_100g: it?.kcal_100g ?? '' }))
  const [err, setErr] = useState('')
  if (!it) return <Navigate to="/comidas/nueva/revision" replace />

  const set = (k) => (e) => setF((p) => ({ ...p, [k]: e.target.value }))
  const bump = (d) => setF((p) => ({ ...p, porcion_g: Math.min(2000, Math.max(1, (Number(p.porcion_g) || 0) + d)) }))
  const live = inRange(f.porcion_g, 1, 2000) && inRange(f.kcal_100g, 0, 900) ? calc({ ...it, porcion_g: Number(f.porcion_g), kcal_100g: Number(f.kcal_100g) }).kcal : null

  function save(e) {
    e.preventDefault()
    if (f.nombre.trim().length < 2) return setErr('Escribe el nombre del alimento.')
    if (!inRange(f.porcion_g, 1, 2000)) return setErr('La porción debe estar entre 1 y 2000 g.')
    if (!inRange(f.kcal_100g, 0, 900)) return setErr('Las kcal por 100 g deben estar entre 0 y 900.')
    // Si cambia el nombre o la densidad, ya no corresponde al catálogo.
    const changedFood = f.nombre.trim() !== it.nombre || Number(f.kcal_100g) !== it.kcal_100g
    setItems(items.map((x) => (x.id === id
      ? { ...x, nombre: f.nombre.trim(), porcion_g: Number(f.porcion_g), kcal_100g: Number(f.kcal_100g), ...(changedFood ? { alimento_id: null, fuente: 'usuario' } : {}) }
      : x)))
    nav('/comidas/nueva/revision')
  }

  return (
    <main className="page narrow">
      <header><h1>Corregir alimento</h1></header>
      <form className="card form-card" onSubmit={save} noValidate>
        <label>Nombre<input value={f.nombre} onChange={set('nombre')} /></label>
        <label>Porción (g)
          <span className="stepper">
            <button type="button" className="btn" onClick={() => bump(-10)} aria-label="Restar 10 gramos">−10</button>
            <input type="number" inputMode="numeric" value={f.porcion_g} onChange={set('porcion_g')} />
            <button type="button" className="btn" onClick={() => bump(10)} aria-label="Sumar 10 gramos">+10</button>
          </span>
        </label>
        <label>kcal por 100 g<input type="number" inputMode="numeric" value={f.kcal_100g} onChange={set('kcal_100g')} /></label>
        <div className="preview"><span>Calorías de este alimento</span><b>{live === null ? '…' : `${live} kcal`}</b></div>
        {err && <p className="err box" role="alert">{err}</p>}
        <button className="btn p full">Guardar cambios</button>
        <Link className="btn full" to={`/comidas/nueva/buscar?reemplazar=${id}`}>Reemplazar por otro alimento</Link>
        <button type="button" className="link-btn danger" onClick={() => { setItems(items.filter((x) => x.id !== id)); nav('/comidas/nueva/revision') }}>Quitar alimento</button>
      </form>
      <Link className="hint center" to="/comidas/nueva/revision">Cancelar</Link>
    </main>
  )
}

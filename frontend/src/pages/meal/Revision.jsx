import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMealDraft, newItem, calc, totals } from '../../context/MealDraft.jsx'
import '../../app2.css'

const inRange = (v, a, b) => Number(v) >= a && Number(v) <= b

export default function Revision() {
  const nav = useNavigate()
  const { origen, fotoUrl, items, setItems, reset } = useMealDraft()
  const [add, setAdd] = useState({ nombre: '', porcion_g: '', kcal_100g: '' })
  const [addErr, setAddErr] = useState('')
  const [err, setErr] = useState('')
  const t = totals(items)

  useEffect(() => { if (origen === 'foto' && !fotoUrl) nav('/comidas/nueva', { replace: true }) }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const setPorcion = (id, v) => setItems(items.map((x) => (x.id === id ? { ...x, porcion_g: v === '' ? '' : Number(v) } : x)))
  const remove = (id) => setItems(items.filter((x) => x.id !== id))

  function addItem(e) {
    e.preventDefault()
    if (add.nombre.trim().length < 2) return setAddErr('Escribe el nombre del alimento.')
    if (!inRange(add.porcion_g, 1, 2000)) return setAddErr('La porción debe estar entre 1 y 2000 g.')
    if (add.kcal_100g === '' || !inRange(add.kcal_100g, 0, 900)) return setAddErr('Las kcal por 100 g deben estar entre 0 y 900.')
    setAddErr('')
    setItems([...items, newItem({ nombre: add.nombre.trim(), porcion_g: Number(add.porcion_g), kcal_100g: Number(add.kcal_100g) }, 'usuario')])
    setAdd({ nombre: '', porcion_g: '', kcal_100g: '' })
  }

  function next() {
    if (!items.length) return setErr('Agrega al menos un alimento.')
    if (items.some((x) => !inRange(x.porcion_g, 1, 2000))) return setErr('Cada porción debe estar entre 1 y 2000 g.')
    if (t.total > 5000) return setErr('El total supera el máximo permitido de 5000 kcal. Revisa las porciones.')
    setErr(''); nav('/comidas/nueva/confirmar')
  }

  return (
    <main className="page">
      <header>
        <h1>{origen === 'foto' ? 'Revisa lo que detectamos' : 'Tu comida'}</h1>
        <p className="hint">Son estimaciones. Ajusta las porciones o agrega lo que falte.</p>
      </header>

      <div className="review">
        <section className="card">
          {fotoUrl && <img className="thumb-l" src={fotoUrl} alt="Foto de tu comida" />}
          {items.length === 0 && <p className="hint">Todavía no hay alimentos. Búscalos en el catálogo.</p>}
          <ul className="items">
            {items.map((x) => {
              const c = calc(x)
              return (
                <li key={x.id}>
                  <div className="it-main">
                    <b>{x.nombre}</b>
                    {x.origen === 'ia' && x.confianza < 0.6 && <small className="warn">Poca confianza: revisa este alimento</small>}
                    <label className="it-g">Porción (g)
                      <input type="number" inputMode="numeric" min="1" max="2000" value={x.porcion_g} onChange={(e) => setPorcion(x.id, e.target.value)} aria-label={`Porción de ${x.nombre} en gramos`} />
                    </label>
                  </div>
                  <div className="it-k"><b>{c.kcal} kcal</b>{c.min !== c.max && <small>{c.min} a {c.max}</small>}
                    <Link className="link-btn" to={`/comidas/nueva/item/${x.id}`} aria-label={`Editar ${x.nombre}`}>Editar</Link>
                    <button type="button" className="link-btn" onClick={() => remove(x.id)} aria-label={`Quitar ${x.nombre}`}>Quitar</button>
                  </div>
                </li>
              )
            })}
          </ul>
          <Link className="btn full" to="/comidas/nueva/buscar">Buscar alimento en el catálogo</Link>

          <details className="manual">
            <summary>¿No lo encuentras? Agrégalo manualmente</summary>
            <form className="add" onSubmit={addItem} noValidate>
              <div className="add-grid">
                <label>Nombre<input value={add.nombre} onChange={(e) => setAdd({ ...add, nombre: e.target.value })} /></label>
                <label>Porción (g)<input type="number" inputMode="numeric" value={add.porcion_g} onChange={(e) => setAdd({ ...add, porcion_g: e.target.value })} /></label>
                <label>kcal por 100 g<input type="number" inputMode="numeric" value={add.kcal_100g} onChange={(e) => setAdd({ ...add, kcal_100g: e.target.value })} /></label>
              </div>
              {addErr && <small className="err" role="alert">{addErr}</small>}
              <button className="btn">Agregar</button>
            </form>
          </details>
        </section>

        <aside className="card total">
          <small>Total aproximado</small>
          <div className="big">{t.total}<span> kcal</span></div>
          {t.min !== t.max && <small>Rango estimado: {t.min} a {t.max} kcal</small>}
          {err && <p className="err box" role="alert">{err}</p>}
          <button type="button" className="btn p full" onClick={next}>Continuar</button>
          <Link className="hint center" to="/comidas/nueva" onClick={() => reset()}>Descartar</Link>
        </aside>
      </div>
    </main>
  )
}

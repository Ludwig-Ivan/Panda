import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useMealDraft, newItem } from '../../context/MealDraft.jsx'
import { mealsApi } from '../../lib/mealsApi.js'
import '../../app2.css'

export default function BuscarAlimento() {
  const nav = useNavigate()
  const [params] = useSearchParams()
  const reemplazar = params.get('reemplazar')
  const { items, setItems } = useMealDraft()
  const [q, setQ] = useState('')
  const [res, setRes] = useState(null)
  const [state, setState] = useState('idle') // idle | loading | error
  const seq = useRef(0)

  useEffect(() => {
    if (q.trim().length < 2) { setRes(null); setState('idle'); return }
    const mine = ++seq.current
    setState('loading')
    const t = setTimeout(() => {
      mealsApi.searchAlimentos(q)
        .then((r) => { if (mine === seq.current) { setRes(r); setState('idle') } })
        .catch(() => mine === seq.current && setState('error'))
    }, 300)
    return () => clearTimeout(t)
  }, [q])

  function pick(a) {
    const it = newItem({ nombre: a.nombre, alimento_id: a.id, porcion_g: a.porcion_tipica_g || 100, kcal_100g: a.kcal_100g, fuente: 'catalogo' }, 'usuario')
    setItems(reemplazar ? items.map((x) => (x.id === reemplazar ? { ...it, id: x.id } : x)) : [...items, it])
    nav(reemplazar ? `/comidas/nueva/item/${reemplazar}` : '/comidas/nueva/revision', { replace: true })
  }

  return (
    <main className="page narrow">
      <header><h1>{reemplazar ? 'Reemplazar alimento' : 'Buscar alimento'}</h1><p className="hint">Escribe al menos 2 letras. Puedes buscar por nombre o sinónimo.</p></header>
      <div className="search">
        <input type="search" autoFocus value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ej. pollo, tortilla, aguacate" aria-label="Buscar alimento" />
        {state === 'loading' && <p className="hint" role="status">Buscando…</p>}
        {state === 'error' && <p className="err box" role="alert">No pudimos buscar ahora. Inténtalo de nuevo.</p>}
        {res && res.length === 0 && state === 'idle' && <p className="hint">Sin resultados para «{q}». Puedes agregarlo manualmente desde la revisión.</p>}
        <ul className="res-list">
          {res?.map((a) => (
            <li key={a.id}>
              <button type="button" className="res-item" onClick={() => pick(a)}>
                <span><b>{a.nombre}</b><small>{a.kcal_100g} kcal por 100 g</small></span>
                <small>{a.porcion_tipica_g ? `Porción típica ${a.porcion_tipica_g} g` : ''}</small>
              </button>
            </li>
          ))}
        </ul>
      </div>
      <Link className="hint center" to={reemplazar ? `/comidas/nueva/item/${reemplazar}` : '/comidas/nueva/revision'}>Volver</Link>
    </main>
  )
}

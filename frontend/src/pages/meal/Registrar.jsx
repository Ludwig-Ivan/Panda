import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMealDraft } from '../../context/MealDraft.jsx'

export default function Registrar() {
  const nav = useNavigate()
  const { reset } = useMealDraft()
  useEffect(() => { reset() }, [reset]) // empezar siempre con un borrador limpio

  return (
    <main className="page narrow">
      <header><h1>Registrar comida</h1><p className="hint">¿Cómo quieres añadirla?</p></header>
      <button type="button" className="card choice" onClick={() => { reset('foto'); nav('/comidas/nueva/foto') }}>
        <span className="choice-ico" aria-hidden="true">📷</span>
        <span><b>Con una foto</b><small>Detectamos los alimentos y estimamos las calorías. Tú revisas el resultado.</small></span>
      </button>
      <button type="button" className="card choice" onClick={() => { reset('manual'); nav('/comidas/nueva/revision') }}>
        <span className="choice-ico" aria-hidden="true">✍️</span>
        <span><b>De forma manual</b><small>Agrega cada alimento con su porción.</small></span>
      </button>
    </main>
  )
}

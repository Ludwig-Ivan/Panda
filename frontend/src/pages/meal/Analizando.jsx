import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Orb from '../../components/Orb.jsx'
import { useMealDraft, newItem } from '../../context/MealDraft.jsx'
import { mealsApi } from '../../lib/mealsApi.js'

const MSGS = ['Identificando alimentos…', 'Estimando porciones…', 'Calculando calorías…']

export default function Analizando() {
  const nav = useNavigate()
  const { foto, fotoUrl, setItems, setComidaId, reset } = useMealDraft()
  const [i, setI] = useState(0)
  const [state, setState] = useState('loading') // loading | error | empty
  const [tries, setTries] = useState(0)

  useEffect(() => {
    if (!foto) { nav('/comidas/nueva', { replace: true }); return }
    let alive = true
    setState('loading')
    const t = setInterval(() => setI((n) => (n + 1) % MSGS.length), 1100)
    mealsApi.analyze(foto)
      .then((r) => {
        if (!alive) return
        if (!r.items?.length) return setState('empty')
        setComidaId(r.comida_id)
        setItems(r.items.map((x) => newItem(x, 'ia')))
        nav('/comidas/nueva/revision', { replace: true })
      })
      .catch(() => alive && setState('error'))
      .finally(() => clearInterval(t))
    return () => { alive = false; clearInterval(t) }
  }, [tries]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <main className="page narrow center-col">
      <div className={`photo scan${state === 'loading' ? ' on' : ''}`}>{fotoUrl && <img src={fotoUrl} alt="Tu comida" />}</div>

      {state === 'loading' && (
        <>
          <Orb size={44} />
          <p role="status" className="status">{MSGS[i]}</p>
          <Link className="hint" to="/comidas/nueva" onClick={() => reset()}>Cancelar</Link>
        </>
      )}
      {state === 'error' && (
        <>
          <p className="err box" role="alert">No pudimos analizar la foto. Revisa tu conexión e inténtalo de nuevo.</p>
          <div className="row-btns">
            <button type="button" className="btn p" onClick={() => setTries((n) => n + 1)}>Reintentar</button>
            <Link className="btn" to="/comidas/nueva/foto">Cambiar foto</Link>
          </div>
        </>
      )}
      {state === 'empty' && (
        <>
          <p className="ok box" role="status">No identificamos alimentos en esta foto. Prueba con otra o agrégalos manualmente.</p>
          <div className="row-btns">
            <Link className="btn p" to="/comidas/nueva/foto">Probar otra foto</Link>
            <Link className="btn" to="/comidas/nueva/revision">Agregar manualmente</Link>
          </div>
        </>
      )}
    </main>
  )
}

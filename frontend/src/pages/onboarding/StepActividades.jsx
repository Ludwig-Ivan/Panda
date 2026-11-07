import { useEffect, useState } from 'react'
import { api } from '../../lib/api.js'

const GRUPOS = [['ligera', 'Ligeras'], ['moderada', 'Moderadas'], ['vigorosa', 'Vigorosas']]

export default function StepActividades({ d, setD }) {
  const [list, setList] = useState(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => { api.getActividades().then(setList).catch(() => setFailed(true)) }, [])

  const toggle = (id) => setD((p) => ({
    ...p,
    actividades: p.actividades.includes(id) ? p.actividades.filter((x) => x !== id) : [...p.actividades, id],
  }))

  return (
    <fieldset className="onb-step">
      <legend>Actividades preferidas</legend>
      <p className="sub">Elige las que más te gustan y las priorizaremos en tus recomendaciones. Es opcional.</p>
      {failed && <p className="err box" role="alert">No pudimos cargar las actividades. Puedes continuar y elegirlas después.</p>}
      {!list && !failed && <p className="hint" role="status">Cargando actividades…</p>}
      {list && GRUPOS.map(([k, titulo]) => {
        const items = list.filter((a) => a.intensidad === k)
        return items.length ? (
          <div className="group" key={k}>
            <h2>{titulo}</h2>
            <div className="chips">
              {items.map((a) => (
                <button type="button" key={a.id} className="chip" aria-pressed={d.actividades.includes(a.id)} onClick={() => toggle(a.id)}>{a.nombre}</button>
              ))}
            </div>
          </div>
        ) : null
      })}
    </fieldset>
  )
}

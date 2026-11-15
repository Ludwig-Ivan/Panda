import { useEffect, useState } from 'react'
import { api } from '../../lib/api.js'

const GRUPOS = [
  ['ligera', 'Ligeras'], 
  ['moderada', 'Moderadas'], 
  ['vigorosa', 'Vigorosas']
]

export default function StepActividades({ d, setD }) {
  const [activitiesList, setActivitiesList] = useState(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    api.getActividades()
      .then(setActivitiesList)
      .catch(() => setFailed(true))
  }, [])

  const toggleActivity = (id) => {
    setD((prev) => ({
      ...prev,
      actividades: prev.actividades.includes(id) 
        ? prev.actividades.filter((activityId) => activityId !== id) 
        : [...prev.actividades, id],
    }))
  }

  return (
    <fieldset className="onb-step">
      <legend>Actividades preferidas</legend>
      <p className="sub">
        Elige las que más te gustan y las priorizaremos en tus recomendaciones. Es opcional.
      </p>
      
      {failed && (
        <p className="err box" role="alert">
          No pudimos cargar las actividades. Puedes continuar y elegirlas después.
        </p>
      )}
      
      {!activitiesList && !failed && (
        <p className="hint" role="status">Cargando actividades…</p>
      )}
      
      {activitiesList && GRUPOS.map(([key, titulo]) => {
        const filteredItems = activitiesList.filter((activity) => activity.intensidad === key)
        
        if (filteredItems.length === 0) return null

        return (
          <div className="group" key={key}>
            <h2>{titulo}</h2>
            <div className="chips">
              {filteredItems.map((activity) => {
                const isSelected = d.actividades.includes(activity.id)
                return (
                  <button 
                    type="button" 
                    key={activity.id} 
                    className="chip" 
                    aria-pressed={isSelected} 
                    onClick={() => toggleActivity(activity.id)}
                  >
                    {activity.nombre}
                  </button>
                )
              })}
            </div>
          </div>
        )
      })}
    </fieldset>
  )
}
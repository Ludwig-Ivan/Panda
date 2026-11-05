import { Link, Navigate, useParams } from 'react-router-dom'
import { AVISOS, VERSION } from '../data/avisos.js'

export default function Legal() {
  const { slug } = useParams()
  const a = AVISOS[slug]
  if (!a) return <Navigate to="/" replace />
  return (
    <main className="wrap legal">
      <h1>{a.titulo}</h1>
      <p className="hint">Versión {VERSION}</p>
      <p className="ok box">Texto de ejemplo: debe ser revisado por un profesional legal antes de publicarse.</p>
      {a.secciones.map(([h, p]) => (<section key={h}><h2>{h}</h2><p>{p}</p></section>))}
      <p className="hint"><Link to="/registro">Volver al registro</Link></p>
    </main>
  )
}

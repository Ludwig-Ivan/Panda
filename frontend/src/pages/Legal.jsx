import { Link, Navigate, useParams } from 'react-router-dom'
import { AVISOS, VERSION } from '../data/avisos.js'

export default function Legal() {
  const { slug } = useParams()
  const aviso = AVISOS[slug]

  if (!aviso) {
    return <Navigate to="/" replace />
  }

  return (
    <main className="wrap legal">
      <h1>{aviso.titulo}</h1>
      <p className="hint">Versión {VERSION}</p>
      <p className="ok box">Texto de ejemplo: debe ser revisado por un profesional legal antes de publicarse.</p>
      
      {aviso.secciones?.map(([heading, content]) => (
        <section key={heading}>
          <h2>{heading}</h2>
          <p>{content}</p>
        </section>
      ))}
      
      <p className="hint">
        <Link to="/registro">Volver al registro</Link>
      </p>
    </main>
  )
}
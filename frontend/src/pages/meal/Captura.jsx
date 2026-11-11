import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMealDraft } from '../../context/MealDraft.jsx'
import { Camera } from 'lucide-react'

const MAX_MB = 10

export default function Captura() {
  const nav = useNavigate()
  const { foto, fotoUrl, setFoto } = useMealDraft()
  const [err, setErr] = useState('')

  function pick(e) {
    const f = e.target.files?.[0]
    e.target.value = ''
    if (!f) return
    if (!f.type.startsWith('image/')) return setErr('El archivo debe ser una imagen.')
    if (f.size > MAX_MB * 1024 * 1024) return setErr(`La imagen pesa más de ${MAX_MB} MB. Elige una más ligera.`)
    setErr(''); setFoto(f)
  }

  return (
    <main className="page narrow">
      <header><h1>Foto de tu comida</h1><p className="hint">Con buena luz y el plato completo en la imagen, la estimación mejora.</p></header>

      <div className="photo">
        {fotoUrl ? <img src={fotoUrl} alt="Vista previa de tu comida" /> : <p className="hint">Aún no hay foto</p>}
      </div>
      {err && <p className="err box" role="alert">{err}</p>}

      <div className="row-btns">
        <label className="btn">
          <Camera size={20} aria-hidden="true"/> Tomar foto
          <input type="file" accept="image/*" capture="environment" onChange={pick} hidden />
        </label>
        <label className="btn">
          <Image size={20} aria-hidden="true"/> Elegir de galería
          <input type="file" accept="image/*" onChange={pick} hidden />
        </label>
      </div>

      <button type="button" className="btn p" disabled={!foto} onClick={() => nav('/comidas/nueva/analizando')}>Usar esta foto</button>
      <Link className="hint center" to="/comidas/nueva">Volver</Link>
    </main>
  )
}

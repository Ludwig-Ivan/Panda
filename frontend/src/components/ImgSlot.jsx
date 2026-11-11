import s from './ImgSlot.module.css'

// Muestra la imagen si existe "src"; si no, un recuadro verde con las dimensiones para reemplazarlo.
export default function ImgSlot({ src, w, h, label, alt = '', round = false, className = '' }) {
  const cls = `${round ? s.round : ''} ${className}`
  if (src) return <img src={src} alt={alt} width={w} height={h} className={`${s.img} ${cls}`} />
  return (
    <div className={`${s.slot} ${cls}`} style={{ width: w, height: h }} role="img" aria-label={`Imagen pendiente: ${label}, ${w} por ${h} píxeles`}>
      {h >= 60 && w >= 60 && <span>{label}</span>}
      {w >= 48 && <b>{w}×{h}</b>}
    </div>
  )
}

// Icono provisional del asistente de IA: una esfera verde.
export default function Orb({ size = 48, pulse = true }) {
  return <span className={`orb${pulse ? ' pulse' : ''}`} style={{ '--s': `${size}px` }} aria-hidden="true" />
}

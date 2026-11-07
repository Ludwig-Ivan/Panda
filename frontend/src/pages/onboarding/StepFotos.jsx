export default function StepFotos({ d, setD }) {
  const set = (v) => () => setD((p) => ({ ...p, guardar_fotos: v }))
  return (
    <fieldset className="onb-step">
      <legend>Preferencia de fotos</legend>
      <p className="sub">Decide si quieres conservar las fotos de tus comidas en tu historial. Podrás cambiarlo cuando quieras y borrar tus fotos en cualquier momento.</p>
      <label className="opt">
        <input type="radio" name="fotos" checked={d.guardar_fotos} onChange={set(true)} />
        <span><b>Guardar mis fotos</b><small>Verás cada comida con su imagen en el historial.</small></span>
      </label>
      <label className="opt">
        <input type="radio" name="fotos" checked={!d.guardar_fotos} onChange={set(false)} />
        <span><b>No conservar mis fotos</b><small>Solo se guardará el análisis, sin la imagen.</small></span>
      </label>
    </fieldset>
  )
}

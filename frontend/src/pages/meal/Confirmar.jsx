import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMealDraft, calc, totals } from '../../context/MealDraft.jsx'
import { mealsApi } from '../../lib/mealsApi.js'
import '../../app2.css'

const localNow = () => { const d = new Date(); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16) }

export default function Confirmar() {
  const nav = useNavigate()
  const { origen, comidaId, fotoUrl, items, reset } = useMealDraft()
  const [when, setWhen] = useState(localNow)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const t = totals(items)

  useEffect(() => { if (!items.length) nav('/comidas/nueva/revision', { replace: true }) }, []) // eslint-disable-line react-hooks/exhaustive-deps

  async function confirm() {
    if (!when) return setErr('Indica cuándo la comiste.')
    setBusy(true); setErr('')
    try {
      const r = await mealsApi.save({
        comidaId,
        payload: {
          estado: 'confirmada', origen,
          consumida_at: new Date(when).toISOString(),
          kcal_total: t.total, kcal_min: t.min, kcal_max: t.max,
          items: items.map((x) => {
            const c = calc(x)
            return { nombre: x.nombre, alimento_id: x.alimento_id, porcion_g: Number(x.porcion_g), kcal_100g: x.kcal_100g, kcal: c.kcal, kcal_min: c.min, kcal_max: c.max, confianza: x.confianza, origen: x.origen, fuente_kcal: x.fuente }
          }),
        },
      })
      const id = r.id ?? comidaId
      reset(); nav(`/comidas/${id}`, { replace: true })
    } catch { setErr('No pudimos guardar la comida. Inténtalo de nuevo.') } finally { setBusy(false) }
  }

  return (
    <main className="page narrow">
      <header><h1>Confirma tu comida</h1><p className="hint">Revisa el resumen antes de guardarla en tu historial.</p></header>
      <section className="card form-card">
        {fotoUrl && <img className="thumb-l" src={fotoUrl} alt="Foto de tu comida" />}
        <ul className="recap">
          {items.map((x) => <li key={x.id}><span>{x.nombre}<small> · {x.porcion_g} g</small></span><b>{calc(x).kcal} kcal</b></li>)}
        </ul>
        <div className="preview"><span>Total aproximado</span><b>{t.total} kcal</b></div>
        {t.min !== t.max && <small className="hint">Rango estimado: {t.min} a {t.max} kcal</small>}
        <label>¿Cuándo la comiste?<input type="datetime-local" value={when} max={localNow()} onChange={(e) => setWhen(e.target.value)} /></label>
        {err && <p className="err box" role="alert">{err}</p>}
        <button type="button" className="btn p full" onClick={confirm} disabled={busy}>{busy ? 'Guardando…' : 'Confirmar comida'}</button>
      </section>
      <Link className="hint center" to="/comidas/nueva/revision">Volver a la revisión</Link>
    </main>
  )
}

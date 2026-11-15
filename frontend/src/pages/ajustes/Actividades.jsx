import { useEffect, useState } from 'react'
import { api } from '../../lib/api.js'
import { userApi } from '../../lib/userApi.js'
import SubPage from './SubPage.jsx'
import s from './Ajustes.module.css'

const GRUPOS = [['ligera', 'Ligeras'], ['moderada', 'Moderadas'], ['vigorosa', 'Vigorosas']]

export default function Actividades() {
  const [list, setList] = useState(null)
  const [sel, setSel] = useState([])
  const [state, setState] = useState('loading')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  useEffect(() => {
    Promise.all([api.getActividades(), userApi.getPreferencias()])
      .then(([cat, pref]) => { setList(cat); setSel(pref.actividades || []); setState('ok') })
      .catch(() => setState('error'))
  }, [])

  const toggle = (id) => { setMsg(''); setSel((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id])) }

  async function save() {
    setBusy(true); setMsg('')
    try { await userApi.savePreferencias(sel); setMsg('ok') } catch { setMsg('error') } finally { setBusy(false) }
  }

  return (
    <SubPage title="Actividades preferidas" desc="Las que elijas se priorizan en tus recomendaciones. Es opcional.">
      {state === 'loading' && <p className={s.hint} role="status">Cargando…</p>}
      {state === 'error' && <p className={s.msgErr} role="alert">No pudimos cargar las actividades.</p>}
      {list && (
        <section className={s.card}>
          {GRUPOS.map(([k, titulo]) => {
            const items = list.filter((a) => a.intensidad === k)
            return items.length ? (
              <div key={k} style={{ display: 'grid', gap: 8 }}>
                <h2 className={s.sectionTitle}>{titulo}</h2>
                <div className={s.chips}>
                  {items.map((a) => <button type="button" key={a.id} className={s.chip} aria-pressed={sel.includes(a.id)} onClick={() => toggle(a.id)}>{a.nombre}</button>)}
                </div>
              </div>
            ) : null
          })}
          {msg === 'ok' && <p className={s.msgOk} role="status">Preferencias guardadas.</p>}
          {msg === 'error' && <p className={s.msgErr} role="alert">No pudimos guardar los cambios. Inténtalo de nuevo.</p>}
          <button type="button" className={`${s.btn} ${s.btnP}`} onClick={save} disabled={busy}>{busy ? 'Guardando…' : 'Guardar cambios'}</button>
        </section>
      )}
    </SubPage>
  )
}

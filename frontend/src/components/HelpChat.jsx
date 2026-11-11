import { useEffect, useRef, useState } from 'react'
import Orb from './Orb.jsx'
import { mealsApi } from '../lib/mealsApi.js'
import { X } from 'lucide-react'

const SUGERENCIAS = ['¿Cómo registro una comida?', '¿Qué tan exactas son las calorías?', '¿Cómo corrijo un alimento?']

export default function HelpChat() {
  const [open, setOpen] = useState(false)
  const [msgs, setMsgs] = useState([{ r: 'bot', t: 'Hola, soy el asistente de Panda. Puedo ayudarte a usar la app. ¿Qué necesitas?' }])
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const end = useRef(null)
  const input = useRef(null)

  useEffect(() => { if (open) input.current?.focus() }, [open])
  useEffect(() => { end.current?.scrollIntoView({ block: 'end' }) }, [msgs, busy, open])
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && setOpen(false)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  async function ask(t) {
    const q = t.trim()
    if (!q || busy) return
    setMsgs((m) => [...m, { r: 'user', t: q }]); setText(''); setBusy(true)
    try {
      const a = await mealsApi.askHelp(q)
      setMsgs((m) => [...m, { r: 'bot', t: a }])
    } catch {
      setMsgs((m) => [...m, { r: 'bot', t: 'No pude responder ahora. Inténtalo de nuevo en un momento.' }])
    } finally { setBusy(false) }
  }

  return (
    <>
      <button type="button" className="fab-orb" onClick={() => setOpen((o) => !o)} aria-label={open ? 'Cerrar asistente de ayuda' : 'Abrir asistente de ayuda'} aria-expanded={open}>
        <Orb size={56} pulse={!open} />
      </button>
      {open && (
        <section className="chat" role="dialog" aria-label="Asistente de ayuda">
          <header className="chat-head">
            <Orb size={28} pulse={false} /><b>Asistente de ayuda</b>
            <button type="button" className="chat-x" onClick={() => setOpen(false)} aria-label="Cerrar"><X size={20} aria-hidden="true"/></button>
          </header>
          <div className="chat-body" aria-live="polite">
            {msgs.map((m, i) => <p key={i} className={`msg ${m.r}`}>{m.t}</p>)}
            {msgs.length === 1 && (
              <div className="sugs">{SUGERENCIAS.map((s) => <button key={s} type="button" className="sug" onClick={() => ask(s)}>{s}</button>)}</div>
            )}
            {busy && <p className="msg bot typing" aria-label="Escribiendo">…</p>}
            <div ref={end} />
          </div>
          <form className="chat-form" onSubmit={(e) => { e.preventDefault(); ask(text) }}>
            <input ref={input} value={text} onChange={(e) => setText(e.target.value)} placeholder="Escribe tu duda…" aria-label="Mensaje" maxLength={300} />
            <button className="btn p" disabled={busy || !text.trim()}>Enviar</button>
          </form>
          <small className="chat-note">Asistente de ayuda de la app. No ofrece diagnósticos ni consejo médico.</small>
        </section>
      )}
    </>
  )
}

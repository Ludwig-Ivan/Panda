import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthShell from '../components/AuthShell.jsx'
import Field from '../components/Field.jsx'
import { api } from '../lib/api.js'

export default function Forgot() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    if (!email.trim()) return
    setBusy(true)
    try { await api.requestReset({ email: email.trim().toLowerCase() }) } catch { /* no revelamos si el correo existe */ }
    setBusy(false); setSent(true)
  }

  return (
    <AuthShell title="Recupera tu contraseña" sub="Te enviaremos un enlace para restablecerla."
      foot={<Link to="/acceso">Volver a iniciar sesión</Link>}>
      {sent ? (
        <p className="ok box" role="status">Si el correo está registrado, recibirás un enlace en unos minutos. Revisa también tu carpeta de spam.</p>
      ) : (
        <form onSubmit={submit} noValidate>
          <Field id="email" label="Correo" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <button className="btn p full" disabled={busy}>{busy ? 'Enviando…' : 'Enviar enlace'}</button>
        </form>
      )}
    </AuthShell>
  )
}

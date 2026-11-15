import { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthShell from '../../components/AuthShell.jsx'
import Field from '../../components/Field.jsx'
import { api } from '../../lib/api.js'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function Forgot() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmedEmail = email.trim().toLowerCase()

    if (!EMAIL_REGEX.test(trimmedEmail)) {
      return setError('Escribe un correo válido.')
    }

    setBusy(true)
    setError('')

    try { 
      await api.requestReset({ email: trimmedEmail }) 
    } catch { 
      // Silenciosamente ignoramos el error para no revelar si el correo existe por seguridad
    } finally {
      setBusy(false)
      setSent(true)
    }
  }

  return (
    <AuthShell 
      title="Recupera tu contraseña" 
      sub="Te enviaremos un enlace para restablecerla."
      foot={<Link to="/acceso">Volver a iniciar sesión</Link>}
    >
      {sent ? (
        <p className="ok box" role="status">
          Si el correo está registrado, recibirás un enlace en unos minutos. Revisa también tu carpeta de spam.
        </p>
      ) : (
        <form onSubmit={handleSubmit} noValidate>
          <Field 
            id="email" 
            label="Correo" 
            type="email" 
            autoComplete="email" 
            value={email} 
            onChange={(e) => {
              setEmail(e.target.value)
              if (error) setError('')
            }} 
            disabled={busy}
          />
          
          {error && <p className="err" role="alert">{error}</p>}
          
          <button className="btn p full" disabled={busy}>
            {busy ? 'Enviando…' : 'Enviar enlace'}
          </button>
        </form>
      )}
    </AuthShell>
  )
}
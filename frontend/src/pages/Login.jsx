import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthShell from '../components/AuthShell.jsx'
import Field from '../components/Field.jsx'
import { api } from '../lib/api.js'
import { EyeOff, Eye } from 'lucide-react'

export default function Login() {
  const nav = useNavigate()
  const [v, setV] = useState({ email: '', password: '' })
  const [show, setShow] = useState(false)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setV((p) => ({ ...p, [k]: e.target.value }))

  async function submit(e) {
    e.preventDefault()
    if (!v.email.trim() || !v.password) return setErr('Escribe tu correo y tu contraseña.')
    setBusy(true); setErr('')
    try {
      await api.login({ email: v.email.trim().toLowerCase(), password: v.password })
      nav('/inicio')
    } catch {
      setErr('Correo o contraseña incorrectos.')
    } finally { setBusy(false) }
  }

  return (
    <AuthShell title="Bienvenido de nuevo" sub="Inicia sesión para ver tu día."
      foot={<>¿Aún no tienes cuenta? <Link to="/registro">Créala gratis</Link></>}>
      <form onSubmit={submit} noValidate>
        <Field id="email" label="Correo" type="email" autoComplete="email" value={v.email} onChange={set('email')} />
        <Field id="password" label="Contraseña" type={show ? 'text' : 'password'} autoComplete="current-password" value={v.password} onChange={set('password')}>
          <button type="button" className="eye" onClick={() => setShow((s) => !s)} aria-label={show ? 'Ocultar contraseña' : 'Mostrar contraseña'}>{show ? <EyeOff size={20} aria-hidden="true"/> : <Eye size={20} aria-hidden="true"/>}</button>
        </Field>
        <p className="hint right"><Link to="/recuperar">¿Olvidaste tu contraseña?</Link></p>
        {err && <p className="err box" role="alert">{err}</p>}
        <button className="btn p full" disabled={busy}>{busy ? 'Entrando…' : 'Iniciar sesión'}</button>
      </form>
    </AuthShell>
  )
}

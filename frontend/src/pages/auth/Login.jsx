import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { EyeOff, Eye } from 'lucide-react'
import AuthShell from '../../components/AuthShell.jsx'
import Field from '../../components/Field.jsx'
import { api } from '../../lib/api.js'

export default function Login() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const handleChange = (key) => (e) => {
    setForm((prev) => ({ ...prev, [key]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.email.trim() || !form.password) {
      return setError('Escribe tu correo y tu contraseña.')
    }

    setBusy(true)
    setError('')

    try {
      await api.login({ 
        email: form.email.trim().toLowerCase(), 
        password: form.password 
      })
      navigate('/inicio')
    } catch {
      setError('Correo o contraseña incorrectos.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell 
      title="Bienvenido de nuevo" 
      sub="Inicia sesión para ver tu día."
      foot={<>¿Aún no tienes cuenta? <Link to="/registro">Créala gratis</Link></>}
    >
      <form onSubmit={handleSubmit} noValidate>
        <Field 
          id="email" 
          label="Correo" 
          type="email" 
          autoComplete="email" 
          value={form.email} 
          onChange={handleChange('email')}
          disabled={busy}
        />
        <Field 
          id="password" 
          label="Contraseña" 
          type={showPassword ? 'text' : 'password'} 
          autoComplete="current-password" 
          value={form.password} 
          onChange={handleChange('password')}
          disabled={busy}
        >
          <button 
            type="button" 
            className="eye" 
            onClick={() => setShowPassword((prev) => !prev)} 
            aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            {showPassword ? <EyeOff size={20} aria-hidden="true" /> : <Eye size={20} aria-hidden="true" />}
          </button>
        </Field>
        
        <p className="hint right">
          <Link to="/recuperar">¿Olvidaste tu contraseña?</Link>
        </p>
        
        {error && <p className="err box" role="alert">{error}</p>}
        
        <button className="btn p full" disabled={busy}>
          {busy ? 'Entrando…' : 'Iniciar sesión'}
        </button>
      </form>
    </AuthShell>
  )
}
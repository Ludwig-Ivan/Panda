import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthShell from '../../components/AuthShell.jsx'
import Field from '../../components/Field.jsx'
import { api } from '../../lib/api.js'

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', confirm: '', adult: false })
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)
  const [serverError, setServerError] = useState('')

  // Manejador genérico optimizado para inputs de texto y checkboxes
  const handleChange = (key) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const newErrors = {}

    if (!EMAIL_REGEX.test(form.email.trim())) newErrors.email = 'Escribe un correo válido.'
    if (form.password.length < 8) newErrors.password = 'Usa al menos 8 caracteres.'
    if (form.confirm !== form.password) newErrors.confirm = 'Las contraseñas no coinciden.'
    if (!form.adult) newErrors.adult = 'Debes tener 18 años o más para usar Panda.'

    setErrors(newErrors)
    setServerError('')

    if (Object.keys(newErrors).length > 0) return

    setBusy(true)
    try {
      await api.register({ 
        email: form.email.trim().toLowerCase(), 
        password: form.password, 
        mayor_edad_declarado: true 
      })
      navigate('/onboarding')
    } catch (err) {
      setServerError(
        err.status === 400 
          ? 'No pudimos crear la cuenta con esos datos. Revisa el correo o intenta iniciar sesión.' 
          : 'Algo salió mal. Inténtalo de nuevo.'
      )
    } finally { 
      setBusy(false) 
    }
  }

  return (
    <AuthShell 
      title="Crea tu cuenta" 
      sub="Empieza a registrar tus comidas en minutos."
      foot={<>¿Ya tienes cuenta? <Link to="/acceso">Inicia sesión</Link></>}
    >
      <form onSubmit={handleSubmit} noValidate>
        <Field 
          id="email" 
          label="Correo" 
          type="email" 
          autoComplete="email" 
          value={form.email} 
          onChange={handleChange('email')} 
          error={errors.email} 
        />
        <Field 
          id="password" 
          label="Contraseña" 
          type="password" 
          autoComplete="new-password" 
          value={form.password} 
          onChange={handleChange('password')} 
          error={errors.password} 
        />
        <Field 
          id="confirm" 
          label="Confirmar contraseña" 
          type="password" 
          autoComplete="new-password" 
          value={form.confirm} 
          onChange={handleChange('confirm')} 
          error={errors.confirm} 
        />
        
        <label className="check">
          <input type="checkbox" checked={form.adult} onChange={handleChange('adult')} />
          <span>Declaro que tengo 18 años o más.</span>
        </label>
        
        {errors.adult && <small className="err" role="alert">{errors.adult}</small>}
        
        <p className="hint">
          Revisa nuestro <Link to="/avisos/privacidad">aviso de privacidad</Link>; aceptarás los avisos en el siguiente paso.
        </p>
        
        {serverError && <p className="err box" role="alert">{serverError}</p>}
        
        <button className="btn p full" disabled={busy}>
          {busy ? 'Creando cuenta…' : 'Crear cuenta'}
        </button>
      </form>
    </AuthShell>
  )
}
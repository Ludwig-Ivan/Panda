import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthShell from '../components/AuthShell.jsx'
import Field from '../components/Field.jsx'
import { api } from '../lib/api.js'

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function Register() {
  const nav = useNavigate()
  const [v, setV] = useState({ email: '', password: '', confirm: '', adult: false })
  const [errs, setErrs] = useState({})
  const [busy, setBusy] = useState(false)
  const [server, setServer] = useState('')
  const set = (k) => (e) => setV((p) => ({ ...p, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))

  async function submit(e) {
    e.preventDefault()
    const er = {}
    if (!EMAIL.test(v.email.trim())) er.email = 'Escribe un correo válido.'
    if (v.password.length < 8) er.password = 'Usa al menos 8 caracteres.'
    if (v.confirm !== v.password) er.confirm = 'Las contraseñas no coinciden.'
    if (!v.adult) er.adult = 'Debes tener 18 años o más para usar Panda.'
    setErrs(er); setServer('')
    if (Object.keys(er).length) return
    setBusy(true)
    try {
      await api.register({ email: v.email.trim().toLowerCase(), password: v.password, mayor_edad_declarado: true })
      nav('/onboarding')
    } catch (err) {
      setServer(err.status === 400 ? 'No pudimos crear la cuenta con esos datos. Revisa el correo o intenta iniciar sesión.' : 'Algo salió mal. Inténtalo de nuevo.')
    } finally { setBusy(false) }
  }

  return (
    <AuthShell title="Crea tu cuenta" sub="Empieza a registrar tus comidas en minutos."
      foot={<>¿Ya tienes cuenta? <Link to="/acceso">Inicia sesión</Link></>}>
      <form onSubmit={submit} noValidate>
        <Field id="email" label="Correo" type="email" autoComplete="email" value={v.email} onChange={set('email')} error={errs.email} />
        <Field id="password" label="Contraseña" type="password" autoComplete="new-password" value={v.password} onChange={set('password')} error={errs.password} />
        <Field id="confirm" label="Confirmar contraseña" type="password" autoComplete="new-password" value={v.confirm} onChange={set('confirm')} error={errs.confirm} />
        <label className="check">
          <input type="checkbox" checked={v.adult} onChange={set('adult')} />
          <span>Declaro que tengo 18 años o más.</span>
        </label>
        {errs.adult && <small className="err" role="alert">{errs.adult}</small>}
        <p className="hint">Revisa nuestro <Link to="/avisos/privacidad">aviso de privacidad</Link>; aceptarás los avisos en el siguiente paso.</p>
        {server && <p className="err box" role="alert">{server}</p>}
        <button className="btn p full" disabled={busy}>{busy ? 'Creando cuenta…' : 'Crear cuenta'}</button>
      </form>
    </AuthShell>
  )
}

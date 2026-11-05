import { Routes, Route, Navigate, Link } from 'react-router-dom'
import PublicLayout from './components/PublicLayout.jsx'
import Landing from './pages/Landing.jsx'
import Register from './pages/Register.jsx'
import Login from './pages/Login.jsx'
import Forgot from './pages/Forgot.jsx'
import Legal from './pages/Legal.jsx'
import AuthShell from './components/AuthShell.jsx'

// Marcador temporal: aquí empezará la etapa de onboarding y la app.
const Pending = () => (
  <AuthShell title="Sesión iniciada" sub="La siguiente etapa (onboarding y panel) aún está en construcción.">
    <Link className="btn" to="/">Volver al inicio</Link>
  </AuthShell>
)

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<Landing />} />
        <Route path="registro" element={<Register />} />
        <Route path="acceso" element={<Login />} />
        <Route path="recuperar" element={<Forgot />} />
        <Route path="avisos/:slug" element={<Legal />} />
        <Route path="inicio" element={<Pending />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

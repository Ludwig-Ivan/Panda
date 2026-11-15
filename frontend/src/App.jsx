import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { MealDraftProvider } from './context/MealDraft.jsx'
import PublicLayout from './components/PublicLayout.jsx'
import AppLayout from './components/AppLayout.jsx'

// Carga perezosa (Lazy loading) para optimizar el rendimiento con Vite
const Landing = lazy(() => import('./pages/auth/Landing.jsx'))
const Register = lazy(() => import('./pages/auth/Register.jsx'))
const Login = lazy(() => import('./pages/auth/Login.jsx'))
const Forgot = lazy(() => import('./pages/auth/Forgot.jsx'))
const Legal = lazy(() => import('./pages/Legal.jsx'))
const Onboarding = lazy(() => import('./pages/onboarding/Onboarding.jsx'))

const Home = lazy(() => import('./pages/Home.jsx'))
const Registrar = lazy(() => import('./pages/meal/Registrar.jsx'))
const Captura = lazy(() => import('./pages/meal/Captura.jsx'))
const Analizando = lazy(() => import('./pages/meal/Analizando.jsx'))
const Revision = lazy(() => import('./pages/meal/Revision.jsx'))
const BuscarAlimento = lazy(() => import('./pages/meal/BuscarAlimento.jsx'))
const EditarItem = lazy(() => import('./pages/meal/EditarItem.jsx'))
const Confirmar = lazy(() => import('./pages/meal/Confirmar.jsx'))
const ComidaDetalle = lazy(() => import('./pages/ComidaDetalle.jsx'))
const Recomendacion = lazy(() => import('./pages/Recomendacion.jsx'))
const Historial = lazy(() => import('./pages/Historial.jsx'))

const Ajustes = lazy(() => import('./pages/ajustes/Ajustes.jsx'))
const Perfil = lazy(() => import('./pages/ajustes/Perfil.jsx'))
const Actividades = lazy(() => import('./pages/ajustes/Actividades.jsx'))
const Privacidad = lazy(() => import('./pages/ajustes/Privacidad.jsx'))
const EliminarHistorial = lazy(() => import('./pages/ajustes/EliminarHistorial.jsx'))
const EliminarCuenta = lazy(() => import('./pages/ajustes/EliminarCuenta.jsx'))

// Componente de carga simple mientras se descargan las vistas
const LoadingSpinner = () => (
  <div className="flex items-center justify-center min-h-screen">
    <p className="text-gray-500 font-medium">Cargando...</p>
  </div>
)

export default function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        {/* Rutas Públicas */}
        <Route element={<PublicLayout />}>
          <Route index element={<Landing />} />
          <Route path="registro" element={<Register />} />
          <Route path="acceso" element={<Login />} />
          <Route path="recuperar" element={<Forgot />} />
          <Route path="avisos/:slug" element={<Legal />} />
        </Route>

        {/* Onboarding (Flujo inicial post-registro) */}
        <Route path="onboarding" element={<Onboarding />} />

        {/* Rutas Privadas de la App (Protegidas por AppLayout) */}
        <Route element={<AppLayout />}>
          <Route path="inicio" element={<Home />} />
          <Route path="historial" element={<Historial />} />
          
          {/* Detalles y recomendaciones de comidas existentes */}
          <Route path="comidas/:id" element={<ComidaDetalle />} />
          <Route path="comidas/:id/actividad" element={<Recomendacion />} />

          {/* Flujo de nueva comida envuelto en su propio Provider para aislar estados */}
          <Route path="comidas/nueva" element={<MealDraftProvider><Registrar /></MealDraftProvider>} />
          <Route path="comidas/nueva/foto" element={<MealDraftProvider><Captura /></MealDraftProvider>} />
          <Route path="comidas/nueva/analizando" element={<MealDraftProvider><Analizando /></MealDraftProvider>} />
          <Route path="comidas/nueva/revision" element={<MealDraftProvider><Revision /></MealDraftProvider>} />
          <Route path="comidas/nueva/buscar" element={<MealDraftProvider><BuscarAlimento /></MealDraftProvider>} />
          <Route path="comidas/nueva/item/:id" element={<MealDraftProvider><EditarItem /></MealDraftProvider>} />
          <Route path="comidas/nueva/confirmar" element={<MealDraftProvider><Confirmar /></MealDraftProvider>} />

          {/* Sección de Ajustes agrupada */}
          <Route path="ajustes">
            <Route index element={<Ajustes />} />
            <Route path="perfil" element={<Perfil />} />
            <Route path="actividades" element={<Actividades />} />
            <Route path="privacidad" element={<Privacidad />} />
            <Route path="historial" element={<EliminarHistorial />} />
            <Route path="cuenta" element={<EliminarCuenta />} />
          </Route>
        </Route>

        {/* Ruta comodín para redireccionar URLs no encontradas */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
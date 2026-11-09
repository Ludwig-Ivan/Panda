import { Routes, Route, Navigate } from 'react-router-dom'
import PublicLayout from './components/PublicLayout.jsx'
import AppLayout from './components/AppLayout.jsx'
import { MealDraftProvider } from './context/MealDraft.jsx'
import Landing from './pages/Landing.jsx'
import Register from './pages/Register.jsx'
import Login from './pages/Login.jsx'
import Forgot from './pages/Forgot.jsx'
import Legal from './pages/Legal.jsx'
import Onboarding from './pages/Onboarding.jsx'
import Home from './pages/Home.jsx'
import Registrar from './pages/meal/Registrar.jsx'
import Captura from './pages/meal/Captura.jsx'
import Analizando from './pages/meal/Analizando.jsx'
import Revision from './pages/meal/Revision.jsx'
import BuscarAlimento from './pages/meal/BuscarAlimento.jsx'
import EditarItem from './pages/meal/EditarItem.jsx'
import Confirmar from './pages/meal/Confirmar.jsx'
import ComidaDetalle from './pages/ComidaDetalle.jsx'
import Recomendacion from './pages/Recomendacion.jsx'
import Historial from './pages/Historial.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<Landing />} />
        <Route path="registro" element={<Register />} />
        <Route path="acceso" element={<Login />} />
        <Route path="recuperar" element={<Forgot />} />
        <Route path="avisos/:slug" element={<Legal />} />
      </Route>

      <Route path="onboarding" element={<Onboarding />} />

      <Route element={<MealDraftProvider><AppLayout /></MealDraftProvider>}>
        <Route path="inicio" element={<Home />} />
        <Route path="comidas/nueva" element={<Registrar />} />
        <Route path="comidas/nueva/foto" element={<Captura />} />
        <Route path="comidas/nueva/analizando" element={<Analizando />} />
        <Route path="comidas/nueva/revision" element={<Revision />} />
        <Route path="comidas/nueva/buscar" element={<BuscarAlimento />} />
        <Route path="comidas/nueva/item/:id" element={<EditarItem />} />
        <Route path="comidas/nueva/confirmar" element={<Confirmar />} />
        <Route path="comidas/:id" element={<ComidaDetalle />} />
        <Route path="comidas/:id/actividad" element={<Recomendacion />} />
        <Route path="historial" element={<Historial />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
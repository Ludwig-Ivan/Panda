// Cliente de la API de Django. Los endpoints son supuestos: ajústalos a la API Specification.
// Con VITE_USE_MOCK=true (por defecto) responde sin backend para probar el diseño.
import { ACTIVIDADES_MOCK } from '../data/actividades.js'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const MOCK = import.meta.env.VITE_USE_MOCK !== 'false'
const wait = (ms) => new Promise((r) => setTimeout(r, ms))

async function send(method, path, body) {
  if (MOCK) { await wait(300); return {} }
  const res = await fetch(`${BASE}${path}`, {
    method,
    credentials: 'include', // el refresh token viaja en cookie HttpOnly
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw Object.assign(new Error(data.detail || 'Error de servidor'), { status: res.status, data })
  return data
}
const post = (path, body) => send('POST', path, body)

export const api = {
  register: (b) => post('/auth/registro/', b),      // { email, password, mayor_edad_declarado }
  login: (b) => post('/auth/login/', b),            // { email, password }
  requestReset: (b) => post('/auth/recuperar/', b), // { email }

  // Catálogo de actividades (puede venir paginado como { results: [...] })
  async getActividades() {
    if (MOCK) { await wait(300); return ACTIVIDADES_MOCK }
    const res = await fetch(`${BASE}/catalogos/actividades/`, { credentials: 'include' })
    if (!res.ok) throw new Error('No se pudo cargar el catálogo')
    const data = await res.json()
    return data.results || data
  },

  // Onboarding: cada llamada corresponde a una tabla del diseño de base de datos.
  async completeOnboarding(b) {
    await send('POST', '/consentimientos/', b.consentimientos)        // consentimientos
    await send('PUT', '/perfil/', b.perfil)                           // perfiles
    await send('PUT', '/preferencias-actividad/', { actividades: b.actividades }) // preferencias_actividad
    await send('PATCH', '/usuarios/me/', { guardar_fotos: b.guardar_fotos })      // usuarios.guardar_fotos
  },
}

export { send, BASE, MOCK, wait }
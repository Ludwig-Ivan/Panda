// Cliente de la API de Django. Los endpoints son supuestos: ajústalos a la API Specification.
// Con VITE_USE_MOCK=true (por defecto) responde sin backend para probar el diseño.
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const MOCK = import.meta.env.VITE_USE_MOCK !== 'false'
const wait = (ms) => new Promise((r) => setTimeout(r, ms))

async function post(path, body) {
  if (MOCK) { await wait(600); return {} }
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    credentials: 'include', // el refresh token viaja en cookie HttpOnly
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw Object.assign(new Error(data.detail || 'Error de servidor'), { status: res.status, data })
  return data
}

export const api = {
  register: (b) => post('/auth/registro/', b),      // { email, password, mayor_edad_declarado }
  login: (b) => post('/auth/login/', b),            // { email, password }
  requestReset: (b) => post('/auth/recuperar/', b), // { email }
}

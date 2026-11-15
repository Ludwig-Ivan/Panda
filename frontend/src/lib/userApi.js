// Endpoints de cuenta y ajustes. Son supuestos: ajústalos a la API Specification.
import { send, MOCK, wait } from './api.js'
import { mockUser } from './mockStore.js'

const mock = async (fn) => { await wait(300); return fn() }

export const userApi = {
  getCuenta: () => (MOCK ? mock(() => { const u = mockUser.read(); return { email: u.email, guardar_fotos: u.guardar_fotos } }) : send('GET', '/usuarios/me/')),
  saveFotos: (v) => (MOCK ? mock(() => { mockUser.save({ guardar_fotos: v }); return {} }) : send('PATCH', '/usuarios/me/', { guardar_fotos: v })),

  getPerfil: () => (MOCK ? mock(() => mockUser.read().perfil) : send('GET', '/perfil/')),
  savePerfil: (p) => (MOCK ? mock(() => { mockUser.save({ perfil: p }); return p }) : send('PUT', '/perfil/', p)),

  getPreferencias: () => (MOCK ? mock(() => ({ actividades: mockUser.read().actividades })) : send('GET', '/preferencias-actividad/')),
  savePreferencias: (ids) => (MOCK ? mock(() => { mockUser.save({ actividades: ids }); return {} }) : send('PUT', '/preferencias-actividad/', { actividades: ids })),

  getConsentimientos: () => (MOCK ? mock(() => mockUser.read().consentimientos) : send('GET', '/consentimientos/')),

  // Borra todas las comidas del usuario (items, correcciones, recomendaciones) y sus fotos en R2.
  deleteHistorial: () => (MOCK ? mock(() => { try { sessionStorage.removeItem('panda_mock_meals') } catch { /* nada */ } return {} }) : send('DELETE', '/comidas/')),
  // Borra la cuenta en cascada; el servidor valida la contraseña y elimina las fotos (RD-08).
  deleteCuenta: (password) => (MOCK ? mock(() => { mockUser.clear(); return {} }) : send('DELETE', '/usuarios/me/', { password })),
  // Pone en la blacklist los refresh tokens vigentes del usuario.
  logout: () => (MOCK ? mock(() => ({})) : send('POST', '/auth/logout/')),
}

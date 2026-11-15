// Datos de usuario simulados (modo VITE_USE_MOCK=true). Se guardan en sessionStorage.
const KEY = 'panda_mock_user'
const FECHA = '2026-11-02T10:00:00.000Z'
const DEFAULT = {
  email: 'tu@correo.com',
  perfil: { edad: 25, sexo: 'masculino', peso_kg: 108, estatura_cm: 175, nivel_actividad: 'ligero' },
  actividades: [],
  guardar_fotos: true,
  consentimientos: [
    { tipo: 'privacidad', version: '2026-10', aceptado_at: FECHA },
    { tipo: 'avisos_salud', version: '2026-10', aceptado_at: FECHA },
    { tipo: 'procesamiento_terceros', version: '2026-10', aceptado_at: FECHA },
  ],
}

const read = () => { try { return { ...DEFAULT, ...JSON.parse(sessionStorage.getItem(KEY)) } } catch { return DEFAULT } }

export const mockUser = {
  read,
  save: (patch) => { try { sessionStorage.setItem(KEY, JSON.stringify({ ...read(), ...patch })) } catch { /* sin almacenamiento */ } },
  clear: () => { try { sessionStorage.removeItem(KEY); sessionStorage.removeItem('panda_mock_meals') } catch { /* sin almacenamiento */ } },
}

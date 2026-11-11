// Endpoints de comidas y asistente. Son supuestos: ajústalos a la API Specification.
// En modo simulado, las comidas confirmadas se guardan en sessionStorage para probar el flujo completo.
import { send, BASE, MOCK, wait } from './api.js'
import { ANALISIS_MOCK, respuestaAyuda } from '../data/mocks.js'
import { ACTIVIDADES_MOCK } from '../data/actividades.js'
import { ALIMENTOS_MOCK } from '../data/alimentos.js'
import { MET } from '../data/met.js'

const KEY = 'panda_mock_meals'
const read = () => { try { return JSON.parse(sessionStorage.getItem(KEY)) || [] } catch { return [] } }
const write = (m) => { try { sessionStorage.setItem(KEY, JSON.stringify(m)) } catch { /* sin almacenamiento */ } }
const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
const hhmm = (iso) => new Date(iso).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false })
const notFound = () => Object.assign(new Error('No encontrada'), { status: 404 })
const resumen = (m) => ({ id: m.id, hora: hhmm(m.consumida_at), nombre: m.items.map((i) => i.nombre).join(', '), kcal: m.kcal_total, consumida_at: m.consumida_at })

// Misma idea que la fórmula del documento: minutos = kcal a equilibrar / (MET neto × peso) × 60.
function mockRecomendacion(m) {
  const peso = 75 // en producción sale del perfil
  const items = ACTIVIDADES_MOCK.map((a) => {
    const neto = MET[a.id] - 1
    const min = Math.min(180, Math.max(5, Math.round(((m.kcal_total / (neto * peso)) * 60) / 5) * 5))
    return { actividad: a, duracion_min: min, sesiones: Math.min(4, Math.ceil(min / 60)), kcal_estimadas: Math.round((neto * peso * min) / 60), es_preferida: [3, 4].includes(a.id) } // preferidas: ejemplo
  })
    .sort((a, b) => Number(b.es_preferida) - Number(a.es_preferida) || a.duracion_min - b.duracion_min)
    .slice(0, 6).map((x, i) => ({ ...x, orden: i + 1 }))
  return { kcal_objetivo: m.kcal_total, peso_kg_usado: peso, formula_version: 'met-neto-v1', items }
}

export const mealsApi = {
async getHoy() {
  if (MOCK) {
    await wait(300)
    const hoy = read().filter((m) => new Date(m.consumida_at).toDateString() === new Date().toDateString())
    const comidas = hoy.sort((a, b) => a.consumida_at.localeCompare(b.consumida_at)).map(resumen)
    const kcal = comidas.reduce((a, c) => a + c.kcal, 0)
    return {
      meta_kcal: 1800,
      comidas,
      // Simulado: vendrá del servidor cuando el esquema guarde macros, objetivo y peso.
      macros: {
        consumido: { p: Math.round((kcal * 0.25) / 4), c: Math.round((kcal * 0.45) / 4), g: Math.round((kcal * 0.3) / 9) },
        meta: { p: 135, c: 180, g: 60 },
      },
      objetivo: { tipo: 'Perder peso', peso_inicial: 114, peso_actual: 108, peso_meta: 100 },
      peso_semana: [
        { d: 'Lun', v: 110.4 }, { d: 'Mar', v: 109.9 }, { d: 'Mié', v: 109.3 }, { d: 'Jue', v: 108.9 },
        { d: 'Vie', v: 108.4 }, { d: 'Sáb', v: 108.1 }, { d: 'Dom', v: 108 },
      ],
    }
  }
  return send('GET', '/comidas/hoy/')
},

  // Envía la foto; el servidor crea la comida en borrador y devuelve { comida_id, items }.
  async analyze(file) {
    if (MOCK) { await wait(2600); return ANALISIS_MOCK }
    const fd = new FormData()
    fd.append('foto', file)
    const res = await fetch(`${BASE}/comidas/analizar/`, { method: 'POST', credentials: 'include', body: fd })
    if (!res.ok) throw new Error('No se pudo analizar la imagen')
    return res.json()
  },

  // Con comidaId confirma el borrador (el servidor registra las correcciones); sin él crea una comida manual.
  async save({ comidaId, payload }) {
    if (MOCK) { await wait(500); const m = { ...payload, id: crypto.randomUUID() }; write([...read(), m]); return { id: m.id } }
    return comidaId ? send('PATCH', `/comidas/${comidaId}/`, payload) : send('POST', '/comidas/', payload)
  },

  async searchAlimentos(q) {
    if (MOCK) {
      await wait(250)
      const n = norm(q.trim())
      return ALIMENTOS_MOCK.filter((a) => norm(a.nombre).includes(n) || a.alias.some((x) => norm(x).includes(n))).slice(0, 8)
    }
    const r = await send('GET', `/catalogos/alimentos/?q=${encodeURIComponent(q.trim())}`) // búsqueda con pg_trgm en el servidor
    return r.results || r
  },

  async getComida(id) {
    if (MOCK) { await wait(250); const m = read().find((x) => x.id === id); if (!m) throw notFound(); return { ...m, foto: null } }
    return send('GET', `/comidas/${id}/`)
  },

  async getRecomendacion(id) {
    if (MOCK) { await wait(300); const m = read().find((x) => x.id === id); if (!m) throw notFound(); return mockRecomendacion(m) }
    return send('GET', `/comidas/${id}/recomendacion/`)
  },

  async deleteComida(id) { // el servidor también borra la foto en R2 (RD-08)
    if (MOCK) { await wait(300); write(read().filter((x) => x.id !== id)); return {} }
    return send('DELETE', `/comidas/${id}/`)
  },

  // Paginación por cursor: devuelve { results, next } donde next es el cursor siguiente o null.
  async getHistorial(cursor) {
    if (MOCK) {
      await wait(300)
      const all = read().sort((a, b) => b.consumida_at.localeCompare(a.consumida_at)), from = Number(cursor || 0), size = 20
      return { results: all.slice(from, from + size).map(resumen), next: from + size < all.length ? String(from + size) : null }
    }
    const r = await send('GET', cursor ? `/comidas/?cursor=${encodeURIComponent(cursor)}` : '/comidas/')
    return { results: r.results, next: r.next ? new URL(r.next).searchParams.get('cursor') : null }
  },

  async askHelp(mensaje) {
    if (MOCK) { await wait(700); return respuestaAyuda(mensaje) }
    const r = await send('POST', '/asistente/ayuda/', { mensaje })
    return r.respuesta
  },
}

import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'

const Ctx = createContext(null)
export const useMealDraft = () => useContext(Ctx)

// En producción el servidor devuelve kcal_min y kcal_max; aquí se derivan de un margen por confianza.
export const newItem = (raw, origen = 'ia') => ({
  id: crypto.randomUUID(),
  nombre: raw.nombre,
  alimento_id: raw.alimento_id ?? null,
  porcion_g: raw.porcion_g,
  kcal_100g: raw.kcal_100g,
  confianza: raw.confianza ?? null,
  fuente: raw.fuente ?? (origen === 'ia' ? 'estimado_ia' : 'usuario'),
  origen,
  margen: origen === 'ia' ? 0.1 + (1 - (raw.confianza ?? 1)) * 0.4 : 0,
})

export function calc(it) {
  const kcal = Math.round((Number(it.porcion_g) || 0) * it.kcal_100g / 100)
  return { kcal, min: Math.round(kcal * (1 - it.margen)), max: Math.round(kcal * (1 + it.margen)) }
}

// RD-03: el total es la suma redondeada a la decena y siempre queda dentro de su rango.
export function totals(items) {
  const s = items.reduce((a, i) => { const c = calc(i); return { k: a.k + c.kcal, mn: a.mn + c.min, mx: a.mx + c.max } }, { k: 0, mn: 0, mx: 0 })
  const r = (n) => Math.round(n / 10) * 10
  const total = r(s.k)
  return { total, min: Math.min(r(s.mn), total), max: Math.max(r(s.mx), total) }
}

const empty = (origen = 'foto') => ({ origen, comidaId: null, foto: null, fotoUrl: null, items: [] })

export function MealDraftProvider({ children }) {
  const [d, setD] = useState(empty())
  const urlRef = useRef(null)
  const revoke = () => { if (urlRef.current) { URL.revokeObjectURL(urlRef.current); urlRef.current = null } }

  const reset = useCallback((origen = 'foto') => { revoke(); setD(empty(origen)) }, [])
  const setFoto = useCallback((f) => {
    revoke(); urlRef.current = URL.createObjectURL(f)
    const u = urlRef.current
    setD((p) => ({ ...p, foto: f, fotoUrl: u }))
  }, [])
  const setItems = useCallback((items) => setD((p) => ({ ...p, items })), [])
  const setComidaId = useCallback((comidaId) => setD((p) => ({ ...p, comidaId })), [])

  const value = useMemo(() => ({ ...d, reset, setFoto, setItems, setComidaId }), [d, reset, setFoto, setItems, setComidaId])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

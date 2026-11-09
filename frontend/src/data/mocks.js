// Datos de ejemplo para probar sin backend (VITE_USE_MOCK=true).
export const HOY_MOCK = {
  meta_kcal: 1800,
  comidas: [
    { id: '1', hora: '08:12', nombre: 'Avena con plátano y chía', kcal: 320 },
    { id: '2', hora: '13:45', nombre: 'Bowl de pollo con arroz', kcal: 430 },
  ],
}

// El servidor real crea un borrador de comida y devuelve su id junto con los alimentos detectados.
export const ANALISIS_MOCK = {
  comida_id: 'mock-1',
  items: [
    { nombre: 'Pechuga de pollo', porcion_g: 150, kcal_100g: 165, confianza: 0.92 },
    { nombre: 'Arroz blanco', porcion_g: 180, kcal_100g: 130, confianza: 0.85 },
    { nombre: 'Ensalada mixta', porcion_g: 90, kcal_100g: 25, confianza: 0.55 },
  ],
}

const norm = (s) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
const FAQ = [
  [['registr', 'foto', 'subir', 'nueva comida'], 'Toca «Registrar comida», elige foto o manual, revisa lo que detectamos y confirma. Si usas foto, analizamos la imagen y te mostramos cada alimento con sus calorías.'],
  [['exact', 'precis', 'aproxim', 'confiable', 'rango'], 'Las calorías son estimaciones y por eso se muestran como un rango. Mientras más clara sea la foto, mejor, y siempre puedes corregir las porciones.'],
  [['corregir', 'editar', 'cambiar', 'porcion', 'quitar'], 'En la pantalla de revisión puedes cambiar los gramos de cada alimento, quitarlo o agregar uno que falte. El total se actualiza al momento.'],
  [['historial', 'anteriores'], 'El historial de comidas llegará en una próxima versión. Por ahora ves las comidas de hoy en Inicio.'],
  [['privacidad', 'datos', 'borrar', 'cuenta'], 'Puedes elegir si guardar tus fotos y revisar los avisos de privacidad cuando quieras. Más adelante podrás borrar tu historial o tu cuenta desde Ajustes.'],
  [['hola', 'buenas', 'ayuda'], '¡Hola! Puedo ayudarte a registrar comidas, entender las estimaciones o corregir lo que detectamos.'],
]
export function respuestaAyuda(texto) {
  const t = norm(texto)
  const hit = FAQ.find(([keys]) => keys.some((k) => t.includes(k)))
  return hit ? hit[1] : 'Todavía no tengo una respuesta para eso. Prueba preguntando cómo registrar una comida, qué tan exactas son las calorías o cómo corregir un alimento.'
}

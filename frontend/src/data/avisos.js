// Textos de ejemplo. Deben ser revisados por un profesional legal antes de publicarse.
// "tipo" coincide con los valores permitidos en consentimientos.tipo de la base de datos.
export const VERSION = '2026-10'
export const AVISOS = {
  privacidad: {
    tipo: 'privacidad',
    titulo: 'Aviso de privacidad',
    secciones: [
      ['Qué datos recopilamos', 'Correo, contraseña (almacenada como hash), edad, sexo, peso, estatura, nivel de actividad, fotos de tus comidas y la fecha y hora en que comes.'],
      ['Para qué los usamos', 'Calcular tus calorías, estimar tus comidas y recomendarte actividad física. No usamos tus datos para fines distintos sin tu consentimiento.'],
      ['Tus derechos', 'Puedes eliminar una comida, tu historial o tu cuenta completa. La eliminación borra tus datos y tus fotos de forma inmediata.'],
    ],
  },
  'avisos-salud': {
    tipo: 'avisos_salud',
    titulo: 'Avisos de salud',
    secciones: [
      ['Son estimaciones', 'Las calorías y las recomendaciones son aproximadas y no sustituyen la orientación de un profesional de la salud.'],
      ['Consulta a un profesional', 'Antes de cambiar tu alimentación o iniciar actividad física intensa, consulta a un médico o nutriólogo, sobre todo si tienes alguna condición de salud.'],
    ],
  },
  'procesamiento-terceros': {
    tipo: 'procesamiento_terceros',
    titulo: 'Procesamiento por terceros',
    secciones: [
      ['Qué se comparte', 'Para estimar tus comidas y responder en el asistente de IA, las fotos y textos que envías se procesan con un proveedor externo de IA.'],
      ['Almacenamiento', 'Las fotos se guardan cifradas en un servicio de almacenamiento de objetos. Puedes decidir si se conservan en tu historial.'],
    ],
  },
}

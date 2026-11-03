export default function HowItWorks() {
  const steps = [
    { title: 'Define tu objetivo', desc: 'Indica tu peso actual y tu meta. Bamboo calcula tus calorías y macros.' },
    { title: 'Registra tus comidas', desc: 'Busca, escanea o fotografía lo que comes. Cada comida se suma al anillo del día.' },
    { title: 'Revisa tu semana', desc: 'Consulta tu tendencia de peso y recibe un consejo para el día siguiente.' }
  ];

  return (
    <section id="como" className="py-16">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight mb-3.5">Empieza en tres pasos</h2>
        <p className="text-[var(--mut)] max-w-xl mb-9">Sin hojas de cálculo ni pesar cada gramo.</p>

        <div className="grid md:grid-cols-3 gap-4.5">
          {steps.map((step, idx) => (
            <div key={idx} className="border-l-2 border-[var(--or)] pl-5 py-1">
              <span className="text-3xl font-semibold text-[var(--or)] block leading-tight">
                {idx + 1}
              </span>
              <h3 className="font-medium mb-1">{step.title}</h3>
              <p className="text-[var(--mut)] text-sm">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
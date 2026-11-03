import { useEffect, useRef, useState } from 'react';

const demoData = [
  { label: 'Proteínas', current: 72, total: 135 },
  { label: 'Carbohidratos', current: 88, total: 180 },
  { label: 'Grasas', current: 26, total: 60 }
];

export default function Features() {
  const [isVisible, setIsVisible] = useState(false);
  const barsRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.4 }
    );

    if (barsRef.current) observer.observe(barsRef.current);

    return () => observer.disconnect();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-6 py-6 pb-18" id="funciones">
      <div className="grid grid-cols-1 md:grid-cols-[1.4fr_1fr_1fr] gap-4.5">
        <article className="bg-[var(--surf)] border border-[var(--line)] rounded-3xl p-7 flex flex-col gap-2.5 overflow-hidden">
          <span className="text-xl">🔥</span>
          <h3 className="font-medium text-lg">Calorías y macros del día</h3>
          <p className="text-[var(--mut)] text-sm">
            <strong className="text-[var(--tx)] font-medium">Registra lo que comes</strong> y ve al instante cuántas calorías y gramos de proteína, carbohidratos y grasas te quedan.
          </p>
          <div ref={barsRef} className="mt-auto grid gap-2.5 pt-4.5">
            {demoData.map((item, idx) => (
              <div key={idx} className="grid grid-cols-[90px_1fr_56px] gap-2.5 items-center text-xs text-[var(--mut)]">
                <span>{item.label}</span>
                <div className="h-2 rounded-full bg-[var(--line)] overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#c2410c] to-[#f97316] rounded-full transition-all duration-1000 ease-out"
                    style={{ width: isVisible ? `${(item.current / item.total) * 100}%` : '0%' }}
                  />
                </div>
                <span>{item.current}/{item.total} g</span>
              </div>
            ))}
          </div>
        </article>

        <article className="bg-[var(--surf)] border border-[var(--line)] rounded-3xl p-7 flex flex-col gap-2.5">
          <span className="text-xl">📷</span>
          <h3 className="font-medium text-lg">Registro rápido</h3>
          <p className="text-[var(--mut)] text-sm">
            <strong className="text-[var(--tx)] font-medium">Escanea un código de barras</strong> o toma una foto de tu plato en lugar de buscar cada ingrediente.
          </p>
        </article>

        <article className="bg-[var(--surf)] border border-[var(--line)] rounded-3xl p-7 flex flex-col gap-2.5">
          <span className="text-xl">📉</span>
          <h3 className="font-medium text-lg">Progreso semanal</h3>
          <p className="text-[var(--mut)] text-sm">
            Una gráfica con tu peso de la semana. <strong className="text-[var(--tx)] font-medium">Ves la tendencia</strong>, no solo el número de hoy.
          </p>
        </article>
      </div>
    </div>
  );
}
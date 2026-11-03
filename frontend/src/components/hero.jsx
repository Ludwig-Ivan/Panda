export default function Hero() {
  return (
    <section className="py-24 md:py-14">
      <div className="max-w-6xl mx-auto px-6 grid md:grid-cols-[1.1fr_0.9fr] gap-12 items-end">
        <div>
          <h1 className="text-4xl md:text-6xl font-medium tracking-tight leading-tight">
            Come mejor.<em className="block not-italic text-[var(--or)]">Pierde grasa sin adivinar.</em>
          </h1>
          <div className="flex gap-3 mt-8 flex-wrap">
            <a href="#unirme" className="px-6.5 py-3.5 rounded-xl border border-[var(--or)] bg-[var(--btn)] text-[var(--btn-tx)] font-medium">
              Unirme a la lista de espera
            </a>
            <a href="#calculadora" className="px-6.5 py-3.5 rounded-xl border border-[var(--line)] bg-[var(--surf)] font-medium">
              Calcular mi meta
            </a>
          </div>
        </div>
        <p className="text-[var(--mut)] text-lg max-w-prose">
          Bamboo cuenta tus calorías y macros, y te muestra cuánto te falta cada día para llegar a tu peso meta.
        </p>
      </div>
    </section>
  );
}
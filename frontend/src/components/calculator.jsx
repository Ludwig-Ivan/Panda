import { useState } from 'react';

export default function Calculator() {
  const [formData, setFormData] = useState({
    sex: 'm',
    age: 25,
    weight: 108,
    height: 175,
    activity: 1.375,
    deficit: 20
  });

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData((prev) => ({ ...prev, [id]: value }));
  };

  const calculateResults = () => {
    const w = parseFloat(formData.weight);
    const h = parseFloat(formData.height);
    const a = parseFloat(formData.age);
    const d = parseFloat(formData.deficit);
    const act = parseFloat(formData.activity);

    if (!w || !h || !a) return { kcal: 0, protein: 0 };

    const bmr = 10 * w + 6.25 * h - 5 * a + (formData.sex === 'm' ? 5 : -161);
    const kcal = Math.max(Math.round((bmr * act * (1 - d / 100)) / 10) * 10, 1200);
    const protein = Math.round(w * 1.6);

    return { kcal, protein };
  };

  const { kcal, protein } = calculateResults();

  return (
    <section id="calculadora" className="py-16">
      <div className="max-w-6xl mx-auto px-6">
        <h2 className="text-3xl md:text-4xl font-medium tracking-tight mb-3.5">Calcula tu meta diaria</h2>
        <p className="text-[var(--mut)] max-w-xl mb-9">
          Una estimación con déficit moderado para empezar. Ajústala con tus resultados de cada semana.
        </p>

        <div className="grid md:grid-cols-2 gap-4.5">
          <div className="bg-[var(--surf)] border border-[var(--line)] rounded-3xl p-7">
            <form className="grid grid-cols-2 gap-3.5">
              <label className="grid gap-1.5 text-xs text-[var(--mut)]">
                Sexo
                <select id="sex" value={formData.sex} onChange={handleChange} className="p-2.5 rounded-xl border border-[var(--line)] bg-[var(--bg)]">
                  <option value="m">Hombre</option>
                  <option value="f">Mujer</option>
                </select>
              </label>

              <label className="grid gap-1.5 text-xs text-[var(--mut)]">
                Edad
                <input id="age" type="number" min="15" max="90" value={formData.age} onChange={handleChange} className="p-2.5 rounded-xl border border-[var(--line)] bg-[var(--bg)]" />
              </label>

              <label className="grid gap-1.5 text-xs text-[var(--mut)]">
                Peso (kg)
                <input id="weight" type="number" min="35" max="300" value={formData.weight} onChange={handleChange} className="p-2.5 rounded-xl border border-[var(--line)] bg-[var(--bg)]" />
              </label>

              <label className="grid gap-1.5 text-xs text-[var(--mut)]">
                Estatura (cm)
                <input id="height" type="number" min="120" max="230" value={formData.height} onChange={handleChange} className="p-2.5 rounded-xl border border-[var(--line)] bg-[var(--bg)]" />
              </label>

              <label className="col-span-2 grid gap-1.5 text-xs text-[var(--mut)]">
                Actividad
                <select id="activity" value={formData.activity} onChange={handleChange} className="p-2.5 rounded-xl border border-[var(--line)] bg-[var(--bg)]">
                  <option value="1.2">Sedentaria</option>
                  <option value="1.375">Ligera, 1 a 3 días por semana</option>
                  <option value="1.55">Moderada, 3 a 5 días por semana</option>
                  <option value="1.725">Alta, 6 a 7 días por semana</option>
                </select>
              </label>

              <label className="col-span-2 grid gap-1.5 text-xs text-[var(--mut)]">
                Déficit: <b className="text-[var(--tx)] font-semibold">{formData.deficit}%</b>
                <input id="deficit" type="range" min="10" max="25" value={formData.deficit} onChange={handleChange} />
              </label>
            </form>
          </div>

          <div className="bg-[var(--surf)] border border-[var(--line)] rounded-3xl p-7 flex flex-col justify-center gap-1.5">
            <small className="text-[var(--mut)]">Tu meta de calorías al día</small>
            <div className="text-5xl md:text-7xl font-semibold text-[var(--or)]">
              {kcal.toLocaleString('es-MX')}
            </div>
            <div className="flex gap-2.5 flex-wrap my-3.5">
              <span className="border border-[var(--line)] rounded-full px-3.5 py-1 text-xs">
                Proteína: {protein} g
              </span>
              <span className="border border-[var(--line)] rounded-full px-3.5 py-1 text-xs">
                Déficit: {formData.deficit}%
              </span>
            </div>
            <small className="text-[var(--mut)] text-xs">
              Es una estimación general y no sustituye la guía de un profesional de la salud.
            </small>
          </div>
        </div>
      </div>
    </section>
  );
}
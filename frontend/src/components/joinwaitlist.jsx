import { useState } from 'react';

export default function JoinWaitlist({ showToast }) {
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email) return;
    setEmail('');
    showToast('¡Gracias! Te avisaremos pronto.');
  };

  return (
    <div className="max-w-6xl mx-auto px-6" id="unirme">
      <div className="bg-[var(--surf)] border border-[var(--line)] rounded-3xl p-14 text-center my-6 mb-18">
        <h2 className="text-3xl font-medium mb-2">Sé de los primeros en probar Bamboo</h2>
        <p className="text-[var(--mut)] mx-auto mb-6.5 max-w-md text-sm">
          Estamos terminando la app. Deja tu correo y te avisamos cuando abramos el acceso.
        </p>
        <form onSubmit={handleSubmit} className="flex gap-2.5 justify-center flex-wrap">
          <input
            type="email"
            required
            placeholder="tu@correo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="max-w-xs p-2.5 rounded-xl border border-[var(--line)] bg-[var(--bg)] text-sm"
          />
          <button type="submit" className="px-5 py-2.5 rounded-xl border border-[var(--or)] bg-[var(--btn)] text-[var(--btn-tx)] text-sm font-medium cursor-pointer">
            Unirme a la lista
          </button>
        </form>
      </div>
    </div>
  );
}
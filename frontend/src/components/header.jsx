export default function Header({ darkMode, setDarkMode }) {
  return (
    <header className="sticky top-0 z-10 bg-[var(--bg)]/88 backdrop-blur-md border-b border-[var(--line)]">
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between md:justify-start gap-7 h-16">
        <a href="#" className="flex items-center gap-2.5 font-bold tracking-widest text-[var(--tx)]">
          <span className="w-8 h-8 rounded-full border-2 border-[var(--or)] grid place-items-center text-sm">
            🐼
          </span>
          BAMBOO
        </a>

        <nav className="hidden md:flex gap-6 flex-1 text-[var(--mut)] text-sm">
          <a href="#funciones" className="hover:text-[var(--tx)] transition-colors">Funciones</a>
          <a href="#calculadora" className="hover:text-[var(--tx)] transition-colors">Calculadora</a>
          <a href="#como" className="hover:text-[var(--tx)] transition-colors">Cómo funciona</a>
        </nav>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="w-9.5 h-9.5 rounded-xl border border-[var(--line)] bg-[var(--surf)] cursor-pointer"
            aria-label="Cambiar tema"
          >
            🌓
          </button>
          <a href="#unirme" className="hidden md:inline-block px-5 py-2.5 rounded-xl border border-[var(--line)] bg-[var(--surf)] text-sm font-medium">
            Iniciar sesión
          </a>
          <a href="#unirme" className="px-5 py-2.5 rounded-xl border border-[var(--or)] bg-[var(--btn)] text-[var(--btn-tx)] text-sm font-medium">
            Unirme a la lista
          </a>
        </div>
      </div>
    </header>
  );
}
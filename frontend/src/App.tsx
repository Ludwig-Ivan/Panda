import { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Features from './components/Features';
import Calculator from './components/Calculator';
import HowItWorks from './components/HowItWorks';
import JoinWaitlist from './components/JoinWaitlist';
import Toast from './components/Toast';

export default function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [toastMessage, setToastMessage] = useState('');

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 2400);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between">
      <Header darkMode={darkMode} setDarkMode={setDarkMode} />
      <main className="flex-grow">
        <Hero />
        <Features />
        <Calculator />
        <HowItWorks />
        <JoinWaitlist showToast={showToast} />
      </main>

      <footer className="border-t border-[var(--line)] py-7 text-[var(--mut)] text-sm">
        <div className="max-w-6xl mx-auto px-6 flex justify-between gap-3 flex-wrap">
          <span>Bamboo · Pequeños cambios, grandes resultados.</span>
          <span>Vista previa de diseño (React)</span>
        </div>
      </footer>

      <Toast message={toastMessage} />
    </div>
  );
}
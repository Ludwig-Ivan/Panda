export default function Toast({ message }) {
  if (!message) return null;

  return (
    <div className="fixed left-1/2 bottom-6 -translate-x-1/2 bg-[var(--tx)] text-[var(--bg)] px-5 py-2.5 rounded-full text-sm shadow-md animate-fade-in pointer-events-none">
      {message}
    </div>
  );
}
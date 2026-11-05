import Orb from './Orb.jsx'

export default function AuthShell({ title, sub, children, foot }) {
  return (
    <main className="auth">
      <div className="auth-card">
        <Orb size={44} />
        <h1>{title}</h1>
        {sub && <p className="sub">{sub}</p>}
        {children}
        {foot && <p className="foot">{foot}</p>}
      </div>
    </main>
  )
}

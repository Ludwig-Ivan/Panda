import { Link } from 'react-router-dom'
import s from './Ajustes.module.css'

export default function SubPage({ title, desc, children }) {
  return (
    <main className={s.page}>
      <Link className={s.back} to="/ajustes">‹ Ajustes</Link>
      <header><h1>{title}</h1>{desc && <p className={s.desc}>{desc}</p>}</header>
      {children}
    </main>
  )
}

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ImgSlot from '../components/ImgSlot.jsx'
import { IMG } from '../data/imagenes.js'
import { mealsApi } from '../lib/mealsApi.js'
import s from './Home.module.css'
import { ArrowBigDown, ArrowDown, ArrowRight, ArrowUp, Calendar, Camera, ChevronLeft, ChevronRight, Droplet, Drumstick, Dumbbell, Flame, Footprints, Lightbulb, Pencil, Plus, Target, TrendingDown, Utensils, Wheat } from 'lucide-react'

const AGUA_META = 2500
const TIPS = [
  'Mantén una buena hidratación. El agua te ayuda a sentirte más lleno y mejora tu rendimiento.',
  'Incluye proteína en cada comida: te ayuda a sentirte satisfecho por más tiempo.',
  'Registra tus comidas en el momento: es más fácil recordar las porciones.',
  'Dormir bien ayuda a regular el hambre y mejora tus resultados.',
]
const tipoComida = (iso) => { const h = new Date(iso).getHours(); return h < 11 ? 'Desayuno' : h < 17 ? 'Comida' : h < 22 ? 'Cena' : 'Snack' }

// Hidratación guardada solo en este dispositivo (aún no existe tabla en la base de datos).
const keyAgua = () => `panda_agua_${new Date().toDateString()}`
function useAgua() {
  const [v, setV] = useState(() => { try { return Number(localStorage.getItem(keyAgua())) || 0 } catch { return 0 } })
  const add = (ml) => {
    const n = Math.min(v + ml, AGUA_META)
    setV(n)
    try { localStorage.setItem(keyAgua(), String(n)) } catch { /* sin almacenamiento */ }
  }
  return [v, add]
}

function Chart({ data }) {
  if (data.length < 2) return null
  const W = 320, H = 170, L = 30, R = 12, T = 12, B = 28
  const vals = data.map((d) => d.v)
  const min = Math.floor(Math.min(...vals) - 1), max = Math.ceil(Math.max(...vals) + 1)
  const x = (i) => L + (i * (W - L - R)) / (data.length - 1)
  const y = (v) => T + ((max - v) / (max - min)) * (H - T - B)
  const pts = data.map((p, i) => `${x(i)},${y(p.v)}`).join(' ')
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className={s.chart} role="img" aria-label="Gráfica de peso de la semana">
      {[min, Math.round((min + max) / 2), max].map((g) => (
        <g key={g}><line x1={L} x2={W - R} y1={y(g)} y2={y(g)} stroke="#2e2622" /><text x="2" y={y(g) + 3}>{g}</text></g>
      ))}
      <polygon points={`${x(0)},${H - B} ${pts} ${x(data.length - 1)},${H - B}`} fill="#f9731622" />
      <polyline points={pts} fill="none" stroke="#f97316" strokeWidth="2" />
      {data.map((p, i) => (
        <g key={p.d}><circle cx={x(i)} cy={y(p.v)} r="3.5" fill="#f97316"><title>{p.d}: {p.v} kg</title></circle><text x={x(i) - 8} y={H - 8}>{p.d}</text></g>
      ))}
    </svg>
  )
}

export default function Home() {
  const [h, setH] = useState(null)
  const [failed, setFailed] = useState(false)
  const [tip, setTip] = useState(0)
  const [agua, addAgua] = useAgua()
  useEffect(() => { mealsApi.getHoy().then(setH).catch(() => setFailed(true)) }, [])

  const fecha = new Date().toLocaleDateString('es-MX', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
  const total = h ? h.comidas.reduce((a, c) => a + c.kcal, 0) : 0
  const left = h ? h.meta_kcal - total : 0
  const o = h?.objetivo
  const span = o ? o.peso_inicial - o.peso_meta : 0
  const progreso = o && span > 0 ? Math.max(0, Math.min(1, (o.peso_inicial - o.peso_actual) / span)) : 0
  const semana = h?.peso_semana
  const delta = semana?.length > 1 ? (semana[semana.length - 1].v - semana[0].v).toFixed(1) : null

  return (
    <main className={s.home}>
      <header className={s.head}>
        <div>
          <h1>¡Hola!</h1>
          <p className={s.sub}>{h && h.comidas.length ? 'Cada registro te acerca a tus objetivos.' : 'Empieza registrando tu primera comida de hoy.'}</p>
        </div>
        <div className={s.dateBox}>
          <div><b className={s.date}><Calendar size={20} aria-hidden="true" />{fecha}</b></div>
          <ImgSlot className={s.mascot} src={IMG.mascotaSaludo} w={120} h={90} label="Panda saludo" alt="" />
        </div>
      </header>
      {failed && <p className={s.error} role="alert">No pudimos cargar tu resumen. Inténtalo de nuevo más tarde.</p>}

      <div className={s.dash}>
        <div className={s.mainCol}>
          <div className={s.topRow}>
            <section className={`${s.card} ${s.dark} ${s.kcal}`} aria-label="Calorías de hoy">
              <div className={s.ring}>
                <svg viewBox="0 0 120 120" aria-hidden="true">
                  <circle className={s.trk} cx="60" cy="60" r="52" />
                  <circle className={s.fill} cx="60" cy="60" r="52" style={{ strokeDashoffset: 326.7 * (1 - Math.min(total / (h?.meta_kcal || 1), 1)) }} />
                </svg>
                <div className={s.ringTxt}><b>{total}</b><span>kcal</span><small>de {h ? h.meta_kcal.toLocaleString('es-MX') : '…'}</small></div>
              </div>
              <div className={s.kcalInfo}>
                <h2><Flame size={20} aria-hidden="true" /> Calorías</h2>
                <p>{!h ? 'Cargando…' : left >= 0 ? <>Restantes: <b>{left} kcal</b></> : <>Superaste tu meta por <b>{-left} kcal</b></>}</p>
                <div className={s.barDark}><i style={{ width: `${Math.min((total / (h?.meta_kcal || 1)) * 100, 100)}%` }} /></div>
              </div>
            </section>

            {h?.macros && (
              <section className={s.card} aria-label="Macros">
                <h2>Macros</h2>
                {[['p', 'Proteínas', <Drumstick size={20} aria-hidden="true" />], ['c', 'Carbohidratos', <Wheat size={20} aria-hidden="true" />], ['g', 'Grasas', <Droplet size={20} aria-hidden="true" />]].map(([k, n, ic]) => (
                  <div className={s.macro} key={k}>
                    <span className={s.macroIco} aria-hidden="true">{ic}</span><span>{n}</span>
                    <span>{h.macros.consumido[k]} g / {h.macros.meta[k]} g</span>
                    <div className={s.bar}><i style={{ width: `${Math.min((h.macros.consumido[k] / h.macros.meta[k]) * 100, 100)}%` }} /></div>
                  </div>
                ))}
              </section>
            )}
          </div>

          <section className={s.card} aria-label="Comidas de hoy">
            <div className={s.rowBetween}><h2><Utensils size={20} aria-hidden="true" /> Comidas de hoy</h2><Link className={s.link} to="/historial">Ver todas <ArrowRight size={20} aria-hidden="true" /></Link></div>
            {h && h.comidas.length === 0 && <p className={s.muted}>Aún no registras comidas hoy.</p>}
            <ul className={s.meals}>
              {h?.comidas.map((c) => (
                <li key={c.id}>
                  <Link className={s.meal} to={`/comidas/${c.id}`}>
                    <ImgSlot src={c.foto} w={64} h={52} label="Foto" alt={`Foto de ${c.nombre}`} />
                    <span className={s.mealTxt}>
                      {c.consumida_at && <small>{tipoComida(c.consumida_at)}</small>}
                      <b>{c.nombre}</b>
                      <small>{c.kcal} kcal{c.macros && <>   P {c.macros.p} g   C {c.macros.c} g   G {c.macros.g} g</>}</small>
                    </span>
                    <time>{c.consumida_at ? new Date(c.consumida_at).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }) : c.hora}</time>
                    <span aria-hidden="true"><ChevronRight size={20} aria-hidden="true" /></span>
                  </Link>
                </li>
              ))}
            </ul>
            <div className={s.actions}>
              <Link className={s.primary} to="/comidas/nueva"><b><Plus size={20} aria-hidden="true" /> Registrar comida</b><small>Añade lo que comiste con una foto o de forma manual</small></Link>
              <Link className={s.ghost} to="/comidas/nueva/foto"><b><Camera size={20} aria-hidden="true" /> Escanear alimento</b><small>Usa la cámara para un registro rápido</small></Link>
            </div>
          </section>

          <div className={s.trio}>
            <div className={s.mini}>
              <span className={s.miniIco} aria-hidden="true"><Droplet size={20} aria-hidden="true" /></span>
              <div><b>Hidratación</b><small>{(agua / 1000).toFixed(1)} L de {(AGUA_META / 1000).toFixed(1)} L</small><div className={s.bar}><i style={{ width: `${(agua / AGUA_META) * 100}%` }} /></div></div>
              <button type="button" className={s.round} onClick={() => addAgua(250)} aria-label="Añadir 250 mililitros de agua"><Plus size={20} aria-hidden="true" /></button>
            </div>
            <div className={`${s.mini} ${s.soonCard}`} aria-disabled="true"><span className={s.miniIco} aria-hidden="true"><Footprints size={20} aria-hidden="true" /></span><div><b>Actividad</b><small>Próximamente</small></div></div>
            <div className={`${s.mini} ${s.soonCard}`} aria-disabled="true"><span className={s.miniIco} aria-hidden="true"><Dumbbell size={20} aria-hidden="true" /></span><div><b>Entrenamiento</b><small>Próximamente</small></div></div>
          </div>
        </div>

        <aside className={s.sideCol}>
          {o && (
            <section className={s.goal} aria-label="Tu objetivo">
              <div className={s.goalHead}><span aria-hidden="true"><Target size={20} aria-hidden="true" /></span><div><small>Tu objetivo</small><h2>{o.tipo}</h2></div><button type="button" className={s.edit} disabled aria-label="Editar objetivo (próximamente)"><Pencil size={20} aria-hidden="true" /></button></div>
              <div className={s.goalNums}><div><small>Meta de peso</small><b>{o.peso_meta} kg</b></div><div><small>Peso actual</small><b>{o.peso_actual} kg</b></div></div>
              <div><small>Progreso</small><div className={s.barLight}><i style={{ width: `${progreso * 100}%` }} /></div><b className={s.goalDelta}>{(o.peso_actual - o.peso_inicial).toFixed(0)} kg</b></div>
            </section>
          )}

          {semana && (
            <section className={`${s.card} ${s.dark}`} aria-label="Progreso semanal">
              <div className={s.rowBetween}><h2><TrendingDown size={20} aria-hidden="true" /> Tu progreso semanal</h2>{delta && <span className={s.pill}>{delta} kg {Number(delta) <= 0 ? <ArrowDown size={20} aria-hidden="true" /> : <ArrowUp size={20} aria-hidden="true" />}</span>}</div>
              <Chart data={semana} />
            </section>
          )}

          <section className={`${s.card} ${s.tips}`} aria-label="Consejos de hoy">
            <h2><Lightbulb size={20} aria-hidden="true" /> Consejos de hoy</h2>
            <div className={s.tipBody}>
              <button type="button" onClick={() => setTip((t) => (t + TIPS.length - 1) % TIPS.length)} aria-label="Consejo anterior"><ChevronLeft size={20} aria-hidden="true" /></button>
              <p aria-live="polite">{TIPS[tip]}</p>
              <button type="button" onClick={() => setTip((t) => (t + 1) % TIPS.length)} aria-label="Consejo siguiente"><ChevronRight size={20} aria-hidden="true" /></button>
            </div>
            <div className={s.dots}>{TIPS.map((_, i) => <i key={i} className={i === tip ? s.dotOn : ''} />)}</div>
          </section>

          <section className={`${s.card} ${s.dark} ${s.motto}`}>
            <p>Disciplina hoy, resultados mañana.</p>
            <ImgSlot className={s.mascot} src={IMG.mascotaLema} w={150} h={110} label="Panda lema" alt="" />
          </section>
        </aside>
      </div>
    </main>
  )
}

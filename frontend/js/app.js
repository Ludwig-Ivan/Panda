// Datos de ejemplo: reemplazar por la API / base de datos cuando esté lista.
const state = {
  meta: 1800,
  macrosMeta: { p: 135, c: 180, g: 60 },
  pesoInicial: 114, pesoActual: 108, pesoMeta: 100,
  semana: [{d:'Lun',v:110.4},{d:'Mar',v:109.9},{d:'Mié',v:109.3},{d:'Jue',v:108.9},{d:'Vie',v:108.4},{d:'Sáb',v:108.1},{d:'Dom',v:108}],
  agua: 1200, aguaMeta: 2500,
  meals: [
    { tipo:'Desayuno', nombre:'Avena con plátano y chía', kcal:318, p:12, c:52, g:8, hora:'08:12 a. m.', e:'🥣' },
    { tipo:'Comida', nombre:'Bowl de pollo con arroz, aguacate y verduras', kcal:432, p:45, c:48, g:12, hora:'01:45 p. m.', e:'🥗' },
    { tipo:'Cena', nombre:'Yogur griego con frutos rojos y nueces', kcal:192, p:20, c:14, g:7, hora:'08:20 p. m.', e:'🍓' }
  ],
  tips: [
    'Mantén una buena hidratación. El agua te ayuda a sentirte más lleno, mejora tu rendimiento y acelera tu metabolismo.',
    'Prioriza la proteína en cada comida: ayuda a conservar músculo mientras pierdes grasa.',
    'Pésate a la misma hora y compara el promedio semanal, no el día a día.',
    'Dormir 7–8 horas regula el hambre y mejora tus resultados.'
  ]
};

const $ = (id) => document.getElementById(id);
const sum = (k) => state.meals.reduce((a, m) => a + m[k], 0);
const toast = (t) => { const el = $('toast'); el.textContent = t; el.classList.add('show'); clearTimeout(el._t); el._t = setTimeout(() => el.classList.remove('show'), 2200); };

// Navegación (escritorio y móvil)
const items = [['🏠','Inicio'],['🍴','Comidas'],['＋','Registro rápido'],['📊','Progreso'],['👨‍🍳','Recetas'],['📖','Biblioteca de alimentos'],['⚙️','Ajustes']];
$('nav').innerHTML = items.map((x, i) => `<a href="#" class="${i === 0 ? 'on' : ''}"><span>${x[0]}</span>${x[1]}</a>`).join('');
const tabs = [['🏠','Inicio'],['🍴','Comidas'],['＋',''],['📊','Progreso'],['👤','Perfil']];
$('tabbar').innerHTML = tabs.map((x, i) => i === 2 ? `<a href="#" class="fab" id="fab" aria-label="Registrar comida">＋</a>` : `<a href="#" class="${i === 0 ? 'on' : ''}"><span>${x[0]}</span>${x[1]}</a>`).join('');
document.querySelectorAll('#nav a, #tabbar a:not(.fab)').forEach(a => a.addEventListener('click', e => {
  e.preventDefault();
  a.parentElement.querySelectorAll('a').forEach(n => n.classList.remove('on'));
  a.classList.add('on');
  if (!a.textContent.includes('Inicio')) toast('Vista en construcción (preview)');
}));

// Fecha
const f = new Date().toLocaleDateString('es-MX', { weekday:'short', day:'numeric', month:'short', year:'numeric' });
$('fecha').textContent = f.charAt(0).toUpperCase() + f.slice(1);

// Calorías y macros
function renderTotals() {
  const kcal = sum('kcal'), left = Math.max(state.meta - kcal, 0);
  $('kcalConsumed').textContent = kcal;
  $('kcalOf').textContent = `de ${state.meta.toLocaleString('es-MX')}`;
  $('kcalLeft').textContent = `${left} kcal`;
  $('kcalBar').style.width = Math.min(kcal / state.meta * 100, 100) + '%';
  $('ringFill').style.strokeDashoffset = 326.7 * (1 - Math.min(kcal / state.meta, 1));
  const defs = [['p','Proteínas','🌿'],['c','Carbohidratos','🌾'],['g','Grasas','💧']];
  $('macros').innerHTML = defs.map(([k, n, ic]) => {
    const v = sum(k), m = state.macrosMeta[k];
    return `<div class="macro"><span class="mi">${ic}</span><span>${n}</span><span>${v} g / ${m} g</span><div class="bar"><i style="width:${Math.min(v / m * 100, 100)}%"></i></div></div>`;
  }).join('');
}

function renderMeals() {
  $('mealList').innerHTML = state.meals.map(m => `
    <li class="meal"><div class="thumb">${m.e}</div>
      <div><small class="t">${m.tipo}</small><b>${m.nombre}</b><small>${m.kcal} kcal · P ${m.p} g · C ${m.c} g · G ${m.g} g</small></div>
      <time>${m.hora}</time></li>`).join('');
}

// Objetivo
function renderGoal() {
  const perdido = state.pesoInicial - state.pesoActual, total = state.pesoInicial - state.pesoMeta;
  $('pesoActual').textContent = state.pesoActual + ' kg';
  $('goalBar').style.width = (perdido / total * 100) + '%';
  $('goalTxt').textContent = `-${perdido} kg`;
}

// Gráfica semanal (SVG propio, sin librerías)
function renderChart() {
  const d = state.semana, W = 320, H = 170, L = 30, R = 12, T = 12, B = 28;
  const min = 100, max = 120;
  const x = i => L + i * (W - L - R) / (d.length - 1);
  const y = v => T + (max - v) / (max - min) * (H - T - B);
  const pts = d.map((p, i) => `${x(i)},${y(p.v)}`).join(' ');
  let s = [120, 110, 100].map(g => `<line x1="${L}" x2="${W - R}" y1="${y(g)}" y2="${y(g)}" stroke="#2e2622"/><text x="2" y="${y(g) + 3}">${g}</text>`).join('');
  s += `<polygon points="${x(0)},${H - B} ${pts} ${x(d.length - 1)},${H - B}" fill="#f9731622"/>`;
  s += `<polyline points="${pts}" fill="none" stroke="#f97316" stroke-width="2"/>`;
  s += d.map((p, i) => `<circle cx="${x(i)}" cy="${y(p.v)}" r="3.5" fill="#f97316"><title>${p.d}: ${p.v} kg</title></circle><text x="${x(i) - 8}" y="${H - 8}">${p.d}</text>`).join('');
  $('chart').innerHTML = s;
  $('weekDelta').textContent = `${(d[d.length - 1].v - d[0].v).toFixed(1)} kg ↓`;
}

// Hidratación
function renderAgua() {
  $('hidTxt').textContent = `${(state.agua / 1000).toFixed(1)} L de ${(state.aguaMeta / 1000).toFixed(1)} L`;
  $('hidBar').style.width = Math.min(state.agua / state.aguaMeta * 100, 100) + '%';
}
$('hidAdd').onclick = () => { state.agua = Math.min(state.agua + 250, state.aguaMeta); renderAgua(); toast('+250 ml de agua'); };

// Consejos
let tip = 0;
function renderTip() {
  $('tipText').textContent = state.tips[tip];
  $('tipDots').innerHTML = state.tips.map((_, i) => `<i class="${i === tip ? 'on' : ''}"></i>`).join('');
}
$('tipPrev').onclick = () => { tip = (tip + state.tips.length - 1) % state.tips.length; renderTip(); };
$('tipNext').onclick = () => { tip = (tip + 1) % state.tips.length; renderTip(); };

// Registrar comida
const dlg = $('mealDialog');
const abrir = () => dlg.showModal();
['btnRegistrar', 'fab'].forEach(id => $(id) && $(id).addEventListener('click', e => { e.preventDefault(); abrir(); }));
$('cancelar').onclick = () => dlg.close();
$('btnEscanear').onclick = () => toast('Escáner disponible cuando conectemos la base de datos');
$('verTodas').onclick = () => toast('Vista de comidas en construcción');
$('mealForm').addEventListener('submit', () => {
  const d = Object.fromEntries(new FormData($('mealForm')));
  state.meals.push({ tipo: d.tipo, nombre: d.nombre, kcal: +d.kcal, p: +d.p, c: +d.c, g: +d.g,
    hora: new Date().toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' }), e: '🍽️' });
  $('mealForm').reset(); renderAll(); toast('Comida registrada');
});

function renderAll() { renderTotals(); renderMeals(); renderGoal(); renderChart(); renderAgua(); renderTip(); }
renderAll();

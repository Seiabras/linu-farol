// O contador de visitas do Linu Farol (11/11/2026), sem cookie e sem guardar quem visitou. O site do cliente carrega
// https://farol.linupedia.com.br/v.js, que manda um aviso curto a cada página aberta para /api/visita; o Caddy do
// Farol encaminha para cá. O painel (ferramentas/painel.py, no Actions) lê os totais do mês em /api/visitas, com a chave.
//
// Como conta pessoas sem cookie: cada aviso vira um resumo (sha256) de sal do dia + site + IP + navegador. O sal é
// sorteado a cada dia e apagado no dia seguinte, junto com os resumos; depois disso não há como saber quem foi. O IP e o
// navegador nunca são gravados. "Pessoas" do mês = a soma das pessoas de cada dia (quem volta em outro dia conta de
// novo: é o que dá para saber sem guardar nada por mais de um dia).
//
// Só conta site que o painel pediu nos últimos 60 dias (o painel pede a cada ronda, de 6 em 6 horas): cliente novo
// começa a contar na ronda seguinte ao cadastro, e ninguém de fora enche o disco. Sem dependências: Node 24.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const PORTA = Number(process.env.PORTA || 8095);
const DADOS = process.env.DADOS || '/opt/linu-visitas/dados';
const CHAVE = process.env.CHAVE_LEITURA || '';
const TOTAIS = path.join(DADOS, 'visitas.json');
const HOJE = path.join(DADOS, 'hoje.json');
const PEDIDOS = path.join(DADOS, 'sites.json');
const GUARDAR_MESES = 25;
const SITE_VALE_DIAS = 60;
const MAX_PAGINAS = 300;
const ROBO = /bot|crawl|spider|slurp|preview|headless|lighthouse|pingdom|uptime|monitor|curl|wget|python|node-fetch|axios|go-http|java\/|facebookexternalhit|whatsapp|telegram|discord|linkedin/i;

fs.mkdirSync(DADOS, { recursive: true });
const ler = (f, padrao) => { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch { return padrao; } };
function gravar(f, d) {
  fs.writeFileSync(f + '.novo', JSON.stringify(d), { mode: 0o600 });
  fs.renameSync(f + '.novo', f);
}

// o dia e o mês de Brasília
function agoraBR() {
  const s = new Date(Date.now() - 3 * 3600_000).toISOString();
  return { dia: s.slice(0, 10), mes: s.slice(0, 7), d: s.slice(8, 10) };
}

let totais = ler(TOTAIS, {});
let sites = ler(PEDIDOS, {});
let hoje = ler(HOJE, null);
let vistos = new Set();
function virarDia() {
  const { dia } = agoraBR();
  if (hoje && hoje.dia === dia) return;
  hoje = { dia, sal: crypto.randomBytes(32).toString('hex'), vistos: [] };
  vistos = new Set();
  gravar(HOJE, hoje);
  // apaga os meses velhos e os sites que o painel deixou de pedir
  const limite = new Date(Date.now() - 3 * 3600_000);
  limite.setUTCMonth(limite.getUTCMonth() - GUARDAR_MESES);
  const corte = limite.toISOString().slice(0, 7);
  for (const host of Object.keys(totais)) {
    for (const mes of Object.keys(totais[host])) if (mes < corte) delete totais[host][mes];
    if (!Object.keys(totais[host]).length) delete totais[host];
  }
  for (const [host, quando] of Object.entries(sites)) if (Date.now() - quando > SITE_VALE_DIAS * 86400_000) delete sites[host];
  gravar(PEDIDOS, sites);
  sujo = true;
}
if (hoje) vistos = new Set(hoje.vistos);
let sujo = false;
virarDia();
setInterval(virarDia, 60_000).unref();
setInterval(() => {
  if (!sujo) return;
  gravar(TOTAIS, totais);
  hoje.vistos = [...vistos];
  gravar(HOJE, hoje);
  sujo = false;
}, 30_000).unref();
for (const sinal of ['SIGTERM', 'SIGINT']) process.on(sinal, () => {
  if (sujo) { gravar(TOTAIS, totais); hoje.vistos = [...vistos]; gravar(HOJE, hoje); }
  process.exit(0);
});

// limite por IP: 300 avisos por hora, só na memória
const vezes = new Map();
function demais(ip) {
  const agora = Date.now();
  const l = (vezes.get(ip) || []).filter((t) => agora - t < 3600_000);
  l.push(agora);
  vezes.set(ip, l);
  return l.length > 300;
}
setInterval(() => { const a = Date.now(); for (const [ip, l] of vezes) if (!l.some((t) => a - t < 3600_000)) vezes.delete(ip); }, 600_000).unref();

const semWww = (h) => String(h || '').toLowerCase().replace(/^www\./, '').split(':')[0];
function hostDe(url) {
  const t = String(url || '').trim();
  if (!t) return '';
  try { return semWww(new URL(/^[a-z][a-z0-9+.-]*:\/\//i.test(t) ? t : `https://${t}`).hostname); } catch { return ''; }
}

// de onde veio: a busca, as redes, outro site, ou ninguém (digitou, favorito, WhatsApp, que não manda a origem)
export function origem(ref, utm, host) {
  const u = String(utm || '').toLowerCase();
  const r = hostDe(ref);
  const de = u || r;
  if (!de || r === host) return u ? classificar(u) : 'Direto ou WhatsApp';
  return classificar(de);
}
function classificar(de) {
  if (/google|bing|duckduckgo|yahoo|ecosia|brave|yandex/.test(de)) return 'Busca (Google e outros)';
  if (/instagram/.test(de)) return 'Instagram';
  if (/facebook|fb\.|^fb$|meta/.test(de)) return 'Facebook';
  if (/whatsapp|wa\.me/.test(de)) return 'Direto ou WhatsApp';
  if (/tiktok/.test(de)) return 'TikTok';
  if (/youtube|youtu\.be/.test(de)) return 'YouTube';
  if (/linkedin|lnkd/.test(de)) return 'LinkedIn';
  if (/t\.co$|twitter|^x\.com/.test(de)) return 'X (Twitter)';
  return 'Outros sites';
}
export function caminho(p) {
  let c = String(p || '/').split(/[?#]/)[0].replace(/\/+$/, '').replace(/\/index\.html?$/, '') || '/';
  try { c = decodeURIComponent(c); } catch { /* fica como veio */ }
  return c.replace(/[\u0000-\u001F\u007F]/g, '').slice(0, 120) || '/';
}

function contar(host, d, ip, ua) {
  const { mes, d: diaDoMes } = agoraBR();
  const m = ((totais[host] ||= {})[mes] ||= { pessoas: 0, vistas: 0, dias: {}, origens: {}, paginas: {} });
  const dia = (m.dias[diaDoMes] ||= { p: 0, v: 0 });
  const quem = crypto.createHash('sha256').update(`${hoje.sal}|${host}|${ip}|${ua}`).digest('hex').slice(0, 20);
  m.vistas++; dia.v++;
  const nova = !vistos.has(quem);
  if (nova) {
    vistos.add(quem);
    m.pessoas++; dia.p++;
    const o = origem(d.r, d.u, host);   // a origem conta uma vez por pessoa no dia: a primeira página que abriu
    m.origens[o] = (m.origens[o] || 0) + 1;
  }
  let p = caminho(d.p);
  if (!(p in m.paginas) && Object.keys(m.paginas).length >= MAX_PAGINAS) p = '(outras)';
  m.paginas[p] = (m.paginas[p] || 0) + 1;
  sujo = true;
}

const ordenar = (o, n) => Object.entries(o || {}).sort((a, b) => b[1] - a[1]).slice(0, n);
function iguais(a, b) {
  const x = Buffer.from(String(a)), y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
}

const servidor = http.createServer((req, res) => {
  const fim = (codigo, corpo = '', tipo = 'text/plain') => {
    res.writeHead(codigo, { 'content-type': `${tipo}; charset=utf-8`, 'cache-control': 'no-store' });
    res.end(corpo);
  };
  const url = new URL(req.url, 'http://x');
  if (req.method === 'GET' && url.pathname === '/api/visita') return fim(200, 'ok');

  // o painel lê os totais: GET /api/visitas?site=cafe.linupedia.com.br, com "Authorization: Bearer <chave>"
  if (req.method === 'GET' && url.pathname === '/api/visitas') {
    if (!CHAVE || !iguais(String(req.headers.authorization || ''), `Bearer ${CHAVE}`)) return fim(401);
    const host = semWww(url.searchParams.get('site'));
    if (!/^[a-z0-9.-]{3,120}$/.test(host)) return fim(400);
    if (!sites[host]) { sites[host] = Date.now(); gravar(PEDIDOS, sites); } else sites[host] = Date.now();
    const meses = Object.fromEntries(Object.entries(totais[host] || {}).map(([mes, m]) => [mes, {
      pessoas: m.pessoas, vistas: m.vistas, dias: m.dias,
      origens: ordenar(m.origens, 6), paginas: ordenar(m.paginas, 8),
    }]));
    return fim(200, JSON.stringify({ site: host, desde: sites[host], meses }), 'application/json');
  }

  if (req.method !== 'POST' || url.pathname !== '/api/visita') return fim(404);
  const host = hostDe(req.headers.origin);
  const ua = String(req.headers['user-agent'] || '');
  if (!host || !sites[host] || ROBO.test(ua) || ua.length < 20) return fim(204);
  const ip = String(req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  if (demais(ip)) return fim(429);
  let corpo = '';
  req.setEncoding('utf8');
  req.on('data', (c) => { corpo += c; if (corpo.length > 2048) req.destroy(); });
  req.on('end', () => {
    let d;
    try { d = JSON.parse(corpo); } catch { return fim(400); }
    if (typeof d !== 'object' || !d) return fim(400);
    contar(host, d, ip, ua);
    fim(204);
  });
});
if (process.argv[1] && import.meta.url.endsWith(path.basename(process.argv[1]))) {
  servidor.listen(PORTA, '127.0.0.1', () => console.log(`linu-visitas em 127.0.0.1:${PORTA}`));
}

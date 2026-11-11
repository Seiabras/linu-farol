// Teste do linu-visitas: sobe o servidor numa pasta temporária, manda avisos e confere os totais. node teste.mjs
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';

const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'linu-visitas-'));
const PORTA = 18000 + Math.floor(Math.random() * 1000);
const base = `http://127.0.0.1:${PORTA}`;
const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36';
const subir = () => spawn(process.execPath, ['servidor.mjs'], { env: { ...process.env, DADOS: pasta, PORTA, CHAVE_LEITURA: 'k'.repeat(40) }, stdio: 'ignore' });
const esperar = async () => { for (let i = 0; i < 50; i++) { try { await fetch(`${base}/api/visita`); return; } catch { await new Promise((r) => setTimeout(r, 100)); } } throw new Error('não subiu'); };
const aviso = (origin, ip, corpo, ua = UA) => fetch(`${base}/api/visita`, { method: 'POST', headers: { origin, 'user-agent': ua, 'x-forwarded-for': ip, 'content-type': 'text/plain' }, body: typeof corpo === 'string' ? corpo : JSON.stringify(corpo) }).then((r) => r.status);
const ler = (chave = 'k'.repeat(40)) => fetch(`${base}/api/visitas?site=cafe.linupedia.com.br`, { headers: { authorization: `Bearer ${chave}` } });

let filho = subir();
try {
  await esperar();
  const C = 'https://cafe.linupedia.com.br';
  assert.equal(await aviso(C, '1.1.1.1', { p: '/' }), 204);
  assert.equal((await ler('errada'.repeat(7))).status, 401);
  let r = await (await ler()).json();
  assert.deepEqual(r.meses, {}, 'antes de o painel pedir, não conta');
  assert.equal(await aviso(C, '1.1.1.1', { p: '/', r: 'www.google.com' }), 204);
  await aviso(C, '1.1.1.1', { p: '/cardapio/?x=1', r: 'cafe.linupedia.com.br' });
  await aviso(C, '2.2.2.2', { p: '/', r: 'l.instagram.com' });
  await aviso(C, '3.3.3.3', { p: '/index.html', r: '' });
  await aviso('https://www.cafe.linupedia.com.br', '4.4.4.4', { p: '/', u: 'instagram' });
  await aviso(C, '5.5.5.5', { p: '/' }, 'Googlebot/2.1 (+http://www.google.com/bot.html)');
  await aviso('https://outro.com', '6.6.6.6', { p: '/' });
  assert.equal(await aviso(C, '7.7.7.7', 'nao-json'), 400);
  r = await (await ler()).json();
  const [m] = Object.values(r.meses);
  assert.equal(m.pessoas, 4); assert.equal(m.vistas, 5);
  assert.deepEqual(Object.fromEntries(m.origens), { 'Busca (Google e outros)': 1, Instagram: 2, 'Direto ou WhatsApp': 1 });
  assert.deepEqual(Object.fromEntries(m.paginas), { '/': 4, '/cardapio': 1 });
  // depois de reiniciar, a mesma pessoa no mesmo dia não conta de novo
  await new Promise((res) => { filho.once('exit', res); filho.kill('SIGTERM'); });
  const salvo = fs.readFileSync(path.join(pasta, 'visitas.json'), 'utf8');
  assert.ok(!salvo.includes('1.1.1.1') && !salvo.includes('Chrome'), 'IP e navegador não ficam no disco');
  filho = subir(); await esperar();
  await aviso(C, '1.1.1.1', { p: '/' });
  r = await (await ler()).json();
  assert.equal(Object.values(r.meses)[0].pessoas, 4);
  console.log('linu-visitas: tudo certo');
} finally {
  filho.kill('SIGTERM');
  fs.rmSync(pasta, { recursive: true, force: true });
}

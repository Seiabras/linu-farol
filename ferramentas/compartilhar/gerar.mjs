// Gera img/compartilhar.png (1200 × 630) do Linu Farol a partir de imagem.html (o molde da Família Linu), abaixo de 300 KB (senão o WhatsApp não
// mostra). O Playwright não é dependência do site: passe a pasta dele ou deixe a ferramenta procurar.
// Uso: node ferramentas/compartilhar/gerar.mjs [pasta/do/node_modules/playwright]
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';

const aqui = path.dirname(new URL(import.meta.url).pathname);
const projetos = path.join(os.homedir(), 'Documentos', 'projetos');
const candidatos = [process.argv[2], process.env.PLAYWRIGHT_DIR,
  ...(fs.existsSync(projetos) ? fs.readdirSync(projetos).map((p) => path.join(projetos, p, 'node_modules', 'playwright')) : [])].filter(Boolean);
const achado = candidatos.find((c) => fs.existsSync(path.join(c, 'package.json')));
if (!achado) { console.error('Playwright não encontrado: passe a pasta (…/node_modules/playwright).'); process.exit(1); }
const { chromium } = createRequire(import.meta.url)(achado);
const saida = path.join(aqui, '../../img/compartilhar.png');
const nav = await chromium.launch();
const pg = await nav.newPage({ viewport: { width: 1200, height: 630 } });
await pg.goto('file://' + path.join(aqui, 'imagem.html'));
await pg.evaluate(() => document.fonts.ready);
await pg.screenshot({ path: saida, type: 'png' });
await nav.close();
const kb = Math.round(fs.statSync(saida).size / 1024);
console.log(`img/compartilhar.png: ${kb} KB${kb >= 300 ? ' (passou de 300 KB: simplifique a imagem)' : ''}`);

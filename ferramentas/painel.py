"""O painel de cada cliente do Linu Farol (07/11/2026): uma página por cliente, num endereço só dele.

    python3 ferramentas/painel.py [--anterior https://farol.linupedia.com.br] [--sem-rede]
    python3 ferramentas/painel.py --novo-codigo

De onde vêm os clientes:
  - ferramentas/painel-exemplo.json: o painel de exemplo (/p/exemplo/), sempre;
  - a variável FAROL_CLIENTES (o segredo de mesmo nome no GitHub, no Actions) ou o arquivo dados/clientes.json (fora do
    git), com o mesmo formato. O repositório é público: nome, site e números de cliente nunca entram nele.

Para cada cliente, faz a ronda do site (as mesmas quatro luzes da lista, do ferramentas/ronda.py), junta com o
histórico publicado (p/<código>/ronda.json, lido de --anterior; até 120 rondas, 30 dias) e escreve p/<código>/index.html
e p/<código>/ronda.json. Os números do mês (visitas, Google, Instagram) e o rumo vêm do cadastro, lançados à mão todo
mês. --sem-rede não faz a ronda (usa só o histórico; para olhar o visual no computador).
--novo-codigo sorteia o código de um cliente novo (o endereço é https://farol.linupedia.com.br/p/<código>/).
"""
import datetime
import html
import json
import os
import re
import secrets
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ronda import LUZES, baixar, rondar  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
GUARDAR = 120
BRASILIA = datetime.timezone(datetime.timedelta(hours=-3))
MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro',
         'novembro', 'dezembro']
PLANOS = {'site': 'Farol do site', 'completo': 'Farol completo', 'avulsa': 'Ronda avulsa'}
WHATS = 'https://wa.me/5561996672610?text='
e = html.escape


def ler_clientes():
    clientes = json.loads((RAIZ / 'ferramentas' / 'painel-exemplo.json').read_text(encoding='utf-8'))['clientes']
    texto = os.environ.get('FAROL_CLIENTES', '').strip()
    local = RAIZ / 'dados' / 'clientes.json'
    if not texto and local.exists():
        texto = local.read_text(encoding='utf-8')
    if texto:
        clientes += json.loads(texto)['clientes']
    for c in clientes:
        if not re.fullmatch(r'[A-Za-z0-9_-]{6,64}', c['codigo']):
            sys.exit(f'código inválido para {c["nome"]}: use --novo-codigo')
    if len({c['codigo'] for c in clientes}) != len(clientes):
        sys.exit('dois clientes com o mesmo código')
    return clientes


def ler_anterior(base, codigo):
    local = RAIZ / 'p' / codigo / 'ronda.json'
    try:
        if base:
            return json.loads(baixar(f'{base.rstrip("/")}/p/{codigo}/ronda.json')[2].decode('utf-8'))
        if local.exists():
            return json.loads(local.read_text(encoding='utf-8'))
    except Exception as erro:
        print(f'{codigo}: sem o histórico anterior ({erro.__class__.__name__}), começa agora')
    return {}


def nome_mes(chave, ano=True):
    a, m = chave.split('-')
    return f'{MESES[int(m) - 1]} de {a}' if ano else MESES[int(m) - 1]


def numero(n):
    return f'{n:,}'.replace(',', '.')


def variacao(agora, antes, mes_antes):
    if not antes:
        return ''
    d = round((agora - antes) / antes * 100)
    if d == 0:
        return f'<p class="mes-variacao">igual a {e(mes_antes)}</p>'
    lado = 'sobe' if d > 0 else 'desce'
    seta = '↑' if d > 0 else '↓'
    return f'<p class="mes-variacao mes-{lado}"><span aria-hidden="true">{seta}</span> {abs(d)}% {"a mais" if d > 0 else "a menos"} que em {e(mes_antes)}</p>'


def barras(titulo, linhas):
    if not linhas:
        return ''
    maior = max(v for _, v in linhas) or 1
    itens = ''.join(
        f'<li><span class="barra-nome">{e(n)}</span><span class="barra-valor">{numero(v)}</span>'
        f'<svg class="barra" viewBox="0 0 100 6" preserveAspectRatio="none" aria-hidden="true"><rect width="100" height="6" class="barra-fundo"/>'
        f'<rect width="{max(2, round(v / maior * 100))}" height="6" class="barra-cheia"/></svg></li>' for n, v in linhas)
    return f'<h4>{e(titulo)}</h4><ul class="barras">{itens}</ul>'


def cartao(icone, titulo, grande, rotulo, var, resto=''):
    return (f'<article class="mes-cartao"><h3><svg class="icone" aria-hidden="true"><use href="#{icone}"/></svg>{titulo}</h3>'
            f'<p class="mes-grande"><b>{grande}</b> <span>{rotulo}</span></p>{var}{resto}</article>')


def secao_mes(c):
    if c['plano'] == 'site':
        return ('<section class="painel-secao" id="mes" aria-labelledby="mes-titulo"><h2 id="mes-titulo">O mês</h2>'
                '<p class="secao-sub">No Farol do site, o painel são as quatro luzes e o histórico. As visitas, o Google e o '
                'Instagram do mês entram no <a href="/#planos">Farol completo</a>.</p></section>')
    meses = sorted(c.get('meses', []), key=lambda m: m['mes'])
    if not meses:
        return ('<section class="painel-secao" id="mes" aria-labelledby="mes-titulo"><h2 id="mes-titulo">O mês</h2>'
                '<p class="secao-sub">Os números do primeiro mês (visitas, Google e Instagram) entram aqui até o dia 5 do mês '
                'que vem, com o rumo.</p></section>')
    m = meses[-1]
    a = meses[-2] if len(meses) > 1 else {}
    antes = nome_mes(a['mes'], False) if a else ''
    cartoes = []
    v, va = m.get('visitas'), a.get('visitas', {})
    if v:
        cartoes.append(cartao('i-visitas', 'Visitas do site', numero(v['pessoas']), 'pessoas',
                              variacao(v['pessoas'], va.get('pessoas'), antes),
                              barras('De onde vieram', v.get('origens')) + barras('O que mais abriram', v.get('paginas'))))
    g, ga = m.get('google'), a.get('google', {})
    if g:
        extra = (f'<dl class="mes-miudos"><div><dt>Ligações</dt><dd>{numero(g.get("ligacoes", 0))}</dd></div>'
                 f'<div><dt>Pedidos de rota</dt><dd>{numero(g.get("rotas", 0))}</dd></div>'
                 f'<div><dt>Cliques no site</dt><dd>{numero(g.get("site", 0))}</dd></div></dl>')
        cartoes.append(cartao('i-mapa', 'Google e Maps', numero(g['aparicoes']), 'vezes que o negócio apareceu',
                              variacao(g['aparicoes'], ga.get('aparicoes'), antes), extra))
    i, ia = m.get('instagram'), a.get('instagram', {})
    if i:
        extra = (f'<dl class="mes-miudos"><div><dt>Seguidores novos</dt><dd>{numero(i.get("seguidores_novos", 0))}</dd></div>'
                 f'<div><dt>Publicações</dt><dd>{numero(i.get("posts", 0))}</dd></div></dl>')
        cartoes.append(cartao('i-camera', 'Instagram', numero(i['alcance']), 'contas alcançadas',
                              variacao(i['alcance'], ia.get('alcance'), antes), extra))
    titulo = nome_mes(m['mes']).capitalize()
    return (f'<section class="painel-secao" id="mes" aria-labelledby="mes-titulo"><h2 id="mes-titulo">{e(titulo)}</h2>'
            f'<p class="secao-sub">O mês fechado, comparado com {e(antes) if antes else "o anterior quando houver"}.</p>'
            f'<div class="mes-cartoes">{"".join(cartoes)}</div></section>')


def secao_rumo(c):
    meses = sorted(c.get('meses', []), key=lambda m: m['mes'])
    rumo = meses[-1].get('rumo') if meses else None
    if not rumo:
        return ''
    itens = ''.join(f'<li>{e(r)}</li>' for r in rumo)
    return (f'<section class="painel-secao" id="rumo" aria-labelledby="rumo-titulo"><h2 id="rumo-titulo">O rumo</h2>'
            f'<p class="secao-sub">O que fazer neste mês, em ordem.</p><ol class="rumo">{itens}</ol></section>')


def secao_dias(hist):
    if not hist:
        return ''
    n = len(hist)
    no_ar = sum(1 for h in hist if h['luz'] == 'acesa')
    tempos = [h['ms'] for h in hist if h.get('ms')]
    pct = f'{no_ar / n * 100:.1f}'.replace('.', ',').replace(',0', '')
    dias = n * 6 // 24
    periodo = f'nos últimos {dias} dias' if dias >= 2 else 'desde o começo'
    resumo = f'No ar em {no_ar} de {n} rondas ({pct}%), {periodo}.'
    if tempos:
        resumo += f' Respondeu em {round(sum(tempos) / len(tempos))} ms em média; a vez mais lenta, {max(tempos)} ms.'
    largura = GUARDAR * 5
    rects = ''.join(f'<rect x="{largura - (n - k) * 5}" y="0" width="4" height="24" class="h-{h["luz"]}"/>' for k, h in enumerate(hist))
    falhas = [h for h in hist if h['luz'] != 'acesa']
    lista = ''
    if falhas:
        itens = ''.join(f'<li><time datetime="{h["q"]}">{datetime.datetime.fromisoformat(h["q"]).astimezone(BRASILIA):%d/%m, %H:%M}</time>: '
                        f'luz {e(h["luz"])}</li>' for h in falhas[-5:])
        lista = f'<h3 class="dias-falhas-titulo">Quando não estava tudo certo</h3><ul class="dias-falhas">{itens}</ul>'
    return (f'<section class="painel-secao" id="dias" aria-labelledby="dias-titulo"><h2 id="dias-titulo">Os últimos 30 dias</h2>'
            f'<p class="secao-sub">{e(resumo)}</p>'
            f'<figure class="dias"><svg class="dias-faixa" viewBox="0 0 {largura} 24" preserveAspectRatio="none" role="img" '
            f'aria-label="{e(resumo)}"><rect width="{largura}" height="24" class="h-vazio"/>{rects}</svg>'
            f'<figcaption><span>30 dias atrás</span><span class="dias-legenda"><i class="h-acesa"></i>no ar '
            f'<i class="h-fraca"></i>lento <i class="h-apagada"></i>fora</span><span>agora</span></figcaption></figure>{lista}</section>')


def pagina(c, r, hist, sprite, quando):
    acesas = sum(1 for k, _ in LUZES if r[k][0] == 'acesa')
    geral = 'acesa' if acesas == 4 else 'apagada' if r['luz'][0] == 'apagada' else 'fraca'
    hora = datetime.datetime.fromisoformat(quando).astimezone(BRASILIA)
    host = re.sub(r'^https?://', '', c['site']).rstrip('/')
    luzes = ''.join(f'<div class="luz luz-{r[k][0]}"><dt><span class="sinal sinal-{r[k][0]}" aria-hidden="true"></span>{rot} '
                    f'<span class="luz-estado">{r[k][0]}</span></dt><dd>{e(r[k][1])}</dd></div>' for k, rot in LUZES)
    desde = f'<div><dt>Desde</dt><dd>{e(nome_mes(c["desde"]))}</dd></div>' if c.get('desde') else ''
    aviso = ''
    if c.get('exemplo'):
        aviso = ('<p class="painel-aviso"><b>Painel de exemplo.</b> O Café Aurora é o site de demonstração do Linu Sites: '
                 'as luzes e os 30 dias são de verdade, conferidos de 6 em 6 horas; os números do mês e o rumo são inventados, '
                 'para mostrar como fica. <a href="/#planos">Ver os planos</a></p>')
    fala = WHATS + urllib.parse.quote(f'Olá! Sobre o painel do {c["nome"]} no Linu Farol: ')
    titulo = f'Painel de {c["nome"]} · Linu Farol'
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(titulo)}</title>
  <!-- O painel de um cliente (ferramentas/painel.py, refeito a cada ronda): endereço só dele, fora do Google -->
  <meta name="robots" content="noindex, nofollow">
  <meta name="referrer" content="no-referrer">
  <meta name="theme-color" content="#F4F7FA" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#06101F" media="(prefers-color-scheme: dark)">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' data:; font-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'">
  <link rel="icon" href="/img/icone-32.png" type="image/png" sizes="32x32">
  <link rel="preload" href="/fontes/big-shoulders-display-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fontes/public-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
  <script src="/js/tema-inicio.js"></script>
  <link rel="stylesheet" href="/css/fontes.css">
  <link rel="stylesheet" href="/css/estilo.css">
  <link rel="stylesheet" href="/css/painel.css">
  <script src="/js/painel.js" defer></script>
</head>
<body class="painel-pagina">
{sprite}
  <header class="topo">
    <div class="dentro topo-dentro">
      <a class="marca" href="/" aria-label="Linu Farol, início">
        <svg class="marca-icone" viewBox="0 0 24 24" width="30" height="30" aria-hidden="true"><use href="#i-farol"/></svg>
        <span>Linu Farol</span>
      </a>
      <span class="topo-painel">Painel de {e(c["nome"])}</span>
      <button class="tema" type="button" data-tema aria-label="Mudar o tema">
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path class="tema-sol" d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10ZM12 1.5v2M12 20.5v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1.5 12h2M20.5 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4"/><path class="tema-lua" d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z"/></svg>
      </button>
    </div>
  </header>

  <main id="conteudo" class="painel">
    <div class="dentro painel-dentro">
      {aviso}
      <aside class="painel-lado" aria-label="Resumo">
        <p class="sobretitulo">O painel do mês</p>
        <h1>{e(c["nome"])}</h1>
        <p class="painel-site"><a href="{e(c["site"])}" rel="noopener noreferrer">{e(host)}</a></p>
        <p class="painel-geral farol-{geral}"><span class="sinal sinal-{geral}" aria-hidden="true"></span><b>{acesas} de 4 luzes acesas</b>
          <span>Última ronda: <time datetime="{quando}">{hora:%d/%m/%Y, %H:%M}</time> (Brasília)</span></p>
        <dl class="painel-ficha">
          <div><dt>Plano</dt><dd>{e(PLANOS.get(c["plano"], c["plano"]))}</dd></div>{desde}
          <div><dt>Próxima ronda</dt><dd>em até 6 horas</dd></div>
        </dl>
        <img class="pixel painel-linu" src="/img/linu-luneta.png" alt="" width="124" height="198">
        <div class="botoes painel-botoes">
          <button class="botao" type="button" data-pdf>Salvar em PDF</button>
          <a class="botao botao-contorno" href="{fala}" target="_blank" rel="noopener">Falar sobre o painel</a>
        </div>
      </aside>
      <div class="painel-corpo">
        <section class="painel-secao" id="agora" aria-labelledby="agora-titulo">
          <h2 id="agora-titulo">As luzes agora</h2>
          <p class="secao-sub">O site olhado de fora, como um visitante: se abre, o cadeado, a rapidez e as trancas.</p>
          <dl class="luzes painel-luzes">{luzes}</dl>
        </section>
        {secao_dias(hist)}
        {secao_mes(c)}
        {secao_rumo(c)}
      </div>
    </div>
  </main>

  <!-- No celular, o resumo e o PDF ficam presos embaixo, ao alcance do polegar -->
  <aside class="barra-painel" aria-label="Resumo do painel">
    <span class="painel-geral-curto farol-{geral}"><span class="sinal sinal-{geral}" aria-hidden="true"></span>{acesas} de 4 acesas</span>
    <button class="botao" type="button" data-pdf>Salvar em PDF</button>
  </aside>

  <footer class="rodape">
    <div class="dentro rodape-dentro">
      <p><b>Linu Farol</b>: o painel do mês do seu negócio. Este endereço é só seu e não aparece no Google; quem tiver o
        link vê o painel, então compartilhe só com quem quiser. Para trocar o endereço: contato@linupedia.com.br.</p>
    </div>
  </footer>
</body>
</html>
'''


def sprite_da_pagina():
    t = (RAIZ / 'index.html').read_text(encoding='utf-8')
    a = t.index('<svg class="sprite"')
    return '  ' + t[a:t.index('</svg>', a) + 6]


def main():
    if '--novo-codigo' in sys.argv:
        print(secrets.token_urlsafe(12))
        return
    base = sys.argv[sys.argv.index('--anterior') + 1] if '--anterior' in sys.argv else None
    sem_rede = '--sem-rede' in sys.argv
    sprite = sprite_da_pagina()
    for c in ler_clientes():
        anterior = ler_anterior(base, c['codigo'])
        quando = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()
        if sem_rede and anterior.get('luzes'):
            r, quando, hist = anterior['luzes'], anterior['quando'], anterior.get('historico', [])
        else:
            r = rondar(c['nome'], c['site'], c.get('trecho', c['nome']))
            hist = (anterior.get('historico', []) + [{'q': quando, 'luz': r['luz'][0], 'ms': r.get('resposta_ms')}])[-GUARDAR:]
        pasta = RAIZ / 'p' / c['codigo']
        pasta.mkdir(parents=True, exist_ok=True)
        luzes = {k: list(r[k]) for k, _ in LUZES}
        (pasta / 'ronda.json').write_text(json.dumps({'quando': quando, 'luzes': luzes, 'historico': hist}, ensure_ascii=False) + '\n', encoding='utf-8')
        html_ = '\n'.join(l.rstrip() for l in pagina(c, luzes, hist, sprite, quando).split('\n') if l.strip()) + '\n'
        (pasta / 'index.html').write_text(html_, encoding='utf-8')
        nome = c['nome'] if c.get('exemplo') else c['codigo'][:4] + '…'  # o log do Actions é público
        print(f'painel {nome}: ' + ' · '.join(f'{rot} {r[k][0]}' for k, rot in LUZES))


if __name__ == '__main__':
    main()

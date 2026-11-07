"""A ronda do Linu Farol (07/11/2026): confere as quatro luzes de cada site e escreve a lista de faróis.

    python3 ferramentas/ronda.py [--anterior URL-ou-arquivo] [--conferir]

As luzes de cada site:
  - Luz:      o site abre (200) e é o site certo (um trecho do título), e em quanto tempo responde;
  - Cadeado:  quantos dias faltam para o certificado HTTPS vencer (os da família renovam sozinhos a cada poucos dias);
  - Rapidez:  o tempo de resposta e o peso da primeira visita (a página e o que ela carrega do próprio site);
  - Trancas:  os 6 cabeçalhos de segurança (HSTS, CSP, nosniff, referrer, quadro, permissões).
Cada luz fica "acesa" (tudo certo), "fraca" (vale olhar) ou "apagada" (problema).

Escreve dados/ronda.json (com o histórico das últimas 120 rondas de cada site, lido de --anterior) e o bloco da lista
no index.html, entre <!-- ronda:inicio --> e <!-- ronda:fim -->, para a lista aparecer sem JavaScript. No Actions,
roda de 6 em 6 horas antes de publicar, com --anterior https://farol.linupedia.com.br/dados/ronda.json.
--conferir só confere se o bloco do index.html está bem formado (para o computador, sem rede)."""
import datetime
import html
import json
import re
import socket
import ssl
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SITES = [
    # (nome, endereço, trecho do título, a ilha / o que é)
    ('Família Linu', 'https://familia.linupedia.com.br/', 'Família Linu', 'o mapa das ilhas'),
    ('Linu Sites', 'https://sites.linupedia.com.br/', 'Linu Sites', 'a estação'),
    ('Digital Linu', 'https://digital.linupedia.com.br/', 'Digital Linu', 'a ilha de edição'),
    ('Linu Seguro', 'https://seguro.linupedia.com.br/', 'Linu Seguro', 'o iglu'),
    ('Linu Farol', 'https://farol.linupedia.com.br/', 'Linu Farol', 'este farol'),
    ('LinuPedia', 'https://linupedia.com.br/', 'LinuPedia', 'o acampamento'),
]
TRANCAS = [
    ('strict-transport-security', 'HTTPS sempre (HSTS)'),
    ('content-security-policy', 'só carrega o que é do site (CSP)'),
    ('x-content-type-options', 'não adivinha tipo de arquivo'),
    ('referrer-policy', 'não conta de onde a pessoa veio'),
    ('x-frame-options', 'não abre dentro de outro site'),
    ('permissions-policy', 'não pede câmera, microfone nem local'),
]
UA = 'linu-farol (ronda; https://farol.linupedia.com.br/)'
GUARDAR = 120


class Recursos(HTMLParser):
    """Os arquivos que a página carrega na primeira visita: CSS, scripts, imagens (menos as preguiçosas) e fontes
    pré-carregadas."""
    def __init__(self):
        super().__init__(); self.urls = []

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == 'link' and a.get('rel') in ('stylesheet', 'preload', 'icon') and a.get('href'):
            self.urls.append(a['href'])
        elif tag == 'script' and a.get('src'):
            self.urls.append(a['src'])
        elif tag == 'img' and a.get('src') and a.get('loading') != 'lazy':
            self.urls.append(a['src'])


def baixar(url, limite=8_000_000):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=20) as r:
        primeiro = time.perf_counter() - t0
        corpo = r.read(limite)
        return r.status, {k.lower(): v for k, v in r.headers.items()}, corpo, primeiro


def dias_do_certificado(host):
    ctx = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=15) as s, ctx.wrap_socket(s, server_hostname=host) as t:
        fim = datetime.datetime.strptime(t.getpeercert()['notAfter'], '%b %d %H:%M:%S %Y %Z')
    return round((fim - datetime.datetime.now(datetime.UTC).replace(tzinfo=None)).total_seconds() / 86400, 1)


def rondar(nome, url, trecho):
    r = {'nome': nome, 'url': url}
    # Luz e Rapidez (o tempo: o menor de três pedidos, para um soluço da rede não apagar a luz)
    try:
        tempos = []
        for _ in range(3):
            status, cab, corpo, t = baixar(url)
            tempos.append(t)
        pagina = corpo.decode('utf-8', 'replace')
        r['resposta_ms'] = round(min(tempos) * 1000)
        if status != 200:
            r['luz'] = ('apagada', f'respondeu {status}')
        elif trecho not in pagina:
            r['luz'] = ('apagada', 'abriu outra coisa no lugar do site')
        elif r['resposta_ms'] > 3000:
            r['luz'] = ('fraca', f'no ar, mas demorou {r["resposta_ms"] / 1000:.1f} s para responder')
        else:
            r['luz'] = ('acesa', 'no ar')
        # o peso da primeira visita: a página e o que ela carrega do próprio site
        leitor = Recursos(); leitor.feed(pagina)
        host = urllib.parse.urlsplit(url).netloc
        peso = len(corpo); vistos = set()
        for u in leitor.urls:
            u = urllib.parse.urljoin(url, u)
            if urllib.parse.urlsplit(u).netloc != host or u in vistos:
                continue
            vistos.add(u)
            try:
                peso += len(baixar(u)[2])
            except Exception:
                pass
        r['peso_kb'] = round(peso / 1024)
        if r['resposta_ms'] <= 800 and r['peso_kb'] <= 1500:
            r['rapidez'] = ('acesa', f'responde em {r["resposta_ms"]} ms; a primeira visita baixa {kb(r["peso_kb"])}')
        elif r['resposta_ms'] <= 2000 and r['peso_kb'] <= 3000:
            r['rapidez'] = ('fraca', f'responde em {r["resposta_ms"]} ms; a primeira visita baixa {kb(r["peso_kb"])}')
        else:
            r['rapidez'] = ('apagada', f'responde em {r["resposta_ms"]} ms; a primeira visita baixa {kb(r["peso_kb"])}')
        # Trancas: cabeçalho, ou a CSP na própria página
        postas = [k for k, _ in TRANCAS if k in cab]
        if 'content-security-policy' not in postas and re.search(r'http-equiv=["\']Content-Security-Policy', pagina, re.I):
            postas.append('content-security-policy')
        if 'x-frame-options' not in postas and 'frame-ancestors' in cab.get('content-security-policy', ''):
            postas.append('x-frame-options')
        r['trancas_postas'] = len(postas)
        faltam = [rotulo for k, rotulo in TRANCAS if k not in postas]
        txt = f'{len(postas)} de {len(TRANCAS)} trancas' + (f'; falta: {", ".join(faltam)}' if faltam else '')
        r['trancas'] = ('acesa' if len(postas) >= 5 else 'fraca' if len(postas) >= 3 else 'apagada', txt)
    except Exception as e:
        motivo = e.__class__.__name__
        r['luz'] = ('apagada', f'não abriu ({motivo})')
        r['rapidez'] = ('apagada', 'sem resposta')
        r['trancas'] = ('apagada', 'sem resposta')
    # Cadeado
    try:
        dias = dias_do_certificado(urllib.parse.urlsplit(url).netloc)
        r['cadeado_dias'] = dias
        if dias >= 2:
            r['cadeado'] = ('acesa', f'em dia: vale por mais {dias:.0f} dias e renova sozinho')
        elif dias > 0:
            r['cadeado'] = ('fraca', f'vence em {dias * 24:.0f} horas e ainda não renovou')
        else:
            r['cadeado'] = ('apagada', 'vencido')
    except Exception as e:
        r['cadeado'] = ('apagada', f'não deu para ler o certificado ({e.__class__.__name__})')
    return r


def kb(n):
    return f'{n} KB' if n < 1024 else f'{n / 1024:.1f} MB'.replace('.', ',')


def ler_anterior(origem):
    if not origem:
        local = RAIZ / 'dados' / 'ronda.json'
        return json.loads(local.read_text(encoding='utf-8')) if local.exists() else {}
    try:
        if origem.startswith('http'):
            return json.loads(baixar(origem)[2].decode('utf-8'))
        return json.loads(Path(origem).read_text(encoding='utf-8'))
    except Exception as e:
        print(f'sem a ronda anterior ({e.__class__.__name__}): o histórico começa agora')
        return {}


LUZES = [('luz', 'Luz'), ('cadeado', 'Cadeado'), ('rapidez', 'Rapidez'), ('trancas', 'Trancas')]
PALAVRA = {'acesa': 'acesa', 'fraca': 'fraca', 'apagada': 'apagada'}


def bloco_html(dados):
    quando = datetime.datetime.fromisoformat(dados['quando']).astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
    linhas = [f'          <p class="lista-quando">Última ronda: <time datetime="{dados["quando"]}">'
              f'{quando:%d/%m/%Y, %H:%M}</time> (Brasília). A próxima, em até 6 horas.</p>',
              '          <ol class="faroes">']
    for s in dados['sites']:
        hist = s.get('historico', [])
        no_ar = sum(1 for h in hist if h == 'acesa')
        acesas = sum(1 for k, _ in LUZES if s[k][0] == 'acesa')
        geral = 'acesa' if acesas == 4 else 'apagada' if s['luz'][0] == 'apagada' else 'fraca'
        linhas.append(f'            <li class="farol-item farol-{geral}">')
        linhas.append(f'              <div class="farol-cabeca"><span class="sinal sinal-{geral}" aria-hidden="true"></span>'
                      f'<h3><a href="{html.escape(s["url"])}">{html.escape(s["nome"])}</a></h3>'
                      f'<span class="farol-ilha">{html.escape(s["ilha"])}</span>'
                      f'<span class="farol-geral">{acesas} de 4 luzes acesas</span></div>')
        linhas.append('              <dl class="luzes">')
        for k, rotulo in LUZES:
            estado, texto = s[k]
            linhas.append(f'                <div class="luz luz-{estado}"><dt><span class="sinal sinal-{estado}" aria-hidden="true"></span>'
                          f'{rotulo} <span class="luz-estado">{PALAVRA[estado]}</span></dt><dd>{html.escape(texto)}</dd></div>')
        linhas.append('              </dl>')
        if len(hist) >= 4:
            linhas.append(f'              <p class="farol-historico">No ar em {no_ar} das últimas {len(hist)} rondas'
                          f'{" (" + str(len(hist) * 6 // 24) + " dias)" if len(hist) >= 8 else ""}.</p>')
        elif hist:
            linhas.append('              <p class="farol-historico">O histórico começou agora: a conta aparece a partir da 4ª ronda.</p>')
        linhas.append('            </li>')
    linhas.append('          </ol>')
    return '\n'.join(linhas)


def escrever_bloco(dados):
    p = RAIZ / 'index.html'
    t = p.read_text(encoding='utf-8')
    ini, fim = '<!-- ronda:inicio -->', '<!-- ronda:fim -->'
    a, b = t.index(ini) + len(ini), t.index(fim)
    novo = t[:a] + '\n' + bloco_html(dados) + '\n          ' + t[b:]
    p.write_text(novo, encoding='utf-8')


def main():
    if '--conferir' in sys.argv:
        t = (RAIZ / 'index.html').read_text(encoding='utf-8')
        ok = t.count('<!-- ronda:inicio -->') == 1 and t.count('<!-- ronda:fim -->') == 1 and (RAIZ / 'dados' / 'ronda.json').exists()
        print('A lista de faróis está no lugar.' if ok else 'Falta o bloco da ronda no index.html ou o dados/ronda.json.')
        sys.exit(0 if ok else 1)
    origem = sys.argv[sys.argv.index('--anterior') + 1] if '--anterior' in sys.argv else None
    anterior = {s['url']: s.get('historico', []) for s in ler_anterior(origem).get('sites', [])}
    sites = []
    for nome, url, trecho, ilha in SITES:
        r = rondar(nome, url, trecho)
        r['ilha'] = ilha
        r['historico'] = (anterior.get(url, []) + [r['luz'][0]])[-GUARDAR:]
        sites.append(r)
        print(f'{nome}: ' + ' · '.join(f'{rot} {r[k][0]}' for k, rot in LUZES))
    dados = {'quando': datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(), 'sites': sites}
    (RAIZ / 'dados').mkdir(exist_ok=True)
    (RAIZ / 'dados' / 'ronda.json').write_text(json.dumps(dados, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    escrever_bloco(dados)


if __name__ == '__main__':
    main()

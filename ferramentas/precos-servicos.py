"""Preços numa fonte só (07/11/2026): o precos.json do site é a fonte, e o index.html é escrito a partir dele.

Em cada cartão de serviço (o elemento com data-id), acerta o data-preco e o data-tipo, a linha
<p class="servico-preco"> e, no JSON-LD do <head>, o minPrice do serviço com o mesmo nome do <h3> do cartão. Nos
pacotes prontos (<p class="pacote-preco" data-pacote-preco="id id id">), reescreve o total que aparece sem JavaScript.

    python3 ferramentas/precos-servicos.py            escreve o index.html a partir do precos.json
    python3 ferramentas/precos-servicos.py --conferir  só confere (o Actions roda assim e reprova se discordarem)

O precos.json:  {"servicos": {"<id>": {"valor": 400, "tipo": "mensal" | "unico", "detalhe": "4 vídeos"}}}
O original mora em linuarquivos/modelos/ferramentas/; cada site tem uma cópia em ferramentas/.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def brl(v):
    return 'R$&nbsp;' + f'{v:,}'.replace(',', '.')


def linha(p):
    texto = f'a partir de <b>{brl(p["valor"])}</b>' + (' por mês' if p['tipo'] == 'mensal' else '')
    return texto + (f' <span>({p["detalhe"]})</span>' if p.get('detalhe') else '')


def total(ids, servicos):
    unico = sum(servicos[i]['valor'] for i in ids if servicos[i]['tipo'] == 'unico')
    mensal = sum(servicos[i]['valor'] for i in ids if servicos[i]['tipo'] == 'mensal')
    partes = ([f'<b>{brl(unico)}</b>'] if unico else []) + ([f'<b>{brl(mensal)}</b> por mês'] if mensal else [])
    return 'a partir de ' + ' + '.join(partes)


def aplicar(html, servicos):
    faltam = []
    nomes = {}
    for sid, p in servicos.items():
        m = re.search(r'<(\w+)([^>]*\bdata-id="' + re.escape(sid) + r'"[^>]*)>', html)
        if not m:
            faltam.append(sid)
            continue
        attrs = re.sub(r'\bdata-preco="[^"]*"', f'data-preco="{p["valor"]}"', m.group(2))
        attrs = re.sub(r'\bdata-tipo="[^"]*"', f'data-tipo="{p["tipo"]}"', attrs)
        html = html[:m.start(2)] + attrs + html[m.end(2):]
        fim = html.index(f'</{m.group(1)}>', m.start())
        trecho = html[m.start():fim]
        h3 = re.search(r'<h3[^>]*>(.*?)</h3>', trecho, re.S)
        if h3:
            nomes[re.sub(r'<[^>]+>', '', h3.group(1)).strip()] = p
        novo = re.sub(r'(<p class="servico-preco">).*?(</p>)', lambda x: x.group(1) + linha(p) + x.group(2), trecho, count=1, flags=re.S)
        html = html[:m.start()] + novo + html[fim:]
    for sid in re.findall(r'\bdata-id="([^"]+)"', html):
        if sid not in servicos:
            faltam.append(f'{sid} (está na página e não no precos.json)')
    html = re.sub(r'(<p class="pacote-preco" data-pacote-preco="([^"]+)">).*?(</p>)',
                  lambda x: x.group(1) + total(x.group(2).split(), servicos) + x.group(3), html, flags=re.S)
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', html, re.S)
    if m:
        ld = json.loads(m.group(2))
        for oferta in ld.get('hasOfferCatalog', {}).get('itemListElement', []):
            p = nomes.get(oferta.get('itemOffered', {}).get('name'))
            if p:
                spec = {'@type': 'UnitPriceSpecification', 'minPrice': p['valor'], 'priceCurrency': 'BRL'}
                if p['tipo'] == 'mensal':
                    spec['unitText'] = 'mês'
                oferta['priceSpecification'] = spec
        html = html[:m.start(2)] + json.dumps(ld, ensure_ascii=False, separators=(',', ':')) + html[m.end(2):]
    return html, faltam


def main():
    servicos = json.loads((RAIZ / 'precos.json').read_text(encoding='utf-8'))['servicos']
    pagina = RAIZ / 'index.html'
    antes = pagina.read_text(encoding='utf-8')
    depois, faltam = aplicar(antes, servicos)
    if faltam:
        print('Serviços sem par entre o precos.json e a página:\n  ' + '\n  '.join(faltam))
        sys.exit(1)
    if '--conferir' in sys.argv:
        if depois != antes:
            print('O index.html não bate com o precos.json. Rode: python3 ferramentas/precos-servicos.py')
            sys.exit(1)
        print('Os preços da página batem com o precos.json.')
        return
    if depois != antes:
        pagina.write_text(depois, encoding='utf-8')
        print('index.html atualizado a partir do precos.json.')
    else:
        print('Nada a mudar: a página já bate com o precos.json.')


if __name__ == '__main__':
    main()

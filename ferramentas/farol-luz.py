"""O farol à noite (07/11/2026): faz img/farol-noite.png, img/farol-luz.png e img/farol-feixe.png a partir do
img/farol.png (a pixel art do dia, 110 × 221).

    python3 ferramentas/farol-luz.py

- farol-noite.png: o mesmo desenho com a luz da noite (azul-ardósia), pixel por pixel.
- farol-luz.png: o vidro da lanterna e as duas janelas acesos; cada pixel troca a cor por um amarelo do mesmo
  claro-escuro (as grades e o caixilho continuam lá).
- farol-feixe.png: o facho, para os dois lados, em degraus de transparência (sem degradê liso). A tela é mais larga
  que o farol (FEIXE_L de cada lado) e fica centrada nele no CSS.
Tudo na grade do desenho; a página mostra em 2× (css/estilo.css)."""
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
LANTERNA = (34, 26, 78, 64)      # a caixa do vidro, na grade do farol
JANELAS = [(60, 96, 76, 116), (60, 126, 76, 146)]
CENTRO = (56, 44)                 # o meio da lanterna
FEIXE_L = 150                     # quanto o facho passa de cada lado
AMARELO = [(0x8A, 0x5A, 0x12), (0xD9, 0x9A, 0x1E), (0xF8, 0xCB, 0x4A), (0xFF, 0xE8, 0x8C), (0xFF, 0xF6, 0xD2)]
FACHO = (0xFF, 0xE7, 0x9A)


def lum(c):
    return (c[0] * 299 + c[1] * 587 + c[2] * 114) / 1000


def azulado(c):
    return c[2] > c[0] + 8 and max(c[:3]) - min(c[:3]) < 90


def noite(c):
    r, g, b = c[:3]; L = lum(c)
    base = (L * .17 + 8, L * .25 + 16, L * .36 + 32)
    return tuple(round(v * .8 + o * .2 * .35) for v, o in zip(base, (r, g, b))) + (c[3],)


def main():
    farol = Image.open(RAIZ / 'img' / 'farol.png').convert('RGBA')
    w, h = farol.size; px = farol.load()
    escuro = Image.new('RGBA', (w, h)); pe = escuro.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                pe[x, y] = noite(px[x, y])
    escuro.save(RAIZ / 'img' / 'farol-noite.png', optimize=True)

    luz = Image.new('RGBA', (w, h), (0, 0, 0, 0)); pl = luz.load()
    # o vidro: os pixels claros e azulados dentro da caixa da lanterna
    for y in range(LANTERNA[1], LANTERNA[3]):
        for x in range(LANTERNA[0], LANTERNA[2]):
            c = px[x, y]
            if c[3] and lum(c) > 120 and azulado(c):
                t = (lum(c) - 120) / 135
                pl[x, y] = AMARELO[min(4, 2 + int(t * 3))] + (255,)
    # as janelas: os pixels escuros de dentro
    for x0, y0, x1, y1 in JANELAS:
        for y in range(y0, y1):
            for x in range(x0, x1):
                c = px[x, y]
                if c[3] and lum(c) < 90:
                    pl[x, y] = AMARELO[2 if lum(c) > 40 else 1] + (255,)
    luz.save(RAIZ / 'img' / 'farol-luz.png', optimize=True)

    # o facho: dois triângulos que abrem a partir da lanterna, mais fracos longe dela
    W = w + 2 * FEIXE_L
    feixe = Image.new('RGBA', (W, h), (0, 0, 0, 0)); pf = feixe.load()
    cx, cy = CENTRO[0] + FEIXE_L, CENTRO[1]
    for x in range(W):
        d = abs(x - cx)
        if d < 22:
            continue
        meia = 3 + (d - 22) * .16       # o facho abre devagar
        alfa = (110, 84, 60, 40, 22)[min(4, int((d - 22) / 34))]
        for y in range(max(0, round(cy - meia)), min(h, round(cy + meia) + 1)):
            borda = abs(y - cy) > meia - 2
            pf[x, y] = FACHO + ((alfa * 2) // 3 if borda else alfa,)
    feixe.save(RAIZ / 'img' / 'farol-feixe.png', optimize=True)
    print('img/farol-noite.png, img/farol-luz.png e img/farol-feixe.png prontos')


if __name__ == '__main__':
    main()

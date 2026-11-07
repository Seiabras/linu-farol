# Linu Farol na Oracle Cloud

Endereço: **https://farol.linupedia.com.br**. Mesma VM do Linu Sites, do Digital Linu e da LinuPedia (Ubuntu, IP 168.138.155.95),
mas com publicação própria: este repositório não depende dos irmãos, e o contrário também vale.
O site é só arquivos: o Caddy entrega a pasta `/opt/linu-farol/app` direto.

## DNS (uma vez, feito em 07/11/2026)

Registro A `farol` → `168.138.155.95` na zona do `linupedia.com.br` (Registro.br).

## Caddy (uma vez, feito em 07/11/2026)

O bloco de [`Caddyfile-bloco`](Caddyfile-bloco) fica em `/etc/caddy/Caddyfile`. Quando o bloco mudar, trocar o antigo
pelo novo e recarregar:

```bash
sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.antes-farol
sudo nano /etc/caddy/Caddyfile   # trocar o bloco "farol.linupedia.com.br { … }"
sudo caddy validate --config /etc/caddy/Caddyfile && sudo systemctl reload caddy
```

## Publicação automática

A cada push na `main`, o GitHub Actions ([`oracle.yml`](../.github/workflows/oracle.yml)) valida o HTML, confere que
todo arquivo usado existe (`deploy/conferir-pagina.py`) e manda o site para a VM: as páginas, `css/`, `js/`, `img/`,
`fontes/`, `robots.txt` e `sitemap.xml` (os `.md` e `deploy/` não vão). Entra como o usuário `linufarol`, **sem
sudo**, com uma chave presa ao comando `/opt/linu-farol/receber.sh`: ela só consegue trocar `/opt/linu-farol/app`
(a versão anterior fica em `app.anterior`).

Preparação (uma vez): `bash deploy/ligar-publicacao.sh` no computador faz tudo. À mão: `sudo bash
deploy/instalar-uma-vez.sh "<chave pública>"` na VM, a chave privada no segredo
`ORACLE_SSH_KEY` e a linha da chave da VM no segredo `ORACLE_HOST_KEY` (Settings → Secrets and variables → Actions).
A linha da VM sai de `echo "168.138.155.95 $(cut -d' ' -f1,2 /etc/ssh/ssh_host_ed25519_key.pub)"`.
**Para cortar o acesso do GitHub:** apagar `/home/linufarol/.ssh/authorized_keys`.

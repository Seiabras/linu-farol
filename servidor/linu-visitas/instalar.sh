#!/usr/bin/env bash
# Instala o linu-visitas na VM. Roda como administrador, na VM (o ligar-visitas.sh manda e roda):
#   sudo bash instalar.sh            (a chave de leitura vem pela entrada, uma linha; só na primeira vez ou com TROCAR_CHAVE=1)
# Cria o usuário linuvisitas (sem login), /opt/linu-visitas (app + dados, só ele lê), o .env com a chave e o serviço
# do systemd, com as mesmas proteções do linu-pedidos. Liga o /api/visita no bloco do Farol no Caddy, se ainda não
# estiver (com cópia antes e volta atrás se o Caddy reprovar). Pode rodar de novo para atualizar o servidor.mjs.
set -euo pipefail
BASE=/opt/linu-visitas
AQUI="$(cd "$(dirname "$0")" && pwd)"
id linuvisitas >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin linuvisitas
install -d -m 755 -o root -g root "$BASE" "$BASE/app"
install -d -m 700 -o linuvisitas -g linuvisitas "$BASE/dados"
install -m 644 -o root -g root "$AQUI/servidor.mjs" "$BASE/app/servidor.mjs"
if [ ! -s "$BASE/.env" ] || [ "${TROCAR_CHAVE:-}" = 1 ]; then
  read -r CHAVE
  [ ${#CHAVE} -ge 32 ] || { echo "Chave curta demais."; exit 1; }
  umask 077
  printf 'CHAVE_LEITURA=%s\nPORTA=8095\nDADOS=%s/dados\n' "$CHAVE" "$BASE" > "$BASE/.env"
  chown root:linuvisitas "$BASE/.env"; chmod 640 "$BASE/.env"
fi
cat > /etc/systemd/system/linu-visitas.service <<UNIT
[Unit]
Description=linu-visitas (o contador de visitas sem cookie do Linu Farol)
After=network-online.target

[Service]
User=linuvisitas
WorkingDirectory=$BASE/app
EnvironmentFile=$BASE/.env
ExecStart=/usr/bin/node servidor.mjs
Restart=always
RestartSec=2
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=$BASE/dados
ProtectHome=true
PrivateTmp=true
MemoryMax=200M

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now linu-visitas
systemctl restart linu-visitas
sleep 1
curl -fsS http://127.0.0.1:8095/api/visita >/dev/null && echo "linu-visitas no ar em 127.0.0.1:8095."

# o Caddy: o /api/visita dentro do bloco do Farol
CF=/etc/caddy/Caddyfile
if grep -q '127.0.0.1:8095' "$CF"; then
  echo "O Caddy já encaminha o /api/visita."
else
  cp "$CF" "$CF.antes-visitas"
  awk '
    { print }
    /^farol\.linupedia\.com\.br[[:space:]]*\{/ && !feito {
      print "\t# o contador de visitas sem cookie (linu-farol/servidor/linu-visitas)"
      print "\t@visitas path /api/visita /api/visitas"
      print "\thandle @visitas {"
      print "\t\trequest_body {"
      print "\t\t\tmax_size 2KB"
      print "\t\t}"
      print "\t\treverse_proxy 127.0.0.1:8095"
      print "\t}"
      print "\theader /v.js Cache-Control \"public, max-age=86400\""
      feito = 1
    }' "$CF.antes-visitas" > "$CF"
  if grep -q '127.0.0.1:8095' "$CF" && caddy validate --config "$CF" --adapter caddyfile > /tmp/caddy-validar.txt 2>&1; then
    systemctl reload caddy && echo "Caddy: /api/visita ligado (cópia em $CF.antes-visitas)."
  else
    cp "$CF.antes-visitas" "$CF"
    tail -n 3 /tmp/caddy-validar.txt 2>/dev/null || true
    echo "O Caddy reprovou (ou o bloco do Farol não foi achado): voltei o Caddyfile como estava. Pôr o bloco à mão (deploy/Caddyfile-bloco)."
  fi
fi

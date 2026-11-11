#!/usr/bin/env bash
# Liga o contador de visitas do Farol. Rodar no computador, uma vez:
#   bash ~/Documentos/projetos/linu-farol/servidor/linu-visitas/ligar-visitas.sh
# Sorteia a chave de leitura, guarda no segredo FAROL_VISITAS_CHAVE do GitHub (o painel lê com ela) e no
# /opt/linu-visitas/.env da VM (legível só pelo serviço), instala o serviço e liga o /api/visita no Caddy do Farol.
# A chave não aparece na tela nem fica no computador. Atualizar o código: rodar de novo (a chave fica).
# Trocar a chave: TROCAR_CHAVE=1 bash ligar-visitas.sh
set -euo pipefail
cd "$(dirname "$0")"
VM=ubuntu@168.138.155.95
ADM=~/.ssh/id_ed25519_linulingo
REPO=Seiabras/linu-farol
CHAVE=""
if [ "${TROCAR_CHAVE:-}" = 1 ] || ! gh secret list -R "$REPO" | grep -q '^FAROL_VISITAS_CHAVE'; then
  CHAVE="$(openssl rand -hex 32)"
  printf '%s' "$CHAVE" | gh secret set FAROL_VISITAS_CHAVE -R "$REPO"
  echo "Segredo FAROL_VISITAS_CHAVE guardado no GitHub."
  TROCAR_CHAVE=1
fi
scp -q -i "$ADM" servidor.mjs instalar.sh "$VM:/tmp/"
printf '%s\n' "$CHAVE" | ssh -i "$ADM" "$VM" "sudo TROCAR_CHAVE=${TROCAR_CHAVE:-} bash /tmp/instalar.sh; rm -f /tmp/servidor.mjs /tmp/instalar.sh"

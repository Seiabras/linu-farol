#!/usr/bin/env bash
# Deixa os sites da família mandarem o aviso de visita para o Farol (11/11/2026). Rodar no computador, uma vez:
#   bash ~/Documentos/projetos/linu-farol/servidor/linu-visitas/liberar-sites-da-casa.sh
# Na regra de segurança (CSP) do Caddy de cada site da família, o connect-src 'self' passa a aceitar também
# https://farol.linupedia.com.br. Só nos blocos de sites, digital, familia e seguro.linupedia.com.br; nada mais muda.
# Guarda uma cópia antes, confere com o caddy validate e volta atrás se reprovar.
set -euo pipefail
VM=ubuntu@168.138.155.95
ADM=~/.ssh/id_ed25519_linulingo
ssh -i "$ADM" "$VM" 'sudo bash -s' <<'NA_VM'
set -euo pipefail
CF=/etc/caddy/Caddyfile
if awk '/^(sites|digital|familia|seguro)\.linupedia\.com\.br[[:space:]]*\{/{b=1} b&&/^\}/{b=0} b&&/connect-src .self. https:\/\/farol/{n++} END{exit !(n>=4)}' "$CF"; then
  echo "Já estava liberado nos quatro sites."; exit 0
fi
cp "$CF" "$CF.antes-visitas-casa"
awk '
  /^(sites|digital|familia|seguro)\.linupedia\.com\.br[[:space:]]*\{/ { bloco = 1 }
  bloco && /^\}/ { bloco = 0 }
  bloco && /connect-src .self.;/ && !/farol\.linupedia/ { sub(/connect-src .self.;/, "connect-src '"'"'self'"'"' https://farol.linupedia.com.br;") }
  { print }' "$CF.antes-visitas-casa" > "$CF"
echo "Linhas trocadas: $(diff "$CF.antes-visitas-casa" "$CF" | grep -c '^>' || true)"
if caddy validate --config "$CF" --adapter caddyfile > /tmp/caddy-validar.txt 2>&1; then
  systemctl reload caddy && echo "Pronto: os sites da família já podem mandar as visitas ao Farol (cópia em $CF.antes-visitas-casa)."
else
  tail -n 3 /tmp/caddy-validar.txt
  cp "$CF.antes-visitas-casa" "$CF"
  echo "O Caddy reprovou: voltei o Caddyfile como estava."
fi
NA_VM

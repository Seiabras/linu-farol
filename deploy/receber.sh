#!/usr/bin/env bash
# Único comando que a chave do GitHub Actions pode rodar na VM (comando forçado no authorized_keys do
# usuário linufarol). Recebe pela entrada um .tar.gz com o site e troca /opt/linu-farol/app.
# A versão anterior fica em app.anterior; se o pacote vier sem index.html, nada é trocado.
set -euo pipefail
BASE=/opt/linu-farol
NOVA="$BASE/app.nova"; VELHA="$BASE/app.anterior"

rm -rf "$NOVA"; mkdir -p "$NOVA"
head -c 50000000 | tar xzf - -C "$NOVA" --no-same-owner
[ -f "$NOVA/index.html" ] || { echo "Pacote inválido (sem index.html)."; rm -rf "$NOVA"; exit 1; }
chmod -R a+rX "$NOVA"

rm -rf "$VELHA"
[ -d "$BASE/app" ] && mv "$BASE/app" "$VELHA"
mv "$NOVA" "$BASE/app"
echo "Linu Farol atualizado."

#!/usr/bin/env bash
# Prepara a VM para receber o Linu Farol pelo GitHub Actions. Rodar uma vez, como administrador:
#   sudo bash instalar-uma-vez.sh "<chave pública do GitHub Actions>"
# Cria o usuário linufarol (sem sudo), dono de /opt/linu-farol, e prende a chave ao receber.sh.
# Pode rodar de novo sem estragar nada.
set -euo pipefail
CHAVE="${1:?passe a chave pública}"
BASE=/opt/linu-farol
AQUI="$(cd "$(dirname "$0")" && pwd)"

id linufarol >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash linufarol
mkdir -p "$BASE/app"
install -m 755 -o root -g root "$AQUI/receber.sh" "$BASE/receber.sh"
chown linufarol: "$BASE" && chown -R linufarol: "$BASE/app"
chmod 755 "$BASE"

install -d -m 700 -o linufarol -g linufarol /home/linufarol/.ssh
echo "restrict,command=\"$BASE/receber.sh\" $CHAVE" > /home/linufarol/.ssh/authorized_keys
chown linufarol: /home/linufarol/.ssh/authorized_keys && chmod 600 /home/linufarol/.ssh/authorized_keys
echo "Pronto: linufarol recebe versões novas em $BASE/app."

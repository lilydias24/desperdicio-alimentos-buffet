#!/usr/bin/env bash
# Encerra o dashboard iniciado por apresentar.sh.
# Uso: ./parar.sh

cd "$(dirname "${BASH_SOURCE[0]}")"

if command -v docker >/dev/null 2>&1; then
    echo "Encerrando o container Docker (docker compose down)..."
    docker compose down
fi

echo
echo "Se o dashboard estiver rodando localmente (fora do Docker), encerre o"
echo "processo do Streamlit (Ctrl+C no terminal onde ele foi iniciado)."

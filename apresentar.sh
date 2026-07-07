#!/usr/bin/env bash
# Sobe o dashboard do Grupo 03 para a apresentacao/demo.
# Uso: ./apresentar.sh  (ou: bash apresentar.sh)
#
# Tenta Docker Compose primeiro (caminho documentado no README). Se o Docker
# nao estiver disponivel na maquina da apresentacao, cai para execucao local
# com Python. Ao final, abre o navegador em http://localhost:8501.

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "================================================================"
echo " Grupo 03 - Investigacao do Desperdicio de Alimentos em Buffets"
echo "================================================================"
echo

wait_dashboard() {
    local timeout=90
    local elapsed=0
    while [ "$elapsed" -lt "$timeout" ]; do
        if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8501/_stcore/health" 2>/dev/null | grep -q "200"; then
            return 0
        fi
        sleep 2
        elapsed=$((elapsed + 2))
        printf "."
    done
    return 1
}

open_browser() {
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$1" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then
        open "$1"
    elif command -v start >/dev/null 2>&1; then
        start "$1"
    else
        echo "Abra manualmente no navegador: $1"
    fi
}

if command -v docker >/dev/null 2>&1; then
    echo "[1/2] Docker encontrado. Subindo o dashboard com 'docker compose up --build -d'..."
    if ! docker compose up --build -d; then
        echo
        echo "Falha ao subir o container. Veja o erro acima ou rode: docker compose logs"
        exit 1
    fi
    echo -n "[2/2] Aguardando o dashboard ficar pronto"
else
    echo "[1/2] Docker nao encontrado nesta maquina. Rodando localmente com Python..."
    if ! command -v python >/dev/null 2>&1 && ! command -v python3 >/dev/null 2>&1; then
        echo "Python nao encontrado no PATH. Instale Python 3.10+ ou use uma maquina com Docker."
        exit 1
    fi
    PY=$(command -v python || command -v python3)
    echo "      Instalando dependencias (requirements.txt)..."
    "$PY" -m pip install -r requirements.txt --quiet
    nohup "$PY" -m streamlit run app/app.py > /tmp/streamlit_apresentacao.log 2>&1 &
    echo -n "[2/2] Aguardando o dashboard ficar pronto"
fi

if wait_dashboard; then
    echo
    echo
    echo "Dashboard pronto! Abrindo http://localhost:8501 no navegador..."
    open_browser "http://localhost:8501"
else
    echo
    echo
    echo "O dashboard nao respondeu em 90s."
    if command -v docker >/dev/null 2>&1; then
        echo "Verifique os logs com: docker compose logs -f"
    else
        echo "Veja o log em /tmp/streamlit_apresentacao.log"
    fi
    echo "Voce tambem pode abrir manualmente: http://localhost:8501"
fi

# Imagem do dashboard Streamlit do Grupo 03.
# O codigo do projeto usa sintaxe de tipos do Python 3.10+ (ex.: `str | Path`),
# entao a imagem base precisa ser 3.10 ou superior.
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Instala as dependencias antes de copiar o restante do projeto para
# aproveitar o cache de camadas do Docker em rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

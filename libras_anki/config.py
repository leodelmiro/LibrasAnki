"""Caminhos e constantes do projeto."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

CACHE = RAIZ / ".cache"
CACHE_DADOS = CACHE / "dados"
CACHE_VIDEOS = CACHE / "videos"
LISTAS = RAIZ / "listas"
SAIDA = RAIZ / "out"

BASE_URL = "https://dicionario.ines.gov.br/"
URL_PALAVRAS = BASE_URL + "public/site/js/palavras.js"
URL_VIDEOS = BASE_URL + "public/media/palavras/videos/"

# Tabelas auxiliares: nome do arquivo -> nome da variável no JS.
TABELAS_AUXILIARES = {
    "classes": "classes",
    "assuntos": "assuntos",
    "mao": "mao",
    "origem": "origem",
}
URL_AUXILIAR = BASE_URL + "public/site/js/{nome}.js"

TIMEOUT = 30

# Campos que todo verbete válido precisa ter — usado para detectar mudança de
# formato no INES antes de gravar cache ruim por cima do bom.
CAMPOS_OBRIGATORIOS = frozenset(
    {"ident", "palavra", "descricao", "libras", "exemplo", "video", "classe", "status"}
)


def criar_diretorios():
    """Cria a árvore de diretórios usada em disco. Idempotente."""
    for d in (CACHE_DADOS, CACHE_VIDEOS, LISTAS, SAIDA):
        d.mkdir(parents=True, exist_ok=True)

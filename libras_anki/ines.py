"""Obtenção, cache e carregamento do dataset do dicionário do INES.

O site não tem API: a navegação inteira é client-side sobre um único arquivo
JavaScript (`palavras.js`, ~2 MB) que declara `var palavras = [ ... ];`. O
conteúdo entre o primeiro `[` e o último `]` é JSON válido, então não é preciso
interpretar JavaScript — basta recortar e passar por `json.loads`.
"""

import json

import requests

from . import config


class FormatoInesMudou(RuntimeError):
    """O conteúdo baixado não tem a estrutura esperada do INES."""


def _extrair_array(texto, origem):
    """Recorta o array JSON de dentro da declaração `var X = [...];`."""
    inicio = texto.find("[")
    fim = texto.rfind("]")
    if inicio == -1 or fim == -1 or fim < inicio:
        raise FormatoInesMudou(
            f"{origem}: não foi encontrado um array JSON no arquivo. "
            "O formato do INES provavelmente mudou; o cache anterior foi preservado."
        )
    try:
        return json.loads(texto[inicio : fim + 1])
    except json.JSONDecodeError as erro:
        raise FormatoInesMudou(
            f"{origem}: o array encontrado não é JSON válido ({erro}). "
            "O formato do INES provavelmente mudou; o cache anterior foi preservado."
        ) from erro


def _validar_verbetes(dados):
    """Confere que o dataset tem cara de dicionário do INES antes de virar cache."""
    if not isinstance(dados, list) or not dados:
        raise FormatoInesMudou(
            "palavras.js: esperava uma lista não vazia de verbetes. "
            "O cache anterior foi preservado."
        )
    amostra = dados[: min(50, len(dados))]
    for verbete in amostra:
        if not isinstance(verbete, dict):
            raise FormatoInesMudou(
                "palavras.js: um item do array não é um objeto. "
                "O cache anterior foi preservado."
            )
        faltando = config.CAMPOS_OBRIGATORIOS - verbete.keys()
        if faltando:
            raise FormatoInesMudou(
                f"palavras.js: verbete sem os campos {sorted(faltando)}. "
                "O formato do INES mudou; o cache anterior foi preservado."
            )
    return dados


def _buscar(url):
    resposta = requests.get(url, timeout=config.TIMEOUT)
    resposta.raise_for_status()
    # O servidor devolve application/x-javascript sem charset; as strings do
    # JSON vêm com escapes \uXXXX, mas forçamos utf-8 para o resto do arquivo.
    resposta.encoding = "utf-8"
    return resposta.text


def _caminho_cache(nome):
    return config.CACHE_DADOS / f"{nome}.json"


def _gravar_cache(nome, dados):
    config.CACHE_DADOS.mkdir(parents=True, exist_ok=True)
    # Grava em arquivo temporário e só então substitui, para nunca deixar um
    # cache pela metade se a escrita for interrompida.
    temporario = _caminho_cache(nome).with_suffix(".json.tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    temporario.replace(_caminho_cache(nome))


def _ler_cache(nome):
    caminho = _caminho_cache(nome)
    if not caminho.exists():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def obter_verbetes(forcar=False, apenas_ativos=True):
    """Devolve os verbetes do INES, usando cache local quando disponível.

    Com o cache presente, nenhuma requisição de rede é feita. Se o download
    falhar na validação, a exceção sobe e o cache anterior permanece intacto.
    """
    dados = None if forcar else _ler_cache("palavras")
    if dados is None:
        dados = _validar_verbetes(_extrair_array(_buscar(config.URL_PALAVRAS), "palavras.js"))
        _gravar_cache("palavras", dados)

    if apenas_ativos:
        # `status: 0` marca verbetes desativados — na prática duas linhas de
        # campos vazios que quebrariam a geração adiante.
        dados = [v for v in dados if str(v.get("status")) == "1"]
    return dados


def obter_tabela(nome, forcar=False):
    """Devolve uma tabela auxiliar (`classes`, `assuntos`, `mao`) como dict id -> registro."""
    if nome not in config.TABELAS_AUXILIARES:
        raise ValueError(f"tabela auxiliar desconhecida: {nome}")

    dados = None if forcar else _ler_cache(nome)
    if dados is None:
        url = config.URL_AUXILIAR.format(nome=nome)
        dados = _extrair_array(_buscar(url), f"{nome}.js")
        if not isinstance(dados, list):
            raise FormatoInesMudou(f"{nome}.js: esperava uma lista.")
        _gravar_cache(nome, dados)
    return {str(item["id"]): item for item in dados if "id" in item}


def obter_tabelas(forcar=False):
    """Devolve as três tabelas auxiliares de uma vez."""
    return {nome: obter_tabela(nome, forcar=forcar) for nome in config.TABELAS_AUXILIARES}

"""Números de 1 a 10 tratados como contraste de função, não como vocabulário.

A aula ensina uma regra morfológica: a mesma configuração de mão muda de sentido
pelo movimento.

    ordinais 1–9     movimento trêmulo
    cardinais        sem movimento
    quantidade 1–4   forma própria; de 5 em diante igual ao cardinal

O INES é um dicionário de itens — um verbete, um vídeo — e não tem campo para
"trêmulo". Mas guarda parte da distinção na prosa da descrição:

    UM1  mão 12  "O primeiro de todos os números inteiros."
    UM2  mão 82  "Algarismo representativo para QUANTIDADE dos números inteiros."

Onde existem dois verbetes com descrições distintas, monta-se um card que mostra
os dois vídeos e pergunta qual é qual. Onde só existe um, valem os cards normais.

O escopo para em 10 porque a base não tem 13, 18, 19, 90 nem as centenas de 500
a 900 — números maiores não teriam como ser montados.
"""

from .indice import NUMERAIS

MINIMO = 1
MAXIMO = 10

TAG_NUMERO = "numero"
TAG_ORDINAL = "ordinal"
TAG_FALTA_VIDEO = "falta-video"

EXPLICACAO_CONTRASTE = (
    "O INES traz dois verbetes para este número, com descrições e configurações "
    "de mão diferentes. Repare na mão: é o mesmo número em funções distintas — "
    "contar (cardinal) e indicar quantidade."
)

OBSERVACAO_ORDINAL = (
    "O ordinal de 1 a 9 se faz com a MESMA mão do cardinal, mas com movimento "
    "trêmulo. De 10 em diante é igual ao cardinal. O dicionário do INES não "
    "registra movimento, então este vídeo precisa vir da sua aula."
)


def faixa():
    """Os números no escopo, como texto."""
    return [str(n) for n in range(MINIMO, MAXIMO + 1)]


def no_escopo(texto):
    termo = texto.strip()
    return termo.isdigit() and MINIMO <= int(termo) <= MAXIMO


def verbetes_do_numero(numero, indice):
    """Verbetes do INES para um dígito, via mapa de numerais por extenso."""
    resolucao = indice.resolver(str(numero))
    return resolucao.verbetes if resolucao else []


def eh_contraste(verbetes):
    """Dois ou mais verbetes com descrições distintas viram card de contraste."""
    if len(verbetes) < 2:
        return False
    return len({v.get("descricao", "") for v in verbetes}) > 1


def rotulo_funcao(verbete):
    """Deduz a função a partir da prosa da descrição do INES."""
    descricao = (verbete.get("descricao") or "").lower()
    if "quantidade" in descricao:
        return "quantidade"
    if "camisa" in descricao or "atleta" in descricao:
        return "número como etiqueta (camisa, telefone)"
    return "cardinal"


def chave_ordinal(numero):
    return f"ordinal-{numero}"


def ordinais_pendentes():
    """Números 1–9, que precisam do trêmulo gravado na aula."""
    return [str(n) for n in range(MINIMO, min(MAXIMO, 9) + 1)]


def por_extenso(numero):
    return NUMERAIS.get(str(numero), str(numero))

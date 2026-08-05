"""Índice normalizado e resolução de termos em português corrente.

As listas de estudo são escritas como a gente fala ("cheguei atrasado"); a base
do INES é em caixa alta, acentuada, no infinitivo e com sufixo numérico para
desambiguar homônimos ("CHEGAR1", "CHEGAR2"). A resolução tenta, em ordem:
exato, normalizado, sem sufixo numérico, lematizado e por sinônimo.

Sem lematização a cobertura das 14 frases da apostila é 57%; com ela, 88%.
"""

import re
import unicodedata
from collections import defaultdict

# Flexões que aparecem no currículo atual. Tabela manual de propósito: uma
# biblioteca de stemming acertaria mais casos, mas erraria em silêncio nos que
# importam. Quando esta tabela começar a doer, aí vale trocar.
LEMAS = {
    "APRENDENDO": "APRENDER",
    "CHEGUEI": "CHEGAR",
    # O INES cataloga o verbo, não o particípio nem o substantivo derivado.
    "ATRASADO": "ATRASAR",
    "DESCANSO": "DESCANSAR",
    "DESCULPA": "DESCULPAR",
    "ESTA": "ESTAR",
    "ESTAO": "ESTAR",
    "ESTOU": "ESTAR",
    "COMECOU": "COMEÇAR",
    "DORMI": "DORMIR",
    "ESTUDA": "ESTUDAR",
    "ESTUDEI": "ESTUDAR",
    "ESTUDOU": "ESTUDAR",
    "GOSTA": "GOSTAR",
    # "gosto" NÃO entra aqui: ele resolve sozinho no passo de normalização, para
    # o substantivo GOSTO ("o que é percebido pelo paladar"). Um lema nunca
    # chegaria a rodar. Escreva "gostar" para o verbo — e "paladar" para o
    # sentido, que tem verbete próprio.
    "PREFERIDO": "PREFERIR",
    "QUER": "QUERER",
    "QUERO": "QUERER",
    "MINHA": "MEU",
    "MORA": "MORAR",
    "SAIU": "SAIR",
    "TEM": "TER",
    "TEMOS": "TER",
    "TENHO": "TER",
    "VAI": "IR",
    "VAMOS": "IR",
    "VOCES": "VOCE",
    "VOU": "IR",
}

# Palavras que existem no dicionário sob outro nome.
SINONIMOS = {
    "MAE": "MAMAE",
    # Em LIBRAS o pronome de 3ª pessoa é apontar e não marca gênero: "ela" e
    # "ele" são o mesmo sinal. Não é lacuna do dicionário, é a gramática.
    "ELA": "ELE",
    "ELAS": "ELE",
    # Possessivos: a apostila descreve cada par masculino/feminino com uma
    # única configuração de mão (não marcam gênero, como ELE/ELA). TEU/TUA e
    # VOSSO/VOSSA não entram aqui porque nenhum dos dois tem verbete no INES
    # para servir de âncora — ficam como lacuna mesmo, nas listas de estudo.
    "SUA": "SEU",
    "DELA": "DELE",
    "NOSSA": "NOSSO",
    # "Pertencimento" e "pertence" são glosas alternativas da apostila para o
    # mesmo sinal de PRÓPRIO (mão em P batendo na palma da outra mão).
    "PERTENCIMENTO": "PROPRIO",
    "PERTENCE": "PROPRIO",
    # O INES tem um verbete só para os dois avós — "VOVÓ-VOVÔ", descrito como
    # "o avô, pai do pai ou da mãe; a avó, mãe do pai ou da mãe". Como "vô" e
    # "vó" normalizam os dois para "VO", uma entrada cobre o par.
    "VO": "VOVÓ-VOVÔ",
    # IRMÃO é descrito genericamente ("filhos do mesmo pai e da mesma mãe"),
    # sem marcar gênero — mesmo caso de ELE/ELA.
    "IRMA": "IRMÃO",
}

# Falsos amigos: termos que a normalização resolveria para um verbete de sentido
# completamente diferente. Bloqueados de propósito — é melhor cair em
# `falta-video` do que aprender o sinal errado.
FALSOS_AMIGOS = {
    # "LIBRAS"[:-1] == "LIBRA", que no dicionário é a unidade de peso e o signo
    # do zodíaco, nada a ver com a língua de sinais.
    "LIBRAS": "no INES só existe LIBRA (unidade de peso / signo), não a língua",
    # "por" (de "por que") sem acento normaliza igual a "PÔR", o verbo colocar —
    # sinal completamente diferente do usado na pergunta "por quê".
    "POR": "no INES 'por' sem acento cai em PÔR (colocar), verbo diferente",
}

# Verbetes que a normalização cola em outro de sentido completamente diferente,
# e que não interessam ao currículo. Sem isso a palavra pedida geraria dois
# cards: um do sentido que você quer, outro de um homônimo acidental.
#
# Diferente de FALSOS_AMIGOS, que bloqueia o termo inteiro: aqui o termo resolve
# normalmente, só este verbete é que sai do índice.
IGNORADOS = {
    # "carne" e "CARNÊ" viram a mesma chave quando a normalização tira o acento.
    # CARNÊ é bloco de pagamento — nada a ver com o alimento, e fora do escopo.
    "CARNÊ",
}

# O currículo escreve números como dígito ("dormir às 10 horas"), a base os
# guarda por extenso. Escopo 1–10, faixa em que o dicionário é completo.
NUMERAIS = {
    "0": "ZERO",
    "1": "UM",
    "2": "DOIS",
    "3": "TRES",
    "4": "QUATRO",
    "5": "CINCO",
    "6": "SEIS",
    "7": "SETE",
    "8": "OITO",
    "9": "NOVE",
    "10": "DEZ",
}

# O sufixo de desambiguação é quase sempre colado ("ABANDONAR2"), mas 9 verbetes
# usam espaço ("DIA 1", "BOLO 2", "MAIS 1", "REDE 1"). Sem tolerar o espaço,
# `raiz` devolvia "DIA " e duas coisas quebravam: "dia" e "bolo" ficavam
# inalcançáveis na busca, e MAIS/REDE — que misturam os dois padrões — eram
# partidos em dois grupos quando são um só.
_SUFIXO_NUMERICO = re.compile(r"\s*\d+$")


def normalizar(texto):
    """Caixa alta, sem acento, sem espaço nas pontas."""
    texto = unicodedata.normalize("NFD", texto.strip().upper())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def raiz(palavra):
    """Remove o sufixo numérico: ABANDONAR2 -> ABANDONAR, DIA 1 -> DIA."""
    return _SUFIXO_NUMERICO.sub("", palavra)


class Resolucao:
    """Resultado de resolver um termo contra o dicionário."""

    def __init__(self, termo, verbetes=(), via=None, alvo=None, motivo=None):
        self.termo = termo
        self.verbetes = list(verbetes)
        self.via = via
        self.alvo = alvo
        # Preenchido quando a falha tem explicação conhecida (falso amigo).
        self.motivo = motivo

    def __bool__(self):
        return bool(self.verbetes)

    def __repr__(self):
        if not self:
            return f"<Resolucao {self.termo!r} NAO RESOLVIDO>"
        palavras = ", ".join(v["palavra"] for v in self.verbetes)
        return f"<Resolucao {self.termo!r} via {self.via} -> {palavras}>"


class Indice:
    """Busca tolerante sobre os verbetes do INES."""

    def __init__(self, verbetes):
        self.verbetes = [v for v in verbetes if raiz(v["palavra"]) not in IGNORADOS]
        self._por_palavra = defaultdict(list)
        self._por_raiz = defaultdict(list)
        for verbete in self.verbetes:
            normalizada = normalizar(verbete["palavra"])
            if not normalizada:
                continue
            self._por_palavra[normalizada].append(verbete)
            self._por_raiz[raiz(normalizada)].append(verbete)

    def _buscar(self, chave):
        return self._por_palavra.get(chave) or self._por_raiz.get(chave)

    def resolver(self, termo):
        """Resolve um termo, devolvendo sempre uma Resolucao (falsa se não achou)."""
        bruto = termo.strip()
        if not bruto:
            return Resolucao(termo)

        # 1. exato, como está na base
        for verbete in self.verbetes:
            if verbete["palavra"] == bruto:
                return Resolucao(termo, [verbete], "exato", bruto)

        chave = normalizar(bruto)

        # Falso amigo: interrompe antes de qualquer normalização resolver errado.
        if chave in FALSOS_AMIGOS:
            return Resolucao(termo, motivo=FALSOS_AMIGOS[chave])

        # Dígito escrito no currículo -> numeral por extenso na base.
        if chave in NUMERAIS:
            achados = self._buscar(NUMERAIS[chave])
            if achados:
                return Resolucao(termo, achados, "numeral", NUMERAIS[chave])

        # 2. normalizado (acento e caixa) e 3. sem sufixo numérico
        achados = self._buscar(chave)
        if achados:
            return Resolucao(termo, achados, "normalizado", chave)

        chave_raiz = raiz(chave)
        if chave_raiz != chave:
            achados = self._buscar(chave_raiz)
            if achados:
                return Resolucao(termo, achados, "sem-sufixo", chave_raiz)

        # 4. plural simples
        if chave.endswith("S"):
            achados = self._buscar(chave[:-1])
            if achados:
                return Resolucao(termo, achados, "plural", chave[:-1])

        # 5. tabela de lematização
        lema = LEMAS.get(chave)
        if lema:
            achados = self._buscar(normalizar(lema))
            if achados:
                return Resolucao(termo, achados, "lema", lema)

        # 6. tabela de sinônimos
        sinonimo = SINONIMOS.get(chave)
        if sinonimo:
            achados = self._buscar(normalizar(sinonimo))
            if achados:
                return Resolucao(termo, achados, "sinonimo", sinonimo)

        return Resolucao(termo)

    def resolver_muitos(self, termos):
        """Resolve vários termos; devolve (resolvidos, nao_resolvidos)."""
        resolvidos, nao_resolvidos = [], []
        for termo in termos:
            resolucao = self.resolver(termo)
            (resolvidos if resolucao else nao_resolvidos).append(resolucao)
        return resolvidos, nao_resolvidos


# Palavras funcionais que não têm sinal próprio e não devem contar como falha
# ao analisar uma frase.
VAZIAS = frozenset(
    "O A OS AS DE DO DA DOS DAS EM NO NA NUM UM UMA E AO AOS À ÀS PARA COM SE QUE".split()
)


def palavras_da_frase(frase):
    """Extrai as palavras significativas de uma frase, ignorando as funcionais."""
    encontradas = re.findall(r"[0-9A-Za-zÀ-ÿ]+(?:-[0-9A-Za-zÀ-ÿ]+)*", frase)
    return [p for p in encontradas if len(p) > 1 and normalizar(p) not in VAZIAS]

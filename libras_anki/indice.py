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
    "AJUDA": "AJUDAR",
    "APRENDENDO": "APRENDER",
    "CHEGUEI": "CHEGAR",
    # O INES cataloga o verbo, não o particípio nem o substantivo derivado.
    "ATRASADO": "ATRASAR",
    "DESCANSO": "DESCANSAR",
    "DESCULPA": "DESCULPAR",
    "ENSINO": "ENSINAR",
    # Caminho inverso dos de cima: aqui a base cataloga o substantivo e não o
    # verbo. NOIVO1 e NOIVO2 têm descrições diferentes e viram dois cards.
    "NOIVAR": "NOIVO",
    "ESTA": "ESTAR",
    "ESTAO": "ESTAR",
    "ESTOU": "ESTAR",
    "COMECOU": "COMEÇAR",
    "COMPRAS": "COMPRAR",
    "CONHECI": "CONHECER",
    "DORMI": "DORMIR",
    "ESTUDA": "ESTUDAR",
    "ESTUDEI": "ESTUDAR",
    "ESTUDOU": "ESTUDAR",
    "GOSTA": "GOSTAR",
    # "gosto" NÃO entra aqui: ele resolve sozinho no passo de normalização, para
    # o substantivo GOSTO ("o que é percebido pelo paladar"). Um lema nunca
    # chegaria a rodar. Escreva "gostar" para o verbo — e "paladar" para o
    # sentido, que tem verbete próprio.
    "FAZ": "FAZER",
    "PREFERIDO": "PREFERIR",
    "QUER": "QUERER",
    "QUERO": "QUERER",
    "MINHA": "MEU",
    "MORA": "MORAR",
    "NASCEU": "NASCER",
    "OUTRA": "OUTRO",
    "SAIU": "SAIR",
    "SAO": "SER",
    "TEM": "TER",
    "TEMOS": "TER",
    "TENHO": "TER",
    "TRABALHA": "TRABALHAR",
    "VAI": "IR",
    "VAMOS": "IR",
    "VAO": "IR",
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
    # "avô" e "avó" caem no mesmo sinal, mas por um caminho que a normalização
    # não faz sozinha. O INES tem um segundo par de verbetes — "AVÔ/AVÓ1" e
    # "AVÔ/AVÓ2" — que nenhuma escrita alcança: a normalização tira acento e
    # caixa, não a barra do meio do nome. E os dois dão 404 no servidor, assim
    # como VOVÓ-VOVÔ1 e VOVÓ-VOVÔ2 — o sinal vem do @yt declarado em "vô".
    # Apontar para VOVÓ-VOVÔ é cair no card que já existe e já tem vídeo.
    "AVO": "VOVÓ-VOVÔ",
    # IRMÃO é descrito genericamente ("filhos do mesmo pai e da mesma mãe"),
    # sem marcar gênero — mesmo caso de ELE/ELA.
    "IRMA": "IRMÃO",
    # Femininos de parentesco: o INES cataloga só o masculino, como já fazia
    # com IRMÃO. Em dois deles o próprio verbete descreve os dois gêneros —
    # PRIMO é "o filho OU A FILHA de sua tia", CUNHADO é "o irmão (OU IRMÃ) do
    # seu marido ou da sua mulher". FILHA, SOBRINHA e SOGRA não têm essa
    # ressalva no dicionário e são as primeiras a confirmar na aula: se o
    # gênero for marcado (o sinal mais MULHER), estas três linhas saem e viram
    # @yt, sem mexer em código.
    "FILHA": "FILHO",
    "SOBRINHA": "SOBRINHO",
    "CUNHADA": "CUNHADO",
    "SOGRA": "SOGRO",
    "PRIMA": "PRIMO",
    # Vocabulário das frases de família. "duas" e "amiga" são flexão de gênero,
    # e o INES cataloga só uma das formas. "EUA" é sigla: o verbete está pelo
    # nome por extenso. "bastante" não tem verbete e é MUITO — decidido na
    # aula; MUITO tem três verbetes de descrições distintas, então a palavra
    # cai no mecanismo de escolha de sentido do verso da frase.
    "DUAS": "DOIS",
    "AMIGA": "AMIGO",
    "EUA": "ESTADOS UNIDOS",
    "BASTANTE": "MUITO",
}

# Falsos amigos: termos que a normalização resolveria para um verbete de sentido
# completamente diferente. Bloqueados de propósito — é melhor cair em
# `falta-video` do que aprender o sinal errado.
FALSOS_AMIGOS = {
    # "LIBRAS"[:-1] == "LIBRA", que no dicionário é a unidade de peso e o signo
    # do zodíaco, nada a ver com a língua de sinais.
    "LIBRAS": "no INES só existe LIBRA (unidade de peso / signo), não a língua",
    # "por" sozinho, sem acento, normaliza igual a "PÔR", o verbo colocar —
    # sinal completamente diferente. O "por" de "por que" não chega até aqui:
    # o par vira PORQUE em EXPRESSOES, antes da frase ser quebrada.
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
    # Mesmo caso: sem acento, "MAIÔ" vira a chave de "MAIO". O traje de banho
    # não tem nada a ver com o mês do calendário.
    "MAIÔ",
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
        singular = chave[:-1] if chave.endswith("S") else None
        if singular:
            achados = self._buscar(singular)
            if achados:
                return Resolucao(termo, achados, "plural", singular)

        # 5. e 6. tabelas de lematização e de sinônimos, na forma pedida e —
        # se ela for plural — também no singular. Sem a segunda passada o
        # plural falha justamente onde o singular resolveria: "cunhadas" para
        # e "cunhada" passa, e a alternativa seria repetir cada entrada das
        # tabelas nas duas formas, esquecendo a segunda em silêncio.
        resolucao = self._por_tabela(termo, chave)
        if resolucao:
            return resolucao
        if singular:
            resolucao = self._por_tabela(termo, singular)
            if resolucao:
                return resolucao

        return Resolucao(termo)

    def _por_tabela(self, termo, chave):
        """Tenta lema e depois sinônimo para uma chave. None se nenhum resolver."""
        for tabela, via in ((LEMAS, "lema"), (SINONIMOS, "sinonimo")):
            alvo = tabela.get(chave)
            if not alvo:
                continue
            achados = self._buscar(normalizar(alvo))
            if achados:
                return Resolucao(termo, achados, via, alvo)
        return None

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
    "O A OS AS DE DO DA DOS DAS EM NO NA NUM UM UMA E AO AOS À ÀS PARA COM SE QUE "
    "ME".split()
)

# Sequências de palavras que são um sinal só. Precisam ser reconhecidas antes da
# quebra em palavras, porque separadas os pedaços se perdem ou enganam.
#
# "por que": "que" é funcional e cai em VAZIAS, e "por" sozinho é falso amigo
# (PÔR). O sinal da pergunta é PORQUE, o mesmo da conjunção — "por que" e
# "porque" não se distinguem em LIBRAS, a diferença é ortografia do português.
#
# "mais ou menos": os três pedaços resolvem, e é justamente esse o problema —
# daria MAIS 1 ("o que supera o outro"), OU e MENOS1 ("exceto"), três sinais que
# não têm nada a ver com aproximação. A expressão não tem verbete no INES e
# entra por vídeo de fora.
# "o que": não é sinal composto nem sinal próprio, é o mesmo QUE — mas separado
# some inteiro, porque "o" e "que" são as duas funcionais. Resolve para os dois
# verbetes de QUE, e o verso da frase mostra os dois para você escolher.
EXPRESSOES = {
    ("MAIS", "OU", "MENOS"): "mais ou menos",
    ("POR", "QUE"): "porque",
    ("O", "QUE"): "que",
}

_MAIOR_EXPRESSAO = max(len(sequencia) for sequencia in EXPRESSOES)


def palavras_da_frase(frase):
    """Extrai as palavras significativas de uma frase, ignorando as funcionais."""
    brutas = re.findall(r"[0-9A-Za-zÀ-ÿ]+(?:-[0-9A-Za-zÀ-ÿ]+)*", frase)
    palavras, i = [], 0
    while i < len(brutas):
        # Da maior para a menor: se um dia houver expressão que comece igual a
        # outra, a mais longa é a que descreve o sinal inteiro.
        expressao = None
        for tamanho in range(_MAIOR_EXPRESSAO, 1, -1):
            sequencia = tuple(normalizar(p) for p in brutas[i:i + tamanho])
            if len(sequencia) == tamanho and sequencia in EXPRESSOES:
                expressao = (EXPRESSOES[sequencia], tamanho)
                break
        if expressao:
            palavras.append(expressao[0])
            i += expressao[1]
            continue

        atual = brutas[i]
        if len(atual) > 1 and normalizar(atual) not in VAZIAS:
            palavras.append(atual)
        i += 1
    return palavras

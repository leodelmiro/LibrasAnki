"""Montagem do baralho a partir das listas de estudo.

Regra que atravessa tudo: nada é descartado em silêncio. Palavra sem verbete,
vídeo que não baixou, palavra da frase sem sinal — tudo vira nota marcada por
tag, para você filtrar no Anki (`tag:falta-video`) e completar com material da
aula. Pular em silêncio esconderia a lacuna; abortar impediria de estudar o
resto.
"""

from collections import namedtuple
from pathlib import Path

import genanki

from . import config, grupos, indice, ines, listas, midia, modelo, numeros, youtube

TAG_FALTA_VIDEO = "falta-video"
TAG_COMPOSTO = "composto"
TAG_CONFIRMAR_SINAL = "confirmar-sinal"
TAG_FORMA_INCORRETA = "forma-incorreta"

# Um composto não tem verbete próprio, mas os componentes têm — então o card
# mostra os vídeos deles em sequência, em vez de ficar sem vídeo nenhum.
#
# `sinais` nomeia os verbetes exatos do INES em vez de dividir a string em
# palavras e resolver cada uma. Três motivos:
#
#   - palavras funcionais não têm sinal ("de" em "de nada", "tenha")
#   - homônimos exigem escolha: BOM tem 3 sentidos no INES e BOA tem 2, e a
#     resolução automática pegaria o primeiro no escuro
#   - o composto nem sempre é o split literal do português
#
# `confirmar` lista os componentes cuja escolha veio da descrição do INES por
# eliminação, não de conhecimento confirmado. Essas notas levam a tag
# `confirmar-sinal` — é palpite informado, e o card diz isso.
Composto = namedtuple("Composto", "nota sinais confirmar")

COMPOSTOS = {
    # BOM1 "situação agradável; o que é prazeiroso" — um cumprimento deseja um
    # dia agradável. BOM2 é "características positivas" (qualificar uma coisa) e
    # BOM3 é sobre roupa que veste bem. DIA 1 a 4 têm descrição idêntica, então
    # são variantes do mesmo sinal e tanto faz qual.
    "bom dia": Composto(
        "Composto: sinaliza-se BOM + DIA em sequência. Não existe como verbete "
        "único — nem no INES, nem no Spread the Sign.",
        ["BOM1", "DIA 1"],
        ["BOM"],
    ),
    # BOA2 é "mulher atraente", claramente não é o cumprimento. Sobra BOA1.
    "boa tarde": Composto(
        "Composto: BOA + TARDE em sequência.",
        ["BOA1", "TARDE"],
        ["BOA"],
    ),
    # NOITE1 e NOITE2 têm descrição idêntica — variantes, tanto faz qual.
    "boa noite": Composto(
        "Composto: BOA + NOITE em sequência.",
        ["BOA1", "NOITE1"],
        ["BOA"],
    ),
    # Não se sinaliza FIM + SEMANA. O INES tem os dois verbetes, e traduzir o
    # português palavra por palavra daria um par que ninguém usa: em LIBRAS o
    # fim de semana se diz nomeando os dois dias.
    "fim de semana": Composto(
        "Composto: SÁBADO + DOMINGO. Não se sinaliza FIM + SEMANA — em LIBRAS o "
        "fim de semana se diz nomeando os dois dias.",
        ["SÁBADO", "DOMINGO"],
        [],
    ),
    # "de" é palavra funcional, sem sinal próprio: sobra NADA.
    "de nada": Composto(
        "Expressão composta, sem verbete próprio no INES. O sinal de NADA é a "
        "parte que o dicionário tem.",
        ["NADA"],
        [],
    ),
    # Os dois componentes são únicos no INES: nenhuma escolha a fazer.
    "até amanhã": Composto(
        "Composto: ATÉ + AMANHÃ.",
        ["ATÉ", "AMANHÃ"],
        [],
    ),
    # Sequência informada em aula, não deduzida. Sem ela seria impossível
    # acertar: o "prazer" do cumprimento é GOSTAR, e nenhum dos três verbetes
    # de PRAZER serve — PRAZER1 e PRAZER2 são "alegria, satisfação" e PRAZER3
    # é "satisfação sexual". Resolver pela palavra levaria ao sinal errado.
    # "gosto" aqui é o verbo, mas resolve sozinho para o substantivo GOSTO
    # ("percebido pelo paladar") no passo de normalização — nem lema nem
    # sinônimo alcançam. Declarar os sinais é a única forma de acertar.
    "gosto de laranja": Composto(
        "GOSTAR + LARANJA. O 'gosto' daqui é o verbo; o INES tem GOSTO como "
        "substantivo do paladar, que é outro sinal.",
        ["GOSTAR", "LARANJA"],
        [],
    ),
    "prazer em conhecer você": Composto(
        "Composto: GOSTAR + CONHECER + VOCÊ. Não se usa o sinal de PRAZER "
        "aqui — o cumprimento se faz com GOSTAR.",
        ["GOSTAR", "CONHECER", "VOCÊ"],
        [],
    ),
    # "tenha" e "um" não entram: o primeiro não tem verbete, o segundo é
    # numeral e não cabe aqui. O "fim de semana" segue a mesma regra da entrada
    # acima — SÁBADO + DOMINGO, não FIM + SEMANA.
    "tenha um bom fim de semana": Composto(
        "Expressão composta: BOM + SÁBADO + DOMINGO. Confirme a sequência na aula.",
        ["BOM1", "SÁBADO", "DOMINGO"],
        ["BOM", "a sequência"],
    ),
}

# Formas que não existem em LIBRAS porque são transporte direto do português.
# O card continua existindo — é justamente ele que desfaz o engano — e mostra o
# vídeo do sinal correto, em vez de ficar esperando gravação da aula.
Correcao = namedtuple("Correcao", "nota sinais")

CORRECOES = {
    "teu": Correcao(
        "Não existe TEU em LIBRAS. O possessivo de 2ª pessoa é SEU — é este o "
        "sinal a fazer.",
        ["SEU"],
    ),
    "tua": Correcao(
        "Não existe TUA em LIBRAS. O possessivo de 2ª pessoa é SEU, que não "
        "marca gênero — é este o sinal a fazer.",
        ["SEU"],
    ),
}

# Verbetes cujo vídeo o INES declara mas não entrega (404), e cujo sinal é o
# mesmo de outro verbete que entrega. Emprestar o vídeo do irmão dá o que
# estudar hoje, em vez de deixar o card esperando gravação de um sinal que o
# próprio dicionário já mostra em outra entrada.
#
# Só entra aqui quando os dois são o mesmo sinal de fato — não sinônimo
# aproximado, não sentido vizinho.
MESMO_SINAL = {
    "FEMININO": ("MULHER", "Mesmo sinal de MULHER."),
}

TAG_MESMO_SINAL = "mesmo-sinal"

# Observações presas ao sinal, para o que o verbete do INES não diz sozinho.
NOTAS_DE_SINAL = {
    # O INES tem um verbete só para os dois avós, descrito como "o avô, pai do
    # pai ou da mãe; a avó, mãe do pai ou da mãe".
    "VOVÓ-VOVÔ": "Um sinal só para os dois avós: vovó é o mesmo sinal de vovô, "
                 "marcado com o feminino.",
}

# Explicações de casos que parecem lacuna mas são gramática da língua.
NOTAS_DE_LINGUA = {
    "ela": "Em LIBRAS o pronome de 3ª pessoa é apontar e não marca gênero: "
           "'ele' e 'ela' são o mesmo sinal.",
    # TEU/TUA saíram daqui: não são lacuna do dicionário, são forma que não
    # existe na língua — estão em CORRECOES, apontando para SEU.
    "vosso": "Sem verbete no INES. Indica plural: configuração de mão em P "
             "(apostila).",
    "vossa": "Sem verbete no INES. Indica plural: configuração de mão em P "
             "(apostila).",
    # Não é lacuna: abreviatura se soletra. As duas letras têm verbete próprio
    # no INES (K e G), e QUILO por extenso também — são coisas diferentes.
    "kg": "Abreviatura, feita por datilologia: soletra-se K + G. O INES tem as "
          "duas letras separadas e QUILO por extenso, mas não a abreviatura.",
    # Não é lacuna do dicionário: é termo que a comunidade surda rejeita, e o
    # card existe para reconhecê-lo e saber por quê.
    "surdo mudo": "Termo incorreto, rejeitado pela comunidade surda: pessoas "
                  "surdas têm as cordas vocais funcionando, e o termo confunde "
                  "não ouvir com não poder falar. Diga apenas SURDO. O INES tem "
                  "SURDO e MUDO como sinais separados, e não o composto.",
}


TAG_ESCOLHER_SENTIDO = "escolher-sentido"

# Em LIBRAS o interrogativo vai para o FIM da frase; o português põe na frente,
# e é aí que se erra. O verso listava o vocabulário na ordem do português, o que
# treinava justamente o erro — "Quem mora com você?" abria por QUEM, quando se
# sinaliza MORAR COM VOCÊ QUEM.
#
# Declarados pela raiz do verbete, e não pela palavra da frase: assim "o que",
# que resolve para QUE pela tabela de EXPRESSOES, entra junto sem precisar de
# entrada própria.
INTERROGATIVOS = frozenset(
    "QUE QUAL ONDE COMO QUANTO QUANTOS QUEM QUANDO PORQUE".split()
)

NOTA_ORDEM_LIBRAS = ("Vocabulário na ordem de LIBRAS: o interrogativo vai para "
                     "o fim da frase, não para o começo como no português.")


def _caminho(arquivo):
    """Caminho absoluto e resolvido, para comparar arquivo por identidade.

    `self.arquivos` guarda string e o cache devolve Path; sem normalizar os
    dois, a comparação erraria e a limpeza apagaria vídeo em uso.
    """
    return Path(arquivo).resolve()


def _rotulo_de_sentido(palavra, sinal):
    """Rótulo de um sentido no verso da frase: a palavra e o que o INES diz dela.

    A descrição é o que permite escolher — sem ela sobrariam "qual 1, 2, 3",
    que não dizem nada a quem está sinalizando.
    """
    descricao = (sinal.principal.get("descricao") or "").strip().rstrip(".")
    return f"{palavra} — {descricao}" if descricao else f"{palavra} ({sinal.palavra})"


def _chave_de_sinal(sinal):
    """Identidade de um Sinal. `ident` sozinho não serve: verbetes diferentes
    repetem ident na base, e é o par com o vídeo que os separa."""
    return (sinal.ident, sinal.videos[0] if sinal.videos else sinal.palavra)


class Relatorio:
    """Contabiliza o que entrou no baralho e o que precisa de atenção."""

    def __init__(self):
        self.notas = 0
        self.por_tipo = {}
        self.nao_resolvidos = []
        self.falta_video = []
        self.compostos = []
        self.correcoes = []
        self.mesmo_sinal = []
        self.video_suspeito = []
        self.grupo_misto = []
        self.escolha_de_sentido = []
        self.midia = {}
        self.externos = {}
        self.problemas = []
        self.cache = {}

    def conta(self, tipo):
        self.por_tipo[tipo] = self.por_tipo.get(tipo, 0) + 1
        self.notas += 1

    def texto(self):
        linhas = [f"{self.notas} notas geradas"]
        for tipo, quantidade in sorted(self.por_tipo.items()):
            linhas.append(f"   {quantidade:>4}  {tipo}")

        if self.midia:
            linhas.append(
                f"\nvídeos: {self.midia.get('baixados', 0)} baixados, "
                f"{self.midia.get('do_cache', 0)} do cache, "
                f"{self.midia.get('convertidos', 0)} convertidos para WebM"
            )

        if self.externos.get("clipes") or self.externos.get("do_cache"):
            linhas.append(
                f"vídeos de fora: {self.externos.get('clipes', 0)} clipes gerados, "
                f"{self.externos.get('do_cache', 0)} do cache, "
                f"{self.externos.get('fontes_baixadas', 0)} downloads"
            )

        def bloco(titulo, itens, dica=None):
            if not itens:
                return
            linhas.append(f"\n{titulo} ({len(itens)})")
            if dica:
                linhas.append(f"   {dica}")
            for item in itens:
                linhas.append(f"   - {item}")

        bloco("SEM SINAL NO INES", self.nao_resolvidos,
              "geradas assim mesmo; sem componentes, ficam com tag falta-video")
        bloco("COMPOSTOS", self.compostos,
              "sem verbete próprio, montados com os vídeos dos componentes")
        bloco("FORMA INCORRETA", self.correcoes,
              "não existe em LIBRAS; o card mostra o sinal correto")
        bloco("VÍDEO EMPRESTADO", self.mesmo_sinal,
              "o vídeo próprio dá 404 no INES; é o mesmo sinal de outro verbete")
        bloco("VÍDEO SUSPEITO", self.video_suspeito,
              "o mesmo arquivo é usado por outro verbete — confira antes de decorar")
        bloco("GRUPO MISTO", self.grupo_misto,
              "parte do grupo tem o mesmo sentido, parte não — separados por precaução")
        bloco("ESCOLHA NO VERSO", self.escolha_de_sentido,
              "o INES tem mais de um sinal; o verso mostra todos, você escolhe pelo sentido")
        bloco("PROBLEMAS NAS LISTAS", self.problemas,
              "a linha virou card, só o @yt foi ignorado — corrija e regere")
        if self.cache:
            linhas.append(
                f"\ncache limpo: {self.cache['fontes']} fontes de vídeo externo e "
                f"{len(self.cache['orfaos'])} vídeos sem uso, "
                f"{self.cache['megabytes']:.2f} MB"
            )
            bloco("VÍDEOS QUE SAÍRAM DO CACHE", self.cache["orfaos"],
                  "nenhuma nota os referencia mais — confira se alguma palavra sumiu sem querer")
        bloco("VÍDEO EXTERNO FALHOU", [
            f"{rotulo} — {motivo}" for rotulo, motivo in
            sorted(self.externos.get("falhas", {}).items())
        ], "o card ficou com o vídeo do INES, ou sem vídeo")
        bloco("CLIPE LONGO", self.externos.get("longos", []),
              f"acima de {youtube.SEGUNDOS_SUSPEITOS}s — faltou o intervalo no @yt?")
        return "\n".join(linhas)


class Gerador:
    def __init__(self, nome_baralho=modelo.NOME_BARALHO):
        self.verbetes = ines.obter_verbetes()
        self.tabelas = ines.obter_tabelas()
        self.indice = indice.Indice(self.verbetes)
        self.sinais, self.anomalias = grupos.construir(self.verbetes)
        self.recursos = midia.Midia()
        self.externos = youtube.Externos()
        self.baralho = modelo.criar_baralho(nome_baralho)
        self.relatorio = Relatorio()
        self.arquivos = set()
        self._vistos = set()

        # Do verbete de volta para o Sinal que o contém.
        self._por_verbete = {}
        for sinal in self.sinais:
            for verbete in sinal.verbetes:
                self._por_verbete[(verbete["ident"], verbete.get("video"))] = sinal

        # Os `@yt` declarados nas linhas de palavra, para o verso das frases
        # achar. Preenchidos em `adicionar`, antes de qualquer nota sair.
        self._externo_de_sinal = {}
        self._externo_de_texto = {}

    # -- mídia -------------------------------------------------------------

    def _pares(self, videos):
        """Baixa e converte; devolve pares (mp4, webm) prontos para o template."""
        pares = []
        for nome in videos:
            mp4, webm = self.recursos.obter_par(nome)
            if mp4 is None:
                continue
            self.arquivos.add(str(mp4))
            if webm:
                self.arquivos.add(str(webm))
            pares.append((mp4.name, webm.name if webm else None))
        return pares

    def _par_externo(self, externo):
        """Baixa e recorta o `@yt` da linha. Devolve (mp4, webm) ou None.

        None quando não havia link ou quando o download falhou — nos dois casos
        o card segue com o que o INES tiver. A falha fica no relatório.
        """
        if externo is None:
            return None
        mp4, webm = self.externos.obter_par(externo)
        if mp4 is None:
            return None
        self.arquivos.add(str(mp4))
        self.arquivos.add(str(webm))
        return mp4.name, webm.name

    def _externo_do_sinal(self, sinal):
        """O `@yt` declarado para este sinal em alguma lista, se houver."""
        return self._externo_de_sinal.get(_chave_de_sinal(sinal))

    def _sinais_de(self, resolucao):
        """Os sinais distintos de uma resolução, na ordem do dicionário.

        Homônimos são um Sinal cada; variantes do mesmo sinal são vários
        verbetes num Sinal só, e não podem virar duas opções de escolha.
        """
        sinais = []
        for verbete in resolucao.verbetes:
            sinal = self._por_verbete.get((verbete["ident"], verbete.get("video")))
            if sinal is None or any(s is sinal for s in sinais):
                continue
            sinais.append(sinal)
        return sinais

    def _campos_auxiliares(self, verbete):
        return {
            "origem": self.tabelas["origem"].get(str(verbete.get("origem")), {}).get("nome", ""),
        }

    # -- notas -------------------------------------------------------------

    def _nota_de_sinal(self, sinal, tags_extra=(), externo=None):
        chave = ("sinal", sinal.ident, sinal.videos[0] if sinal.videos else sinal.palavra)
        if chave in self._vistos:
            return
        self._vistos.add(chave)

        tags = set(sinal.tags) | set(tags_extra)
        observacao = ""

        # O link tem prioridade: quem escreveu `@yt` numa palavra que o INES já
        # cobre quis justamente outro vídeo. O do INES sai do card, mas o fato
        # de existir fica registrado na observação e na tag.
        par = self._par_externo(externo)
        if par:
            pares = [par]
            tags.add(youtube.TAG)
            observacao = f"Vídeo de fonte externa, não do INES: {externo.rotulo}."
            if sinal.videos:
                observacao += " O INES também tem vídeo próprio para esta palavra."
        else:
            pares = self._pares(sinal.videos)

        nome = indice.raiz(sinal.palavra)
        if not pares and nome in MESMO_SINAL:
            alvo, nota = MESMO_SINAL[nome]
            blocos, _ = self._componentes([alvo])
            if blocos:
                pares = [(blocos[0][1], blocos[0][2])]
                tags.add(TAG_MESMO_SINAL)
                observacao = f"{observacao} {nota}".strip()
                self.relatorio.mesmo_sinal.append(f"{sinal.palavra} = {alvo}")

        if nome in NOTAS_DE_SINAL:
            observacao = f"{observacao} {NOTAS_DE_SINAL[nome]}".strip()

        if not pares:
            # O aviso já vai dentro do campo Videos (modelo.html_videos); aqui só
            # falta marcar a tag para dar pra filtrar no Anki.
            tags.add(TAG_FALTA_VIDEO)
            self.relatorio.falta_video.append(sinal.palavra)
        if grupos.TAG_VIDEO_SUSPEITO in tags:
            self.relatorio.video_suspeito.append(sinal.palavra)
        if grupos.TAG_GRUPO_MISTO in tags:
            self.relatorio.grupo_misto.append(sinal.palavra)

        aux = self._campos_auxiliares(sinal.principal)
        self.baralho.add_note(
            modelo.criar_nota(
                palavra=sinal.palavra,
                pares_video=pares,
                descricao=sinal.descricao,
                observacao=observacao,
                tags=tags,
                guid=modelo.guid_para(
                    sinal.ident, sinal.videos[0] if sinal.videos else sinal.palavra
                ),
                **aux,
            )
        )
        self.relatorio.conta(sinal.tipo)

    def _componentes(self, nomes):
        """Resolve os componentes de um composto pelo nome exato do verbete.

        Devolve `[(rótulo, mp4, webm)]` na ordem de sinalização, mais a lista dos
        que não foram encontrados — um nome digitado errado na tabela viraria uma
        omissão silenciosa, e isso o projeto não faz.
        """
        blocos, faltando = [], []
        for nome in nomes:
            resolucao = self.indice.resolver(nome)
            if not resolucao:
                faltando.append(nome)
                continue
            verbete = resolucao.verbetes[0]
            pares = self._pares([verbete["video"]]) if verbete.get("video") else []
            if not pares:
                faltando.append(nome)
                continue
            blocos.append((indice.raiz(verbete["palavra"]).strip(), pares[0][0], pares[0][1]))
        return blocos, faltando

    def _nota_ausente(self, texto, tags_extra=(), externo=None):
        """Palavra sem verbete próprio: nota marcada, nunca omissão.

        Se for um composto conhecido, o card mostra os vídeos dos componentes em
        sequência — dá o que estudar hoje, em vez de esperar a gravação da aula.
        Um `@yt` na linha passa na frente de tudo: com o sinal inteiro em vídeo,
        não há motivo para montá-lo peça por peça.
        """
        chave = ("ausente", texto.lower())
        if chave in self._vistos:
            return
        self._vistos.add(chave)

        minusculo = texto.strip().lower()
        composto = COMPOSTOS.get(minusculo)
        correcao = CORRECOES.get(minusculo)
        par = self._par_externo(externo)

        # Sem explicação própria, o card diz o que fazer a respeito — e isso
        # muda conforme haja vídeo: mandar gravar na aula um sinal que já está
        # ali em cima seria mandar refazer trabalho feito.
        padrao = "Sem verbete no dicionário do INES." if par else \
            "Sem verbete no dicionário do INES — preencher com material da aula."
        observacao = (composto.nota if composto else None) or \
            (correcao.nota if correcao else None) or \
            NOTAS_DE_LINGUA.get(minusculo) or padrao

        resolucao = self.indice.resolver(texto)
        if resolucao.motivo:
            observacao = f"{resolucao.motivo.capitalize()}. {observacao}"

        componentes, faltando = ([], [])
        tags = set(tags_extra)
        if composto:
            tags.add(TAG_COMPOSTO)
            if composto.confirmar:
                tags.add(TAG_CONFIRMAR_SINAL)
                observacao += (
                    " Confirme na aula: "
                    + ", ".join(composto.confirmar)
                    + "."
                )
        elif correcao:
            tags.add(TAG_FORMA_INCORRETA)

        if par:
            tags.add(youtube.TAG)
            observacao += f" Vídeo de fonte externa: {externo.rotulo}."
        elif composto or correcao:
            componentes, faltando = self._componentes(
                composto.sinais if composto else correcao.sinais
            )
            if faltando:
                observacao += f" Sem vídeo para: {', '.join(faltando)}."

        # Com vídeo — próprio ou dos componentes — já há o que praticar, então
        # não é `falta-video`: nada precisa ser gravado para o card funcionar.
        if not componentes and not par:
            tags.add(TAG_FALTA_VIDEO)
            self.relatorio.falta_video.append(texto)

        self.baralho.add_note(
            modelo.criar_nota(
                palavra=texto.strip().upper(),
                pares_video=[par] if par else [],
                descricao="",
                observacao=observacao,
                tags=tags,
                guid=modelo.guid_para(f"ausente:{minusculo}", texto),
                componentes=componentes,
            )
        )
        self.relatorio.nao_resolvidos.append(texto)
        if componentes:
            resumo = f"{texto} = {' + '.join(r for r, _, _ in componentes)}"
            destino = self.relatorio.correcoes if correcao else self.relatorio.compostos
            destino.append(resumo)
        self.relatorio.conta("ausente")

    def _nota_frase(self, item):
        vocabulario, ausentes, de_fora, escolhas = [], [], [], []
        interrogativos = []
        for palavra in indice.palavras_da_frase(item.texto):
            resolucao = self.indice.resolver(palavra)
            sinais = self._sinais_de(resolucao)

            # Decidido antes dos ramos abaixo porque vale para todos: a palavra
            # é interrogativa mesmo quando o vídeo vem de fora ou não existe.
            eh_interrogativo = (
                indice.raiz(sinais[0].palavra) in INTERROGATIVOS if sinais
                else indice.normalizar(palavra) in INTERROGATIVOS
            )
            destino = interrogativos if eh_interrogativo else vocabulario

            # O clipe de fora vem antes do INES, como no card da palavra: quem
            # foi atrás de outro vídeo quer estudar aquele, e ver dois vídeos
            # diferentes do mesmo sinal — um aqui, outro no card — só atrapalha.
            # É também o que salva palavra cujo vídeo do INES dá 404 (DORMIR),
            # que sem isso cairia no aviso mesmo tendo clipe declarado.
            externo = (
                self._externo_do_sinal(sinais[0]) if sinais
                else self._externo_de_texto.get(indice.normalizar(palavra))
            )
            par = self._par_externo(externo)
            if par:
                destino.append((palavra, par[0], par[1]))
                de_fora.append(palavra)
                continue

            # Mais de um sentido: o card mostra todos, lado a lado e rotulados
            # pela descrição do INES, para você escolher na hora de sinalizar.
            # Escolher aqui pelo primeiro seria chutar — "qual" tem três
            # sentidos, e o primeiro é o de identificar um local.
            blocos = []
            for sinal in sinais:
                pares = self._pares(sinal.videos[:1])
                if pares:
                    blocos.append((sinal, pares[0]))

            if not blocos:
                ausentes.append(palavra)
                continue
            if len(blocos) == 1:
                (_, (mp4, webm)), = blocos
                destino.append((palavra, mp4, webm))
                continue

            escolhas.append(f"{palavra} ({len(blocos)})")
            for sinal, (mp4, webm) in blocos:
                destino.append((_rotulo_de_sentido(palavra, sinal), mp4, webm))

        # O interrogativo vai para o fim, que é o lugar dele em LIBRAS. Sai daqui
        # e não da leitura da frase para que a frente do card continue sendo o
        # português como se escreve — quem muda de ordem é o vocabulário do
        # verso, que é o que se pratica sinalizando.
        reordenou = bool(interrogativos) and bool(vocabulario)
        vocabulario += interrogativos

        tags = {"frase"}
        observacao = ""
        if ausentes:
            nota = [NOTAS_DE_LINGUA[p.lower()] for p in ausentes if p.lower() in NOTAS_DE_LINGUA]
            observacao = " ".join(nota)

        if reordenou:
            observacao = (observacao + " " if observacao else "") + NOTA_ORDEM_LIBRAS

        if de_fora:
            tags.add(youtube.TAG)
            observacao = (observacao + " " if observacao else "") + \
                "Vocabulário com vídeo de fora do INES: " + ", ".join(de_fora) + "."

        if escolhas:
            tags.add(TAG_ESCOLHER_SENTIDO)
            observacao = (observacao + " " if observacao else "") + \
                "O INES tem mais de um sinal para " + ", ".join(escolhas) + \
                " — o verso mostra todos, escolha pelo sentido da frase."
            self.relatorio.escolha_de_sentido.append(
                f"{item.texto} — {', '.join(escolhas)}"
            )

        # A frase inteira sinalizada vale mais que a soma do vocabulário: ela
        # mostra a ordem e o encadeamento, que é justamente o que o card pede.
        # Por isso vem no topo, antes das palavras soltas.
        par = self._par_externo(item.video)
        if par:
            vocabulario.insert(0, ("a frase sinalizada", par[0], par[1]))
            tags.add(youtube.TAG)
            observacao = (observacao + " " if observacao else "") + \
                f"Vídeo de fonte externa: {item.video.rotulo}."

        self.baralho.add_note(
            modelo.criar_nota_frase(
                frase=item.texto,
                vocabulario=vocabulario,
                ausentes=ausentes,
                observacao=observacao,
                tags=tags,
            )
        )
        self.relatorio.conta("frase")

    def _notas_de_numero(self, texto):
        """Números viram contraste quando o INES oferece mais de um verbete."""
        verbetes = numeros.verbetes_do_numero(texto, self.indice)
        if not verbetes:
            self._nota_ausente(texto, {numeros.TAG_NUMERO})
            return

        if numeros.eh_contraste(verbetes):
            blocos = []
            for verbete in verbetes:
                pares = self._pares([verbete["video"]]) if verbete.get("video") else []
                rotulo = f"{verbete['palavra']} — {numeros.rotulo_funcao(verbete)}"
                blocos.append(
                    (rotulo, pares[0][0] if pares else None, pares[0][1] if pares else None)
                )
            self.baralho.add_note(
                modelo.criar_nota_contraste(
                    numero=texto,
                    titulo="Qual é qual?",
                    blocos=blocos,
                    explicacao=numeros.EXPLICACAO_CONTRASTE,
                    tags={numeros.TAG_NUMERO},
                    chave=f"contraste-{texto}",
                )
            )
            self.relatorio.conta("número (contraste)")
            return

        sinal = self._por_verbete.get((verbetes[0]["ident"], verbetes[0].get("video")))
        if sinal:
            self._nota_de_sinal(sinal, {numeros.TAG_NUMERO})

    def _notas_ordinais(self):
        """O trêmulo dos ordinais não existe no INES: cards marcados para gravar."""
        for numero in numeros.ordinais_pendentes():
            self.baralho.add_note(
                modelo.criar_nota_contraste(
                    numero=f"{numero}º",
                    titulo="Ordinal — como se faz?",
                    blocos=[],
                    explicacao=f"Ordinal de {numero}: mesma mão do cardinal {numero}, "
                               "com movimento trêmulo.",
                    observacao=numeros.OBSERVACAO_ORDINAL,
                    tags={numeros.TAG_NUMERO, numeros.TAG_ORDINAL, TAG_FALTA_VIDEO},
                    chave=numeros.chave_ordinal(numero),
                )
            )
            self.relatorio.falta_video.append(f"{numero}º (ordinal)")
            self.relatorio.conta("ordinal (sem vídeo)")

    # -- fluxo -------------------------------------------------------------

    def _indexar_externos(self, itens):
        """Registra os `@yt` das linhas de palavra, antes de gerar nota nenhuma.

        Um clipe declarado em `dormir @yt ...` vale para o sinal, não para a
        linha: as frases que usam DORMIR devem mostrar o mesmo vídeo que o card
        da palavra. Sem esta passagem prévia isso não teria como funcionar — as
        listas de frases são lidas antes das de vocabulário, e o clipe ainda não
        seria conhecido na hora de montar o verso.
        """
        for item in itens:
            if item.video is None or item.tipo == listas.TIPO_FRASE:
                continue
            resolucao = self.indice.resolver(item.texto)
            if not resolucao:
                # Palavra sem verbete (LIBRAS, PAMONHA): a chave é o texto.
                self._externo_de_texto.setdefault(
                    indice.normalizar(item.texto), item.video
                )
                continue
            # Mesma regra do card: o link vale para o primeiro verbete resolvido.
            verbete = resolucao.verbetes[0]
            sinal = self._por_verbete.get((verbete["ident"], verbete.get("video")))
            if sinal is not None:
                self._externo_de_sinal.setdefault(_chave_de_sinal(sinal), item.video)

    def adicionar(self, itens):
        self._indexar_externos(itens)
        for item in itens:
            if item.problema:
                self.relatorio.problemas.append(f"{item.local} — {item.problema}")

            if item.tipo == listas.TIPO_FRASE:
                self._nota_frase(item)
                continue

            if numeros.no_escopo(item.texto):
                self._notas_de_numero(item.texto)
                continue

            resolucao = self.indice.resolver(item.texto)
            if not resolucao:
                self._nota_ausente(item.texto, externo=item.video)
                continue

            # Homônimos viram um card cada. O `@yt` vai para o primeiro: um link
            # só não tem como dizer qual dos sentidos ele ilustra, e espalhá-lo
            # por todos poria o mesmo vídeo em cards de significados diferentes.
            #
            # Contar sinais e não verbetes: variantes do mesmo sinal (VOVÓ-VOVÔ1
            # e VOVÓ-VOVÔ2) são dois verbetes e um card só, e aí não há escolha
            # nenhuma a avisar.
            atingidos = []
            for verbete in resolucao.verbetes:
                sinal = self._por_verbete.get((verbete["ident"], verbete.get("video")))
                if sinal is None or any(s is sinal for s in atingidos):
                    continue
                self._nota_de_sinal(sinal, externo=item.video if not atingidos else None)
                atingidos.append(sinal)

            if item.video and len(atingidos) > 1:
                self.relatorio.problemas.append(
                    f"{item.local} — '{item.texto}' vira {len(atingidos)} cards no "
                    f"INES; o @yt foi para o primeiro ({atingidos[0].palavra})"
                )

    def escrever(self, destino):
        self.relatorio.midia = self.recursos.resumo()
        self.relatorio.externos = self.externos.resumo()
        pacote = genanki.Package(self.baralho, media_files=sorted(self.arquivos))
        pacote.write_to_file(str(destino))
        return destino

    # -- cache ---------------------------------------------------------------

    def limpar_cache(self):
        """Apaga o cache que o baralho recém-escrito não usa.

        Só pode ser chamada depois de `escrever`, e só quando a geração cobriu
        todas as listas: `self.arquivos` é a resposta para "o que tem uso", e
        numa geração de lista avulsa ela descreve um pedaço do baralho, não o
        baralho. Quem decide isso é a linha de comando, que sabe o que foi
        pedido; aqui não há como distinguir.

        Duas coisas saem, por motivos diferentes:

          fontes    o vídeo inteiro de onde os clipes foram recortados. Depois
                    do clipe pronto ele não tem uso nenhum — só voltaria a ter
                    se um trecho `@yt` mudasse, e aí baixa de novo.
          órfãos    vídeo em cache que nenhuma nota referencia mais, de palavra
                    que saiu das listas ou que passou a usar vídeo de fora.
                    Inclui os `.tmp` de uma escrita interrompida.

        O dicionário em `.cache/dados` nunca entra: ele é a base, não mídia de
        card, e rebaixá-lo custa muito mais que os poucos MB que ocupa.
        """
        usados = {_caminho(a) for a in self.arquivos}
        fontes, orfaos, bytes_apagados = 0, [], 0

        for arquivo in sorted(config.CACHE_EXTERNOS.glob("*")):
            if not arquivo.is_file():
                continue
            bytes_apagados += arquivo.stat().st_size
            arquivo.unlink()
            fontes += 1

        for arquivo in sorted(config.CACHE_VIDEOS.glob("*")):
            if not arquivo.is_file() or _caminho(arquivo) in usados:
                continue
            bytes_apagados += arquivo.stat().st_size
            arquivo.unlink()
            # Os dois formatos do mesmo sinal viram uma linha só no relatório:
            # o que interessa é qual palavra saiu, não que ela tinha mp4 e webm.
            orfaos.append(arquivo.stem)

        self.relatorio.cache = {
            "fontes": fontes,
            "orfaos": sorted(set(orfaos)),
            "megabytes": bytes_apagados / 1048576,
        }
        return self.relatorio.cache

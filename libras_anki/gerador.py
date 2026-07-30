"""Montagem do baralho a partir das listas de estudo.

Regra que atravessa tudo: nada é descartado em silêncio. Palavra sem verbete,
vídeo que não baixou, palavra da frase sem sinal — tudo vira nota marcada por
tag, para você filtrar no Anki (`tag:falta-video`) e completar com material da
aula. Pular em silêncio esconderia a lacuna; abortar impediria de estudar o
resto.
"""

from collections import namedtuple

import genanki

from . import grupos, indice, ines, listas, midia, modelo, numeros

TAG_FALTA_VIDEO = "falta-video"
TAG_COMPOSTO = "composto"
TAG_CONFIRMAR_SINAL = "confirmar-sinal"

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
    # "tenha" e "um" não entram: o primeiro não tem verbete, o segundo é
    # numeral e não cabe aqui. A ordem exata desta é a menos certa das seis.
    "tenha um bom fim de semana": Composto(
        "Expressão composta. Os componentes que o INES tem estão aí, mas "
        "confirme a sequência na aula.",
        ["BOM1", "FIM", "SEMANA"],
        ["BOM", "a sequência"],
    ),
}

# Explicações de casos que parecem lacuna mas são gramática da língua.
NOTAS_DE_LINGUA = {
    "ela": "Em LIBRAS o pronome de 3ª pessoa é apontar e não marca gênero: "
           "'ele' e 'ela' são o mesmo sinal.",
    # TEU/TUA e VOSSO/VOSSA não têm verbete no INES (nem um masculino para
    # servir de âncora, como SEU/DELE/NOSSO têm). Descrição da apostila, para
    # gravar na aula.
    "teu": "Sem verbete no INES. Configuração de mão em P, apontando para a "
           "pessoa com quem se fala (apostila).",
    "tua": "Sem verbete no INES. Configuração de mão em P, apontando para a "
           "pessoa com quem se fala (apostila).",
    "vosso": "Sem verbete no INES. Indica plural: configuração de mão em P "
             "(apostila).",
    "vossa": "Sem verbete no INES. Indica plural: configuração de mão em P "
             "(apostila).",
}


class Relatorio:
    """Contabiliza o que entrou no baralho e o que precisa de atenção."""

    def __init__(self):
        self.notas = 0
        self.por_tipo = {}
        self.nao_resolvidos = []
        self.falta_video = []
        self.compostos = []
        self.video_suspeito = []
        self.grupo_misto = []
        self.midia = {}

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
        bloco("VÍDEO SUSPEITO", self.video_suspeito,
              "o mesmo arquivo é usado por outro verbete — confira antes de decorar")
        bloco("GRUPO MISTO", self.grupo_misto,
              "parte do grupo tem o mesmo sentido, parte não — separados por precaução")
        return "\n".join(linhas)


class Gerador:
    def __init__(self, nome_baralho=modelo.NOME_BARALHO):
        self.verbetes = ines.obter_verbetes()
        self.tabelas = ines.obter_tabelas()
        self.indice = indice.Indice(self.verbetes)
        self.sinais, self.anomalias = grupos.construir(self.verbetes)
        self.recursos = midia.Midia()
        self.baralho = modelo.criar_baralho(nome_baralho)
        self.relatorio = Relatorio()
        self.arquivos = set()
        self._vistos = set()

        # Do verbete de volta para o Sinal que o contém.
        self._por_verbete = {}
        for sinal in self.sinais:
            for verbete in sinal.verbetes:
                self._por_verbete[(verbete["ident"], verbete.get("video"))] = sinal

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

    def _campos_auxiliares(self, verbete):
        return {
            "origem": self.tabelas["origem"].get(str(verbete.get("origem")), {}).get("nome", ""),
        }

    # -- notas -------------------------------------------------------------

    def _nota_de_sinal(self, sinal, tags_extra=()):
        chave = ("sinal", sinal.ident, sinal.videos[0] if sinal.videos else sinal.palavra)
        if chave in self._vistos:
            return
        self._vistos.add(chave)

        pares = self._pares(sinal.videos)
        tags = set(sinal.tags) | set(tags_extra)

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

    def _nota_ausente(self, texto, tags_extra=()):
        """Palavra sem verbete próprio: nota marcada, nunca omissão.

        Se for um composto conhecido, o card mostra os vídeos dos componentes em
        sequência — dá o que estudar hoje, em vez de esperar a gravação da aula.
        """
        chave = ("ausente", texto.lower())
        if chave in self._vistos:
            return
        self._vistos.add(chave)

        minusculo = texto.strip().lower()
        composto = COMPOSTOS.get(minusculo)
        observacao = (composto.nota if composto else None) or \
            NOTAS_DE_LINGUA.get(minusculo) or \
            "Sem verbete no dicionário do INES — preencher com material da aula."

        resolucao = self.indice.resolver(texto)
        if resolucao.motivo:
            observacao = f"{resolucao.motivo.capitalize()}. {observacao}"

        componentes, faltando = ([], [])
        tags = set(tags_extra)
        if composto:
            componentes, faltando = self._componentes(composto.sinais)
            tags.add(TAG_COMPOSTO)
            if composto.confirmar:
                tags.add(TAG_CONFIRMAR_SINAL)
                observacao += (
                    " Confirme na aula: "
                    + ", ".join(composto.confirmar)
                    + "."
                )
            if faltando:
                observacao += f" Sem vídeo para: {', '.join(faltando)}."

        # Com os componentes disponíveis já há o que praticar, então não é
        # `falta-video`: nada precisa ser gravado para o card funcionar.
        if not componentes:
            tags.add(TAG_FALTA_VIDEO)
            self.relatorio.falta_video.append(texto)

        self.baralho.add_note(
            modelo.criar_nota(
                palavra=texto.strip().upper(),
                pares_video=[],
                descricao="",
                observacao=observacao,
                tags=tags,
                guid=modelo.guid_para(f"ausente:{minusculo}", texto),
                componentes=componentes,
            )
        )
        self.relatorio.nao_resolvidos.append(texto)
        if componentes:
            self.relatorio.compostos.append(
                f"{texto} = {' + '.join(r for r, _, _ in componentes)}"
            )
        self.relatorio.conta("ausente")

    def _nota_frase(self, item):
        vocabulario, ausentes = [], []
        for palavra in indice.palavras_da_frase(item.texto):
            resolucao = self.indice.resolver(palavra)
            if not resolucao:
                ausentes.append(palavra)
                continue
            sinal = self._por_verbete.get(
                (resolucao.verbetes[0]["ident"], resolucao.verbetes[0].get("video"))
            )
            videos = sinal.videos[:1] if sinal else []
            pares = self._pares(videos)
            if pares:
                vocabulario.append((palavra, pares[0][0], pares[0][1]))
            else:
                ausentes.append(palavra)

        tags = {"frase"}
        observacao = ""
        if ausentes:
            nota = [NOTAS_DE_LINGUA[p.lower()] for p in ausentes if p.lower() in NOTAS_DE_LINGUA]
            observacao = " ".join(nota)

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

    def adicionar(self, itens):
        for item in itens:
            if item.tipo == listas.TIPO_FRASE:
                self._nota_frase(item)
                continue

            if numeros.no_escopo(item.texto):
                self._notas_de_numero(item.texto)
                continue

            resolucao = self.indice.resolver(item.texto)
            if not resolucao:
                self._nota_ausente(item.texto)
                continue

            for verbete in resolucao.verbetes:
                sinal = self._por_verbete.get((verbete["ident"], verbete.get("video")))
                if sinal:
                    self._nota_de_sinal(sinal)

    def escrever(self, destino):
        self.relatorio.midia = self.recursos.resumo()
        pacote = genanki.Package(self.baralho, media_files=sorted(self.arquivos))
        pacote.write_to_file(str(destino))
        return destino

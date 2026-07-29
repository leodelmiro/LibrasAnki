"""Montagem do baralho a partir das listas de estudo.

Regra que atravessa tudo: nada é descartado em silêncio. Palavra sem verbete,
frase sem glosa, vídeo que não baixou — tudo vira nota marcada por tag, para
você filtrar no Anki (`tag:falta-video`, `tag:falta-glosa`) e completar com
material da aula. Pular em silêncio esconderia a lacuna; abortar impediria de
estudar o resto.
"""

import genanki

from . import grupos, indice, ines, listas, midia, modelo, numeros

TAG_FALTA_VIDEO = "falta-video"
TAG_FALTA_GLOSA = "falta-glosa"

# Itens que não existem em dicionário nenhum por serem compostos. Verificado no
# INES e no Spread the Sign: os dois omitem os mesmos. Não é falha de busca.
COMPOSTOS = {
    "bom dia": "Composto: sinaliza-se BOM + DIA em sequência. Não existe como "
               "verbete único — nem no INES, nem no Spread the Sign.",
    "boa tarde": "Composto: BOA + TARDE em sequência.",
    "boa noite": "Composto: BOA + NOITE em sequência.",
    "de nada": "Expressão composta, sem verbete próprio no INES.",
    "até amanhã": "Composto: ATÉ + AMANHÃ.",
    "tenha um bom fim de semana": "Expressão composta.",
}

# Explicações de casos que parecem lacuna mas são gramática da língua.
NOTAS_DE_LINGUA = {
    "ela": "Em LIBRAS o pronome de 3ª pessoa é apontar e não marca gênero: "
           "'ele' e 'ela' são o mesmo sinal.",
}


class Relatorio:
    """Contabiliza o que entrou no baralho e o que precisa de atenção."""

    def __init__(self):
        self.notas = 0
        self.por_tipo = {}
        self.nao_resolvidos = []
        self.falta_video = []
        self.falta_glosa = []
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
              "geradas assim mesmo, com tag falta-video")
        bloco("SEM GLOSA", self.falta_glosa,
              "o card de gramática não é criado até a glosa ser preenchida")
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
            "mao": self.tabelas["mao"].get(str(verbete.get("mao")), {}).get("ordem", ""),
            "classe": self.tabelas["classes"].get(str(verbete.get("classe")), {}).get("nome", ""),
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
        observacao = ""

        if not pares:
            tags.add(TAG_FALTA_VIDEO)
            observacao = "Sem vídeo disponível — preencher com material da aula."
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
                exemplo=sinal.exemplo,
                glosa=sinal.libras,
                observacao=observacao,
                tags=tags,
                guid=modelo.guid_para(
                    sinal.ident, sinal.videos[0] if sinal.videos else sinal.palavra
                ),
                **aux,
            )
        )
        self.relatorio.conta(sinal.tipo)

    def _nota_ausente(self, texto, tags_extra=()):
        """Palavra sem verbete: nota marcada, nunca omissão."""
        chave = ("ausente", texto.lower())
        if chave in self._vistos:
            return
        self._vistos.add(chave)

        minusculo = texto.strip().lower()
        observacao = COMPOSTOS.get(minusculo) or NOTAS_DE_LINGUA.get(minusculo) or (
            "Sem verbete no dicionário do INES — preencher com material da aula."
        )
        resolucao = self.indice.resolver(texto)
        if resolucao.motivo:
            observacao = f"{resolucao.motivo.capitalize()}. {observacao}"

        self.baralho.add_note(
            modelo.criar_nota(
                palavra=texto.strip().upper(),
                pares_video=[],
                descricao="",
                observacao=observacao,
                tags={TAG_FALTA_VIDEO, *tags_extra},
                guid=modelo.guid_para(f"ausente:{minusculo}", texto),
            )
        )
        self.relatorio.nao_resolvidos.append(texto)
        self.relatorio.falta_video.append(texto)
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
        if not item.glosa:
            tags.add(TAG_FALTA_GLOSA)
            self.relatorio.falta_glosa.append(item.texto)

        observacao = ""
        if ausentes:
            nota = [NOTAS_DE_LINGUA[p.lower()] for p in ausentes if p.lower() in NOTAS_DE_LINGUA]
            observacao = " ".join(nota)

        self.baralho.add_note(
            modelo.criar_nota_frase(
                frase=item.texto,
                glosa=item.glosa,
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

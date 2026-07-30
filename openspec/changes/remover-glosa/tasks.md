## 1. Linha de base

- [x] 1.1 Gerar o baralho completo e salvar o relatório atual como referência (hoje: 123 notas, 25 em SEM GLOSA, contagem por tipo `ausente`/`frase`/`homonimo`/`simples`/`variante`)
- [x] 1.2 Confirmar que nenhuma lista tem glosa preenchida após `|`, inclusive arquivos locais não versionados em `listas/`

## 2. Modelo (`libras_anki/modelo.py`)

- [x] 2.1 Remover `"Glosa"` de `CAMPOS_FRASE`
- [x] 2.2 Remover o template `Gramatica` de `TEMPLATES_FRASE`, deixando só `Sinalizar`
- [x] 2.3 Remover o bloco `{{#Glosa}}...{{/Glosa}}` do verso do template `Sinalizar`
- [x] 2.4 Remover o parâmetro `glosa` de `criar_nota_frase` e o valor correspondente em `fields`
- [x] 2.5 Remover as regras CSS `.glosa` e `.nightMode .glosa`, agora sem uso
- [x] 2.6 Atualizar o docstring do módulo, que ainda descreve a gramática como existente para frases

## 3. Gerador (`libras_anki/gerador.py`)

- [x] 3.1 Remover a constante `TAG_FALTA_GLOSA`
- [x] 3.2 Remover `self.falta_glosa` de `Relatorio.__init__` e o bloco `"SEM GLOSA"` de `Relatorio.texto`
- [x] 3.3 Remover de `_nota_frase` a leitura de `item.glosa`, a marcação da tag e o argumento passado a `criar_nota_frase`
- [x] 3.4 Atualizar o docstring do módulo, que cita `tag:falta-glosa` como exemplo de filtro

## 4. Listas (`libras_anki/listas.py`)

- [x] 4.1 Remover a constante `SEPARADOR_GLOSA` e o bloco de `_interpretar` que separa o texto da glosa
- [x] 4.2 Remover o ramo `if glosa: return Item(..., TIPO_FRASE, ...)` que usa a glosa como sinal de tipo
- [x] 4.3 Remover o parâmetro e o atributo `glosa` de `Item`
- [x] 4.4 Atualizar o docstring do módulo, que documenta a sintaxe `|` no formato das linhas

## 5. Conteúdo das listas

- [x] 5.1 Remover de `listas/frases-apostila.txt` o cabeçalho que explica a sintaxe `|` e a menção a `falta-glosa`
- [x] 5.2 Remover de `listas/frases-pronomes.txt` o cabeçalho que explica a sintaxe `|`
- [x] 5.3 Corrigir em `listas/saudacoes.txt` a afirmação "não existem como verbete em dicionário nenhum": dizer que faltam no INES e no Spread the Sign, e que o VLibras registra `BOM_DIA`, `BOA_NOITE` e `DE_NADA` como sinal
- [x] 5.4 Corrigir em `listas/dias-da-semana.txt` a menção a `TERÇA-FEIRA` e `FIM DE SEMANA`, que existem no VLibras como `TERÇA_FEIRA` e `FIM_DE_SEMANA`
- [x] 5.5 Corrigir em `listas/pronomes-possessivos.txt` a afirmação sobre `TEU`/`TUA`/`VOSSO`/`VOSSA`, que existem no VLibras

## 6. README

- [x] 6.1 Remover a linha `Ele está cansado | ELE CANSAD@` da tabela "Formato das linhas" e a menção a frase com glosa
- [x] 6.2 Remover `falta-glosa` da tabela de tags
- [x] 6.3 Atualizar "O que o baralho tem": frase passa a ter um card, sem gramática
- [x] 6.4 Remover o parágrafo "Quando a professora passar a glosa de uma frase, edite a linha e regere"
- [x] 6.5 Acrescentar nota sobre cards órfãos: remover um template não apaga os cards já existentes no Anki, é preciso apagá-los pelo navegador

## 7. Verificação

- [x] 7.1 Gerar o baralho completo e conferir que nenhum erro é levantado
- [x] 7.2 Comparar o relatório com a linha de base de 1.1: a contagem por tipo MUST ser idêntica, e o bloco "SEM GLOSA" MUST ter desaparecido
- [x] 7.3 Confirmar que nenhuma nota de frase gera mais de um card, inspecionando o `.apkg` gerado
- [x] 7.4 Buscar por `glosa` em `libras_anki/` e confirmar que só restam ocorrências intencionais (nenhuma)
- [ ] 7.5 Reimportar no Anki, buscar `card:Gramatica` no navegador e apagar os cards órfãos — **passo manual no app, só você pode fazer**

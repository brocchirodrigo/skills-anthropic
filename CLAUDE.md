# Catálogo de skills oficiais da Anthropic

Este repositório publica, pelo GitHub Pages, um catálogo pesquisável das skills de autoria da Anthropic (sozinha ou em parceria declarada). Cada skill tem resumo em português, área, links para o GitHub, comando de instalação no Claude Code e indicação de conectores e comandos que ela usa.

O site é o arquivo `index.html` na raiz da branch `main`. Ele é gerado por script: nunca edite o `index.html` à mão.

Responda e escreva tudo em português do Brasil.

## Estrutura

1. `index.html`: página publicada. Gerada por `scripts/catalog.py build`.
2. `src/template.html`: código da página (HTML, CSS e JavaScript). Contém os marcadores `__DATA__` (dados das skills) e `__DATE__` (data do levantamento). Toda mudança visual ou de comportamento é feita aqui.
3. `data/skills.json`: a base do catálogo. Uma entrada por skill, com o resumo em português (`pt`) e a área (`a`) escritos à mão e o resto preenchido pelo script.
4. `data/report.json`: relatório da última atualização (novas, alteradas, removidas, pendentes).
5. `config/sources.json`: marketplaces oficiais que o script lê, pastas de terceiros e ruídos conhecidos na detecção de pacotes.
6. `config/areas.json`: área padrão por plugin (`"repositorio:plugin"`) e por skill do repositório `anthropics/skills`.
7. `scripts/catalog.py`: script de atualização. Só precisa de Python 3.9 ou mais novo e git, sem bibliotecas externas.
8. `.cache/`: clones dos repositórios de origem. Fica fora do git.

## Como atualizar o catálogo

Quando for pedido para atualizar a lista de skills, siga estes passos na ordem.

1. Rode a varredura:
   ```bash
   python3 scripts/catalog.py update
   ```
   Ele clona ou atualiza os repositórios em `.cache/`, encontra as skills, aplica as regras de autoria, junta duplicadas e grava `data/skills.json` e `data/report.json`. Resumos e áreas que já existiam são preservados.
2. Leia o resumo que o comando imprime e rode:
   ```bash
   python3 scripts/catalog.py check
   ```
   Ele lista o que precisa de atenção: skills novas (`novo`), skills cuja descrição mudou (`descricao_mudou`), resumos faltando e áreas faltando. As removidas aparecem em `data/report.json`, no campo `removidos`.
3. Resolva cada pendência em `data/skills.json`:
   1. Skill nova: escreva o `pt` seguindo as regras de resumo abaixo e confira a `a` (área).
   2. Descrição mudou: compare `en_anterior` com `en` e ajuste o `pt` se o sentido mudou.
   3. Área faltando: use uma das áreas existentes. Se a skill vier de um plugin novo, acrescente também o plugin em `config/areas.json`, para as próximas skills dele já virem com área.
   4. Depois de revisar uma entrada, apague os campos `status` e `en_anterior` dela.
4. Gere a página:
   ```bash
   python3 scripts/catalog.py build
   ```
   O build falha se alguma skill ainda estiver sem `pt` ou sem `a`. Não use `--allow-missing` para publicar.
5. Confira o resultado antes de commitar:
   1. O total do relatório bate com o esperado e as skills novas aparecem na página.
   2. Abra o `index.html` no navegador e verifique que não há erro no console, que a busca e os filtros funcionam e que o botão "Usar no Claude Code" de uma skill nova copia o comando certo.
   3. Rode `git diff --stat` e confirme que só mudaram `index.html`, `data/` e, se for o caso, `config/areas.json`.
6. Faça o commit e o push (veja as regras de commit abaixo). O GitHub Pages republica sozinho em um ou dois minutos.

Se o relatório mostrar `removidos`, confirme no GitHub que a skill saiu mesmo do repositório de origem antes de publicar.

## Regras de inclusão (quem entra no catálogo)

Estas regras foram decididas pelo dono do repositório. Não mude sem ele pedir.

1. Só entram skills com autoria declarada da Anthropic, sozinha ou em parceria. Exemplos aceitos: "Anthropic", "Anthropic FSI", "Anthropic / Model Context Protocol".
2. O autor vale nesta ordem: o `author` da entrada no marketplace, depois o `author` do `plugin.json`.
3. Se o plugin não declara autor, vale o dono do marketplace, desde que ele seja a Anthropic (nome com "Anthropic" ou e-mail `@anthropic.com`) e o plugin esteja dentro do próprio repositório, fora das pastas de terceiros.
4. Pastas de terceiros (`external_plugins`, `partner-built`) nunca entram sem autor da Anthropic declarado. Por isso os canais Discord, iMessage e Telegram ficam de fora.
5. Plugins só de parceiros (Zoom, Salesforce, LSEG, S&P/Kensho, Apollo, Common Room, Tribe AI e outros) ficam de fora.
6. Plugins da Anthropic que existem no repositório mas não estão em nenhum marketplace (como o `example-plugin`) entram, e a página mostra que eles não têm comando de instalação.
7. Quando um marketplace oficial aponta para um plugin da Anthropic em outro repositório (como o `mcp-apps`, em `modelcontextprotocol/ext-apps`), o script clona esse repositório e inclui as skills. A página marca a coautoria.
8. A mesma skill (mesmo nome e mesma descrição) em vários plugins aparece uma vez só, com todos os lugares onde está.
9. Para incluir um marketplace oficial novo, acrescente o repositório em `config/sources.json`, em `marketplaces`.

Na data do último levantamento eram 351 arquivos `SKILL.md`, que viraram 300 skills distintas e 295 nomes distintos, em 7 repositórios.

## Regras dos resumos em português (`pt`)

1. Uma frase, no máximo duas, com até uns 180 caracteres.
2. Comece com verbo na terceira pessoa do presente: "Gera", "Revisa", "Monta", "Ajuda a".
3. Diga o que a skill faz para quem usa, não como ela funciona por dentro.
4. Mantenha nomes de produtos, padrões e siglas como estão (SQL, KYC, MCP, Excel, HubSpot). Traduza o resto.
5. Sem adjetivos de propaganda ("poderosa", "completa") e sem travessões.
6. Siga o tom das entradas que já existem em `data/skills.json`.

## Áreas (`a`)

Use uma das áreas existentes: Adoção de IA, Busca corporativa, Ciências da vida, Claude Code, Comportamento, Dados, Design, Desenvolvimento, Documentos, Escrita, Finanças e contabilidade, Hardware, Jurídico, Marketing, Matemática, Mercado financeiro, Operações, Pequenas empresas, Produtividade, Produto, RH, Skills e plugins, Suporte ao cliente, Vendas.

Só crie uma área nova se nenhuma servir, e avise o dono do repositório.

## Campos de cada skill em `data/skills.json`

1. `n`: nome da skill (do frontmatter do `SKILL.md`).
2. `pt`: resumo em português. Escrito à mão.
3. `en`: descrição original em inglês. Vem do script.
4. `a`: área. Escrita à mão ou vinda de `config/areas.json`.
5. `loc`: lugares onde a skill está. Cada um tem `o` (dono no GitHub), `r` (repositório), `path` (pasta da skill), `p` (plugin), `m` (marketplace, ou `null`), `mr` (repositório do marketplace), `au` (autor declarado) e `co` (coautoria).
6. `con`: conectores (servidores MCP) que o plugin adiciona ao ser instalado, lidos do `.mcp.json` do plugin.
7. `pkg`: pacotes de software citados nos blocos de código das instruções. Detecção heurística.
8. `cmd`: scripts que acompanham a skill.
9. `sh`: se as instruções trazem blocos de comandos de terminal.
10. `dep`: dependências de fora da pasta da skill: `plugin_root` (usa `${CLAUDE_PLUGIN_ROOT}`), `parent_path` (lê arquivos com `../`) e `connector_placeholder` (usa marcadores `~~` de conector).
11. `status` e `en_anterior`: só aparecem em pendências. Apague depois de revisar.

Não edite à mão os campos que o script preenche (`en`, `loc`, `con`, `pkg`, `cmd`, `sh`, `dep`): eles são recalculados a cada `update`.

## O que a página faz (não pode quebrar)

Ao mexer em `src/template.html`, mantenha tudo isto funcionando:

1. Cabeçalho de largura total com o título, a linha "Por Rodrigo Brocchi", o texto de apresentação e os contadores (skills, nomes diferentes, áreas, repositórios).
2. Busca por nome, descrição, área, plugin e nome de conector.
3. Filtros de área, repositório, autoria ("Só Anthropic" e "Anthropic + parceiro"), conectores ("Com conectores" e "Sem conectores") e comandos ("Roda comandos" e "Não roda comandos"), com a quantidade em cada opção.
4. Linha de contagem que mostra os filtros ativos e o botão "Limpar filtros".
5. A página sempre abre sem filtros. Filtros não são guardados no navegador.
6. Em cada skill:
   1. Nome clicável que copia o nome.
   2. Botão "Acrescentar seleção", que vira "Remover da seleção".
   3. Resumo, chips de repositório e plugin, selo de coautoria, número de conectores e etiqueta "roda comandos".
   4. Botões "Abrir no navegador" (pasta da skill no GitHub) e "Usar no Claude Code" (copia os comandos `/plugin marketplace add` e `/plugin install`).
   5. Blocos recolhidos "O que instala e executa", "Como instalar" e "Descrição original (inglês)".
7. Seleção guardada no navegador (`localStorage`, chave `selecao-skills`), que continua ao trocar filtros e ao reabrir a página. Abaixo dos contadores ficam a lista separada por vírgulas e os botões "Copiar pedido para o Claude Code", "Filtrar selecionadas" (vira "Mostrar todas"), "Copiar lista" e "Limpar seleção".
8. "Filtrar selecionadas" limpa a busca e os filtros e mostra só as selecionadas.
9. "Copiar pedido para o Claude Code" gera um texto que manda o Claude Code baixar cada skill selecionada do GitHub e instalar em `~/.claude/skills/<nome>/`. O texto pede para trazer junto os arquivos referenciados com `../`, instalar o plugin inteiro quando a skill depender de `${CLAUDE_PLUGIN_ROOT}` e não instalar conectores nem pacotes sem perguntar.
10. Toda cópia para a área de transferência tem plano B: se o navegador bloquear, o texto fica selecionado e aparece "use Cmd+C".
11. Visual: tema escuro único, baseado no tema escuro do site rodrigobrocchi.com.br. Fundo `#09090b`, cartões `#18181b`, bordas brancas a 10%, destaque vermelho em oklch, fonte Roboto em tudo, botões e chips arredondados, "Anthropic" do título com brilho em degradê (parado para quem desativou animações).
12. Funciona em celular a partir de 390 px de largura, sem rolagem horizontal.

Depois de mexer no template, rode o `build` e teste no navegador os itens que a mudança tocou.

## Segurança

1. O repositório é público. Nunca grave tokens, chaves, e-mails pessoais ou dados de conta em nenhum arquivo.
2. A página não chama nenhuma API. Só carrega a fonte do Google Fonts e tem links para o github.com. Mantenha assim.
3. O GitHub Pages publica direto da branch `main`. Não crie workflows de Actions com secrets para isso.
4. Não commite a pasta `.cache/`.

## Commits

1. Use Conventional Commits (https://www.conventionalcommits.org/en/v1.0.0/#specification), com a mensagem em português. Exemplos: `chore: atualiza catálogo de skills`, `feat: adiciona filtro por conector`, `fix: corrige comando de instalação de plugins sem marketplace`.
2. Mensagens objetivas e profissionais, sem travessões.
3. Não mencione modelos de IA nem ferramentas de IA na mensagem e não adicione linhas de coautoria (como `Co-Authored-By`).
4. Na atualização periódica do catálogo, o corpo do commit lista as skills novas, alteradas e removidas.

## Limitações conhecidas

1. Conectores são lidos por plugin: todas as skills de um plugin mostram a mesma lista, mesmo que cada uma use só parte dela.
2. A detecção de pacotes e comandos é heurística. Quando aparecer um falso positivo recorrente, acrescente em `package_noise`, no `config/sources.json`.
3. Instalar só a pasta de uma skill pode não bastar quando ela depende de arquivos do plugin. O pedido gerado pela página já orienta o Claude Code a instalar o plugin inteiro nesses casos.
4. O script não lista sozinho todos os repositórios da organização `anthropics`. Ele parte dos marketplaces de `config/sources.json` e segue as referências deles. Se a Anthropic lançar um marketplace novo, ele precisa ser acrescentado lá.

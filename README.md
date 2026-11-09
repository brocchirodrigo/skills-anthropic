# Skills oficiais da Anthropic

Catálogo pesquisável, em português, das skills de autoria da Anthropic publicadas nos repositórios oficiais do GitHub.

**Acesse:** https://brocchirodrigo.github.io/skills-anthropic/

Cada skill aparece com um resumo em português, a área de uso, o link para a pasta no GitHub, o comando de instalação no Claude Code e o que ela instala ou executa (conectores, pacotes e scripts).

> Projeto pessoal e independente, sem vínculo com a Anthropic. As skills, as descrições originais e os direitos sobre elas pertencem aos respectivos repositórios de origem.

## O que tem no catálogo

No levantamento de 09/11/2026 eram **300 skills** (295 nomes distintos), vindas de 351 arquivos `SKILL.md` em 7 repositórios e organizadas em 24 áreas.

| Repositório | Skills |
| --- | ---: |
| [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | 181 |
| [anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) | 53 |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 34 |
| [anthropics/skills](https://github.com/anthropics/skills) | 17 |
| [anthropics/claude-for-financial-advisors](https://github.com/anthropics/claude-for-financial-advisors) | 8 |
| [modelcontextprotocol/ext-apps](https://github.com/modelcontextprotocol/ext-apps) | 4 |
| [anthropics/life-sciences](https://github.com/anthropics/life-sciences) | 3 |

Os números da última atualização ficam em [`data/report.json`](data/report.json).

## Como usar a página

1. **Busque** por nome, descrição, área, plugin ou conector.
2. **Filtre** por área, repositório, autoria (só Anthropic ou Anthropic com parceiro), conectores e se a skill roda comandos no terminal.
3. **Instale uma skill:** o botão "Usar no Claude Code" copia os comandos `/plugin marketplace add` e `/plugin install` para colar no Claude Code. "Abrir no navegador" leva à pasta da skill no GitHub.
4. **Monte uma seleção:** marque várias skills com "Acrescentar seleção". A seleção fica salva no navegador e o botão "Copiar pedido para o Claude Code" gera um texto que pede ao Claude Code para baixar cada skill em `~/.claude/skills/<nome>/`, sem instalar conectores nem pacotes sem perguntar antes.
5. **Confira antes de instalar:** cada skill tem os blocos "O que instala e executa", "Como instalar" e "Descrição original (inglês)".

A página é um único arquivo HTML estático. Não chama nenhuma API, não usa rastreamento e só carrega a fonte do Google Fonts.

## Quem entra no catálogo

Entram apenas skills com autoria declarada da Anthropic, sozinha ou em parceria (por exemplo "Anthropic FSI" ou "Anthropic / Model Context Protocol").

1. O autor vale nesta ordem: o `author` da entrada no marketplace e, depois, o `author` do `plugin.json`.
2. Se o plugin não declara autor, vale o dono do marketplace, desde que seja a Anthropic e o plugin esteja no próprio repositório, fora das pastas de terceiros.
3. Plugins de parceiros e pastas de terceiros (`external_plugins`, `partner-built`) ficam de fora quando não têm a Anthropic como autora.
4. Plugins da Anthropic que não estão em nenhum marketplace também entram. A página avisa que eles não têm comando de instalação.
5. Quando um marketplace oficial aponta para um plugin da Anthropic em outro repositório, as skills dele entram com a coautoria marcada.
6. A mesma skill (mesmo nome e mesma descrição) publicada em vários plugins aparece uma vez só, com todos os lugares onde está.

## Como atualizar

Requisitos: Python 3.9 ou mais novo e git. Não há dependências externas.

```bash
python3 scripts/catalog.py update   # clona os repositórios em .cache/ e atualiza data/skills.json e data/report.json
python3 scripts/catalog.py check    # lista skills novas, descrições alteradas e resumos ou áreas faltando
python3 scripts/catalog.py build    # gera o index.html a partir de src/template.html e data/skills.json
```

Entre o `check` e o `build`, as pendências são resolvidas à mão em `data/skills.json`: escrever o resumo em português (`pt`), conferir a área (`a`) e apagar os campos `status` e `en_anterior` das entradas revisadas. O `build` falha enquanto houver skill sem resumo ou sem área.

O `update` aceita `--no-fetch` para reaproveitar o que já está em `.cache/` sem baixar de novo.

Depois do commit na branch `main`, o GitHub Pages republica a página em um ou dois minutos.

O passo a passo completo, as regras de escrita dos resumos e a lista de áreas estão no [`CLAUDE.md`](CLAUDE.md).

## Estrutura do repositório

```
.
├── index.html            página publicada (gerada pelo build, não editar à mão)
├── src/template.html     HTML, CSS e JavaScript da página
├── data/
│   ├── skills.json       base do catálogo, uma entrada por skill
│   └── report.json       relatório da última atualização
├── config/
│   ├── sources.json      marketplaces lidos, pastas de terceiros e ruídos conhecidos
│   └── areas.json        área padrão por plugin e por skill
├── scripts/catalog.py    script de atualização (update, check, build)
├── .github/              modelos de issue e de pull request
├── CONTRIBUTING.md       guia de contribuição
├── CLAUDE.md             instruções de manutenção
└── LICENSE               licença MIT
```

A pasta `.cache/`, criada pelo `update`, guarda os clones dos repositórios de origem e não vai para o git.

### Campos de `data/skills.json`

| Campo | Conteúdo | Origem |
| --- | --- | --- |
| `n` | nome da skill | script |
| `pt` | resumo em português | à mão |
| `en` | descrição original em inglês | script |
| `a` | área | à mão ou `config/areas.json` |
| `loc` | lugares onde a skill está (repositório, plugin, marketplace, autor, coautoria) | script |
| `con` | conectores (servidores MCP) que o plugin adiciona | script |
| `pkg` | pacotes citados nas instruções | script |
| `cmd` | scripts que acompanham a skill | script |
| `sh` | se as instruções trazem comandos de terminal | script |
| `dep` | dependências de fora da pasta da skill | script |

## Limitações

1. Conectores são lidos por plugin: todas as skills de um plugin mostram a mesma lista, mesmo que cada uma use só parte dela.
2. A detecção de pacotes e comandos é heurística e pode ter falsos positivos.
3. Instalar só a pasta de uma skill pode não bastar quando ela depende de arquivos do plugin. O pedido gerado pela página orienta o Claude Code a instalar o plugin inteiro nesses casos.
4. O script parte dos marketplaces listados em `config/sources.json`. Um marketplace oficial novo precisa ser acrescentado lá para entrar no catálogo.

## Como contribuir

Contribuições são bem-vindas. Encontrou uma skill faltando, um resumo errado ou um problema na página? [Abra uma issue](https://github.com/brocchirodrigo/skills-anthropic/issues/new/choose) escolhendo um dos modelos:

1. Erro na página
2. Skill faltando ou incluída por engano
3. Correção de resumo ou área
4. Sugestão de melhoria

Para mandar um pull request, leia antes o [guia de contribuição](CONTRIBUTING.md). Ele explica como preparar o ambiente, as regras dos resumos e o checklist de cada tipo de mudança.

Problemas no conteúdo de uma skill (instruções ou scripts com erro) devem ser relatados no repositório de origem dela.

## Licença

O código e os resumos em português deste repositório estão sob a [licença MIT](LICENSE).

As skills, as descrições originais em inglês e os demais arquivos dos repositórios de origem seguem as licenças desses repositórios.

## Autor

Feito por [Rodrigo Brocchi](https://rodrigobrocchi.com.br).

# Como contribuir

Obrigado pelo interesse em melhorar o catálogo. Dá para ajudar de dois jeitos: abrindo uma issue ou mandando um pull request.

## Antes de abrir uma issue

1. Busque a skill na [página do catálogo](https://brocchirodrigo.github.io/skills-anthropic/) e veja se já existe uma [issue aberta](https://github.com/brocchirodrigo/skills-anthropic/issues) sobre o mesmo assunto.
2. Problemas no conteúdo de uma skill (instruções erradas, script que não funciona) devem ser relatados no repositório de origem dela, não aqui. Este repositório cuida só do catálogo.
3. Use um dos modelos de issue:
   1. **Erro na página:** algo não funciona no site (busca, filtros, botões de copiar, layout no celular).
   2. **Skill faltando ou incluída por engano:** uma skill da Anthropic que não aparece, ou uma que aparece mas não deveria.
   3. **Correção de resumo ou área:** o resumo em português está errado ou a skill está na área errada.
   4. **Sugestão de melhoria:** uma ideia nova para a página ou para o script.

As regras de quem entra no catálogo estão no [README](README.md#quem-entra-no-catálogo) e foram decididas pelo dono do repositório. Para propor uma mudança nelas, abra uma issue de sugestão antes de mexer no código.

## Preparando o ambiente

Você precisa de Python 3.9 ou mais novo e git. Não há dependências externas.

```bash
git clone https://github.com/<seu-usuario>/skills-anthropic.git
cd skills-anthropic
git checkout -b fix/resumo-da-skill-x
```

## Tipos de mudança

### Corrigir resumo ou área de uma skill

1. Edite só os campos `pt` (resumo) e `a` (área) da skill em `data/skills.json`.
2. Siga as regras de resumo:
   1. Uma frase, no máximo duas, com até uns 180 caracteres.
   2. Comece com verbo na terceira pessoa do presente: "Gera", "Revisa", "Monta", "Ajuda a".
   3. Diga o que a skill faz para quem usa, não como ela funciona por dentro.
   4. Mantenha nomes de produtos, padrões e siglas como estão (SQL, KYC, MCP, Excel). Traduza o resto.
   5. Sem adjetivos de propaganda ("poderosa", "completa") e sem travessões.
3. Use uma das áreas que já existem. A lista está no [`CLAUDE.md`](CLAUDE.md#áreas-a).
4. Não altere os campos preenchidos pelo script (`n`, `en`, `loc`, `con`, `pkg`, `cmd`, `sh`, `dep`). Eles são recalculados a cada atualização.
5. Rode `python3 scripts/catalog.py build` e inclua o `index.html` gerado no pull request.

### Mudar a página

1. Edite `src/template.html`. Nunca edite o `index.html` à mão, porque ele é sobrescrito pelo build.
2. Rode `python3 scripts/catalog.py build`.
3. Abra o `index.html` no navegador e confira que não há erro no console e que a busca, os filtros, a seleção e os botões de copiar continuam funcionando.
4. Teste também em largura de celular (390 px), sem rolagem horizontal.
5. A página não pode chamar nenhuma API nem carregar scripts de fora. Só a fonte do Google Fonts e os links para o github.com são permitidos.

A lista completa do que a página precisa manter funcionando está no [`CLAUDE.md`](CLAUDE.md#o-que-a-página-faz-não-pode-quebrar).

### Mudar o script ou a configuração

1. Descreva no pull request o que muda no resultado (skills que entram, saem ou mudam de dados).
2. Rode `update`, `check` e `build` e confira o `data/report.json`.
3. Falsos positivos recorrentes na detecção de pacotes vão em `package_noise`, no `config/sources.json`.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/) com a mensagem em português, objetiva e sem travessões.

```
fix: corrige resumo da skill pdf
feat: adiciona filtro por conector
chore: atualiza catálogo de skills
docs: explica como rodar o build
```

## Pull requests

1. Um assunto por pull request.
2. Preencha o checklist do modelo de pull request.
3. Se o pull request resolve uma issue, cite o número dela (`Closes #12`).

## Segurança

1. O repositório é público. Nunca grave tokens, chaves, e-mails pessoais ou dados de conta em nenhum arquivo.
2. Não crie workflows do GitHub Actions com secrets. O GitHub Pages publica direto da branch `main`.
3. Não commite a pasta `.cache/`, que guarda os clones dos repositórios de origem.

## Licença

Ao contribuir, você concorda que sua contribuição seja distribuída sob a [licença MIT](LICENSE) do projeto.

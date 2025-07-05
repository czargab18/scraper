# Guia de Mensagens de Commit para Copilot - Projeto Scraper

Este documento orienta humanos e IA (como o GitHub Copilot) a gerar mensagens de commit eficientes, consistentes e automatizáveis neste repositório de web scraping.

---

## 🎯 Formato Padrão Recomendado

```
tipo(escopo): descrição curta

Descrição longa detalhada (opcional).

Fixes #n / Closes #n (opcional)
BREAKING CHANGE: <descrição> (se aplicável)
```

- **tipo:** Veja lista e exemplos abaixo.  
- **escopo:** (opcional) Parte específica afetada (spider, pipeline, middleware, item, etc).
- **descrição curta:** Resuma a alteração em até 50 caracteres, voz ativa e verbo no presente.
- **descrição longa:** Contexto, motivação, impactos, detalhes técnicos.
- **referência a issues:** "Fixes #123" ou "Closes #123" fecha issues automaticamente.
- **breaking change:** Use "BREAKING CHANGE:" para mudanças incompatíveis.

---

## 🏷️ Tipos de Commit e Exemplos

> Copilot: sempre prefira um tipo da lista abaixo; use exemplos como modelo!

- **feat:** Nova funcionalidade  
  `feat(spider): adiciona spider para coleta de departamentos`

- **feature:** Nova funcionalidade (alternativo a feat)  
  `feature(pipeline): implementa pipeline de validação de dados`

- **fix:** Correção de bug  
  `fix(docentes): corrige seletor CSS para dados de docentes`

- **docs:** Mudanças na documentação  
  `docs(readme): atualiza guia de instalação do Scrapy`

- **style:** Mudança de formatação, lint, indentação (sem alterar lógica)  
  `style(spider): ajusta formatação PEP8`

- **refactor:** Refatoração sem alterar funcionalidade  
  `refactor(items): simplifica estrutura de dados`

- **test:** Adiciona ou ajusta testes  
  `test(spider): adiciona testes unitários para docentes spider`

- **ci:** Integração contínua (workflows, pipelines, etc)  
  `ci(github-actions): adiciona verificação de qualidade de código`

- **chore:** Tarefas de build, configs, dependências  
  `chore(deps): atualiza requirements.txt`

- **perf:** Melhoria de performance  
  `perf(spider): otimiza rate limiting e concurrent requests`

- **cleanup:** Remove código morto, logs, variáveis não usadas  
  `cleanup: remove prints de debug obsoletos`

- **folders:** Criação, remoção ou renomeação de diretórios  
  `folders: reorganiza estrutura de dados coletados`

- **files:** Criação, remoção ou renomeação de arquivos  
  `files: move mock data para pasta dedicada`

- **spider:** Mudanças específicas em spiders  
  `spider(docentes): adiciona extração de telefone e email`

- **pipeline:** Mudanças em pipelines de processamento  
  `pipeline(validation): implementa validação de dados obrigatórios`

- **middleware:** Mudanças em middlewares  
  `middleware(headers): adiciona rotação de user agents`

- **data:** Mudanças em estruturas de dados ou arquivos de dados  
  `data(json): atualiza schema de dados de docentes`

- **config:** Mudanças em configurações do Scrapy  
  `config(settings): ajusta delay entre requests`

- **mock:** Adição ou atualização de dados de teste/mock  
  `mock(sigaa): adiciona página HTML de exemplo`

- **scraping:** Melhorias gerais no processo de scraping  
  `scraping(sigaa): implementa retry para falhas de conexão`

- **outros tipos comuns:**  
  - **merge:** Mesclagem de branches  
  - **hotfix:** Correção crítica  
  - **build:** Mudanças em build ou dependências externas  
  - **wip:** Trabalho em andamento  
  - **deps:** Atualização de dependências  
  - **infra:** Infraestrutura  
  - **init:** Commit inicial  
  - **typo:** Correção de erros de digitação  
  - **comment:** Comentários no código  
  - **optimize:** Otimização  
  - **deprecate:** Depreciação  
  - **legal:** Licenciamento ou questões legais  

---

## 🛠️ Boas Práticas para o Copilot

- Sempre respeite o formato: `<tipo>(<escopo>): <descrição curta>`.
- Prefira mensagens específicas e objetivas.  
  - **Ruim:** `fix: várias correções`  
  - **Bom:** `fix(docentes): corrige extração de departamento quando campo está vazio`
- Use o escopo sempre que possível: spider, pipeline, middleware, item, data, config.
- Nunca use pronomes pessoais ("eu", "nós"). Sempre foque na ação.
- Evite termos genéricos como "melhoria", "atualização", "alteração".
- Se exceder 50 caracteres na descrição curta, resuma e transfira detalhes para a descrição longa.
- A descrição longa deve explicar o porquê, o que e o como da alteração.
- Para correções de issues, use "Fixes #num" ou "Closes #num" para fechar automaticamente issues relacionadas.
- Para breaking changes, detalhe claramente o impacto após "BREAKING CHANGE:".
- Liste no corpo do commit as principais mudanças (bullet points) se apropriado.
- Não use "commit", "mensagem de commit" ou "alteração" na descrição curta.

---

## ⚡️ Outras Orientações para o Copilot

Além de gerar commits e descrições de commits, siga estas diretrizes para automatizar e padronizar outras tarefas do repositório:

### Pull Requests

- Escreva títulos objetivos para PRs no mesmo padrão dos commits (`tipo(escopo): descrição curta`).
- Gere descrições claras, explicando o que foi feito, por que e os impactos.
- Liste mudanças principais em tópicos.
- Relacione issues com `Closes #num` quando aplicável.

### Issues

- Siga templates claros para bugs, features e dúvidas.
- Gere títulos automáticos objetivos e específicos.
- Use estrutura de tópicos na descrição para facilitar entendimento.

### Comentários em Código

- Sugira comentários construtivos, claros e objetivos em revisões.
- Explique bugs, dúvidas e sugestões de melhoria de forma direta.

### Releases

- Sugira descrições de releases resumindo novidades, correções e breaking changes.
- Destaque os pontos principais em tópicos.

### Changelogs

- Gere changelogs automáticos agrupando por tipo: features, fixes, refactors etc.
- Inclua referências a issues/PRs relevantes.

### Nomes de Branches

#### Estrutura e padrões das `branchs`
- `main`: branch de **produção**, apenas código final.
- `develop`: branch de **desenvolvimento**, para integração de features.
- `feature/*`: branches de **funcionalidades** (ex: `feature/docentes-spider`, `feature/validation-pipeline`).
- `fix/*`: branches de **correções** (ex: `fix/css-selector`, `fix/rate-limiting`).
- `hotfix/*`: branches de **correções críticas** (ex: `hotfix/production-error`).

**Padronize nomes de branches** conforme exemplos acima.

### Documentação

- Gere documentação padrão para spiders, pipelines e middlewares.
- Sempre inclua: propósito, parâmetros, dados extraídos e exemplo de uso.

---

## ➕ Reforços e Boas Práticas Adicionais

### 🔒 Segurança

- Nunca sugira inclusão de credenciais, tokens ou senhas no código ou nos commits.
- Prefira sugerir o uso de variáveis de ambiente para dados sensíveis.
- Documente práticas de rate limiting para evitar sobrecarga dos servidores.

### 🕷️ Scrapy Best Practices

- Sempre respeite o robots.txt dos sites.
- Implemente delays apropriados entre requests.
- Use user agents realistas e rotativos.
- Trate erros de conexão e timeouts adequadamente.

### 📁 Organização de Projeto

- Siga a estrutura de diretórios do Scrapy.
- Organize dados coletados em estruturas lógicas (`data/spider_name/`).
- Mantenha arquivos mock separados dos dados reais.

### 🧪 Testes

- Nomeie arquivos de teste conforme padrão Python (`test_*.py`).
- Sempre sugira criar ou atualizar testes ao adicionar ou modificar spiders.
- Use dados mock para testes consistentes.

### 📋 Convenções de Código

- Siga PEP8 para formatação Python.
- Use docstrings para documentar classes e métodos.
- Prefira código limpo, modular e reutilizável.

### 🚨 Mensagens de Erro e Logs

- Sugira logs informativos para debugging.
- Use níveis de log apropriados (DEBUG, INFO, WARNING, ERROR).
- Inclua contexto suficiente nos logs para debugging.

### 📚 Exemplos e Snippets

- Inspire-se nos exemplos deste guia e nos arquivos do projeto.
- Sugira snippets comuns ao contexto de web scraping.

### 🏷️ Labels & Automatizações

- Sugira labels padrão para issues/PRs (ex: `spider`, `pipeline`, `bug`, `enhancement`).
- Recomende automações via GitHub Actions para testes e qualidade de código.

### 🎯 Fluxo de Trabalho

- Oriente o fluxo para abertura de PRs, revisões e merges conforme políticas do projeto.
- Sempre lembre de atualizar a documentação após mudanças relevantes.

### 📈 Métricas e Monitoramento

- Sugira integração com ferramentas de monitoramento de scrapers.
- Recomende inclusão de métricas de coleta (items/minute, success rate, etc.).

---

## 🎓 Contexto Específico do Projeto Scraper

Este é um projeto de **web scraping educacional/acadêmico** focado na **coleta de dados do SIGAA (Sistema de Gestão Acadêmica)** usando **Scrapy**. Considere estes aspectos específicos:

### Tecnologias Principais
- **Scrapy:** Framework principal para web scraping
- **Python:** Linguagem de programação
- **JSON:** Formato de dados coletados
- **uv:** Gerenciador de dependências Python

### Estrutura de Diretórios
- `sigaa/`: Projeto Scrapy principal
  - `spiders/`: Spiders para coleta de dados
  - `data/`: Dados coletados organizados
  - `mock/`: Dados de teste e páginas de exemplo
- `aprender/`: Módulos de aprendizado Python

### Escopos Específicos Recomendados
- **docentes**: Para spider de docentes
- **departamentos**: Para dados de departamentos
- **sigaa**: Para configurações gerais do SIGAA
- **spider**: Para mudanças gerais em spiders
- **pipeline**: Para pipelines de processamento
- **middleware**: Para middlewares
- **data**: Para estruturas de dados
- **mock**: Para dados de teste
- **config**: Para configurações

### Exemplos de Commits Contextualizados
```
feat(docentes): adiciona extração de dados de contato
fix(spider): corrige seletor CSS para departamentos
docs(readme): atualiza instruções de instalação
perf(pipeline): otimiza processamento de dados JSON
chore(deps): atualiza Scrapy para versão 2.11
```

### Exemplo Completo de Commit com Descrição Longa
```
feat(docentes): implementa spider completo para coleta de dados

Adiciona spider robusto para extrair informações de docentes do SIGAA:

- Spider: Implementa navegação paginada e extração de dados estruturados
- Items: Define estrutura de dados com campos obrigatórios e opcionais  
- Pipeline: Adiciona validação e limpeza de dados coletados
- Settings: Configura rate limiting e headers apropriados

- Mock: Adiciona página HTML de exemplo para testes
- Data: Organiza saída em formato JSON estruturado
- Tests: Implementa testes unitários para validação

O spider extrai: nome, departamento, email, telefone, titulação e área de pesquisa.

Implementa retry automático para falhas de rede e respeita robots.txt.
```

---

## 🎯 Convenções Específicas do Projeto

#### Estrutura de Arquivos
- Use **snake_case** para nomes de arquivos Python
- Mantenha dados organizados em `data/spider_name/`
- Use `mock/` para dados de teste e páginas HTML de exemplo

#### Nomenclatura
- **Classes Spider:** Use sufixo `Spider` (ex: `DocentesSpider`)
- **Items:** Use sufixo `Item` (ex: `DocenteItem`)
- **Pipelines:** Use sufixo `Pipeline` (ex: `ValidationPipeline`)
- **Arquivos de dados:** Use nomes descritivos (ex: `docentes_2025.json`)

#### Scrapy/Spiders
- Sempre teste spiders com dados mock antes de executar
- Mantenha `settings.py` consistente e documentado
- Use campos obrigatórios em Items para validação
- Documente seletores CSS/XPath complexos

#### Python/Processamento
- Use type hints quando possível
- Adicione docstrings para classes e métodos principais
- Valide dados de entrada em pipelines
- Mantenha separação clara entre extração e processamento

---

## 🤖 Dicas Extras para IAs

- Use exemplos reais do projeto (spiders, items, seletores) ao gerar escopo.
- Quando criar commits para múltiplos componentes Scrapy, prefira escopo mais amplo como "sigaa" ou "core".
- Sempre que possível, relacione o commit a um issue ou PR.
- Para grandes refatorações, use a seção longa para explicar impactos na coleta de dados.
- Para automações, inclua o tipo "ci", "config" ou "chore" conforme o contexto.

---

## 🤖 Marcação de Código Gerado por IA

### Padrão Obrigatório para Identificação de IA

**TODOS os arquivos, trechos de código, spiders ou pipelines gerados por IA devem ser marcados conforme os padrões abaixo:**

#### Para Arquivos Python (Spiders, Pipelines, Items)
```python
"""
Generated by AI (GitHub Copilot)
Date: 2025-07-04
Description: Spider para coleta de dados de docentes do SIGAA
"""

# Ou para trechos específicos:
# AI-GENERATED START - Extração de dados de contato
def parse_contact_info(self, response):
    # código gerado por IA
    pass
# AI-GENERATED END
```

#### Para Arquivos de Configuração (settings.py, scrapy.cfg)
```python
# Generated by AI (GitHub Copilot)
# Date: 2025-07-04
# Description: Configurações otimizadas para scraping do SIGAA

# Ou para seções específicas:
# AI-GENERATED START - Rate limiting settings
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = 0.5
# AI-GENERATED END
```

#### Para Arquivos JSON de Dados
```json
{
  "_metadata": {
    "generated_by": "AI (GitHub Copilot)",
    "date": "2025-07-04",
    "description": "Estrutura de dados para docentes"
  },
  "data": []
}
```

#### Para Documentação (.md, .txt)
```markdown
<!-- 
AI-GENERATED CONTENT
Generated by: GitHub Copilot
Date: 2025-07-04
Description: Documentação de uso do spider de docentes
-->

Ou para seções específicas:

<!-- AI-GENERATED START - Instruções de instalação -->
Conteúdo gerado por IA...
<!-- AI-GENERATED END -->
```

### Regras de Marcação

1. **Spiders Completamente Gerados por IA:**
   - Incluir docstring no topo da classe
   - Especificar data de geração
   - Incluir breve descrição da funcionalidade de scraping

2. **Métodos/Funções Parciais Gerados por IA:**
   - Usar comentários `AI-GENERATED START/END`
   - Incluir descrição do que foi gerado
   - Manter o código humano sem marcação

3. **Informações Obrigatórias:**
   - Identificação: "Generated by AI (GitHub Copilot)"
   - Data de geração no formato YYYY-MM-DD
   - Descrição breve da funcionalidade

4. **Casos Especiais:**
   - **Seletores CSS/XPath:** Sempre marcar se gerados por IA
   - **Pipelines de processamento:** Indicar claramente origem
   - **Configurações críticas:** Documentar origem das configurações

### Benefícios da Marcação

- **Transparência:** Clara identificação de código gerado por IA
- **Manutenibilidade:** Facilita debugging de spiders e pipelines
- **Auditoria:** Permite rastreamento de lógica de scraping
- **Compliance:** Atende requisitos de transparência
- **Colaboração:** Ajuda outros desenvolvedores a entender a origem do código

### Exemplos Práticos do Projeto

```python
"""
Generated by AI (GitHub Copilot)
Date: 2025-07-04
Description: Spider para coleta de dados de docentes do SIGAA/UnB
"""

class DocentesSpider(scrapy.Spider):
    name = 'docentes'
    
    def parse(self, response):
        # AI-GENERATED START - Extração de lista de docentes
        docentes = response.css('.docente-item')
        for docente in docentes:
            # ... lógica gerada por IA
        # AI-GENERATED END
        
        # Paginação implementada manualmente
        next_page = response.css('.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

```python
# Generated by AI (GitHub Copilot)
# Date: 2025-07-04
# Description: Configurações otimizadas para scraping acadêmico

# AI-GENERATED START - Settings de performance
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5
# AI-GENERATED END

# Configuração manual de headers
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Academic Research Bot (+https://unb.br)'
}
```

---

## 🔧 Troubleshooting e Debugging

#### Problemas Comuns
- **Spider não encontra elementos:** Verificar seletores CSS/XPath
- **Rate limiting/bloqueio:** Ajustar delays e headers
- **Dados inconsistentes:** Implementar validação em pipelines  
- **Timeouts frequentes:** Configurar retry middleware

#### Debugging Scrapy
- Use `scrapy shell` para testar seletores
- Ative logs DEBUG para análise detalhada
- Teste com dados mock antes de executar em produção
- Use `response.css()` e `response.xpath()` no shell

#### Logs e Monitoramento
- Configure níveis de log apropriados (INFO para produção)
- Monitore métricas de coleta (items/min, errors, retries)
- Mantenha logs de execução para análise posterior
- Documente erros recorrentes e suas soluções

#### Performance
- Monitore uso de memória em spiders grandes
- Otimize seletores CSS para melhor performance
- Use concurrent requests com moderação
- Implemente cache quando apropriado

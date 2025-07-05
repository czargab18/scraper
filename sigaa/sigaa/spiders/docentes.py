# cd sigaa
#
# === COMANDO PRINCIPAL (TUDO EM UM) ===
# uv run scrapy runspider .\sigaa\spiders\docentes_completo.py -o data\docentes\docentes_test.jsonl
#
# === COMANDOS INDIVIDUAIS (OPCIONAIS) ===
# uv run scrapy crawl departamentos -o data/departamentos/lista_departamentos.jsonl
# uv run scrapy crawl docentes_paginas -o data/docentes/paginas_baixadas.jsonl
# uv run scrapy crawl docentes_completo -o data/docentes/docentes_completo.jsonl
#
# === GERENCIADOR DE CHECKPOINT ===
# python .\sigaa\spiders\docentes_completo.py gerenciar
import re
import json
import scrapy
import os
import sys
from pathlib import Path
import time
from scrapy.http import HtmlResponse


# ================================================================================
# FUNÇÕES DE GERENCIAMENTO DE CHECKPOINT (Integradas)
# ================================================================================

def salvar_checkpoint(departamento_atual, total_departamentos, docentes_coletados, timestamp=None):
    """Salva checkpoint do progresso atual"""
    checkpoint_file = Path("data/docentes/checkpoint.json")
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

    checkpoint_data = {
        'departamento_atual': departamento_atual,
        'total_departamentos': total_departamentos,
        'docentes_coletados': docentes_coletados,
        'timestamp': timestamp or time.time(),
        'versao_checkpoint': '1.0'
    }

    try:
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar checkpoint: {e}")
        return False


def carregar_checkpoint():
    """Carrega checkpoint se existir"""
    checkpoint_file = Path("data/docentes/checkpoint.json")

    if not checkpoint_file.exists():
        return None

    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar checkpoint: {e}")
        return None


def mostrar_status_checkpoint():
    """Mostra status do checkpoint atual"""
    checkpoint = carregar_checkpoint()

    if not checkpoint:
        print("📄 Nenhum checkpoint encontrado")
        return False

    print("📊 STATUS DO CHECKPOINT:")
    print("=" * 50)
    print(f"📋 Departamento atual: {checkpoint.get('departamento_atual', 0)}")
    print(
        f"📈 Total de departamentos: {checkpoint.get('total_departamentos', 'N/A')}")
    print(
        f"👥 Docentes coletados: {len(checkpoint.get('docentes_coletados', []))}")

    timestamp = checkpoint.get('timestamp')
    if timestamp:
        data_checkpoint = time.strftime(
            '%d/%m/%Y %H:%M:%S', time.localtime(timestamp))
        print(f"🕐 Último checkpoint: {data_checkpoint}")

    # Calcular progresso
    dept_atual = checkpoint.get('departamento_atual', 0)
    total_dept = checkpoint.get('total_departamentos', 1)
    progresso = (dept_atual / total_dept) * 100 if total_dept > 0 else 0
    print(f"📊 Progresso: {progresso:.1f}% ({dept_atual}/{total_dept})")

    return True


def limpar_checkpoint():
    """Remove checkpoint e arquivos relacionados"""
    checkpoint_file = Path("data/docentes/checkpoint.json")
    processed_dir = Path("temp/processed")

    removidos = 0

    # Remover arquivo de checkpoint
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        print(f"🗑️ Removido: {checkpoint_file}")
        removidos += 1

    # Remover flags de departamentos processados
    if processed_dir.exists():
        for flag_file in processed_dir.glob("dept_*_done.flag"):
            flag_file.unlink()
            removidos += 1

        # Remover pasta se vazia
        if not any(processed_dir.iterdir()):
            processed_dir.rmdir()
            print(f"📁 Pasta removida: {processed_dir}")

    if removidos > 0:
        print(f"✅ {removidos} arquivos de checkpoint removidos")
    else:
        print("📄 Nenhum arquivo de checkpoint encontrado")


def verificar_arquivos_saida():
    """Verifica arquivos de saída existentes"""
    arquivo_docentes = Path("data/docentes/docentes.jsonl")

    print("📄 STATUS DOS ARQUIVOS DE SAÍDA:")
    print("=" * 50)

    if arquivo_docentes.exists():
        try:
            linhas = 0
            siapes_unicos = set()

            with open(arquivo_docentes, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha:
                        linhas += 1
                        try:
                            docente = json.loads(linha)
                            siape = docente.get('siape')
                            if siape:
                                siapes_unicos.add(siape)
                        except json.JSONDecodeError:
                            continue

            print(f"📊 Arquivo: {arquivo_docentes}")
            print(f"📈 Total de linhas: {linhas}")
            print(f"👥 SIAPEs únicos: {len(siapes_unicos)}")

            # Mostrar últimos 3 registros
            print(f"\n📄 Últimos registros:")
            with open(arquivo_docentes, 'r', encoding='utf-8') as f:
                todas_linhas = f.readlines()
                for i, linha in enumerate(todas_linhas[-3:], 1):
                    try:
                        docente = json.loads(linha.strip())
                        nome = docente.get('nome_docente', 'N/A')
                        dept = docente.get('departamento', 'N/A')
                        print(f"   {i}. {nome} - {dept}")
                    except:
                        print(f"   {i}. [linha inválida]")

        except Exception as e:
            print(f"❌ Erro ao analisar arquivo: {e}")
    else:
        print("📄 Nenhum arquivo de docentes encontrado")


def gerenciar_checkpoint_menu():
    """Menu principal para gerenciar checkpoints"""
    print("🔧 GERENCIADOR DE CHECKPOINTS - Spider Docentes")
    print("=" * 60)

    if not Path("data").exists():
        print("❌ Pasta 'data' não encontrada. Execute dentro do projeto.")
        sys.exit(1)

    while True:
        print(f"\n📋 OPÇÕES:")
        print("1. 📊 Ver status do checkpoint")
        print("2. 📄 Verificar arquivos de saída")
        print("3. 🗑️ Limpar checkpoints")
        print("4. 🔄 Resetar execução completa")
        print("5. 🚪 Sair")

        opcao = input(f"\n❓ Escolha uma opção (1-5): ").strip()

        if opcao == "1":
            print(f"\n" + "=" * 50)
            if not mostrar_status_checkpoint():
                print("💡 Execute o spider para criar um checkpoint")

        elif opcao == "2":
            print(f"\n" + "=" * 50)
            verificar_arquivos_saida()

        elif opcao == "3":
            print(f"\n" + "=" * 50)
            limpar_checkpoint()

        elif opcao == "4":
            print(f"\n" + "=" * 50)
            print("⚠️ RESETAR EXECUÇÃO COMPLETA")
            print("Isso irá:")
            print("  - Remover todos os checkpoints")
            print("  - Remover flags de departamentos processados")
            print("  - Manter dados coletados em docentes.jsonl")

            resposta = input(
                "\n❓ Tem certeza? (digite 'RESET' para confirmar): ")

            if resposta == 'RESET':
                limpar_checkpoint()
                print("🔄 Execução resetada. Próxima execução começará do zero.")
            else:
                print("❌ Operação cancelada")

        elif opcao == "5":
            print("👋 Saindo...")
            break

        else:
            print("❌ Opção inválida")


# ================================================================================
# FUNÇÕES DE EXTRAÇÃO DE DADOS (Compartilhadas entre as classes)
# ================================================================================

def extrair_dados_perfil_docente(response):
    """
    Função fixa para extrair informações do HTML da página do docente
    """
    dados = {}

    try:
        # === INFORMAÇÕES BÁSICAS ===
        nome_completo = response.css("#id-docente h3::text").get()
        if nome_completo:
            dados["nome_completo"] = nome_completo.strip().title()

        departamento_completo = response.css(
            "#id-docente p.departamento::text").get()
        if departamento_completo:
            dados["departamento_completo"] = departamento_completo.strip()

        # Foto do docente
        foto_url = response.css("#left .foto_professor img::attr(src)").get()
        if foto_url:
            if not foto_url.startswith('http'):
                foto_url = f"https://sigaa.unb.br{foto_url}" if foto_url.startswith(
                    '/') else foto_url
            dados["foto_url"] = foto_url

        # === PERFIL PESSOAL ===
        perfil_section = response.css("#perfil-docente")
        if perfil_section:
            # Descrição pessoal
            descricao_xpath = "//dt[contains(text(), 'Descrição pessoal')]/following-sibling::dd[1]/text()"
            descricao = response.xpath(descricao_xpath).get()
            if descricao and descricao.strip():
                dados["descricao_pessoal"] = descricao.strip()

            # Formação acadêmica resumida
            formacao_xpath = "//dt[contains(text(), 'Formação acadêmica')]/following-sibling::dd[1]//text()"
            formacao_textos = response.xpath(formacao_xpath).getall()
            if formacao_textos:
                formacao = " | ".join([t.strip()
                                      for t in formacao_textos if t.strip()])
                dados["formacao_resumida"] = formacao

            # Áreas de interesse
            areas_xpath = "//dt[contains(text(), 'Áreas de Interesse')]/following-sibling::dd[1]/text()"
            areas = response.xpath(areas_xpath).get()
            if areas and areas.strip():
                dados["areas_interesse"] = areas.strip()

            # Currículo Lattes
            lattes_xpath = "//dt[contains(text(), 'Lattes')]/following-sibling::dd[1]/a/@href"
            lattes_link = response.xpath(lattes_xpath).get()
            if lattes_link:
                dados["curriculo_lattes"] = lattes_link.strip()

        # === FORMAÇÃO DETALHADA ===
        formacao_section = response.css("#formacao-academica")
        if formacao_section:
            formacao_detalhes = {}

            # Usar XPath mais preciso para formação
            niveis = response.xpath(
                "//div[@id='formacao-academica']//dt/span[@class='ano']/text()").getall()
            detalhes = response.xpath(
                "//div[@id='formacao-academica']//dd//text()").getall()

            if niveis and detalhes:
                # Agrupar detalhes por nível
                i = 0
                for nivel in niveis:
                    if i < len(detalhes):
                        detalhes_nivel = []
                        # Pegar próximos 3-4 elementos de texto (curso, instituição, período)
                        for j in range(3):
                            if i + j < len(detalhes) and detalhes[i + j].strip():
                                detalhes_nivel.append(detalhes[i + j].strip())

                        if detalhes_nivel:
                            formacao_detalhes[nivel.strip()] = " | ".join(
                                detalhes_nivel)
                        i += len(detalhes_nivel)

            if formacao_detalhes:
                dados["formacao_detalhada"] = formacao_detalhes

        # === CONTATOS ===
        contato_section = response.css("#contato")
        if contato_section:
            # Telefone/Ramal
            telefone_xpath = "//dt[contains(text(), 'Telefone')]/following-sibling::dd[1]/text()"
            telefone = response.xpath(telefone_xpath).get()
            if telefone and "não informado" not in telefone.lower():
                dados["telefone_ramal"] = telefone.strip()

            # Email
            email_xpath = "//dt[contains(text(), 'eletrônico')]/following-sibling::dd[1]/text()"
            email = response.xpath(email_xpath).get()
            if email and "não informado" not in email.lower():
                dados["email"] = email.strip()

            # Sala
            sala_xpath = "//dt[contains(text(), 'Sala')]/following-sibling::dd[1]/text()"
            sala = response.xpath(sala_xpath).get()
            if sala and "não informado" not in sala.lower():
                dados["sala"] = sala.strip()

    except Exception as e:
        dados["erro_extracao"] = str(e)

    return dados


def extrair_dados_curriculo_lattes(script_content):
    """
    Função fixa para extrair dados do currículo Lattes do JavaScript
    """
    try:
        curriculo_info = {}

        # Data de atualização
        match_data = re.search(r'"dataatualizacao":\s*"(\d+)"', script_content)
        if match_data:
            data_raw = match_data.group(1)
            if len(data_raw) == 8:
                curriculo_info["data_atualizacao"] = f"{data_raw[:2]}/{data_raw[2:4]}/{data_raw[4:]}"

        # Nome em citações
        match_citacao = re.search(
            r'"nomeemcitacoesbibliograficas":\s*"([^"]+)"', script_content)
        if match_citacao:
            curriculo_info["nome_citacoes"] = match_citacao.group(1)

        # Resumo (limitado)
        match_resumo = re.search(
            r'"textoresumocvrh":\s*"([^"]+)"', script_content)
        if match_resumo:
            resumo = match_resumo.group(1)
            resumo = resumo.replace("&#201;", "É").replace(
                "&#195;", "Ã").replace("&#231;", "ç")
            curriculo_info["resumo_cv"] = resumo[:300] + \
                "..." if len(resumo) > 300 else resumo

        return curriculo_info if curriculo_info else None

    except Exception:
        return None


# ================================================================================
# CLASSE 1: SPIDER PARA LISTAR DEPARTAMENTOS/UNIDADES
# ================================================================================

class DepartamentosSpider(scrapy.Spider):
    name = "departamentos"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf"]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response):
        """Extrai apenas a lista de departamentos/unidades"""
        self.logger.info("📋 Extraindo lista de departamentos...")

        departamentos = response.css("select#form\\:departamento option")
        total_encontrados = 0

        for opcao in departamentos:
            valor = opcao.attrib.get("value")
            texto = opcao.css("::text").get()

            if valor and valor not in ["", "0"]:
                total_encontrados += 1
                yield {
                    'id_departamento': valor,
                    'nome_departamento': texto.strip(),
                    'timestamp_coleta': time.time()
                }

        self.logger.info(
            f"✅ Total de departamentos coletados: {total_encontrados}")


# ================================================================================
# CLASSE 2: SPIDER PARA BAIXAR PÁGINAS DOS DOCENTES
# ================================================================================

class DocentesPaginasSpider(scrapy.Spider):
    name = "docentes_paginas"
    allowed_domains = ["sigaa.unb.br"]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 4,
    }

    def __init__(self):
        # Pasta para salvar HTMLs
        self.paginas_dir = Path("data/docentes/paginas_html")
        self.paginas_dir.mkdir(parents=True, exist_ok=True)

        self.total_docentes = 0
        self.processados = 0

        self.logger.info(
            f"🚀 Spider de páginas iniciado - Pasta: {self.paginas_dir.absolute()}")

    def start_requests(self):
        """Lê docentes.jsonl e baixa páginas individuais"""
        arquivo_docentes = Path("data/docentes/docentes.jsonl")

        if not arquivo_docentes.exists():
            self.logger.error(f"❌ Arquivo não encontrado: {arquivo_docentes}")
            return

        docentes = []
        with open(arquivo_docentes, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    try:
                        docente = json.loads(linha)
                        docentes.append(docente)
                    except json.JSONDecodeError:
                        continue

        self.total_docentes = len(docentes)
        self.logger.info(
            f"📋 Total de docentes para baixar: {self.total_docentes}")

        for i, docente in enumerate(docentes):
            link_pagina = docente.get("link_pagina")

            if link_pagina:
                url = f"https://sigaa.unb.br{link_pagina}" if link_pagina.startswith(
                    "/") else link_pagina

                yield scrapy.Request(
                    url=url,
                    callback=self.salvar_pagina_docente,
                    meta={"docente": docente, "posicao": i + 1},
                    dont_filter=True
                )

    def salvar_pagina_docente(self, response):
        """Salva HTML da página do docente"""
        docente = response.meta["docente"]
        posicao = response.meta["posicao"]

        siape = docente.get("siape", "unknown")
        nome = docente.get("nome_docente", "N/A")

        self.logger.info(
            f"💾 [{posicao}/{self.total_docentes}] Salvando: {nome}")

        # Salvar HTML
        arquivo_html = self.paginas_dir / f"docente_{siape}.html"
        with open(arquivo_html, "w", encoding="utf-8") as f:
            f.write(response.text)

        self.processados += 1

        yield {
            **docente,  # Dados originais
            "url_acessada": response.url,
            "arquivo_html": str(arquivo_html),
            "tamanho_html": len(response.text),
            "status_download": "sucesso",
            "timestamp_download": time.time()
        }

    def closed(self, reason):
        self.logger.info(
            f"📊 Páginas baixadas: {self.processados}/{self.total_docentes}")


# ================================================================================
# CLASSE 3: SPIDER PARA EXTRAIR INFORMAÇÕES DOS HTMLs SALVOS
# ================================================================================

class DocentesCompletoSpider(scrapy.Spider):
    name = "docentes_completo"

    def __init__(self):
        self.paginas_dir = Path("data/docentes/paginas_html")
        self.processados = 0

        self.logger.info(
            f"🔍 Spider de extração iniciado - Pasta: {self.paginas_dir.absolute()}")

    def start_requests(self):
        """Processa HTMLs salvos localmente"""
        if not self.paginas_dir.exists():
            self.logger.error(f"❌ Pasta não encontrada: {self.paginas_dir}")
            return

        # Buscar arquivos HTML
        arquivos_html = list(self.paginas_dir.glob("docente_*.html"))
        total_arquivos = len(arquivos_html)

        self.logger.info(f"📁 Arquivos HTML encontrados: {total_arquivos}")

        for i, arquivo in enumerate(arquivos_html):
            # Extrair SIAPE do nome do arquivo
            siape = arquivo.stem.replace("docente_", "")

            file_url = arquivo.as_uri()

            yield scrapy.Request(
                url=file_url,
                callback=self.processar_html_local,
                meta={
                    "siape": siape,
                    "arquivo_origem": str(arquivo),
                    "posicao": i + 1,
                    "total": total_arquivos
                }
            )

    def processar_html_local(self, response):
        """Extrai dados do HTML local usando as funções fixas"""
        siape = response.meta["siape"]
        arquivo_origem = response.meta["arquivo_origem"]
        posicao = response.meta["posicao"]
        total = response.meta["total"]

        self.logger.info(f"⚙️ [{posicao}/{total}] Processando SIAPE: {siape}")

        # Buscar dados originais do docente
        dados_originais = self.buscar_dados_originais(siape)

        # Extrair dados da página usando funções fixas
        dados_extraidos = extrair_dados_perfil_docente(response)

        # Extrair dados do Lattes se disponível
        script_content = response.css(
            "script:contains('var curriculo')::text").get()
        if script_content:
            dados_lattes = extrair_dados_curriculo_lattes(script_content)
            if dados_lattes:
                dados_extraidos["curriculo_lattes_dados"] = dados_lattes

        # Combinar todos os dados
        dados_completos = {
            **dados_originais,
            **dados_extraidos,
            "siape_processado": siape,
            "arquivo_html_origem": arquivo_origem,
            "timestamp_processamento": time.time(),
            "status_processamento": "sucesso"
        }

        self.processados += 1
        nome = dados_completos.get(
            "nome_completo", dados_completos.get("nome_docente", "N/A"))
        self.logger.info(f"✅ [{self.processados}] Concluído: {nome}")

        yield dados_completos

    def buscar_dados_originais(self, siape):
        """Busca dados originais do docente no arquivo JSONL"""
        arquivo_docentes = Path("data/docentes/docentes.jsonl")

        if not arquivo_docentes.exists():
            return {"siape": siape}

        try:
            with open(arquivo_docentes, 'r', encoding='utf-8') as f:
                for linha in f:
                    linha = linha.strip()
                    if linha:
                        docente = json.loads(linha)
                        if docente.get("siape") == siape:
                            return docente
        except Exception:
            pass

        return {"siape": siape}

    def closed(self, reason):
        self.logger.info(f"📊 PROCESSAMENTO CONCLUÍDO:")
        self.logger.info(f"   ✅ Docentes processados: {self.processados}")
        self.logger.info(
            f"   💾 Arquivo final: data/docentes/docentes_completo.jsonl")


# ================================================================================
# CLASSE PRINCIPAL: ORQUESTRADOR COMPLETO (Para runspider)
# ================================================================================

class DocentesOrquestradorSpider(scrapy.Spider):
    """
    Spider principal que executa todas as 3 etapas em sequência:
    1. Lista departamentos (se necessário)
    2. Coleta docentes por departamento 
    3. Baixa páginas individuais
    4. Extrai dados completos
    
    USO: uv run scrapy runspider .\sigaa\spiders\docentes_completo.py -o data\docentes\docentes_test.jsonl
    """
    name = "docentes_orquestrador"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf"]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    }

    def __init__(self):
        # Configurar pastas
        self.temp_dir = Path("temp/current_dept")
        self.paginas_dir = Path("data/docentes/paginas_html")
        self.processed_dir = Path("temp/processed")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.paginas_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # === CHECKPOINT/RESUMO ===
        self.checkpoint_file = Path("data/docentes/checkpoint.json")
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.siapes_processados = set()  # SIAPEs já processados no arquivo final

        # Controle do processo
        self.departamentos_fila = []
        self.departamento_atual = 0
        self.docentes_coletados = []
        self.total_docentes_processados = 0
        self.indice_download_atual = 0

        # Carregar estado anterior se existir
        self._carregar_checkpoint()

        # Limpeza inicial
        self._limpar_temp()

        self.logger.info(
            "🚀 ORQUESTRADOR INICIADO - Processo completo em uma execução")
        self.logger.info(
            "📋 Etapas: Departamentos → Docentes → Páginas → Extração")

        if self.siapes_processados:
            self.logger.info(
                f"🔄 RESUMINDO: {len(self.siapes_processados)} docentes já processados")

    def _limpar_temp(self):
        """Limpa arquivos temporários"""
        try:
            for arquivo in self.temp_dir.glob("*.html"):
                arquivo.unlink()
        except Exception:
            pass

    def parse(self, response):
        """ETAPA 1: Coletagem departamentos e inicia processo sequencial"""
        self.logger.info("📋 ETAPA 1: Coletando departamentos...")

        departamentos = response.css("select#form\\:departamento option")

        for opcao in departamentos:
            valor = opcao.attrib.get("value")
            texto = opcao.css("::text").get()

            if valor and valor not in ["", "0"]:
                self.departamentos_fila.append({
                    'id': valor,
                    'nome': texto.strip()
                })

        total_departamentos = len(self.departamentos_fila)
        self.logger.info(f"📊 Departamentos encontrados: {total_departamentos}")

        # Iniciar coleta do primeiro departamento
        if self.departamentos_fila:
            first_request = self.processar_departamento_atual(response)
            if first_request:
                yield first_request

    def processar_departamento_atual(self, response):
        """ETAPA 2: Processa departamento atual"""
        if self.departamento_atual >= len(self.departamentos_fila):
            # Todos os departamentos processados, iniciar download de páginas
            self.logger.info(
                f"📊 Coleta de departamentos concluída. Iniciando download de páginas...")
            # Retornar primeiro request de download
            return self.criar_primeiro_request_download()

        dept = self.departamentos_fila[self.departamento_atual]
        posicao = self.departamento_atual + 1
        total = len(self.departamentos_fila)

        self.logger.info(
            f"📥 ETAPA 2: [{posicao}/{total}] Processando: {dept['nome']}")

        return scrapy.FormRequest.from_response(
            response,
            formname='form',
            formdata={
                'form:departamento': dept['id'],
                'form:buscar': 'Buscar'
            },
            callback=self.coletar_docentes_departamento,
            meta={
                'departamento': dept,
                'response_original': response
            }
        )

    def criar_primeiro_request_download(self):
        """Cria o primeiro request para download de páginas"""
        total_docentes = len(self.docentes_coletados)
        self.logger.info(
            f"📥 ETAPA 3: Baixando {total_docentes} páginas de docentes...")

        if not self.docentes_coletados:
            self.logger.warning("❌ Nenhum docente coletado para download")
            return None

        # Inicializar contador de downloads
        self.indice_download_atual = 0

        # Retornar primeiro request
        primeiro_docente = self.docentes_coletados[0]
        link_pagina = primeiro_docente.get("link_pagina")

        if link_pagina:
            url = f"https://sigaa.unb.br{link_pagina}" if link_pagina.startswith(
                "/") else link_pagina

            return scrapy.Request(
                url=url,
                callback=self.baixar_e_processar_pagina,
                meta={
                    "docente": primeiro_docente,
                    "posicao": 1,
                    "total": total_docentes
                },
                dont_filter=True
            )

        return None

    def coletar_docentes_departamento(self, response):
        """Coleta docentes do departamento atual"""
        departamento = response.meta['departamento']
        response_original = response.meta['response_original']

        # Verificar se há resultados
        tabela_resultados = response.css("table.listagem")
        if not tabela_resultados:
            self.logger.info(f"❌ Nenhum docente em: {departamento['nome']}")
            self.departamento_atual += 1
            yield self.processar_departamento_atual(response_original)
            return

        # Extrair docentes
        linhas_docentes = response.css("table.listagem tbody tr")
        total_docentes = len(linhas_docentes)
        self.logger.info(
            f"👥 Encontrados {total_docentes} docentes em {departamento['nome']}")

        for linha in linhas_docentes:
            nome = linha.css("td:nth-child(2) span.nome::text").get()

            if nome:
                link_pagina = linha.css(
                    "td:nth-child(2) span.pagina a::attr(href)").get()

                siape = None
                if link_pagina and "siape=" in link_pagina:
                    siape = link_pagina.split("siape=")[1].split("&")[0]

                docente_info = {
                    'codigo_departamento': departamento['id'],
                    'departamento': departamento['nome'],
                    'nome_docente': nome.strip(),
                    'siape': siape,
                    'link_pagina': link_pagina,
                    'processamento': 'orquestrador_completo'
                }

                self.docentes_coletados.append(docente_info)

        # Avançar para próximo departamento
        self.departamento_atual += 1
        next_request = self.processar_departamento_atual(response_original)
        if next_request:
            yield next_request

    def baixar_e_processar_pagina(self, response):
        """ETAPA 4: Baixa página e extrai dados completos diretamente"""
        docente = response.meta["docente"]
        posicao = response.meta["posicao"]
        total = response.meta["total"]

        siape = docente.get("siape", "unknown")
        nome = docente.get("nome_docente", "N/A")

        # === VERIFICAR SE JÁ FOI PROCESSADO ===
        if siape in self.siapes_processados:
            self.logger.info(
                f"⏭️ PULANDO [{posicao}/{total}]: {nome} (já processado)")
            # Continuar para próximo sem processar
            self._continuar_proximo_docente()
            return

        self.logger.info(
            f"⚙️ ETAPA 4: [{posicao}/{total}] Processando: {nome}")

        # Salvar HTML temporariamente (opcional, para debug)
        arquivo_temp = self.temp_dir / f"temp_{siape}.html"
        with open(arquivo_temp, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Extrair dados usando funções fixas
        dados_extraidos = extrair_dados_perfil_docente(response)

        # Extrair dados do Lattes
        script_content = response.css(
            "script:contains('var curriculo')::text").get()
        if script_content:
            dados_lattes = extrair_dados_curriculo_lattes(script_content)
            if dados_lattes:
                dados_extraidos["curriculo_lattes_dados"] = dados_lattes

        # Combinar dados
        dados_completos = {
            **docente,  # Dados originais da coleta
            **dados_extraidos,  # Dados extraídos da página
            "url_acessada": response.url,
            "timestamp_processamento": time.time(),
            "status_processamento": "sucesso_completo"
        }

        # Limpar arquivo temporário
        try:
            arquivo_temp.unlink()
        except:
            pass

        # Adicionar SIAPE aos processados
        self.siapes_processados.add(siape)

        self.total_docentes_processados += 1
        self.logger.info(
            f"✅ [{self.total_docentes_processados}] Concluído: {dados_completos.get('nome_completo', nome)}")

        yield dados_completos

        # Continuar para próximo docente
        self._continuar_proximo_docente()

    def _continuar_proximo_docente(self):
        """Continua processamento do próximo docente"""
        # Verificar se há próximo docente para processar
        if hasattr(self, 'indice_download_atual'):
            self.indice_download_atual += 1

            # Salvar checkpoint a cada 10 docentes processados
            if self.total_docentes_processados % 10 == 0:
                self._salvar_checkpoint()

            if self.indice_download_atual < len(self.docentes_coletados):
                # Criar request para próximo docente
                proximo_docente = self.docentes_coletados[self.indice_download_atual]
                siape_proximo = proximo_docente.get("siape", "unknown")

                # Verificar se próximo já foi processado
                if siape_proximo in self.siapes_processados:
                    self.logger.info(
                        f"⏭️ Pulando SIAPE {siape_proximo} (já processado)")
                    self._continuar_proximo_docente()  # Recursão para próximo
                    return

                link_pagina = proximo_docente.get("link_pagina")

                if link_pagina:
                    url = f"https://sigaa.unb.br{link_pagina}" if link_pagina.startswith(
                        "/") else link_pagina

                    return scrapy.Request(
                        url=url,
                        callback=self.baixar_e_processar_pagina,
                        meta={
                            "docente": proximo_docente,
                            "posicao": self.indice_download_atual + 1,
                            "total": len(self.docentes_coletados)
                        },
                        dont_filter=True
                    )

    def _carregar_checkpoint(self):
        """Carrega checkpoint anterior se existir"""
        checkpoint = carregar_checkpoint()

        if checkpoint:
            self.departamento_atual = checkpoint.get('departamento_atual', 0)
            self.docentes_coletados = checkpoint.get('docentes_coletados', [])
            total_coletados = len(self.docentes_coletados)

            # Carregar SIAPEs já processados do arquivo final
            self._carregar_siapes_processados()

            self.logger.info(f"📂 Checkpoint carregado:")
            self.logger.info(
                f"   📋 Departamento atual: {self.departamento_atual}")
            self.logger.info(f"   👥 Docentes coletados: {total_coletados}")
            self.logger.info(
                f"   ✅ SIAPEs já processados: {len(self.siapes_processados)}")
        else:
            self.logger.info(
                "📄 Nenhum checkpoint encontrado - Iniciando do zero")

    def _carregar_siapes_processados(self):
        """Carrega lista de SIAPEs já processados do arquivo final"""
        arquivo_final = Path("data/docentes/docentes_test.jsonl")

        if arquivo_final.exists():
            try:
                with open(arquivo_final, 'r', encoding='utf-8') as f:
                    for linha in f:
                        linha = linha.strip()
                        if linha:
                            try:
                                docente = json.loads(linha)
                                siape = docente.get('siape')
                                if siape:
                                    self.siapes_processados.add(siape)
                            except json.JSONDecodeError:
                                continue

                self.logger.info(
                    f"📊 SIAPEs já no arquivo final: {len(self.siapes_processados)}")
            except Exception as e:
                self.logger.warning(
                    f"⚠️ Erro ao carregar SIAPEs processados: {e}")

    def _salvar_checkpoint(self):
        """Salva checkpoint atual"""
        success = salvar_checkpoint(
            self.departamento_atual,
            len(self.departamentos_fila),
            self.docentes_coletados
        )

        if success:
            self.logger.info(
                f"💾 Checkpoint salvo - Dept: {self.departamento_atual}/{len(self.departamentos_fila)}")

    def _departamento_ja_processado(self, dept_id):
        """Verifica se departamento já foi processado"""
        flag_file = self.processed_dir / f"dept_{dept_id}_done.flag"
        return flag_file.exists()

    def _marcar_departamento_processado(self, dept_id):
        """Marca departamento como processado"""
        flag_file = self.processed_dir / f"dept_{dept_id}_done.flag"
        try:
            flag_file.touch()
        except Exception as e:
            self.logger.warning(
                f"⚠️ Erro ao marcar departamento processado: {e}")

    def closed(self, reason):
        """Estatísticas finais"""
        self.logger.info(f"🎉 PROCESSO ORQUESTRADOR CONCLUÍDO!")
        self.logger.info(f"📊 Estatísticas finais:")
        self.logger.info(
            f"   🏢 Departamentos processados: {self.departamento_atual}")
        self.logger.info(
            f"   👥 Docentes coletados: {len(self.docentes_coletados)}")
        self.logger.info(
            f"   ✅ Páginas processadas: {self.total_docentes_processados}")
        self.logger.info(f"   🏁 Motivo de encerramento: {reason}")

        # Limpeza final
        self._limpar_temp()


# ================================================================================
# MAIN - Suporte a linha de comando para gerenciamento
# ================================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "gerenciar":
        # Modo gerenciador de checkpoint
        gerenciar_checkpoint_menu()
    else:
        print("🔧 SPIDER DOCENTES COMPLETO")
        print("=" * 50)
        print("📋 USO:")
        print("  🕷️ Spider: uv run scrapy runspider .\\sigaa\\spiders\\docentes_completo.py -o data\\docentes\\docentes_test.jsonl")
        print("  🔧 Gerenciar: python .\\sigaa\\spiders\\docentes_completo.py gerenciar")
        print("=" * 50)

# cd sigaa
# uv run scrapy crawl departamentos -o data/departamentos/lista_departamentos.jsonl
# uv run scrapy crawl docentes_paginas -o data/docentes/paginas_baixadas.jsonl  
# uv run scrapy crawl docentes_completo -o data/docentes/docentes_completo.jsonl
import re
import json
import scrapy
import os
from pathlib import Path
import time
from scrapy.http import HtmlResponse


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
        
        departamento_completo = response.css("#id-docente p.departamento::text").get()
        if departamento_completo:
            dados["departamento_completo"] = departamento_completo.strip()
        
        # Foto do docente
        foto_url = response.css("#left .foto_professor img::attr(src)").get()
        if foto_url:
            if not foto_url.startswith('http'):
                foto_url = f"https://sigaa.unb.br{foto_url}" if foto_url.startswith('/') else foto_url
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
                formacao = " | ".join([t.strip() for t in formacao_textos if t.strip()])
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
            niveis = response.xpath("//div[@id='formacao-academica']//dt/span[@class='ano']/text()").getall()
            detalhes = response.xpath("//div[@id='formacao-academica']//dd//text()").getall()
            
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
                            formacao_detalhes[nivel.strip()] = " | ".join(detalhes_nivel)
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
        match_citacao = re.search(r'"nomeemcitacoesbibliograficas":\s*"([^"]+)"', script_content)
        if match_citacao:
            curriculo_info["nome_citacoes"] = match_citacao.group(1)
        
        # Resumo (limitado)
        match_resumo = re.search(r'"textoresumocvrh":\s*"([^"]+)"', script_content)
        if match_resumo:
            resumo = match_resumo.group(1)
            resumo = resumo.replace("&#201;", "É").replace("&#195;", "Ã").replace("&#231;", "ç")
            curriculo_info["resumo_cv"] = resumo[:300] + "..." if len(resumo) > 300 else resumo
        
        return curriculo_info if curriculo_info else None
        
    except Exception:
        return None


# ================================================================================
# CLASSE 1: SPIDER PARA LISTAR DEPARTAMENTOS/UNIDADES
# ================================================================================

class DepartamentosSpider(scrapy.Spider):
    name = "departamentos"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = ["https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf"]
    
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
        
        self.logger.info(f"✅ Total de departamentos coletados: {total_encontrados}")


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
        
        self.logger.info(f"🚀 Spider de páginas iniciado - Pasta: {self.paginas_dir.absolute()}")

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
        self.logger.info(f"📋 Total de docentes para baixar: {self.total_docentes}")
        
        for i, docente in enumerate(docentes):
            link_pagina = docente.get("link_pagina")
            
            if link_pagina:
                url = f"https://sigaa.unb.br{link_pagina}" if link_pagina.startswith("/") else link_pagina
                
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
        
        self.logger.info(f"💾 [{posicao}/{self.total_docentes}] Salvando: {nome}")
        
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
        self.logger.info(f"📊 Páginas baixadas: {self.processados}/{self.total_docentes}")


# ================================================================================
# CLASSE 3: SPIDER PARA EXTRAIR INFORMAÇÕES DOS HTMLs SALVOS
# ================================================================================

class DocentesCompletoSpider(scrapy.Spider):
    name = "docentes_completo"
    
    def __init__(self):
        self.paginas_dir = Path("data/docentes/paginas_html")
        self.processados = 0
        
        self.logger.info(f"🔍 Spider de extração iniciado - Pasta: {self.paginas_dir.absolute()}")

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
        script_content = response.css("script:contains('var curriculo')::text").get()
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
        nome = dados_completos.get("nome_completo", dados_completos.get("nome_docente", "N/A"))
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
        self.logger.info(f"   💾 Arquivo final: data/docentes/docentes_completo.jsonl")

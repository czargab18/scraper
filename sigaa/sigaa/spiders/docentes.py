# cd sigaa
# uv run scrapy runspider .\sigaa\spiders\docentes.py -o data\docentes\docentes.jsonl
import re
import json
import scrapy
import os
from pathlib import Path
import time


class DocentesSpider(scrapy.Spider):
    name = "docentes"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf"]

    # Configurações para processar um por vez
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,  # Apenas 1 requisição por vez
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 3,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    }

    def __init__(self):
        # Configurar pasta temporária
        self.temp_dir = Path("temp/current_dept")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Limpar arquivos antigos
        self._limpar_pasta_temp()

        # Lista de departamentos para processar sequencialmente
        self.departamentos_fila = []
        self.departamento_atual = 0

        self.logger.info(
            f"🚀 Spider iniciado - Pasta temporária: {self.temp_dir.absolute()}")
        self.logger.info(f"📝 Modo: Processamento sequencial (1 por vez)")

    def parse(self, response):
        """Coleta lista de departamentos e inicia processamento sequencial"""
        departamentos = response.css("select#form\\:departamento option")

        # Montar fila de departamentos
        for opcao in departamentos:
            valor = opcao.attrib.get("value")
            texto = opcao.css("::text").get()

            if valor and valor not in ["", "0"]:
                self.departamentos_fila.append({
                    'id': valor,
                    'nome': texto.strip()
                })

        total_departamentos = len(self.departamentos_fila)
        self.logger.info(
            f"📋 Total de departamentos encontrados: {total_departamentos}")

        # Iniciar processamento do primeiro departamento
        if self.departamentos_fila:
            yield self.processar_proximo_departamento(response)

    def processar_proximo_departamento(self, response):
        """Processa o próximo departamento da fila"""
        if self.departamento_atual >= len(self.departamentos_fila):
            self.logger.info("✅ Todos os departamentos foram processados!")
            return

        dept = self.departamentos_fila[self.departamento_atual]
        self.logger.info(
            f"📥 [{self.departamento_atual + 1}/{len(self.departamentos_fila)}] Baixando: {dept['nome']}")

        return scrapy.FormRequest.from_response(
            response,
            formname='form',
            formdata={
                'form:departamento': dept['id'],
                'form:buscar': 'Buscar'
            },
            callback=self.salvar_e_processar_departamento,
            meta={
                'departamento_nome': dept['nome'],
                'departamento_id': dept['id'],
                'response_original': response
            }
        )

    def salvar_e_processar_departamento(self, response):
        """ETAPA 1: Salva HTML da tabela e chama processamento"""
        departamento_nome = response.meta['departamento_nome']
        departamento_id = response.meta['departamento_id']
        response_original = response.meta['response_original']

        # Verificar se há tabela de resultados
        tabela_resultados = response.css("table.listagem")
        if not tabela_resultados:
            self.logger.info(
                f"❌ Nenhum docente encontrado para {departamento_nome}")
            # Avançar para próximo departamento
            self.departamento_atual += 1
            yield self.processar_proximo_departamento(response_original)
            return

        # Extrair apenas o HTML da tabela
        tabela_html = tabela_resultados.get()

        # Salvar em arquivo temporário
        arquivo_temp = self.temp_dir / f"dept_{departamento_id}.html"
        with open(arquivo_temp, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head><body>
<!-- Departamento: {departamento_nome} (ID: {departamento_id}) -->
{tabela_html}
</body></html>""")

        self.logger.info(f"💾 HTML salvo: {arquivo_temp.name}")

        # ETAPA 2: Processar arquivo local
        yield from self.extrair_dados_locais(arquivo_temp, departamento_nome, departamento_id, response_original)

    def extrair_dados_locais(self, arquivo_html, departamento_nome, departamento_id, response_original):
        """ETAPA 2: Extrai dados do HTML local"""
        self.logger.info(f"⚙️ Extraindo dados de {departamento_nome}...")

        # Ler HTML local
        with open(arquivo_html, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Criar response fictício para usar seletores CSS
        from scrapy.http import HtmlResponse
        local_response = HtmlResponse(
            url="file:///" + str(arquivo_html),
            body=html_content,
            encoding='utf-8'
        )

        # Extrair docentes usando mesma lógica
        linhas_docentes = local_response.css("table.listagem tbody tr")
        total_docentes = len(linhas_docentes)
        self.logger.info(
            f"📊 Encontrados {total_docentes} docentes em {departamento_nome}")

        for linha in linhas_docentes:
            nome = linha.css("td:nth-child(2) span.nome::text").get()

            if nome:
                link_pagina = linha.css(
                    "td:nth-child(2) span.pagina a::attr(href)").get()

                siape = None
                if link_pagina and "siape=" in link_pagina:
                    siape = link_pagina.split("siape=")[1].split("&")[0]

                foto_url = linha.css("td.foto img::attr(src)").get()

                yield {
                    'codigo_departamento': departamento_id,
                    'departamento': departamento_nome,
                    'nome_docente': nome.strip(),
                    'siape': siape,
                    'link_pagina': link_pagina,
                    'processamento': 'sequencial_local'
                }

        # ETAPA 3: Limpar arquivo e avançar
        yield from self.limpar_e_avancar(arquivo_html, departamento_nome, response_original)

    def limpar_e_avancar(self, arquivo_html, departamento_nome, response_original):
        """ETAPA 3: Remove arquivo temporário e avança para próximo"""
        # Remover arquivo temporário
        try:
            arquivo_html.unlink()
            self.logger.info(f"🗑️ Arquivo removido: {arquivo_html.name}")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao remover arquivo: {e}")

        # Pausa opcional entre departamentos
        time.sleep(0.5)

        # Avançar para próximo departamento
        self.departamento_atual += 1
        self.logger.info(f"➡️ Concluído: {departamento_nome}")

        # Processar próximo ou finalizar
        if self.departamento_atual < len(self.departamentos_fila):
            yield self.processar_proximo_departamento(response_original)
        else:
            self.logger.info(
                f"🎉 CONCLUÍDO! Processados {len(self.departamentos_fila)} departamentos")

    def closed(self, reason):
        """Método chamado quando spider é finalizado"""
        # Limpar pasta temporária final
        try:
            if self.temp_dir.exists():
                # Remover arquivos restantes
                for arquivo in self.temp_dir.glob("*.html"):
                    arquivo.unlink()
                    self.logger.info(
                        f"🗑️ Limpeza final: removido {arquivo.name}")

                # Remover pasta se vazia
                if not any(self.temp_dir.iterdir()):
                    self.temp_dir.rmdir()
                    self.logger.info(
                        f"📁 Pasta temporária removida: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro na limpeza final: {e}")

        # Estatísticas finais
        total_processados = self.departamento_atual
        self.logger.info(f"📈 ESTATÍSTICAS FINAIS:")
        self.logger.info(
            f"   📋 Departamentos processados: {total_processados}/{len(self.departamentos_fila)}")
        self.logger.info(f"   🏁 Motivo de encerramento: {reason}")

    def _limpar_pasta_temp(self):
        """Limpa arquivos antigos da pasta temporária"""
        try:
            for arquivo in self.temp_dir.glob("*.html"):
                arquivo.unlink()
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao limpar pasta: {e}")


class DocentesConteudoSpider(scrapy.Spider):
    name = "docentes_conteudo"
    allowed_domains = ["sigaa.unb.br"]

    # Configurações para processar um por vez
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'FEEDS': {
            'data/docentes/docentes_detalhes.jsonl': {
                'format': 'jsonlines',
                'encoding': 'utf8',
                'store_empty': False,
            },
        }
    }

    def __init__(self):
        # Pasta para salvar HTMLs das páginas
        self.paginas_dir = Path("data/docentes/paginas_html")
        self.paginas_dir.mkdir(parents=True, exist_ok=True)

        self.total_docentes = 0
        self.processados = 0

        self.logger.info(
            f"🚀 Spider iniciado - Salvando HTMLs em: {self.paginas_dir.absolute()}")

    def start_requests(self):
        """Lê arquivo docentes.jsonl e gera requests para cada docente"""
        arquivo_docentes = Path("data/docentes/docentes.jsonl")

        if not arquivo_docentes.exists():
            self.logger.error(f"❌ Arquivo não encontrado: {arquivo_docentes}")
            return

        docentes = []

        # Ler arquivo JSONL linha por linha
        with open(arquivo_docentes, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    try:
                        docente = json.loads(linha)
                        docentes.append(docente)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"⚠️ Erro ao parsear linha: {e}")

        self.total_docentes = len(docentes)
        self.logger.info(
            f"📋 Total de docentes encontrados: {self.total_docentes}")

        # Gerar requests para cada docente
        for i, docente in enumerate(docentes):
            link_pagina = docente.get("link_pagina")

            if link_pagina:
                # Construir URL completa
                if link_pagina.startswith("/"):
                    url = f"https://sigaa.unb.br{link_pagina}"
                else:
                    url = link_pagina

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_docente,
                    meta={
                        "docente": docente,
                        "posicao": i + 1
                    },
                    dont_filter=True  # Permitir URLs duplicadas se houver
                )
            else:
                self.logger.warning(
                    f"⚠️ Docente sem link: {docente.get('nome_docente', 'N/A')}")

    def parse_docente(self, response):
        """Extrai informações da página do docente"""
        docente_original = response.meta["docente"]
        posicao = response.meta["posicao"]

        # Log de progresso
        self.logger.info(
            f"📥 [{posicao}/{self.total_docentes}] Processando: {docente_original.get('nome_docente', 'N/A')}")

        # Salvar HTML da página
        siape = docente_original.get("siape", "unknown")
        arquivo_html = self.paginas_dir / f"docente_{siape}.html"

        with open(arquivo_html, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Extrair informações da página
        dados_extraidos = self.extrair_dados_pagina(response)

        # Combinar dados originais com dados extraídos
        dados_completos = {
            **docente_original,  # Dados do JSONL original
            **dados_extraidos,  # Dados extraídos da página
            "url_acessada": response.url,
            "arquivo_html_salvo": str(arquivo_html),
            "status_processamento": "sucesso"
        }

        self.processados += 1
        self.logger.info(
            f"✅ [{self.processados}/{self.total_docentes}] Concluído: {dados_completos.get('nome_completo', 'N/A')}")

        yield dados_completos

    def extrair_dados_pagina(self, response):
        """Extrai informações específicas da página do docente"""
        dados = {}

        try:
            # Nome completo (do título da página)
            nome_completo = response.css("#id-docente h3::text").get()
            if nome_completo:
                dados["nome_completo"] = nome_completo.strip().title()

            # Departamento completo
            departamento_completo = response.css(
                "#id-docente p.departamento::text").get()
            if departamento_completo:
                dados["departamento_completo"] = departamento_completo.strip()

            # Foto do docente
            foto_url = response.css(
                "#left .foto_professor img::attr(src)").get()
            if foto_url:
                if foto_url.startswith("/") or foto_url.startswith("https://"):
                    dados["foto_url"] = foto_url
                else:
                    dados["foto_url"] = f"https://sigaa.unb.br{foto_url}"

            # Situação do docente
            situacao = response.css("#left h3.situacao::text").get()
            if situacao:
                dados["situacao"] = situacao.strip()

            # === PERFIL PESSOAL ===
            perfil_section = response.css("#perfil-docente")
            if perfil_section:

                # Descrição pessoal
                descricao = perfil_section.css(
                    "dl:contains('Descrição pessoal') dd::text").get()
                if descricao:
                    dados["descricao_pessoal"] = descricao.strip()

                # Formação acadêmica/profissional
                formacao = perfil_section.css(
                    "dl:contains('Formação acadêmica') dd::text").get()
                if formacao:
                    dados["formacao_academica"] = formacao.strip()

                # Áreas de interesse
                areas = perfil_section.css(
                    "dl:contains('Áreas de Interesse') dd::text").get()
                if areas:
                    dados["areas_interesse"] = areas.strip()

                # Currículo Lattes
                lattes_link = perfil_section.css(
                    "dl:contains('Currículo Lattes') dd a::attr(href)").get()
                if lattes_link:
                    dados["curriculo_lattes"] = lattes_link.strip()

            # === FORMAÇÃO ACADÊMICA ===
            formacao_section = response.css("#formacao-academica")
            if formacao_section:
                formacao_detalhes = {}

                # Extrair cada nível de formação
                for dl in formacao_section.css("dl"):
                    nivel = dl.css("dt span.ano::text").get()
                    detalhes = dl.css("dd::text").getall()

                    if nivel and detalhes:
                        nivel_clean = nivel.strip()
                        detalhes_clean = " | ".join(
                            [d.strip() for d in detalhes if d.strip()])
                        formacao_detalhes[nivel_clean] = detalhes_clean

                if formacao_detalhes:
                    dados["formacao_detalhada"] = formacao_detalhes

            # === CONTATOS ===
            contato_section = response.css("#contato")
            if contato_section:

                # Endereço profissional
                endereco = contato_section.css(
                    "dl:contains('Endereço profissional') dd::text").get()
                if endereco and "não informado" not in endereco.lower():
                    dados["endereco_profissional"] = endereco.strip()

                # Sala
                sala = contato_section.css(
                    "dl:contains('Sala') dd::text").get()
                if sala and "não informado" not in sala.lower():
                    dados["sala"] = sala.strip()

                # Telefone/Ramal
                telefone = contato_section.css(
                    "dl:contains('Telefone') dd::text").get()
                if telefone and "não informado" not in telefone.lower():
                    dados["telefone_ramal"] = telefone.strip()

                # Email
                email = contato_section.css(
                    "dl:contains('Endereço eletrônico') dd::text").get()
                if email and "não informado" not in email.lower():
                    dados["email"] = email.strip()

            # === DADOS DO CURRÍCULO LATTES (JavaScript) ===
            script_content = response.css(
                "script:contains('var curriculo')::text").get()
            if script_content:
                curriculo_data = self.extrair_curriculo_lattes(script_content)
                if curriculo_data:
                    dados["curriculo_lattes_dados"] = curriculo_data

        except Exception as e:
            self.logger.error(f"❌ Erro ao extrair dados: {e}")
            dados["erro_extracao"] = str(e)

        return dados

    def extrair_curriculo_lattes(self, script_content):
        """Extrai dados básicos do currículo Lattes do JavaScript"""
        try:
            # Procurar padrões específicos no script
            curriculo_info = {}

            # Data de atualização
            match_data = re.search(
                r'"dataatualizacao":\s*"(\d+)"', script_content)
            if match_data:
                data_raw = match_data.group(1)
                # Converter formato DDMMAAAA para DD/MM/AAAA
                if len(data_raw) == 8:
                    curriculo_info["data_atualizacao"] = f"{data_raw[:2]}/{data_raw[2:4]}/{data_raw[4:]}"

            # Nome em citações bibliográficas
            match_citacao = re.search(
                r'"nomeemcitacoesbibliograficas":\s*"([^"]+)"', script_content)
            if match_citacao:
                curriculo_info["nome_citacoes"] = match_citacao.group(1)

            # Resumo CV
            match_resumo = re.search(
                r'"textoresumocvrh":\s*"([^"]+)"', script_content)
            if match_resumo:
                resumo = match_resumo.group(1)
                # Limpar HTML entities básicas
                resumo = resumo.replace("&#201;", "É").replace(
                    "&#195;", "Ã").replace("&#231;", "ç")
                curriculo_info["resumo_cv"] = resumo[:500] + \
                    "..." if len(resumo) > 500 else resumo

            return curriculo_info if curriculo_info else None

        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao extrair currículo Lattes: {e}")
            return None

    def closed(self, reason):
        """Método chamado quando spider é finalizado"""
        self.logger.info(f"📈 ESTATÍSTICAS FINAIS:")
        self.logger.info(f"   📋 Total de docentes: {self.total_docentes}")
        self.logger.info(f"   ✅ Processados com sucesso: {self.processados}")
        self.logger.info(f"   💾 HTMLs salvos em: {self.paginas_dir}")
        self.logger.info(f"   🏁 Motivo de encerramento: {reason}")

        if self.processados < self.total_docentes:
            falhas = self.total_docentes - self.processados
            self.logger.warning(f"   ⚠️ Falhas/Não processados: {falhas}")


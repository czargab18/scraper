# cd sigaa
# uv run scrapy runspider .\sigaa\spiders\docentes.py -o data\docentes\docentes.jsonl
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
        
        self.logger.info(f"🚀 Spider iniciado - Pasta temporária: {self.temp_dir.absolute()}")
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
        self.logger.info(f"📋 Total de departamentos encontrados: {total_departamentos}")
        
        # Iniciar processamento do primeiro departamento
        if self.departamentos_fila:
            yield self.processar_proximo_departamento(response)

    def processar_proximo_departamento(self, response):
        """Processa o próximo departamento da fila"""
        if self.departamento_atual >= len(self.departamentos_fila):
            self.logger.info("✅ Todos os departamentos foram processados!")
            return
        
        dept = self.departamentos_fila[self.departamento_atual]
        self.logger.info(f"📥 [{self.departamento_atual + 1}/{len(self.departamentos_fila)}] Baixando: {dept['nome']}")
        
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
            self.logger.info(f"❌ Nenhum docente encontrado para {departamento_nome}")
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
        self.logger.info(f"📊 Encontrados {total_docentes} docentes em {departamento_nome}")

        for linha in linhas_docentes:
            nome = linha.css("td:nth-child(2) span.nome::text").get()

            if nome:
                link_pagina = linha.css("td:nth-child(2) span.pagina a::attr(href)").get()
                
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
            self.logger.info(f"🎉 CONCLUÍDO! Processados {len(self.departamentos_fila)} departamentos")
    
    def closed(self, reason):
        """Método chamado quando spider é finalizado"""
        # Limpar pasta temporária final
        try:
            if self.temp_dir.exists():
                # Remover arquivos restantes
                for arquivo in self.temp_dir.glob("*.html"):
                    arquivo.unlink()
                    self.logger.info(f"🗑️ Limpeza final: removido {arquivo.name}")
                
                # Remover pasta se vazia
                if not any(self.temp_dir.iterdir()):
                    self.temp_dir.rmdir()
                    self.logger.info(f"📁 Pasta temporária removida: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro na limpeza final: {e}")
        
        # Estatísticas finais
        total_processados = self.departamento_atual
        self.logger.info(f"📈 ESTATÍSTICAS FINAIS:")
        self.logger.info(f"   📋 Departamentos processados: {total_processados}/{len(self.departamentos_fila)}")
        self.logger.info(f"   🏁 Motivo de encerramento: {reason}")

    def _limpar_pasta_temp(self):
        """Limpa arquivos antigos da pasta temporária"""
        try:
            for arquivo in self.temp_dir.glob("*.html"):
                arquivo.unlink()
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao limpar pasta: {e}")



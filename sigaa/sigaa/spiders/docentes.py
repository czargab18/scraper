# cd sigaa
# uv run scrapy runspider .\sigaa\spiders\docentes.py -o data\docentes\docentes.json
import scrapy


class DocentesSpider(scrapy.Spider):
    name = "docentes"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf"]
    
    # Configurações para lidar com muitos dados
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Delay entre requisições para não sobrecarregar o servidor
        'CONCURRENT_REQUESTS': 2,  # Uma requisição por vez
        'AUTOTHROTTLE_ENABLED': True,           # Ativa o AutoThrottle
        'AUTOTHROTTLE_START_DELAY': 1,          # Delay inicial: 1 segundo
        'AUTOTHROTTLE_MAX_DELAY': 5,            # Delay máximo: 5 segundos
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0, # Concorrência alvo
    }

    def parse(self, response):
        departamentos = response.css("select#form\\:departamento option")
        total_departamentos = len([d for d in departamentos if d.attrib.get("value") not in ["", "0"]])
        self.logger.info(f"Total de departamentos encontrados: {total_departamentos}")

        for opcao in departamentos:
            valor = opcao.attrib.get("value")
            texto = opcao.css("::text").get()

            if valor and valor not in ["", "0"]:
                self.logger.info(f"Processando departamento: {texto.strip()}")
                # Fazer POST para cada departamento
                yield scrapy.FormRequest.from_response(
                    response,
                    formname='form',
                    formdata={
                        'form:departamento': valor,
                        'form:buscar': 'Buscar'
                    },
                    callback=self.parse_docentes,
                    meta={'departamento_nome': texto.strip(),
                          'departamento_id': valor}
                )

    def parse_docentes(self, response):
        departamento_nome = response.meta['departamento_nome']
        departamento_id = response.meta['departamento_id']

        # Verificar se há resultados
        tabela_resultados = response.css("table.listagem")
        if not tabela_resultados:
            self.logger.info(f"Nenhum docente encontrado para {departamento_nome}")
            return

        # Extrair docentes da tabela de resultados
        linhas_docentes = response.css("table.listagem tbody tr")
        total_docentes = len(linhas_docentes)
        self.logger.info(f"Encontrados {total_docentes} docentes em {departamento_nome}")

        for linha in linhas_docentes:
            nome = linha.css("td:nth-child(2) span.nome::text").get()

            if nome:
                link_pagina = linha.css("td:nth-child(2) span.pagina a::attr(href)").get()
                
                siape = None
                if link_pagina:
                    if not link_pagina.startswith('http'):
                        link_pagina = response.urljoin(link_pagina)
                    
                    if "siape=" in link_pagina:
                        siape = link_pagina.split("siape=")[1].split("&")[0]

                foto_url = linha.css("td.foto img::attr(src)").get()
                if foto_url and not foto_url.startswith('http'):
                    foto_url = response.urljoin(foto_url)

                yield {
                    'codigo_departamento': departamento_id,
                    'departamento': departamento_nome,
                    'nome_docente': nome.strip(),
                    'siape': siape,
                    'link_pagina': link_pagina,
                    # 'url_foto': foto_url
                }



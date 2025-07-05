import scrapy


class DocentesSpider(scrapy.Spider):
    name = "docentes"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf?aba=p-academico"]

    def parse(self, response):
        departamentos = response.css("select#form\\:departamento option")

        for opcao in departamentos:
            valor = opcao.attrib.get("value")
            texto = opcao.css("::text").get()

            if valor and valor not in ["", "0"]:
                # Fazer POST para cada departamento
                yield scrapy.FormRequest.from_response(
                    response,
                    formname='form',
                    formdata={
                        'form:departamento': valor,
                        'form:buscar': 'Buscar'  # Nome do botão
                    },
                    callback=self.parse_docentes,
                    meta={'departamento_nome': texto.strip(),
                          'departamento_id': valor}
                )

    def parse_docentes(self, response):
        # Extrair dados dos docentes da página de resultados
        departamento_nome = response.meta['departamento_nome']
        departamento_id = response.meta['departamento_id']

        # Extrair docentes da tabela de resultados
        for docente in response.css("table.listing tr"):
            # Pular cabeçalho da tabela
            if docente.css("th"):
                continue
                
            nome = docente.css("td:nth-child(1) a::text").get()
            link_pagina = docente.css("td:nth-child(1) a::attr(href)").get()
            situacao = docente.css("td:nth-child(2)::text").get()
            
            if nome:
                if link_pagina and not link_pagina.startswith('http'):
                    link_pagina = response.urljoin(link_pagina)
                    
                yield {
                    'codigo': departamento_id,
                    'unidade': departamento_nome,
                    'docente': nome.strip(),
                    'link_pagina': link_pagina,
                    'situacao': situacao.strip() if situacao else None
                }

#> cd sigaa
# > uv run scrapy runspider .\sigaa\spiders\docentes.py -o data\docentes\docentes_completo.json

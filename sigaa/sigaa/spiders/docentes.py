# cd sigaa & & uv run scrapy runspider .\sigaa\spiders\docentes.py -o data\docentes\docentes.json
import scrapy


class DocentesSpider(scrapy.Spider):
    name = "docentes"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf"]

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

        # Verificar se há resultados
        tabela_resultados = response.css("table.listagem")
        if not tabela_resultados:
            self.logger.info(f"Nenhum docente encontrado para {departamento_nome}")
            return

        # Extrair docentes da tabela de resultados
        linhas_docentes = response.css("table.listagem tbody tr")

        for linha in linhas_docentes:
            # Extrair nome do docente
            nome = linha.css("td:nth-child(2) span.nome::text").get()

            if nome:
                # Extrair link da página pública
                link_pagina = linha.css("td:nth-child(2) span.pagina a::attr(href)").get()

                # Extrair SIAPE do link se disponível
                siape = None
                if link_pagina:
                    if link_pagina and not link_pagina.startswith('http'):
                        link_pagina = response.urljoin(link_pagina)

                    # Extrair SIAPE do parâmetro da URL
                    if "siape=" in link_pagina:
                        siape = link_pagina.split("siape=")[1].split("&")[0]

                # Extrair URL da foto (se disponível)
                foto_url = linha.css("td.foto img::attr(src)").get()
                if foto_url and not foto_url.startswith('http'):
                    foto_url = response.urljoin(foto_url)

                yield {
                    'codigo_departamento': departamento_id,
                    'departamento': departamento_nome,
                    'nome_docente': nome.strip(),
                    'siape': siape,
                    'link_pagina_publica': link_pagina,
                    'url_foto': foto_url
                }

# Para rodar:
# cd sigaa
# uv run scrapy runspider .\sigaa\spiders\docentes.py -o data\docentes\docentes_completo.json



import scrapy

class DocentesSpider(scrapy.Spider):
    name = "docentes"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = ["https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf?aba=p-academico"]

    def parse(self, response):
        departamentos = response.css("select#form\\:departamento option")
        for opcao in departamentos:
            valor = opcao.attrib.get("value")
            texto = opcao.css("::text").get()
            if valor and valor not in ["", "0"]:
                yield {
                    # código = nome departamento
                    valor : texto.strip()
                }


#> cd sigaa
# > uv run scrapy runspider .\sigaa\spiders\docentes.py -o data\docentes\departamentos.json

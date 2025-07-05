import scrapy


class DocentesSpider(scrapy.Spider):
    name = "docentes"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = ["https://sigaa.unb.br/sigaa/public/docente/busca_docentes.jsf?aba=p-academico"]

    def parse(self, response):
        for departamento in response.css("select#form:departamento"):
            yield response.follow(departamento, self.parse_departamento)



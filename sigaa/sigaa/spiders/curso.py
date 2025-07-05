import scrapy


class CursoSpider(scrapy.Spider):
    name = "curso"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = ["https://sigaa.unb.br/sigaa/public/curso/lista.jsf?nivel=G"]

    def parse(self, response):
        pass

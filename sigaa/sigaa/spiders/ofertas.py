import scrapy
import os

class OfertasSpider(scrapy.Spider):
    name = "ofertas"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = ["https://sigaa.unb.br/sigaa/public/curso/lista.jsf?nivel=G"]
    

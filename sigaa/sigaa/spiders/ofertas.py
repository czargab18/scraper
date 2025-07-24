import scrapy
import os


class OfertasSpider(scrapy.Spider):
    name = "ofertas"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
    ]

    def parse(self, response):
        for row in response.css('div#turmasAbertas table.listagem tbody tr'):
            codigo = row.css('td.turma::text').get()
            if not codigo:
                continue
            yield {
                'codigo': codigo.strip(),
                'ano_periodo': row.css('td.anoPeriodo::text').get(default='').strip(),
                'docente': row.css('td.nome::text').get(default='').strip(),
                'horario': row.css('td:nth-child(4)::text').get(default='').strip(),
                'vagas_ofertadas': row.css('td:nth-child(6)::text').get(default='').strip(),
                'vagas_ocupadas': row.css('td:nth-child(7)::text').get(default='').strip(),
                'local': row.css('td:nth-child(8)::text').get(default='').strip(),
            }

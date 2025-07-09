import scrapy
import os

class OfertasSpider(scrapy.Spider):
    name = "ofertas"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        f"file://{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../mock/ofertas.html'))}"
    ]

    def parse(self, response):
        agrupadores = response.css('tr.agrupador')
        for agrupador in agrupadores:
            disciplina = agrupador.css('span.tituloDisciplina::text').get()
            # As linhas das turmas vêm após o agrupador
            turma_rows = agrupador.xpath('following-sibling::tr[contains(@class, "linha")]')
            for turma in turma_rows:
                yield {
                    'disciplina': disciplina.strip() if disciplina else None,
                    'codigo_turma': turma.css('td.turma::text').get(default='').strip(),
                    'ano_periodo': turma.css('td.anoPeriodo::text').get(default='').strip(),
                    'docentes': [d.strip() for d in turma.css('td.nome::text').getall() if d.strip()],
                    'horario': turma.css('td:nth-child(4)::text').get(default='').strip(),
                    'vagas_ofertadas': turma.css('td[6]::text').get(default='').strip(),
                    'vagas_ocupadas': turma.css('td[7]::text').get(default='').strip(),
                    'local': turma.css('td[8]::text').get(default='').strip(),
                }

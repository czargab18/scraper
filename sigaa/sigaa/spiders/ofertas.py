import scrapy
import os

class OfertasSpider(scrapy.Spider):
    name = "ofertas"
    allowed_domains = ["sigaa.unb.br"]

    def start_requests(self):
        file_url = f"file://{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../mock/ofertas.html'))}"
        if file_url.startswith("file://"):
            yield scrapy.Request(
                url=file_url,
                callback=self.parse
            )
        else:
            formdata = {
                'formTurma': 'formTurma',
                'formTurma:inputNivel': 'G',
                'formTurma:inputDepto': '518',
                'formTurma:inputAno': '2025',
                'formTurma:inputPeriodo': '2',
                'formTurma:j_id_jsp_1370969402_11': 'Buscar',
            }
            yield scrapy.FormRequest(
                url=file_url,
                formdata=formdata,
                callback=self.parse
            )

    def parse(self, response):
        agrupadores = response.css('tr.agrupador')
        turmas_extraidas = []
        for agrupador in agrupadores:
            disciplina = agrupador.css('span.tituloDisciplina::text').get()
            # As linhas das turmas vêm após o agrupador
            turma_rows = agrupador.xpath('following-sibling::tr[contains(@class, "linha")]')
            for turma in turma_rows:
                turma_dict = {
                    'disciplina': disciplina.strip() if disciplina else None,
                    'codigo_turma': turma.css('td.turma::text').get(default='').strip(),
                    'ano_periodo': turma.css('td.anoPeriodo::text').get(default='').strip(),
                    'docentes': [d.strip() for d in turma.css('td.nome::text').getall() if d.strip()],
                    'horario': turma.css('td:nth-child(4)::text').get(default='').strip(),
                    'vagas_ofertadas': turma.css('td[6]::text').get(default='').strip(),
                    'vagas_ocupadas': turma.css('td[7]::text').get(default='').strip(),
                    'local': turma.css('td[8]::text').get(default='').strip(),
                }
                turmas_extraidas.append(turma_dict)
                yield turma_dict
        # Extrai ano e período diretamente da página
        ano = response.css('input#formTurma\\:inputAno::attr(value)').get(
            default='').strip()
        periodo = response.css(
            'select#formTurma\\:inputPeriodo option[selected]::attr(value)').get(default='').strip()
        nome_arquivo = f"ofertas_{ano}_{periodo}.json" if ano and periodo else f"ofertas{ano}.json"
        import json
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(turmas_extraidas, f, ensure_ascii=False, indent=2)

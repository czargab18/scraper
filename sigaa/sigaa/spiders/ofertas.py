import scrapy
import os
import glob
import json
from parsel import Selector


class OfertasSpider(scrapy.Spider):
    name = "ofertas"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = [
        "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf?aba=p-ensino"]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
    }

    def start_requests(self):
        import csv
        departamentos_path = os.path.abspath(os.path.join(os.path.dirname(
            __file__), '..', '..', 'data', 'unidades', 'departamentos.csv'))
        with open(departamentos_path, encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile, delimiter=';'))

        # Defina os anos e semestres desejados
        anos = ['2025']  # Adapte conforme necessário
        semestres = ['1', '2', '3', '4']

        for ano in anos:
            for semestre in semestres:
                for row in reader:
                    depto_id = row['id_departamento']
                    meta = {
                        'departamento': row['nome_departamento'],
                        'id_departamento': depto_id,
                        'ano': ano,
                        'semestre': semestre
                    }
                    yield scrapy.Request(
                        url="https://sigaa.unb.br/sigaa/public/turmas/listar.jsf?aba=p-ensino",
                        callback=self.preencher_formulario,
                        meta=meta,
                        dont_filter=True
                    )

    def preencher_formulario(self, response):
        import re
        viewstate = response.css(
            'input[name="javax.faces.ViewState"]::attr(value)').get()
        depto_id = response.meta['id_departamento']
        departamento = response.meta['departamento']
        ano = response.meta['ano']
        semestre = response.meta['semestre']
        formdata = {
            'formTurma': 'formTurma',
            'formTurma:inputNivel': '',
            'formTurma:inputDepto': depto_id,
            'formTurma:inputAno': ano,
            'formTurma:inputPeriodo': semestre,
            'javax.faces.ViewState': viewstate or '',
            'formTurma:j_id_jsp_1370969402_11': 'Buscar',
        }
        yield scrapy.FormRequest(
            url="https://sigaa.unb.br/sigaa/public/turmas/listar.jsf",
            formdata=formdata,
            callback=self.parse,
            meta={
                'departamento': departamento,
                'id_departamento': depto_id,
                'ano': ano,
                'semestre': semestre
            }
        )

    def parse(self, response):
        id_departamento = response.meta.get('id_departamento', '')
        ano = response.meta.get('ano', '')
        semestre = response.meta.get('semestre', '')
        # Cria pasta para ano/semestre
        base_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'mock', ano, semestre))
        os.makedirs(base_dir, exist_ok=True)
        file_path = os.path.join(base_dir, f'ofertas_{id_departamento}.html')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info(f'Página salva: {file_path}')


mock_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', 'mock'))
saida_jsonl = os.path.abspath(os.path.join(os.path.dirname(
    __file__), '..', '..', 'data', 'ofertas', '2025-2.jsonl'))

with open(saida_jsonl, 'w', encoding='utf-8') as fout:
    for html_path in glob.glob(os.path.join(mock_dir, 'ofertas_*.html')):
        with open(html_path, encoding='utf-8') as f:
            html = f.read()
        sel = Selector(text=html)
        id_departamento = os.path.basename(html_path).split('_')[
            1].split('.')[0]
        for row in sel.css('div#turmasAbertas table.listagem tbody tr'):
            codigo = row.css('td.turma::text').get()
            if not codigo:
                continue
            oferta = {
                'id_departamento': id_departamento,
                'codigo': codigo.strip(),
                'ano_periodo': row.css('td.anoPeriodo::text').get(default='').strip(),
                'docente': row.css('td.nome::text').get(default='').strip(),
                'horario': row.css('td:nth-child(4)::text').get(default='').strip(),
                'vagas_ofertadas': row.css('td:nth-child(6)::text').get(default='').strip(),
                'vagas_ocupadas': row.css('td:nth-child(7)::text').get(default='').strip(),
                'local': row.css('td:nth-child(8)::text').get(default='').strip(),
            }
            fout.write(json.dumps(oferta, ensure_ascii=False) + '\n')

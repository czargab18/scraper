import scrapy
import os


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
        # Faz um GET para obter o ViewState antes de cada POST
        for row in reader:
            depto_id = row['id_departamento']
            meta = {
                'departamento': row['nome_departamento'], 'id_departamento': depto_id}
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
        formdata = {
            'formTurma': 'formTurma',
            'formTurma:inputNivel': '',
            'formTurma:inputDepto': depto_id,
            'formTurma:inputAno': '2025',
            'formTurma:inputPeriodo': '1',
            'javax.faces.ViewState': viewstate or '',
            'formTurma:j_id_jsp_1370969402_11': 'Buscar',
        }
        yield scrapy.FormRequest(
            url="https://sigaa.unb.br/sigaa/public/turmas/listar.jsf",
            formdata=formdata,
            callback=self.parse,
            meta={'departamento': departamento, 'id_departamento': depto_id}
        )

    def parse(self, response):
        id_departamento = response.meta.get('id_departamento', '')
        mock_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'mock'))
        os.makedirs(mock_dir, exist_ok=True)
        file_path = os.path.join(mock_dir, f'ofertas_{id_departamento}.html')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        self.logger.info(f'Página salva: {file_path}')

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
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                depto_id = row['id_departamento']
                # Monta os dados do formulário para cada departamento
                formdata = {
                    'formTurma': 'formTurma',
                    'formTurma:inputNivel': '',  # pode ser ajustado se necessário
                    'formTurma:inputDepto': depto_id,
                    'formTurma:inputAno': '2025',
                    'formTurma:inputPeriodo': '1',
                    'javax.faces.ViewState': 'j_id4',  # pode precisar ser dinâmico
                }
                yield scrapy.FormRequest(
                    url="https://sigaa.unb.br/sigaa/public/turmas/listar.jsf",
                    formdata=formdata,
                    callback=self.parse,
                    meta={
                        'departamento': row['nome_departamento'], 'id_departamento': depto_id}
                )

    def parse(self, response):
        departamento = response.meta.get('departamento', '')
        id_departamento = response.meta.get('id_departamento', '')
        for row in response.css('div#turmasAbertas table.listagem tbody tr'):
            codigo = row.css('td.turma::text').get()
            if not codigo:
                continue
            yield {
                'departamento': departamento,
                'id_departamento': id_departamento,
                'codigo': codigo.strip(),
                'ano_periodo': row.css('td.anoPeriodo::text').get(default='').strip(),
                'docente': row.css('td.nome::text').get(default='').strip(),
                'horario': row.css('td:nth-child(4)::text').get(default='').strip(),
                'vagas_ofertadas': row.css('td:nth-child(6)::text').get(default='').strip(),
                'vagas_ocupadas': row.css('td:nth-child(7)::text').get(default='').strip(),
                'local': row.css('td:nth-child(8)::text').get(default='').strip(),
            }

import os
import glob
import json
from parsel import Selector

# Parâmetros
anos = ['2025']  # Adapte conforme necessário
semestres = ['1', '2', '3', '4']

base_mock = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'mock'))
base_saida = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'data', 'ofertas'))
os.makedirs(base_saida, exist_ok=True)

for ano in anos:
    for semestre in semestres:
        pasta_html = os.path.join(base_mock, ano, semestre)
        saida_jsonl = os.path.join(base_saida, f'{ano}-{semestre}.jsonl')
        arquivos_html = glob.glob(os.path.join(pasta_html, 'ofertas_*.html'))
        with open(saida_jsonl, 'w', encoding='utf-8') as fout:
            for html_path in arquivos_html:
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
print('Extração concluída!')

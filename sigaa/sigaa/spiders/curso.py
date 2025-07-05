# > cd sigaa
# > uv run scrapy runspider .\\sigaa\\spiders\\curso.py -o data\\cursos\\cursos.jsonl

import scrapy


class CursoSpider(scrapy.Spider):
    name = "curso"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = ["https://sigaa.unb.br/sigaa/public/curso/lista.jsf?nivel=G"]

    def criar_dados_curso(self, tr, sigla_departamento, departamento):
        """Extrai e organiza os dados de um curso a partir de uma linha da tabela"""
        nome_curso = tr.css("td:nth-child(1)::text").get()
        grau_academico = tr.css("td:nth-child(2)::text").get()
        turno = tr.css("td:nth-child(3)::text").get()
        sede = tr.css("td:nth-child(4)::text").get()
        modalidade = tr.css("td:nth-child(5)::text").get()
        grau_academico_2 = tr.css("td:nth-child(6)::text").get()
        coordenacao = tr.css("td:nth-child(7)::text").get()
        link_curso = tr.css("td:nth-child(8) a::attr(href)").get()

        return {
            'sigla_departamento': sigla_departamento,
            'departamento': departamento,
            'nome': nome_curso.strip() if nome_curso else None,
            'grau_academico': grau_academico.strip() if grau_academico else None,
            'turno': turno.strip() if turno else None,
            'sede': sede.strip() if sede else None,
            'modalidade': modalidade.strip() if modalidade else None,
            'grau_academico_2': grau_academico_2.strip() if grau_academico_2 else None,
            'coordenacao': coordenacao.strip() if coordenacao else None,
            'link_detalhes': link_curso
        }

    def parse(self, response):
        self.logger.info("📋 Extraindo lista de cursos...")

        tabela_cursos = response.css("table.listagem tbody")

        if not tabela_cursos:
            self.logger.warning("⚠️ Tabela de cursos não encontrada")
            return

        departamento_atual = None
        total_cursos = 0

        for tr in tabela_cursos.css("tr"):
            departamento_cell = tr.css("td.subFormulario::text").get()

            if departamento_cell:
                departamento_atual = departamento_cell.strip()
                if " - " in departamento_atual:
                    sigla_departamento_atual = departamento_atual.split(
                        " - ")[0]
                self.logger.info(
                    f"🏢 Processando departamento: {departamento_atual} (Sigla: {sigla_departamento_atual})")
                continue
            nome_curso = tr.css("td:nth-child(1)::text").get()

            if nome_curso and nome_curso.strip():
                curso_data = self.criar_dados_curso(
                    tr, sigla_departamento_atual, departamento_atual)

                total_cursos += 1
                self.logger.info(
                    f"📚 Curso encontrado: {curso_data['nome']} - {curso_data['turno']}")

                yield curso_data

        self.logger.info(f"✅ Total de cursos extraídos: {total_cursos}")

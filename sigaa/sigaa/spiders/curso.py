import scrapy


class CursoSpider(scrapy.Spider):
    name = "curso"
    allowed_domains = ["sigaa.unb.br"]
    start_urls = ["https://sigaa.unb.br/sigaa/public/curso/lista.jsf?nivel=G"]

    def parse(self, response):
        self.logger.info("📋 Extraindo lista de cursos...")
        
        tabela_cursos = response.css("table.listagem tbody")
        
        if not tabela_cursos:
            self.logger.warning("⚠️ Tabela de cursos não encontrada")
            return
        
        departamento_atual = None
        total_cursos = 0
        
        # Iterar por todas as linhas da tabela
        for tr in tabela_cursos.css("tr"):
            # Verificar se é uma linha de departamento
            departamento_cell = tr.css("td.subFormulario::text").get()
            
            if departamento_cell:
                # É uma linha de departamento
                departamento_atual = departamento_cell.strip()
                # Extrair sigla do departamento (parte antes do " - ")
                if " - " in departamento_atual:
                    sigla_departamento_atual = departamento_atual.split(" - ")[0]
                
                self.logger.info(f"🏢 Processando departamento: {departamento_atual} (Sigla: {sigla_departamento_atual})")
                continue
            
            # Verificar se é uma linha de curso
            nome_curso = tr.css("td:nth-child(1)::text").get()
            
            if nome_curso and nome_curso.strip():
                # É uma linha de curso
                grau_academico = tr.css("td:nth-child(2)::text").get()
                turno = tr.css("td:nth-child(3)::text").get()
                sede = tr.css("td:nth-child(4)::text").get()
                modalidade = tr.css("td:nth-child(5)::text").get()
                grau_academico_2 = tr.css("td:nth-child(6)::text").get()
                coordenacao = tr.css("td:nth-child(7)::text").get()
                
                # Link para a página do curso
                link_curso = tr.css("td:nth-child(8) a::attr(href)").get()
                
                curso_data = {
                    'sigla_departamento': sigla_departamento_atual,
                    'departamento': departamento_atual,
                    'nome': nome_curso.strip() if nome_curso else None,
                    'grau_academico': grau_academico.strip() if grau_academico else None,
                    'turno': turno.strip() if turno else None,
                    'sede': sede.strip() if sede else None,
                    'modalidade': modalidade.strip() if modalidade else None,
                    'grau_academico_2': grau_academico_2.strip() if grau_academico_2 else None,
                    'coordenacao': coordenacao.strip() if coordenacao else None,
                    'link_detalhes': link_curso
                }
                
                total_cursos += 1
                self.logger.info(f"📚 Curso encontrado: {curso_data['nome']} - {curso_data['turno']}")
                
                yield curso_data
        
        self.logger.info(f"✅ Total de cursos extraídos: {total_cursos}")






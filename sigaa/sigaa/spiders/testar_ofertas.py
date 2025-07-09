import os
import subprocess

# Caminho para o diretório do projeto scrapy (onde está o scrapy.cfg)
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

cmd = [
    'scrapy',
    'crawl',
    'ofertas'
]

print(f"Executando: {' '.join(cmd)} no diretório {PROJECT_DIR}")

subprocess.run(cmd, cwd=PROJECT_DIR)

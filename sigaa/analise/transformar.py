#!/usr/bin/env python3
#> (scraper) PS C:\Users\cesargabriel\github\scraper>
#> uv run .\sigaa\analise\transformar.py .\sigaa\data\cursos\cursos.jsonl
"""
Script para converter arquivos JSONL para CSV
Lê arquivos .jsonl e converte as informações para formato CSV

Exemplo de uso:
    python transformar.py input.jsonl output.csv
    python transformar.py --input data/cursos/cursos.jsonl --output cursos.csv
"""

import json
import csv
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any


def ler_jsonl(arquivo_jsonl: str) -> List[Dict[str, Any]]:
    """
    Lê um arquivo JSONL e retorna uma lista de dicionários
    
    Args:
        arquivo_jsonl: Caminho para o arquivo JSONL
        
    Returns:
        Lista de dicionários com os dados do arquivo
    """
    dados = []
    
    try:
        with open(arquivo_jsonl, 'r', encoding='utf-8') as arquivo:
            for linha_num, linha in enumerate(arquivo, 1):
                linha = linha.strip()
                if linha:  # Ignora linhas vazias
                    try:
                        dados.append(json.loads(linha))
                    except json.JSONDecodeError as e:
                        print(f"Erro ao processar linha {linha_num}: {e}")
                        print(f"Linha problemática: {linha}")
                        continue
                        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_jsonl}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        sys.exit(1)
        
    return dados


def jsonl_para_csv(arquivo_jsonl: str, arquivo_csv: str = None) -> str:
    """
    Converte um arquivo JSONL para CSV
    
    Args:
        arquivo_jsonl: Caminho para o arquivo JSONL de entrada
        arquivo_csv: Caminho para o arquivo CSV de saída (opcional)
        
    Returns:
        Caminho do arquivo CSV criado
    """
    # Se não especificar arquivo de saída, criar baseado no nome do arquivo de entrada
    if not arquivo_csv:
        caminho_entrada = Path(arquivo_jsonl)
        arquivo_csv = caminho_entrada.with_suffix('.csv')
    
    # Ler dados do JSONL
    dados = ler_jsonl(arquivo_jsonl)
    
    if not dados:
        print("Nenhum dado encontrado no arquivo JSONL")
        return None
    
    # Extrair todas as chaves únicas dos dados
    todas_chaves = set()
    for item in dados:
        todas_chaves.update(item.keys())
    
    # Ordenar as chaves para ter uma ordem consistente
    colunas = sorted(list(todas_chaves))
    
    # Escrever arquivo CSV
    try:
        with open(arquivo_csv, 'w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=colunas)
            
            # Escrever cabeçalho
            escritor.writeheader()
            
            # Escrever dados
            for item in dados:
                escritor.writerow(item)
                
        print(f"Arquivo CSV criado com sucesso: {arquivo_csv}")
        print(f"Total de registros processados: {len(dados)}")
        print(f"Colunas: {', '.join(colunas)}")
        
        return str(arquivo_csv)
        
    except Exception as e:
        print(f"Erro ao escrever arquivo CSV: {e}")
        return None


def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(
        description="Converte arquivos JSONL para CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s cursos.jsonl
  %(prog)s cursos.jsonl cursos.csv
  %(prog)s --input data/cursos/cursos.jsonl --output saida/cursos.csv
  %(prog)s -i departamentos.jsonl -o departamentos.csv
        """
    )
    
    parser.add_argument(
        'input_file', 
        nargs='?',
        help='Arquivo JSONL de entrada'
    )
    
    parser.add_argument(
        'output_file', 
        nargs='?',
        help='Arquivo CSV de saída (opcional)'
    )
    
    parser.add_argument(
        '-i', '--input',
        dest='input_file_flag',
        help='Arquivo JSONL de entrada'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file_flag',
        help='Arquivo CSV de saída'
    )
    
    parser.add_argument(
        '--listar',
        action='store_true',
        help='Lista todos os arquivos JSONL disponíveis no projeto'
    )
    
    args = parser.parse_args()
    
    # Opção para listar arquivos JSONL disponíveis
    if args.listar:
        print("Arquivos JSONL encontrados no projeto:")
        base_path = Path(__file__).parent.parent
        arquivos_jsonl = list(base_path.rglob("*.jsonl"))
        
        if arquivos_jsonl:
            for arquivo in sorted(arquivos_jsonl):
                print(f"  {arquivo.relative_to(base_path)}")
        else:
            print("  Nenhum arquivo JSONL encontrado")
        return
    
    # Determinar arquivo de entrada
    arquivo_entrada = args.input_file or args.input_file_flag
    if not arquivo_entrada:
        parser.print_help()
        print("\nErro: É necessário especificar um arquivo JSONL de entrada")
        sys.exit(1)
    
    # Determinar arquivo de saída
    arquivo_saida = args.output_file or args.output_file_flag
    
    # Verificar se arquivo de entrada existe
    if not Path(arquivo_entrada).exists():
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado")
        sys.exit(1)
    
    # Converter JSONL para CSV
    resultado = jsonl_para_csv(arquivo_entrada, arquivo_saida)
    
    if resultado:
        print(f"\nConversão concluída com sucesso!")
    else:
        print("\nFalha na conversão")
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
Script para processar dados de departamentos da UnB
Lê o arquivo CSV gerado pelo script transformar.py e processa os dados

Formato esperado:
id_departamento;nome_departamento
672;CAMPUS UNB CEILÂNDIA: FACULDADE DE CIENCIAS E TECNOLOGIAS EM SAÚDE - BRASÍLIA
640;CENTRO DE DESENVOLVIMENTO SUSTENTÁVEL - BRASÍLIA
677;CENTRO UNB CERRADO - BRASÍLIA
130;DECANATO DE ENSINO DE GRADUACAO / DEG - BRASÍLIA
392;DEPARTAMENTO DE TEORIA E FUNDAMENTOS - BRASÍLIA
327;DEPTO ADMINISTRAÇÃO - BRASÍLIA
362;DEPTO TEORIA HISTORIA ARQUIT E URBANISM - BRASÍLIA
580;DEPTO TEORIA LITERÁRIA E LITERATURA - BRASÍLIA
472;DEPTO ZOOLOGIA - BRASÍLIA
643;DIRETORIA DO CENTRO DE APOIO AO DESENVOLVIMENTO TECNOLÓGICO - BRASÍLIA
363;FACULDADE DE AGRONOMIA E MEDICINA VETERINÁRIA - BRASÍLIA
288;HOSP-HOSPITAL UNIVERSITÁRIO DE BRASÍLIA - BRASÍLIA
485;INSTITUTO DE ARTES - BRASÍLIA
668;INSTITUTO DE CIÊNCIA POLÍTICA - BRASÍLIA
542;OBSERVATÓRIO SISMOLÓGICO - BRASÍLIA
1080;PARQUE CIENTÍFICO E TECNOLÓGICO DA UNB - BRASÍLIA
1615;PARQUE DE INOVAÇÃO E SUSTENTABILIDADE DO AMBIENTE CONSTRUÍDO - BRASÍLIA
69;REITORIA - BRASÍLIA
140;SECRETARIA DE ADMINISTRACAO ACADEMICA - BRASÍLIA
"""

from turtle import clear
import pandas as pd

# Carregar dados dos departamentos
unidades = pd.read_csv(
    "./sigaa/data/unidades/departamentos.csv",
    sep=";",
    encoding="utf-8",
    dtype={
        "id_departamento": str,
        "nome_departamento": str,
    },
)

# print("\nPrimeiros 10 registros:")
# print(unidades.head(10))
clear
nomes_departamentos = unidades['nome_departamento'].tolist()

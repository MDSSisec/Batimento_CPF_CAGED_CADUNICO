from constantesTextos import *
from funcoesauxiliares import formatar_cpfs, comparar_cpfs, retirar_zeroz, dividir_cpfs


if __name__ == "__main__":
    formatar_cpfs(INPUT_FILE, OUTPUT_FILE)
    comparar_cpfs(ARQUIVO_ORIGINAL, ARQUIVO_SIM)
    retirar_zeroz(ARQUIVO_FINAL)
    dividir_cpfs(ARQUIVO_EXCEL, PASTA_SAIDA, TAMANHO_LOTE)

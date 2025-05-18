import re
import os
import pandas as pd

def formatar_cpfs(input_file, output_file):
    def clean_cpf(cpf):
        return re.sub(r'\D', '', cpf)

    try:
        # Lê os CPFs do arquivo de entrada
        with open(input_file, 'r') as infile:
            raw_cpfs = infile.readlines()

        # Remove espaços e quebras de linha, e formata os CPFs
        formatted_cpfs = [f"{int(clean_cpf(cpf.strip())):011}," for cpf in raw_cpfs if clean_cpf(cpf.strip()).isdigit()]

        # Escreve os CPFs formatados no arquivo de saída
        with open(output_file, 'w') as outfile:
            outfile.write('\n'.join(formatted_cpfs))

        print(f"Processamento concluído! Arquivo salvo em: {output_file}")
    except Exception as e:
        print(f"Erro ao processar os arquivos: {e}")

def comparar_cpfs(arquivo_original, arquivo_sim):
    try:
        # Lendo os arquivos Excel
        df_sim = pd.read_excel(arquivo_sim)
        df_original = pd.read_excel(arquivo_original)

        # Criando um set com os CPFs do arquivo Sim
        cpfs_sim = set(df_sim['NU_CPF_PESSOA'])

        def verificar_cpf(cpf):
            return 'Sim' if cpf in cpfs_sim else 'Não'

        # Aplicando a verificação e criando a nova coluna
        df_original['CAD_UNICO'] = df_original['CPF'].apply(verificar_cpf)

        # Formatando as datas para remover o horário
        for coluna in df_original.columns:
            if pd.api.types.is_datetime64_any_dtype(df_original[coluna]):
                df_original[coluna] = df_original[coluna].dt.date

        # Salvando o arquivo atualizado
        df_original.to_excel(arquivo_original, index=False)

        print(f"Processo concluído! A coluna CAD_UNICO foi adicionada ao arquivo {arquivo_original} e as datas foram formatadas corretamente.")
    except Exception as e:
        print(f"Erro ao processar os arquivos: {e}")

def retirar_zeroz(arquivo):
    try:
        # Lê a planilha
        df = pd.read_excel(arquivo)

        # Remove o horário da coluna DT_NSC, mantendo apenas a data
        if 'DT_NSC' in df.columns:
            df['DT_NSC'] = pd.to_datetime(df['DT_NSC']).dt.date
        else:
            print("Coluna 'DT_NSC' não encontrada!")

        # Substitui valores na coluna CAD_UNICO: 'N' -> 'Não', 'S' -> 'Sim'
        if 'CAD_UNICO' in df.columns:
            df['CAD_UNICO'] = df['CAD_UNICO'].replace({'N': 'Não', 'S': 'Sim'})
        else:
            print("Coluna 'CAD_UNICO' não encontrada!")

        # Salva o resultado (sobrescreve o arquivo original)
        df.to_excel(arquivo, index=False)

        print("✅ Datas formatadas sem horário na coluna DT_NSC e valores de CAD_UNICO substituídos!")
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

def dividir_cpfs(arquivo_excel, pasta_saida, tamanho_lote):
    try:
        # Garante que a pasta de saída existe
        os.makedirs(pasta_saida, exist_ok=True)

        # Lê a coluna CPF da planilha
        df = pd.read_excel(arquivo_excel, usecols=['CPF'])
        cpfs = df['CPF'].astype(str).tolist()

        # Divide em lotes
        for i in range(0, len(cpfs), tamanho_lote):
            lote = cpfs[i:i+tamanho_lote]
            nome_arquivo = os.path.join(pasta_saida, f'cpfs_parte_{i//tamanho_lote + 1}.txt')
            with open(nome_arquivo, 'w') as f:
                for cpf in lote:
                    f.write(f"{cpf}\n")

        print(f"✅ {len(cpfs)} CPFs divididos em arquivos de até {tamanho_lote} linhas na pasta '{pasta_saida}'")
    except Exception as e:
        print(f"Erro ao dividir os CPFs: {e}")

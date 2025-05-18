# Em conversa com o chatgpt ele me sugeriu isso aqui.
# Precisa intalar = pip install pandas teradatasql openpyxl







import pandas as pd
import teradatasql
from time import sleep

# Configurações
ARQUIVO_CPF = 'cpfs.csv'
TAMANHO_BLOCO = 5000
ARQUIVO_SAIDA = 'resultado_cpfs.xlsx'

# Conexão com o Teradata
conn = teradatasql.connect(
    host='SEU_HOST',
    user='SEU_USUARIO',
    password='SUA_SENHA'
)

# Leitura dos CPFs
df_cpfs = pd.read_csv(ARQUIVO_CPF, header=None, names=['cpf'])
cpfs = df_cpfs['cpf'].astype(str).tolist()

# Função que executa a query em blocos
def consultar_em_blocos(cpfs, bloco=5000):
    resultados = []
    total_blocos = len(cpfs) // bloco + 1

    for i in range(0, len(cpfs), bloco):
        bloco_cpfs = cpfs[i:i + bloco]
        cpf_list = ','.join(bloco_cpfs)

        query = f"""
        WITH PessoasExcluidas AS (
            SELECT CO_CHV_NATURAL_PESSOA
            FROM P_CADASTRO_ODS_202503.TB_PESSOA_EXCLUIDA_19
        ), FamiliasValidas AS (
            SELECT CO_FAMILIAR_FAM
            FROM P_CADASTRO_ODS_202503.TB_FAMILIA_01
            WHERE IN_CADASTRO_VALIDO_FAM = 1
        ), PessoasCadastradas AS (
            SELECT P.CO_FAMILIAR_FAM, P.NO_PESSOA, P.CO_CHV_NATURAL_PESSOA
            FROM P_CADASTRO_ODS_202503.TB_PESSOA_04 P
            INNER JOIN FamiliasValidas FV ON P.CO_FAMILIAR_FAM = FV.CO_FAMILIAR_FAM
            WHERE P.CO_EST_CADASTRAL_MEMB = 3
            AND NOT EXISTS (
                SELECT 1
                FROM PessoasExcluidas PE
                WHERE PE.CO_CHV_NATURAL_PESSOA = P.CO_CHV_NATURAL_PESSOA
            )
        )
        SELECT 
            DISTINCT(DOC.NU_CPF_PESSOA),
            PC.NO_PESSOA,
            CASE 
                WHEN DOC.NU_CPF_PESSOA IN ({cpf_list}) THEN 'S'
                ELSE 'N'
            END AS CAD_UNICO
        FROM PessoasCadastradas PC
        INNER JOIN P_CADASTRO_ODS_202503.TB_DOCUMENTO_05 AS DOC
            ON PC.CO_FAMILIAR_FAM = DOC.CO_FAMILIAR_FAM
        WHERE DOC.NU_CPF_PESSOA IN ({cpf_list})
        QUALIFY ROW_NUMBER() OVER (PARTITION BY DOC.NU_CPF_PESSOA ORDER BY PC.NO_PESSOA) = 1
        """

        try:
            print(f"🔄 Executando bloco {i//bloco + 1}/{total_blocos}...")
            df = pd.read_sql(query, conn)
            resultados.append(df)
        except Exception as e:
            print(f"⚠️ Erro no bloco {i//bloco + 1}: {e}")
            sleep(1)

    return pd.concat(resultados, ignore_index=True)

# Executar
resultado = consultar_em_blocos(cpfs, bloco=TAMANHO_BLOCO)

# Salvar no Excel
resultado.to_excel(ARQUIVO_SAIDA, index=False)
print(f"✅ Consulta finalizada! Arquivo salvo como: {ARQUIVO_SAIDA}")

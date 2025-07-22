import pandas as pd

# carregar os dados da planilha
caminho = 'C:/dados/base_inicial.xlsx'

df1 = pd.read_excel(caminho, sheet_name='Relatório de Vendas')
df2 = pd.read_excel(caminho, sheet_name='Relatório de Vendas1')

#exibir as primeiras linhas para conferir como estao os dados
print('----- Primeiro relatorio ------')
print(df1.head())
print('----- Segundo relatorio ------')
print(df2.head())

#verificar se há duplicatas nas duas tabelas
print('Duplicatas no relatorio 1 ')
print(df1.duplicated().sum())
print('Duplicatas no relatorio 2 ')
print(df2.duplicated().sum())

# Agora vamos consolidar as duas tabelas
print('Dados consolidados')
df_consolidado = pd.concat([df1, df2],ignore_index=True)
print(df_consolidado.head())

# Exibir o numero de clientes por cidade
clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
print('Clientes por cidade')
print(clientes_por_cidade)

# numero de vendas por plano
vendas_por_plano = df_consolidado['Plano Vendido'].value_counts()
print('Numero de Vendas por Plano')
print(vendas_por_plano)

# exibir as 3 primeiras cidades com mais clientes
top_3_cidades = clientes_por_cidade.head(3)
print('Top 3 cidades')
print(top_3_cidades)

# exibir o total de clientes
total_clientes = df_consolidado['Cliente'].nunique()
print(f'\n Numero total de clientes: {total_clientes}')

# Adicionar uma coluna de Status ( exemplo ficticio de analise)
# Vamos classificar os planos como premium se for enterprise, caso contrario será padrão
df_consolidado['Status'] = df_consolidado['Plano Vendido'].apply(lambda x: 'Premium' if x == 'Enterprise' else 'Padrão')

# Exibir a distribuição dos status
status_dist = df_consolidado['Status'].value_counts()
print('\n Distribuição dos status:')
print(status_dist)

# Salvar a tabela em um arquivo
#Primeiro em Excel
df_consolidado.to_excel('dados_consolidados_planilha.xlsx', index=False)
#Depois em CSV
df_consolidado.to_csv('dados_consolidados_texto.csv', index=False)

#Exibir Mensagem FInal!
print('\n Arquivos Gerados com sucesso!')
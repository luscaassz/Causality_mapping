from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from scipy import stats
from flask_caching import Cache
import os

app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE': 'simple'})  # ou 'filesystem', 'redis', etc.
cache.init_app(app)

# Variável global para mapeamento de municípios
municipios_map = None
densidade_demografica = None

def init_municipios_map():
    global municipios_map, densidade_demografica
    if municipios_map is None and densidade_demografica is not None:
        municipios_map = dict(zip(
            densidade_demografica['NM_MUN'],
            densidade_demografica['CD_MUN']
        ))

@cache.memoize()
def carregar_dados():
    global densidade_demografica 

    dados = {}
    
    arquivos = {
        # Arquivos principais
        'densidade_demografica': 'data/densidade_demografica.xlsx',
        'emissao_ch4': 'data/emissao_ch4.xls',
        'emissao_co2': 'data/emissao_co2.xls',
        'emissao_n2o': 'data/emissao_n2o.xls',
        'pib_per_capita': 'data/pib_per_capita.xlsx',
        'taxa_urbanizacao': 'data/taxa_urbanizacao.xlsx',

        # Morbidade
        'TX_Morb_Circ_Int': 'data/Taxas/TX_Morb_Circ_Int.xls',
        'TX_Morb_Classe_Circ_FE_Int': 'data/Taxas/TX_Morb_Classe_Circ_FE_Int.xls',
        'TX_Morb_Classe_Circ_Sexo_Int': 'data/Taxas/TX_Morb_Classe_Circ_Sexo_Int.xls',
        'TX_Morb_Resp_Int': 'data/Taxas/TX_Morb_Resp_Int.xls',
        'TX_Morb_Classe_Resp_FE_Int': 'data/Taxas/TX_Morb_Classe_Resp_FE_Int.xls',
        'TX_Morb_Classe_Resp_Sexo_Int': 'data/Taxas/TX_Morb_Classe_Resp_Sexo_Int.xls',
        'TX_Morb_Deng': 'data/Taxas/TX_Morb_Deng_Int.xls',
        'TX_Morb_FebAm': 'data/Taxas/TX_Morb_FebAm_Int.xls',
        'TX_Morb_Leish': 'data/Taxas/TX_Morb_Leish_Int.xls',
        'TX_Morb_Malar': 'data/Taxas/TX_Morb_Malar_Int.xls',

        # Mortalidade
        'TX_Mort_Circ': 'data/Taxas/TX_Mort_Circ.xls',
        'TX_Mort_Classe_Circ_E': 'data/Taxas/TX_Mort_Classe_Circ_E.xls',
        'TX_Mort_Classe_Circ_FE': 'data/Taxas/TX_Mort_Classe_Circ_FE.xls',
        'TX_Mort_Classe_Circ_Raca': 'data/Taxas/TX_Mort_Classe_Circ_Raca.xls',
        'TX_Mort_Classe_Circ_Sexo': 'data/Taxas/TX_Mort_Classe_Circ_Sexo.xls',
        'TX_Mort_Resp': 'data/Taxas/TX_Mort_Resp.xls',
        'TX_Mort_Classe_Resp_E': 'data/Taxas/TX_Mort_Classe_Resp_E.xls',
        'TX_Mort_Classe_Resp_FE': 'data/Taxas/TX_Mort_Classe_Resp_FE.xls',
        'TX_Mort_Classe_Resp_Raca': 'data/Taxas/TX_Mort_Classe_Resp_Raca.xls',
        'TX_Mort_Classe_Resp_Sexo': 'data/Taxas/TX_Mort_Classe_Resp_Sexo.xls',
        'TX_Mort_Deng': 'data/Taxas/TX_Mort_Deng.xls',
        'TX_Mort_FebAm': 'data/Taxas/TX_Mort_FebAm.xls',
        'TX_Mort_Leish': 'data/Taxas/TX_Mort_Leish.xls',
        'TX_Mort_Malar': 'data/Taxas/TX_Mort_Malar.xls',
    }

    for nome_var, caminho_excel in arquivos.items():
        caminho_pickle = os.path.splitext(caminho_excel)[0] + '.pkl'

        try:
            if os.path.exists(caminho_pickle):
                df = pd.read_pickle(caminho_pickle)
            else:
                df = pd.read_excel(caminho_excel)
                df.to_pickle(caminho_pickle)
                print(f"📦 Criado pickle: {caminho_pickle}")
            dados[nome_var] = df
        except Exception as e:
            print(f"❌ Erro ao carregar {caminho_excel}: {e}")

            dados[nome_var] = df
        
        if nome_var == 'densidade_demografica':
            densidade_demografica = df


    init_municipios_map()
    
    return dados


pickle = carregar_dados()

# Variáveis Ambientais e Socioeconômicas______________________________________________________________

densidade_demografica = pickle['densidade_demografica']
emissao_ch4 = pickle['emissao_ch4']
emissao_co2 = pickle['emissao_co2']
emissao_n2o = pickle['emissao_n2o']
pib_per_capita = pickle['pib_per_capita']
taxa_urbanizacao = pickle['taxa_urbanizacao']

# Variáveis de Saúde ______________________________________________________________________________

# Taxas de Morbidade
TX_Morb_Circ_Int = pickle['TX_Morb_Circ_Int']
TX_Morb_Classe_Circ_FE_Int = pickle['TX_Morb_Classe_Circ_FE_Int']
TX_Morb_Classe_Circ_Sexo_Int = pickle['TX_Morb_Classe_Circ_Sexo_Int']

TX_Morb_Resp_Int = pickle['TX_Morb_Resp_Int']
TX_Morb_Classe_Resp_FE_Int = pickle['TX_Morb_Classe_Resp_FE_Int']
TX_Morb_Classe_Resp_Sexo_Int = pickle['TX_Morb_Classe_Resp_Sexo_Int']

TX_Morb_Deng = pickle['TX_Morb_Deng']
TX_Morb_FebAm = pickle['TX_Morb_FebAm']
TX_Morb_Leish = pickle['TX_Morb_Leish']
TX_Morb_Malar = pickle['TX_Morb_Malar']

# Taxas de Mortalidade
TX_Mort_Circ = pickle['TX_Mort_Circ']
TX_Mort_Classe_Circ_E = pickle['TX_Mort_Classe_Circ_E']
TX_Mort_Classe_Circ_FE = pickle['TX_Mort_Classe_Circ_FE']
TX_Mort_Classe_Circ_Raca = pickle['TX_Mort_Classe_Circ_Raca']
TX_Mort_Classe_Circ_Sexo = pickle['TX_Mort_Classe_Circ_Sexo']

TX_Mort_Resp = pickle['TX_Mort_Resp']
TX_Mort_Classe_Resp_E = pickle['TX_Mort_Classe_Resp_E']
TX_Mort_Classe_Resp_FE = pickle['TX_Mort_Classe_Resp_FE']
TX_Mort_Classe_Resp_Raca = pickle['TX_Mort_Classe_Resp_Raca']
TX_Mort_Classe_Resp_Sexo = pickle['TX_Mort_Classe_Resp_Sexo']

TX_Mort_Deng = pickle['TX_Mort_Deng']
TX_Mort_FebAm = pickle['TX_Mort_FebAm']
TX_Mort_Leish = pickle['TX_Mort_Leish']
TX_Mort_Malar = pickle['TX_Mort_Malar']


# Função para calcular estatísticas
import numpy as np

def calcular_estatisticas(dados):
    # Garantir que os dados sejam numéricos
    dados = pd.to_numeric(dados, errors='coerce')

    # Remover valores NaN (se necessário)
    dados = dados.dropna()

    # Verificar se os dados estão vazios após a remoção de NaN
    if dados.empty:
        return {
            'mean': None,
            'median': None,
            'std_dev': None,
            'skewness': None,
            'kurtosis': None,
            'outlier_percentage': None,
            'tipo_distribuicao': None
        }

    # Calcular as estatísticas
    mean = dados.mean()
    median = dados.median()
    std_dev = dados.std()
    skewness = dados.skew()  
    kurtosis = dados.kurt()

    # Calcular a porcentagem de outliers
    Q1 = dados.quantile(0.25)
    Q3 = dados.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = ((dados < lower_bound) | (dados > upper_bound)).sum()
    outlier_percentage = (outliers / len(dados)) * 100

    # Verificação da distribuição
    distribuicoes = {
        'Normal': stats.norm,
        
    }

    '''
    'Exponencial': stats.expon,
    'Weibull': stats.weibull_min,
    'Log-Normal': stats.lognorm,
    'Gama': stats.gamma,
    'Beta': stats.beta,
    'Cauchy': stats.cauchy,
    'Laplace': stats.laplace,
    'Logística': stats.logistic,
    'Pareto': stats.pareto,
    'Rayleigh': stats.rayleigh
    '''

    melhores_distribuicoes = []

    for nome, dist in distribuicoes.items():
        try:
            params = dist.fit(dados)
            ks_stat, p_value = stats.kstest(dados, dist.cdf, args=params)
            melhores_distribuicoes.append((nome, ks_stat, p_value))
        except Exception as e:
            print(f"Erro ao ajustar {nome}: {e}")


    # Escolher a melhor distribuição com base no maior p-value
    tipo_distribuicao = max(melhores_distribuicoes, key=lambda x: x[2])[0]

    

    return {
        'mean': mean,
        'median': median,
        'std_dev': std_dev,
        'skewness': skewness,
        'kurtosis': kurtosis,
        'outlier_percentage': outlier_percentage,
        'tipo_distribuicao': tipo_distribuicao
    }



# Rota para o dashboard
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/estados', methods=['GET'])
def get_estados():
    """Retorna a lista de estados únicos"""
    estados = densidade_demografica['SIGLA_UF'].drop_duplicates().tolist()
    return jsonify(estados)

@app.route('/municipios', methods=['GET'])
def get_municipios():
    """Retorna os municípios de um estado específico"""
    estado = request.args.get('estado')  # Obtém o estado selecionado no front-end
    
    if estado:
        municipios = densidade_demografica[densidade_demografica['SIGLA_UF'] == estado]['NM_MUN'].drop_duplicates().tolist()
    else:
        municipios = densidade_demografica['NM_MUN'].drop_duplicates().tolist()
    
    return jsonify(municipios)


# Rota para obter os dados do gráfico e estatísticas
@app.route('/dados', methods=['GET'])
def dados():
    municipio = request.args.get('municipio')
    variavel = request.args.get('variavel')

    ano_inicio = int(request.args.get('ano_inicio', 1999))  # 1999 é o valor padrão
    ano_fim = int(request.args.get('ano_fim', 2023))       # 2023 como padrão

    # Procurar o CD_MUN do município
    municipio_codigo = None
    for municipio_row in densidade_demografica['NM_MUN'].values:
        if municipio_row == municipio:
            municipio_codigo = densidade_demografica[densidade_demografica['NM_MUN'] == municipio].iloc[0, 0]
            break

    if municipio_codigo is None:
        return jsonify({'error': 'Município não encontrado.'}), 400

    
    '''
    Filtrando os dados com base no município (CD_MUN)
    '''

    # Variáveis Ambientais e Socioeconômicas ___________________________________________________________
    if variavel == 'densidade_demografica':
        dados = densidade_demografica[densidade_demografica['CD_MUN'] == municipio_codigo].drop(columns=['CD_MUN', 'NM_MUN']).iloc[0, 1:]
    elif variavel == 'emissao_ch4':
        dados = emissao_ch4[emissao_ch4['CD_MUN'] == municipio_codigo].iloc[0, 2:]
    elif variavel == 'emissao_co2':
        dados = emissao_co2[emissao_co2['CD_MUN'] == municipio_codigo].iloc[0, 2:]
    elif variavel == 'emissao_n2o':
        dados = emissao_n2o[emissao_n2o['CD_MUN'] == municipio_codigo].iloc[0, 2:]
    elif variavel == 'pib_per_capita':
        dados = pib_per_capita[pib_per_capita['CD_MUN'] == municipio_codigo].iloc[0, 2:].apply(pd.to_numeric, errors='coerce')
        dados = dados.dropna()  # Remover NaNs
        dados.loc[dados.index.isin(['PIB 2022', 'PIB 2023'])] = 0  # Definir PIB 2022 e 2023 como zero
    elif variavel == 'taxa_urbanizacao':
        dados = taxa_urbanizacao[taxa_urbanizacao['CD_MUN'] == municipio_codigo].iloc[0, 1:]

    # Variáveis de Saúde ______________________________________________________________________________
    
    # Morbidade

    elif variavel == 'TX_Morb_Circ_Int':
        dados = TX_Morb_Circ_Int[TX_Morb_Circ_Int['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    
    elif variavel == 'TX_Morb_Classe_Circ_Sexo_Int' or variavel == 'TX_Morb_Classe_Resp_Sexo_Int' or variavel == 'TX_Mort_Classe_Circ_Sexo' or variavel == 'TX_Mort_Classe_Resp_Sexo':
        dados = None

        if variavel == 'TX_Morb_Classe_Circ_Sexo_Int':
            dados_masculino = TX_Morb_Classe_Circ_Sexo_Int[TX_Morb_Classe_Circ_Sexo_Int['CD_MUN'] == municipio_codigo].iloc[0, 31:]
            dados_feminino = TX_Morb_Classe_Circ_Sexo_Int[TX_Morb_Classe_Circ_Sexo_Int['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
        elif variavel == 'TX_Morb_Classe_Resp_Sexo_Int':
            dados_masculino = TX_Morb_Classe_Resp_Sexo_Int[TX_Morb_Classe_Resp_Sexo_Int['CD_MUN'] == municipio_codigo].iloc[0, 31:]
            dados_feminino = TX_Morb_Classe_Resp_Sexo_Int[TX_Morb_Classe_Resp_Sexo_Int['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
        elif variavel == 'TX_Mort_Classe_Circ_Sexo':
            dados_masculino = TX_Mort_Classe_Circ_Sexo[TX_Mort_Classe_Circ_Sexo['CD_MUN'] == municipio_codigo].iloc[0, 31:]
            dados_feminino = TX_Mort_Classe_Circ_Sexo[TX_Mort_Classe_Circ_Sexo['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
        elif variavel == 'TX_Mort_Classe_Resp_Sexo':
            dados_masculino = TX_Mort_Classe_Resp_Sexo[TX_Mort_Classe_Resp_Sexo['CD_MUN'] == municipio_codigo].iloc[0, 31:]
            dados_feminino = TX_Mort_Classe_Resp_Sexo[TX_Mort_Classe_Resp_Sexo['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
        
        if dados_masculino.empty or dados_feminino.empty:
            return jsonify({'error': f'Nenhum dado encontrado para a variável {variavel} no município {municipio}.'}), 400

        # Filtrando os anos com base no intervalo selecionado
        anos = list(range(ano_inicio, ano_fim + 1))
        dados_masculino = dados_masculino[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_feminino = dados_feminino[ano_inicio - 1999:ano_fim - 1999 + 1]

        estatisticas_masculino = calcular_estatisticas(dados_masculino)
        estatisticas_feminino = calcular_estatisticas(dados_feminino)

        return jsonify({
            'anos': anos,
            'dados_masculino': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_masculino.tolist()],
            'dados_feminino': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_feminino.tolist()],

            'estatisticas_masculino': estatisticas_masculino,
            'estatisticas_feminino': estatisticas_feminino
        })
    
    
    elif variavel == 'TX_Morb_Classe_Circ_FE_Int' or variavel == 'TX_Morb_Classe_Resp_FE_Int' or variavel == 'TX_Mort_Classe_Circ_FE' or variavel == 'TX_Mort_Classe_Resp_FE':
        dados = None

        if variavel == 'TX_Morb_Classe_Circ_FE_Int':
            dados_FE1 = TX_Morb_Classe_Circ_FE_Int[TX_Morb_Classe_Circ_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_FE2 = TX_Morb_Classe_Circ_FE_Int[TX_Morb_Classe_Circ_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_FE3 = TX_Morb_Classe_Circ_FE_Int[TX_Morb_Classe_Circ_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 56:82]
            dados_FE4 = TX_Morb_Classe_Circ_FE_Int[TX_Morb_Classe_Circ_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 81:107]
            dados_FE5 = TX_Morb_Classe_Circ_FE_Int[TX_Morb_Classe_Circ_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 106:]
        elif variavel == 'TX_Morb_Classe_Resp_FE_Int':
            dados_FE1 = TX_Morb_Classe_Resp_FE_Int[TX_Morb_Classe_Resp_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_FE2 = TX_Morb_Classe_Resp_FE_Int[TX_Morb_Classe_Resp_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_FE3 = TX_Morb_Classe_Resp_FE_Int[TX_Morb_Classe_Resp_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 56:82]
            dados_FE4 = TX_Morb_Classe_Resp_FE_Int[TX_Morb_Classe_Resp_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 81:107]
            dados_FE5 = TX_Morb_Classe_Resp_FE_Int[TX_Morb_Classe_Resp_FE_Int['CD_MUN'] == municipio_codigo].iloc[0, 106:]
        elif variavel == 'TX_Mort_Classe_Circ_FE':
            dados_FE1 = TX_Mort_Classe_Circ_FE[TX_Mort_Classe_Circ_FE['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_FE2 = TX_Mort_Classe_Circ_FE[TX_Mort_Classe_Circ_FE['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_FE3 = TX_Mort_Classe_Circ_FE[TX_Mort_Classe_Circ_FE['CD_MUN'] == municipio_codigo].iloc[0, 56:82]
            dados_FE4 = TX_Mort_Classe_Circ_FE[TX_Mort_Classe_Circ_FE['CD_MUN'] == municipio_codigo].iloc[0, 81:107]
            dados_FE5 = TX_Mort_Classe_Circ_FE[TX_Mort_Classe_Circ_FE['CD_MUN'] == municipio_codigo].iloc[0, 106:]

            dados_FE5 = dados_FE5.dropna()  # Remover NaNs
            dados_FE5.loc[dados_FE5.index.isin(['TX_FE5_23'])] = 0
        elif variavel == 'TX_Mort_Classe_Resp_FE':
            dados_FE1 = TX_Mort_Classe_Resp_FE[TX_Mort_Classe_Resp_FE['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_FE2 = TX_Mort_Classe_Resp_FE[TX_Mort_Classe_Resp_FE['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_FE3 = TX_Mort_Classe_Resp_FE[TX_Mort_Classe_Resp_FE['CD_MUN'] == municipio_codigo].iloc[0, 56:82]
            dados_FE4 = TX_Mort_Classe_Resp_FE[TX_Mort_Classe_Resp_FE['CD_MUN'] == municipio_codigo].iloc[0, 81:107]
            dados_FE5 = TX_Mort_Classe_Resp_FE[TX_Mort_Classe_Resp_FE['CD_MUN'] == municipio_codigo].iloc[0, 106:]
    
        
        if dados_FE1.empty or dados_FE2.empty or dados_FE3.empty or dados_FE4.empty or dados_FE5.empty:
            return jsonify({'error': f'Nenhum dado encontrado para a variável {variavel} no município {municipio}.'}), 400

        # Filtrando os anos com base no intervalo selecionado
        anos = list(range(ano_inicio, ano_fim + 1))
        dados_FE1 = dados_FE1[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_FE2 = dados_FE2[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_FE3 = dados_FE3[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_FE4 = dados_FE4[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_FE5 = dados_FE5[ano_inicio - 1999:ano_fim - 1999 + 1]

        estatisticas_FE1 = calcular_estatisticas(dados_FE1)
        estatisticas_FE2 = calcular_estatisticas(dados_FE2)
        estatisticas_FE3 = calcular_estatisticas(dados_FE3)
        estatisticas_FE4 = calcular_estatisticas(dados_FE4)
        estatisticas_FE5 = calcular_estatisticas(dados_FE5)

        return jsonify({
            'anos': anos,
            'dados_FE1': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_FE1.tolist()],
            'dados_FE2': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_FE2.tolist()],
            'dados_FE3': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_FE3.tolist()],
            'dados_FE4': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_FE4.tolist()],
            'dados_FE5': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_FE5.tolist()],

            'estatisticas_FE1': estatisticas_FE1,
            'estatisticas_FE2': estatisticas_FE2,
            'estatisticas_FE3': estatisticas_FE3,
            'estatisticas_FE4': estatisticas_FE4,
            'estatisticas_FE5': estatisticas_FE5
        })
        
    elif variavel == 'TX_Morb_Resp_Int':
        dados = TX_Morb_Resp_Int[TX_Morb_Resp_Int['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    
    elif variavel == 'TX_Morb_Deng':
        dados = TX_Morb_Deng[TX_Morb_Deng['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    elif variavel == 'TX_Morb_FebAm':
        dados = TX_Morb_FebAm[TX_Morb_FebAm['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    elif variavel == 'TX_Morb_Leish':
        dados = TX_Morb_Leish[TX_Morb_Leish['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    elif variavel == 'TX_Morb_Malar':
        dados = TX_Morb_Malar[TX_Morb_Malar['CD_MUN'] == municipio_codigo].iloc[0, 6:]

    elif variavel == 'TX_Mort_Circ':
        dados = TX_Mort_Circ[TX_Mort_Circ['CD_MUN'] == municipio_codigo].iloc[0, 6:]

    elif variavel == 'TX_Mort_Classe_Circ_E' or variavel == 'TX_Mort_Classe_Resp_E' or variavel == 'TX_Mort_Classe_Resp_E':
        dados = None

        if variavel == 'TX_Mort_Classe_Circ_E':
            dados_E0 = TX_Mort_Classe_Circ_E[TX_Mort_Classe_Circ_E['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_E1 = TX_Mort_Classe_Circ_E[TX_Mort_Classe_Circ_E['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_E2 = TX_Mort_Classe_Circ_E[TX_Mort_Classe_Circ_E['CD_MUN'] == municipio_codigo].iloc[0, 56:]
        elif variavel == 'TX_Mort_Classe_Resp_E':
            dados_E0 = TX_Mort_Classe_Resp_E[TX_Mort_Classe_Resp_E['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_E1 = TX_Mort_Classe_Resp_E[TX_Mort_Classe_Resp_E['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_E2 = TX_Mort_Classe_Resp_E[TX_Mort_Classe_Resp_E['CD_MUN'] == municipio_codigo].iloc[0, 56:]
            

        if dados_E0.empty or dados_E1.empty or dados_E2.empty:
            return jsonify({'error': f'Nenhum dado encontrado para a variável {variavel} no município {municipio}.'}), 400

        # Filtrando os anos com base no intervalo selecionado
        anos = list(range(ano_inicio, ano_fim + 1))
        dados_E0 = dados_E0[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_E1 = dados_E1[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_E2 = dados_E2[ano_inicio - 1999:ano_fim - 1999 + 1]

        estatisticas_E0 = calcular_estatisticas(dados_E0)
        estatisticas_E1 = calcular_estatisticas(dados_E1)
        estatisticas_E2 = calcular_estatisticas(dados_E2)
        
        return jsonify({
            'anos': anos,
            'dados_E0': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_E0.tolist()],
            'dados_E1': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_E1.tolist()],
            'dados_E2': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_E2.tolist()],
            
            'estatisticas_E0': estatisticas_E0,
            'estatisticas_E1': estatisticas_E1,
            'estatisticas_E2': estatisticas_E2
        })

    elif variavel == 'TX_Mort_Classe_Circ_Raca' or variavel == 'TX_Mort_Classe_Resp_Raca':
        dados = None

        if variavel == 'TX_Mort_Classe_Circ_Raca':
            dados_AM = TX_Mort_Classe_Circ_Raca[TX_Mort_Classe_Circ_Raca['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_B = TX_Mort_Classe_Circ_Raca[TX_Mort_Classe_Circ_Raca['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_IN = TX_Mort_Classe_Circ_Raca[TX_Mort_Classe_Circ_Raca['CD_MUN'] == municipio_codigo].iloc[0, 56:82]
            dados_PR = TX_Mort_Classe_Circ_Raca[TX_Mort_Classe_Circ_Raca['CD_MUN'] == municipio_codigo].iloc[0, 81:107]
            dados_PT = TX_Mort_Classe_Circ_Raca[TX_Mort_Classe_Circ_Raca['CD_MUN'] == municipio_codigo].iloc[0, 106:]
        elif variavel == 'TX_Mort_Classe_Resp_Raca':
            dados_AM = TX_Mort_Classe_Resp_Raca[TX_Mort_Classe_Resp_Raca['CD_MUN'] == municipio_codigo].iloc[0, 6:32]
            dados_B = TX_Mort_Classe_Resp_Raca[TX_Mort_Classe_Resp_Raca['CD_MUN'] == municipio_codigo].iloc[0, 31:57]
            dados_IN = TX_Mort_Classe_Resp_Raca[TX_Mort_Classe_Resp_Raca['CD_MUN'] == municipio_codigo].iloc[0, 56:82]
            dados_PR = TX_Mort_Classe_Circ_Raca[TX_Mort_Classe_Circ_Raca['CD_MUN'] == municipio_codigo].iloc[0, 81:107]
            dados_PT = TX_Mort_Classe_Circ_Raca[TX_Mort_Classe_Circ_Raca['CD_MUN'] == municipio_codigo].iloc[0, 106:]
            

        if dados_AM.empty or dados_B.empty or dados_IN.empty or dados_PR.empty or dados_PT.empty:
            return jsonify({'error': f'Nenhum dado encontrado para a variável {variavel} no município {municipio}.'}), 400

        # Filtrando os anos com base no intervalo selecionado
        anos = list(range(ano_inicio, ano_fim + 1))
        dados_AM = dados_AM[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_B = dados_B[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_IN = dados_IN[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_PR = dados_PR[ano_inicio - 1999:ano_fim - 1999 + 1]
        dados_PT = dados_PT[ano_inicio - 1999:ano_fim - 1999 + 1]
    

        estatisticas_AM = calcular_estatisticas(dados_AM)
        estatisticas_B = calcular_estatisticas(dados_B)
        estatisticas_IN = calcular_estatisticas(dados_IN)
        estatisticas_PR = calcular_estatisticas(dados_PR)
        estatisticas_PT = calcular_estatisticas(dados_PT)
        
        
        return jsonify({
            'anos': anos,
            'dados_AM': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_AM.tolist()],
            'dados_B': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_B.tolist()],
            'dados_IN': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_IN.tolist()],
            'dados_PR': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_PR.tolist()],
            'dados_PT': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados_PT.tolist()],
           
            
            
            'estatisticas_AM': estatisticas_AM,
            'estatisticas_B': estatisticas_B,
            'estatisticas_IN': estatisticas_IN,
            'estatisticas_PR': estatisticas_PR,
            'estatisticas_PT': estatisticas_PT
        })

     
    elif variavel == 'TX_Mort_Resp':
        dados = TX_Mort_Resp[TX_Mort_Resp['CD_MUN'] == municipio_codigo].iloc[0, 6:]

    elif variavel == 'TX_Mort_Deng':
        dados = TX_Mort_Deng[TX_Mort_Deng['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    elif variavel == 'TX_Mort_FebAm':
        dados = TX_Mort_FebAm[TX_Mort_FebAm['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    elif variavel == 'TX_Mort_Leish':
        dados = TX_Mort_Leish[TX_Mort_Leish['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    elif variavel == 'TX_Mort_Malar':
        dados = TX_Mort_Malar[TX_Mort_Malar['CD_MUN'] == municipio_codigo].iloc[0, 6:]
    
    
    if dados.empty:
        return jsonify({'error': f'Nenhum dado encontrado para a variável {variavel} no município {municipio}.'}), 400
    

    # Filtrando os anos com base no intervalo selecionado
    dados = dados[ano_inicio - 1999:ano_fim - 1999 + 1]

    # Calcular as estatísticas
    estatisticas = calcular_estatisticas(dados)

    # Preparar dados para o gráfico
    anos = list(range(ano_inicio, ano_fim + 1))
    return jsonify({
        'anos': anos,
        'dados': [int(valor) if isinstance(valor, (np.integer, int)) else float(valor) for valor in dados.tolist()],
        'estatisticas': estatisticas
    })

@app.route('/previsoes', methods=['GET'])
def get_previsoes():
    municipio_nome = request.args.get('municipio')
    tipo_doenca = request.args.get('tipo_doenca')  # 'circ' ou 'resp'
    
    if municipios_map is None:
        init_municipios_map()
    
    municipio_codigo = municipios_map.get(municipio_nome)
    if municipio_codigo is None:
        return jsonify({'error': 'Município não encontrado.'}), 400

    try:
        # Carrega os três arquivos para cada tipo de doença
        base_path = f"data/Preds/pred_morb_{tipo_doenca}"
        df_mean = pd.read_csv(f"{base_path}.csv")
        df_lower = pd.read_csv(f"{base_path}_lower.csv")
        df_upper = pd.read_csv(f"{base_path}_upper.csv")
        
        # Filtra os dados do município
        dados_mean = df_mean[df_mean['city_code'].astype(str) == str(municipio_codigo)]
        dados_lower = df_lower[df_lower['city_code'].astype(str) == str(municipio_codigo)]
        dados_upper = df_upper[df_upper['city_code'].astype(str) == str(municipio_codigo)]
        
        if dados_mean.empty:
            return jsonify({'error': 'Dados não encontrados para o município.'}), 404
            
        # Processa os dados
        anos = list(range(2022, 2031))
        dados_anuais = {
            'mean': [],
            'lower': [],
            'upper': []
        }
        
        for ano in anos:
            cols_mean = [col for col in df_mean.columns if col.startswith(str(ano))]
            cols_lower = [col for col in df_lower.columns if col.startswith(str(ano))]
            cols_upper = [col for col in df_upper.columns if col.startswith(str(ano))]
            
            if cols_mean:
                dados_anuais['mean'].append(dados_mean.iloc[0][cols_mean].sum())
                dados_anuais['lower'].append(dados_lower.iloc[0][cols_lower].sum())
                dados_anuais['upper'].append(dados_upper.iloc[0][cols_upper].sum())
        
        return jsonify({
            'anos': anos,
            'dados': dados_anuais['mean'],
            'lower': dados_anuais['lower'],
            'upper': dados_anuais['upper'],
            'estatisticas': calcular_estatisticas(pd.Series(dados_anuais['mean']))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

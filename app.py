from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from scipy import stats
from flask_caching import Cache
import os
import pickle

app = Flask(__name__)

# Configuração de cache mais robusta
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 hora de cache
})
cache.init_app(app)

# Variáveis globais para dados pré-carregados
municipios_map = None
densidade_demografica = None
previsoes_cache = {}  # Dicionário para cache de previsões

def init_municipios_map():
    global municipios_map
    if municipios_map is None and densidade_demografica is not None:
        municipios_map = dict(zip(
            densidade_demografica['NM_MUN'],
            densidade_demografica['CD_MUN']
        ))

@cache.memoize(timeout=3600)  # Cache por 1 hora
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
            dados[nome_var] = None
        
        if nome_var == 'densidade_demografica':
            densidade_demografica = dados[nome_var]

    init_municipios_map()
    return dados

# Carrega os dados uma vez no início
dados_globais = carregar_dados()

# Atribui as variáveis globais
for nome_var, df in dados_globais.items():
    globals()[nome_var] = df

# Função para pré-processar e cachear as previsões
def carregar_previsoes():
    global previsoes_cache
    
    tipos_doenca = ['circ', 'resp', 'deng', 'febam', 'leish', 'malar']
    tipos_dados = ['', '_lower', '_upper']
    tipos_mort = ['morb', 'mort']
    
    for tipo in tipos_doenca:
        for sufixo in tipos_dados:
            for tipo_m in tipos_mort:
                caminho_csv = f"data/preds/pred_{tipo_m}_{tipo}{sufixo}.csv"
                caminho_pickle = f"data/preds/pred_{tipo_m}_{tipo}{sufixo}.pkl"
                
                try:
                    if os.path.exists(caminho_pickle):
                        df = pd.read_pickle(caminho_pickle)
                    else:
                        # Força padrão de leitura
                        df = pd.read_csv(
                            caminho_csv,
                            sep=",",       # separador vírgula
                            decimal=".",   # decimal ponto
                            skip_blank_lines=True
                        )

                        # Padroniza nomes de colunas
                        df.columns = df.columns.str.strip().str.lower()

                        # Se city_code estiver no índice, traz para coluna
                        if df.index.name == "city_code":
                            df = df.reset_index()

                        # Verifica se city_code existe
                        if "city_code" not in df.columns:
                            raise ValueError(
                                f"Arquivo {caminho_csv} não possui a coluna 'city_code'. "
                                f"Colunas encontradas: {list(df.columns)}"
                            )

                        # Salva como pickle para acelerar próximas leituras
                        df.to_pickle(caminho_pickle)
                        print(f"📦 Criado pickle para previsões: {caminho_pickle}")
                    
                    # Armazena no cache
                    chave = f"pred_{tipo_m}_{tipo}{sufixo}"
                    previsoes_cache[chave] = df

                except Exception as e:
                    print(f"❌ Erro ao carregar previsões {caminho_csv}: {e}")

# Carrega as previsões no início
carregar_previsoes()
print("Chaves carregadas no cache de previsões:", previsoes_cache.keys())



# Função otimizada para calcular estatísticas
def calcular_estatisticas(dados):
    if dados.empty or dados.isnull().all():
        return {
            'mean': None,
            'median': None,
            'std_dev': None,
            'skewness': None,
            'kurtosis': None,
            'outlier_percentage': None,
            'tipo_distribuicao': None
        }

    dados = pd.to_numeric(dados, errors='coerce').dropna()
    
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

    stats_dict = {
        'mean': dados.mean(),
        'median': dados.median(),
        'std_dev': dados.std(),
        'skewness': dados.skew(),
        'kurtosis': dados.kurt()
    }

    # Cálculo de outliers
    Q1, Q3 = dados.quantile([0.25, 0.75])
    IQR = Q3 - Q1
    outliers = ((dados < (Q1 - 1.5 * IQR))) | (dados > (Q3 + 1.5 * IQR))
    stats_dict['outlier_percentage'] = outliers.mean() * 100

    # Verificação simplificada da distribuição
    try:
        _, p_normal = stats.normaltest(dados)
        stats_dict['tipo_distribuicao'] = 'Normal' if p_normal > 0.05 else 'Não-Normal'
    except:
        stats_dict['tipo_distribuicao'] = 'Indeterminado'

    return stats_dict

# Rotas principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/estados', methods=['GET'])
def get_estados():
    estados = densidade_demografica['SIGLA_UF'].drop_duplicates().tolist()
    return jsonify(estados)

@app.route('/municipios', methods=['GET'])
def get_municipios():
    estado = request.args.get('estado')
    if estado:
        municipios = densidade_demografica[densidade_demografica['SIGLA_UF'] == estado]['NM_MUN'].drop_duplicates().tolist()
    else:
        municipios = densidade_demografica['NM_MUN'].drop_duplicates().tolist()
    return jsonify(municipios)

# Rota otimizada para dados
@app.route('/dados', methods=['GET'])
def dados():
    # Parâmetros da requisição
    municipio = request.args.get('municipio')
    variavel = request.args.get('variavel')
    ano_inicio = int(request.args.get('ano_inicio', 1999))
    ano_fim = int(request.args.get('ano_fim', 2023))

    # Verifica se o município existe
    if municipio not in municipios_map:
        return jsonify({'error': 'Município não encontrado.'}), 400

    municipio_codigo = municipios_map[municipio]
    
    # Obtém o DataFrame correto
    df = dados_globais.get(variavel)
    if df is None:
        return jsonify({'error': f'Variável {variavel} não encontrada.'}), 400

    # Filtra os dados do município
    dados_municipio = df[df['CD_MUN'] == municipio_codigo]
    if dados_municipio.empty:
        return jsonify({'error': f'Nenhum dado encontrado para o município {municipio}.'}), 400

    # Lógica para diferentes tipos de variáveis
    if variavel in ['TX_Morb_Classe_Circ_Sexo_Int', 'TX_Morb_Classe_Resp_Sexo_Int', 
                   'TX_Mort_Classe_Circ_Sexo', 'TX_Mort_Classe_Resp_Sexo']:
        # Lógica para dados separados por sexo
        dados_masculino = dados_municipio.iloc[0, 31:31 + (ano_fim - ano_inicio + 1)]
        dados_feminino = dados_municipio.iloc[0, 6:6 + (ano_fim - ano_inicio + 1)]
        
        return jsonify({
            'anos': list(range(ano_inicio, ano_fim + 1)),
            'dados_masculino': dados_masculino.astype(float).fillna(0).tolist(),
            'dados_feminino': dados_feminino.astype(float).fillna(0).tolist(),
            'estatisticas_masculino': calcular_estatisticas(dados_masculino),
            'estatisticas_feminino': calcular_estatisticas(dados_feminino)
        })
    
    elif variavel in ['TX_Morb_Classe_Circ_FE_Int', 'TX_Morb_Classe_Resp_FE_Int', 
                     'TX_Mort_Classe_Circ_FE', 'TX_Mort_Classe_Resp_FE']:
        # Lógica para dados FE
        fe_data = {
            'FE1': dados_municipio.iloc[0, 6:6 + (ano_fim - ano_inicio + 1)],
            'FE2': dados_municipio.iloc[0, 31:31 + (ano_fim - ano_inicio + 1)],
            'FE3': dados_municipio.iloc[0, 56:56 + (ano_fim - ano_inicio + 1)],
            'FE4': dados_municipio.iloc[0, 81:81 + (ano_fim - ano_inicio + 1)],
            'FE5': dados_municipio.iloc[0, 106:106 + (ano_fim - ano_inicio + 1)]
        }
        
        response_data = {
            'anos': list(range(ano_inicio, ano_fim + 1))
        }
        
        for fe, dados in fe_data.items():
            response_data[f'dados_{fe}'] = dados.astype(float).fillna(0).tolist()
            response_data[f'estatisticas_{fe}'] = calcular_estatisticas(dados)
            
        return jsonify(response_data)
    
    else:
        # Lógica padrão para outras variáveis
        dados = dados_municipio.iloc[0, 6:6 + (ano_fim - ano_inicio + 1)]
        
        return jsonify({
            'anos': list(range(ano_inicio, ano_fim + 1)),
            'dados': dados.astype(float).fillna(0).tolist(),
            'estatisticas': calcular_estatisticas(dados)
        })

# Rota otimizada para previsões
@app.route('/previsoes', methods=['GET'])
def get_previsoes():
    municipio_nome = request.args.get('municipio')
    tipo_doenca = request.args.get('tipo_doenca')  # 'circ', 'resp', 'deng', 'febam', 'leish', 'malar'
    tipo_mort = request.args.get('tipo_mort')  # 'morb' ou 'mort'
    
    if municipio_nome not in municipios_map:
        return jsonify({'error': 'Município não encontrado.'}), 400
    
    municipio_codigo = municipios_map[municipio_nome]
    
    # Obtém os dados do cache
    df_mean = previsoes_cache.get(f'pred_{tipo_mort}_{tipo_doenca}')
    df_lower = previsoes_cache.get(f'pred_{tipo_mort}_{tipo_doenca}_lower')
    df_upper = previsoes_cache.get(f'pred_{tipo_mort}_{tipo_doenca}_upper')
    
    if df_mean is None or df_lower is None or df_upper is None:
        return jsonify({'error': 'Dados de previsão não carregados.'}), 500
    
    # Filtra os dados do município
    try:
        dados_mean = df_mean[df_mean['city_code'].astype(str) == str(municipio_codigo)]
        dados_lower = df_lower[df_lower['city_code'].astype(str) == str(municipio_codigo)]
        dados_upper = df_upper[df_upper['city_code'].astype(str) == str(municipio_codigo)]
        
        if dados_mean.empty:
            return jsonify({'error': 'Dados não encontrados para o município.'}), 404
        
        # Processa os dados
        anos = list(range(2025, 2031))
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
                dados_anuais['mean'].append(dados_mean[cols_mean].sum(axis=1).values[0])
                dados_anuais['lower'].append(dados_lower[cols_lower].sum(axis=1).values[0])
                dados_anuais['upper'].append(dados_upper[cols_upper].sum(axis=1).values[0])
        
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
    app.run(debug=False)  # Desative o debug em produção
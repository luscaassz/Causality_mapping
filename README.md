# Dashboard de Indicadores Socioambientais e de Saúde

Aplicação web interativa para visualização de dados históricos (1999–2023) e previsões (2025–2030) de indicadores socioambientais e de saúde por município brasileiro. Desenvolvida com Flask (backend) e Chart.js (frontend).

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## Funcionalidades

- **Seleção geográfica** – escolha estado e município.
- **Indicadores históricos**:
  - Densidade demográfica, emissões de gases (CH₄, CO₂, N₂O), PIB per capita, taxa de urbanização.
  - Taxas de morbidade e mortalidade (doenças circulatórias, respiratórias, dengue, leishmaniose, malária, febre amarela) – com desagregação por sexo e faixa etária (FE).
- **Previsões (2025–2030)**:
  - Morbidade e mortalidade para doenças circulatórias e respiratórias, dengue, leishmaniose, malária, febre amarela.
  - Exibe previsão central + limites inferior/superior (intervalo de confiança).
- **Estatísticas descritivas**:
  - Média, mediana, desvio padrão, assimetria, curtose, percentual de outliers e classificação da distribuição (Normal/Não‑Normal).
- **Cache inteligente** – arquivos `.pkl` para leitura rápida e cache de requisições.

## Tecnologias utilizadas

| Camada        | Ferramentas                                                                 |
|---------------|-----------------------------------------------------------------------------|
| Backend       | Flask, pandas, numpy, scipy, flask-caching, pickle                          |
| Frontend      | HTML5, JavaScript (jQuery), Chart.js, Bootstrap (opcional no template)      |
| Dados         | Arquivos Excel (`.xls`, `.xlsx`) e CSV de previsões – convertidos para `.pkl` |

## Estrutura do projeto 

```bash
projeto/
├── app.py # Aplicação Flask principal
├── templates/
│ └── index.html # Página principal 
├── static/
│ ├── js/
│ └── script.js # Lógica frontend (gráficos, requisições AJAX)
├── data/
│ ├── densidade_demografica.xlsx
│ ├── emissao_ch4.xls
│ ├── ... # demais arquivos .xls/.xlsx
│ └── preds/ # Previsões em CSV (pred_morb_circ.csv, etc.)
└── requirements.txt # Dependências Python
```


## Instalação e execução

1. **Clone o repositório**
   ```bash
   git clone https://github.com/luscaassz/Causality_mapping.git
   cd Causality_mapping
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

Se não houver requirements.txt, instale manualmente:
flask pandas numpy scipy flask-caching openpyxl

3. **Prepare os dados**

- Coloque todos os arquivos .xls/.xlsx na pasta data/ conforme as chaves do dicionário arquivos no app.py.
- Coloque os CSVs de previsão em data/preds/ (nomes como pred_morb_circ.csv, pred_morb_circ_lower.csv, pred_morb_circ_upper.csv, etc.).
- Na primeira execução, os arquivos .pkl serão gerados automaticamente para acelerar leituras futuras.

4. **Execute a aplicação**
   ```bash
   python app.py
   ```

## Observações importantes
 -- Previsões – são carregadas de arquivos CSV pré‑calculados (não geradas em tempo real). Espera‑se que os CSVs contenham colunas city_code e colunas anuais (ex: 2025, 2026, …).

 -- Cache – a aplicação cria arquivos .pkl ao lado de cada .xls/.csv para leitura mais rápida. Para forçar recarga, delete os .pkl.

 -- Modo de visualização – o frontend alterna entre histórico (1999‑2023, todas as variáveis) e previsões (2025‑2030, apenas morbidade/mortalidade). O botão #toggle-view controla essa troca.

-- Tratamento de outliers – usa o método do IQR (intervalo interquartil) para calcular percentual de outliers.

## Autor
Lucas Vieira dos Santos Souza – [GitHub](https://github.com/luscaassz) – [LinkedIn](https://www.linkedin.com/in/lucas-vieira-dos-santos-souza-45a613305)

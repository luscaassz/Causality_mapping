$(document).ready(function() {

    // Função para ajustar dinamicamente a largura do elemento <select>
    function adjustSelectWidth(selectElement) {
        let longestOption = 0; // Variável para armazenar o comprimento da maior opção

        // Percorre todas as opções dentro do <select>
        $(selectElement).find('option').each(function() {
            let optionWidth = $(this).text().length; // Obtém o comprimento do texto da opção
            if (optionWidth > longestOption) { // Se for a maior opção encontrada até agora
                longestOption = optionWidth; // Atualiza o valor de longestOption
            }
        });

        // Ajusta a largura do <select> com base na maior opção
        // A unidade 'ch' representa o tamanho médio de um caractere, garantindo um ajuste adequado
        $(selectElement).css('width', longestOption+5 + 'ch'); 
    }

    // Chama a função para ajustar a largura do <select> dos municípios
    adjustSelectWidth('#municipio');
    
    let ctx = document.getElementById('grafico').getContext('2d');

    let devicePixelRatio = window.devicePixelRatio || 1;
    let canvasWidth = ctx.canvas.clientWidth;
    let canvasHeight = ctx.canvas.clientHeight;
    ctx.canvas.width = canvasWidth * devicePixelRatio;
    ctx.canvas.height = canvasHeight * devicePixelRatio;
    ctx.scale(devicePixelRatio, devicePixelRatio);

    let chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], 
            datasets: [{
                label: '',
                data: [],
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false,
                spanGaps: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top', // ou 'bottom', 'left', 'right'
                    labels: {
                        color: 'white',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: 'white',
                        font: { size: 14, weight: 'bold' }
                    },
                    title: {
                        display: true,
                        text: 'Ano',
                        color: 'white',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                y: {
                    ticks: {
                        color: 'white',
                        font: { size: 14, weight: 'bold' }
                    },
                    title: {
                        display: true,
                        text: 'Valor',
                        color: 'white',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        }
    });

    function getUnidade(variavel) {
        const unidades = {
            'densidade_demografica': 'pessoas/km²',
            'emissao_ch4': 'kg de CH4/m²',
            'emissao_co2': 'kg de CO2/m²',
            'emissao_n2o': 'kg de N2O/m²',
            'pib_per_capita': 'R$',
            'taxa_urbanizacao': '%',

            'TX_Morb_Circ_Int': 'casos/100.000 habitantes',
            'TX_Morb_Classe_Circ_FE_Int': 'casos/100.000 habitantes',
            'TX_Morb_Classe_Circ_Sexo_Int': 'casos/100.000 habitantes',
            'TX_Morb_Resp_Int': 'casos/100.000 habitantes',
            'TX_Morb_Classe_Resp_FE_Int': 'casos/100.000 habitantes',
            'TX_Morb_Classe_Resp_Sexo_Int': 'casos/100.000 habitantes',
            'TX_Morb_Deng': 'casos/100.000 habitantes',
            'TX_Morb_FebAm': 'casos/100.000 habitantes',
            'TX_Morb_Leish': 'casos/100.000 habitantes',
            'TX_Morb_Malar': 'casos/100.000 habitantes',

            'TX_Mort_Circ': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Circ_E': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Circ_FE': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Circ_Raca': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Circ_Sexo': 'casos/100.000 habitantes',
            'TX_Mort_Resp': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Resp_E': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Resp_FE': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Resp_Raca': 'casos/100.000 habitantes',
            'TX_Mort_Classe_Resp_Sexo': 'casos/100.000 habitantes',
            'TX_Mort_Deng': 'casos/100.000 habitantes',
            'TX_Mort_FebAm': 'casos/100.000 habitantes',
            'TX_Mort_Leish': 'casos/100.000 habitantes',
            'TX_Mort_Malar': 'casos/100.000 habitantes'

        };
        return unidades[variavel] || '';
    }

    function updateGraph() {
        let estado = $('#estado').val();
        let municipio = $('#municipio').val();
        let variavel = $('#variavel').val();
        let ano_inicio = parseInt($('#ano_inicio').val());
        let ano_fim = parseInt($('#ano_fim').val());
        let unidade = getUnidade(variavel);

        const nomesLegendas = {
            densidade_demografica: 'Densidade Demográfica (hab/km²)',
            emissao_ch4: 'Emissão de CH₄ (toneladas)',
            emissao_co2: 'Emissão de CO₂ (toneladas)',
            emissao_n2o: 'Emissão de N₂O (toneladas)',
            pib_per_capita: 'PIB per capita (R$)',
            taxa_urbanizacao: 'Taxa de Urbanização (%)'
        };


         // Verifica se todos os parâmetros estão preenchidos corretamente
        if (!estado || !municipio || !variavel || isNaN(ano_inicio) || isNaN(ano_fim)) {
            console.log('Parâmetros inválidos:', { estado, municipio, variavel, ano_inicio, ano_fim });
            return;
        }

        $.get('/dados', { estado, municipio, variavel, ano_inicio, ano_fim }, function(response) {
            chart.data.labels = response.anos;
            chart.data.datasets = [];

            if (variavel === 'TX_Morb_Classe_Circ_Sexo_Int' || variavel === 'TX_Morb_Classe_Resp_Sexo_Int' || variavel === 'TX_Mort_Classe_Circ_Sexo' || variavel === 'TX_Mort_Classe_Resp_Sexo') {
                chart.data.datasets.push({
                    label: 'Masculino',
                    data: response.dados_masculino,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Feminino',
                    data: response.dados_feminino,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    fill: false,
                    spanGaps: true
                });
            

                atualizarEstatisticas({ 
                    masculino: response.estatisticas_masculino, 
                    feminino: response.estatisticas_feminino 
                });
                

            } 
            else if (variavel === 'TX_Morb_Classe_Circ_FE_Int' || variavel === 'TX_Morb_Classe_Resp_FE_Int' || variavel === 'TX_Mort_Classe_Circ_FE' || variavel === 'TX_Mort_Classe_Resp_FE') {
                chart.data.datasets.push({
                    label: 'Menos de 1 ano',
                    data: response.dados_FE1,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Entre 1 e 14 anos',
                    data: response.dados_FE2,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Entre 15 e 39 anos',
                    data: response.dados_FE3,
                    borderColor: 'rgb(37, 238, 10)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Entre 40 e 59 anos',
                    data: response.dados_FE4,
                    borderColor: 'rgb(47, 15, 230)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: '60 anos ou mais',
                    data: response.dados_FE5,
                    borderColor: 'rgb(237, 253, 4)',
                    fill: false,
                    spanGaps: true
                });
            

                atualizarEstatisticas({ 
                    fe1: response.estatisticas_FE1, 
                    fe2: response.estatisticas_FE2,
                    fe3: response.estatisticas_FE3, 
                    fe4: response.estatisticas_FE4,
                    fe5: response.estatisticas_FE5
                });
                

            }
            else if (variavel === 'TX_Mort_Classe_Circ_E' || variavel === 'TX_Mort_Classe_Resp_E') {
                chart.data.datasets.push({
                    label: 'E0',
                    data: response.dados_E0,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'E1',
                    data: response.dados_E1,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'E2',
                    data: response.dados_E2,
                    borderColor: 'rgb(37, 238, 10)',
                    fill: false,
                    spanGaps: true
                });
            

                atualizarEstatisticas({ 
                    e0: response.estatisticas_E0, 
                    e1: response.estatisticas_E1,
                    e2: response.estatisticas_E2 
                });
                

            } 
            else if (variavel === 'TX_Mort_Classe_Circ_Raca' || variavel === 'TX_Mort_Classe_Resp_Raca') {
                chart.data.datasets.push({
                    label: 'Amarelo',
                    data: response.dados_AM,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Branco',
                    data: response.dados_B,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Indígena',
                    data: response.dados_IN,
                    borderColor: 'rgb(37, 238, 10)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Pardo',
                    data: response.dados_PR,
                    borderColor: 'rgb(47, 15, 230)',
                    fill: false,
                    spanGaps: true
                });
                chart.data.datasets.push({
                    label: 'Preto',
                    data: response.dados_PT,
                    borderColor: 'rgb(237, 253, 4)',
                    fill: false,
                    spanGaps: true
                });
            

                atualizarEstatisticas({ 
                    am: response.estatisticas_AM, 
                    b: response.estatisticas_B,
                    in: response.estatisticas_IN, 
                    pr: response.estatisticas_PR,
                    pt: response.estatisticas_PT
                });
                

            } 
            else {
                chart.data.datasets.push({
                    label: variavel,
                    data: response.dados,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    fill: false,
                    spanGaps: true
                });

                // Atualizar o label com o nome personalizado
                chart.data.datasets[0].label = nomesLegendas[variavel] || variavel;

                atualizarEstatisticas({ 
                    stats: response.estatisticas, 
                });
            }

            chart.options.scales.y.title.text = 'Valor (' + unidade + ')';
            chart.update();

            if (response.estatisticas) {
                $('#media').text('Média: ' + (response.estatisticas.mean?.toFixed(2) || 'N/A'));
                $('#mediana').text('Mediana: ' + (response.estatisticas.median?.toFixed(2) || 'N/A'));
                $('#desvio').text('Desvio Padrão: ' + (response.estatisticas.std_dev?.toFixed(2) || 'N/A'));
                $('#assimetria').text('Assimetria: ' + (response.estatisticas.skewness?.toFixed(2) || 'Dados inválidos'));
                $('#curtose').text('Curtose: ' + (response.estatisticas.kurtosis?.toFixed(2) || 'Dados inválidos'));
                $('#outliers').text('Outliers: ' + (response.estatisticas.outlier_percentage?.toFixed(2) || 'Dados inválidos') + '%');
                $('#tipo_distribuicao').text('Tipo de Distribuição: ' + (response.estatisticas.tipo_distribuicao || 'Não disponível'));
            }                      
        }).fail(function() {
            $('#media, #mediana, #desvio, #assimetria, #curtose, #outliers, #tipo_distribuicao').text('Erro ao obter dados.');
        });
    }

    function atualizarEstatisticas(dados) {
        // Resetar as estatísticas
        $("#stats-container").show();

        $("#stats-container-masc, #stats-container-fem").hide();
        $("#stats-container-masc div.stat-box, #stats-container-fem div.stat-box").text("-");

        $("#stats-container-FE1").hide();
        $("#stats-container-FE2").hide();
        $("#stats-container-FE3").hide();
        $("#stats-container-FE4").hide();
        $("#stats-container-FE5").hide();

        $("#stats-container-E0").hide();
        $("#stats-container-E1").hide();
        $("#stats-container-E2").hide();

        $("#stats-container-AM").hide();
        $("#stats-container-B").hide();
        $("#stats-container-IN").hide();
        $("#stats-container-PR").hide();
        $("#stats-container-PT").hide();
    
        if (!dados)  {
            console.log("Dados estatísticos não encontrados:", dados);
            return;
        }
    
        if (dados.masculino && dados.feminino) {
            $("#stats-container").hide();

            $("#stats-container-FE1").hide();
            $("#stats-container-FE2").hide();
            $("#stats-container-FE3").hide();
            $("#stats-container-FE4").hide();
            $("#stats-container-FE5").hide();

            $("#stats-container-AM").hide();
            $("#stats-container-B").hide();
            $("#stats-container-IN").hide();
            $("#stats-container-PR").hide();
            $("#stats-container-PT").hide();

            $("#stats-container-E0").hide();
            $("#stats-container-E1").hide();
            $("#stats-container-E2").hide();

            $("#stats-container-masc").show();
            $("#stats-container-fem").show();
    
            atualizarCaixasEstatisticas(dados.masculino, "masc");
            atualizarCaixasEstatisticas(dados.feminino, "fem");

        } else if (dados.fe1 && dados.fe2 && dados.fe3 && dados.fe4 && dados.fe5){
            $("#stats-container").hide();

            $("#stats-container-FE1").show();
            $("#stats-container-FE2").show();
            $("#stats-container-FE3").show();
            $("#stats-container-FE4").show();
            $("#stats-container-FE5").show();

            $("#stats-container-AM").hide();
            $("#stats-container-B").hide();
            $("#stats-container-IN").hide();
            $("#stats-container-PR").hide();
            $("#stats-container-PT").hide();

            $("#stats-container-E0").hide();
            $("#stats-container-E1").hide();
            $("#stats-container-E2").hide();

            $("#stats-container-masc").hide();
            $("#stats-container-fem").hide();
    
            atualizarCaixasEstatisticas(dados.fe1, "FE1");
            atualizarCaixasEstatisticas(dados.fe2, "FE2");
            atualizarCaixasEstatisticas(dados.fe3, "FE3");
            atualizarCaixasEstatisticas(dados.fe4, "FE4");
            atualizarCaixasEstatisticas(dados.fe5, "FE5");
        
        } else if (dados.e0 && dados.e1 && dados.e2){
            $("#stats-container").hide();

            $("#stats-container-FE1").hide();
            $("#stats-container-FE2").hide();
            $("#stats-container-FE3").hide();
            $("#stats-container-FE4").hide();
            $("#stats-container-FE5").hide();

            $("#stats-container-AM").hide();
            $("#stats-container-B").hide();
            $("#stats-container-IN").hide();
            $("#stats-container-PR").hide();
            $("#stats-container-PT").hide();

            $("#stats-container-masc").hide();
            $("#stats-container-fem").hide();

            $("#stats-container-E0").show();
            $("#stats-container-E1").show();
            $("#stats-container-E2").show();
    
            atualizarCaixasEstatisticas(dados.e0, "E0");
            atualizarCaixasEstatisticas(dados.e1, "E1");
            atualizarCaixasEstatisticas(dados.e2, "E2");
        
        }
        else if (dados.am && dados.b && dados.in && dados.pr && dados.pt){
            $("#stats-container").hide();

            $("#stats-container-FE1").hide();
            $("#stats-container-FE2").hide();
            $("#stats-container-FE3").hide();
            $("#stats-container-FE4").hide();
            $("#stats-container-FE5").hide();

            $("#stats-container-masc").hide();
            $("#stats-container-fem").hide();

            $("#stats-container-E0").hide();
            $("#stats-container-E1").hide();
            $("#stats-container-E2").hide();

            $("#stats-container-AM").show();
            $("#stats-container-B").show();
            $("#stats-container-IN").show();
            $("#stats-container-PR").show();
            $("#stats-container-PT").show();
    
            atualizarCaixasEstatisticas(dados.am, "AM");
            atualizarCaixasEstatisticas(dados.b, "B");
            atualizarCaixasEstatisticas(dados.in, "IN");
            atualizarCaixasEstatisticas(dados.pr, "PR");
            atualizarCaixasEstatisticas(dados.pt, "PT");
        
        }    
        else {
            atualizarCaixasEstatisticas(dados, "");
        }
    }
    
    function atualizarCaixasEstatisticas(dados, genero) {
        if (!dados) {
            console.log(`Nenhum dado estatístico encontrado para ${genero || "geral"}`);
            return;
        }
    
        $("#media" + (genero ? "-" + genero : "")).text(`Média: ${dados.mean?.toFixed(2) || 'N/A'}`);
        $("#mediana" + (genero ? "-" + genero : "")).text(`Mediana: ${dados.median?.toFixed(2) || 'N/A'}`);
        $("#desvio" + (genero ? "-" + genero : "")).text(`Desvio Padrão: ${dados.std_dev?.toFixed(2) || 'N/A'}`);
        $("#assimetria" + (genero ? "-" + genero : "")).text(`Assimetria: ${dados.skewness?.toFixed(2) || 'N/A'}`);
        $("#curtose" + (genero ? "-" + genero : "")).text(`Curtose: ${dados.kurtosis?.toFixed(2) || 'N/A'}`);
        $("#outliers" + (genero ? "-" + genero : "")).text(`Outliers (%): ${dados.outlier_percentage?.toFixed(2) || 'N/A'}`);
        $("#tipo_distribuicao" + (genero ? "-" + genero : "")).text(`Tipo de Distribuição: ${dados.tipo_distribuicao || 'Não disponível'}`);
    }
    
    

    const variaveis = {
        ambiental: [
            { value: "densidade_demografica", text: "Densidade Demográfica" },
            { value: "emissao_ch4", text: "Emissão de CH4" },
            { value: "emissao_co2", text: "Emissão de CO2" },
            { value: "emissao_n2o", text: "Emissão de N2O" },
            { value: "pib_per_capita", text: "PIB per Capita" },
            { value: "taxa_urbanizacao", text: "Taxa de Urbanização" }
        ],
        morbidade: [
            { value: "TX_Morb_Circ_Int", text: "Taxa de Morbidade de Doenças Circulatórias Geral" },
            { value: "TX_Morb_Classe_Circ_Sexo_Int", text: "Taxa de Morbidade de Doenças Circulatórias por Sexo" },
            { value: "TX_Morb_Classe_Circ_FE_Int", text: "Taxa de Morbidade de Doenças Circulatórias por Faixa Etária" },
            { value: "TX_Morb_Resp_Int", text: "Taxa de Morbidade de Doenças Respiratórias" },
            { value: "TX_Morb_Classe_Resp_FE_Int", text: "Taxa de Morbidade de Doenças Respiratórias por Faixa Etária" },
            { value: "TX_Morb_Classe_Resp_Sexo_Int", text: "Taxa de Morbidade de Doenças Respiratórias por Sexo" },
            { value: "TX_Morb_Deng", text: "Taxa de Morbidade de Dengue" },
            { value: "TX_Morb_FebAm", text: "Taxa de Morbidade de Febre Amarela" },
            { value: "TX_Morb_Leish", text: "Taxa de Morbidade de Leishmaniose" },
            { value: "TX_Morb_Malar", text: "Taxa de Morbidade de Malária" }
        ],
        mortalidade: [
            { value: "TX_Mort_Circ", text: "Taxa de Mortalidade de Doenças Circulatórias" },
            { value: "TX_Mort_Classe_Circ_E", text: "Taxa de Mortalidade de Doenças Circulatórias por Estudo" },
            { value: "TX_Mort_Classe_Circ_FE", text: "Taxa de Mortalidade de Doenças Circulatórias por Faixa Etária" },
            { value: "TX_Mort_Classe_Circ_Raca", text: "Taxa de Mortalidade de Doenças Circulatórias por Raça" },
            { value: "TX_Mort_Classe_Circ_Sexo", text: "Taxa de Mortalidade de Doenças Circulatórias por Sexo" },
            { value: "TX_Mort_Resp", text: "Taxa de Mortalidade de Doenças Respiratórias" },
            { value: "TX_Mort_Classe_Resp_E", text: "Taxa de Mortalidade de Doenças Respiratórias por Estudo" },
            { value: "TX_Mort_Classe_Resp_FE", text: "Taxa de Mortalidade de Doenças Respiratórias por Faixa Etária" },
            { value: "TX_Mort_Classe_Resp_Raca", text: "Taxa de Mortalidade de Doenças Respiratórias por Raça" },
            { value: "TX_Mort_Classe_Resp_Sexo", text: "Taxa de Mortalidade de Doenças Respiratórias por Sexo" },
            { value: "TX_Mort_Deng", text: "Taxa de Mortalidade de Dengue" },
            { value: "TX_Mort_FebAm", text: "Taxa de Mortalidade de Febre Amarela" },
            { value: "TX_Mort_Leish", text: "Taxa de Mortalidade de Leishmaniose" },
            { value: "TX_Mort_Malar", text: "Taxa de Mortalidade de Malária" }
        ]
    };

    function updateVariaveis() {
        const tipoSelecionado = $('#tipo_variavel').val();
        const selectVariavel = $('#variavel');
        
        selectVariavel.empty();
        
        if (variaveis[tipoSelecionado]) {
            variaveis[tipoSelecionado].forEach(v => {
                selectVariavel.append(new Option(v.text, v.value));
            });
        }
    
        updateGraph(); // Atualiza gráfico automaticamente com a nova variável padrão
    }
    

    $.get('/estados', function(estados) {
        let selectEstado = $('#estado');
        selectEstado.empty();
        estados.forEach(estado => {
            selectEstado.append(new Option(estado, estado));
        });
        if (estados.length > 0) {
            selectEstado.val(estados[0]);
            loadMunicipios();
        }
    });

    function loadMunicipios() {
        let estado = $('#estado').val();
        $.get('/municipios', { estado }, function(municipios) {
            let selectMunicipio = $('#municipio');
            selectMunicipio.empty();
            municipios.forEach(mun => {
                selectMunicipio.append(new Option(mun, mun));
            });
            if (municipios.length > 0) {
                selectMunicipio.val(municipios[0]);
                updateGraph();
            }
        });
    }

    
    $('#estado').change(function() {
        loadMunicipios();
    });

    $('#municipio, #variavel, #ano_inicio, #ano_fim').change(function() {
        updateGraph();
    });

    $('#tipo_variavel').change(function() {
        updateVariaveis();
    });

    updateVariaveis();
    updateGraph();
 
});

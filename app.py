# ==============================================================================
# DASHBOARD STREAMLIT - PREVISÃO DE QUEIMADAS NO BRASIL (VERSÃO MELHORADA)
# ==============================================================================

# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import pydeck as pdk

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="Dashboard de Queimadas no Brasil",
    page_icon="🔥",
    layout="wide"
)

# --- CSS Customizado ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3, h4 {
        color: #2c3e50;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stMetric {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNÇÕES DE CARREGAMENTO
# ==============================================================================
@st.cache_data
def carregar_dados_dashboard():
    try:
        return pd.read_csv("dados_para_dashboard.csv")
    except FileNotFoundError:
        st.error("❌ Arquivo 'dados_para_dashboard.csv' não encontrado.")
        return None

@st.cache_data
def carregar_dados_mapa():
    try:
        return pd.read_csv("dados_para_mapa.csv")
    except FileNotFoundError:
        st.error("❌ Arquivo 'dados_para_mapa.csv' não encontrado.")
        return None

@st.cache_resource
def carregar_modelo():
    try:
        return joblib.load("modelo_risco_fogo.joblib")
    except FileNotFoundError:
        st.error("❌ Arquivo 'modelo_risco_fogo.joblib' não encontrado.")
        return None

# Carregamento
df_dashboard = carregar_dados_dashboard()
df_mapa = carregar_dados_mapa()
modelo = carregar_modelo()

colunas_do_modelo = [
    'dias_sem_chuva', 'precipitacao', 'mes', 'latitude', 'longitude',
    'bioma_Caatinga', 'bioma_Cerrado', 'bioma_Mata Atlântica', 'bioma_Pampa', 'bioma_Pantanal',
    'satelite_AQUA_M-T', 'satelite_GOES-16', 'satelite_NOAA-20', 'satelite_NPP-375',
    'satelite_NPP-375D', 'satelite_TERRA_M-M', 'satelite_TERRA_M-T'
]

# ==============================================================================
# 4. SIDEBAR DE NAVEGAÇÃO
# ==============================================================================
st.sidebar.title("Menu")
pagina = st.sidebar.radio(
    "Escolha uma seção:",
    ["Página Inicial", "Análise Histórica", "Mapa de Exploração Anual", "Comparativo Anual de Mapas", "Previsão de Risco de Fogo", "Conclusões"]
)

# ==============================================================================
# 5. CONTEÚDO DAS PÁGINAS
# ==============================================================================

# --- Página Inicial ---
if pagina == "Página Inicial":
    st.title("🔥 Análise e Previsão de Queimadas no Brasil")
    st.markdown("""

        ### Objetivo do Projeto

        Este painel interativo apresenta uma análise detalhada sobre os focos de queimada no Brasil, servindo como uma ferramenta para a compreensão de padrões, sazonalidades e para a prevenção de desastres ambientais. O projeto combina a análise de dados históricos com um modelo preditivo de Machine Learning para estimar o risco de incêndio em tempo real.

        ---

        ### 🌎 Metodologia e Fonte de Dados

        Os dados foram obtidos do **Instituto Nacional de Pesquisas Espaciais (INPE)** e acessados através da plataforma pública [Basedosdados](https://basedosdados.org/dataset/br-inpe-queimadas). A análise abrange o período de 2003 a 2025, permitindo tanto uma visão histórica ampla quanto uma análise aprofundada de dados mais recentes.

        O desenvolvimento seguiu as seguintes etapas:
        1.  **Coleta e Limpeza:** Os dados foram consultados e pré-filtrados diretamente no Google BigQuery para otimizar o processamento.
        2.  **Análise Exploratória (EDA):** Foram investigadas tendências temporais e a distribuição dos focos entre os biomas brasileiros.
        3.  **Modelagem Preditiva:** Foi treinado um modelo `RandomForestRegressor` com dados a partir de 2023 para prever a variável `risco_fogo` com base em características geográficas e meteorológicas.
        4.  **Desenvolvimento do Dashboard:** A interface foi construída em Streamlit para apresentar os resultados de forma interativa.

        **💻 Tecnologias Utilizadas:** Python, Pandas, Scikit-learn, Geopy, Streamlit, Plotly, Pydeck, Google Colab e BigQuery.

        ---

        ### 🧭 Navegação pelo Dashboard

        Utilize o menu na barra lateral para explorar as diferentes seções do projeto:

        * **📊 Análise Histórica:** Explore gráficos sobre a evolução dos focos de queimada ao longo dos anos e a sua distribuição entre os diferentes biomas brasileiros.

        * **🗺️ Mapa de Exploração Anual:** Visualize geograficamente milhares de focos de queimada em um mapa interativo. Use o slider de ano e os filtros de bioma para investigar padrões espaciais e temporais.

        * **🆚 Comparativo Anual de Mapas:** Compare a distribuição dos focos de incêndio entre dois anos diferentes, lado a lado, para identificar mudanças e tendências de forma clara.

        * **🤖 Previsão de Risco de Fogo:** Interaja com o modelo preditivo. Insira condições como dias sem chuva, precipitação e localização para simular um cenário e receber uma estimativa do risco de fogo em tempo real, visualizada em um mapa.
        👉 Use o menu lateral para navegar.
    """)
    st.image("imagem_queimada.png", caption="Ilustração de osgemeos (@osgemeos) by Instagram", use_container_width=True)
    st.divider()

# --- Análise Histórica ---
elif pagina == "Análise Histórica":
    st.title("📊 Análise Histórica dos Focos de Queimada")
    st.markdown("Explore as tendências temporais, geográficas e sazonais dos focos de queimada no Brasil.")

    if df_dashboard is not None:
        
        # O filtro de bioma agora fica no topo e se aplica a todas as abas
        biomas = ['Todos'] + sorted(list(df_dashboard['bioma'].unique()))
        bioma_selecionado = st.selectbox("🌱 Filtre por Bioma:", biomas)

        # Filtra o DataFrame principal uma vez
        df_filtrado = df_dashboard if bioma_selecionado == "Todos" else df_dashboard[df_dashboard['bioma'] == bioma_selecionado]

        # --- CRIAÇÃO DAS ABAS PARA ORGANIZAR OS GRÁFICOS ---
        tab1, tab2, tab3 = st.tabs(["Visão Geral Anual", "Sazonalidade (Heatmap)", "Padrão dos Biomas"])

        # --- Conteúdo da Aba 1: Visão Geral ---
        with tab1:
            st.subheader("Evolução dos Focos de Queimada por Ano")
            focos_por_ano = df_filtrado.groupby('ano')['contagem_focos'].sum().reset_index()
            fig_ano = px.line(focos_por_ano, x='ano', y='contagem_focos',
                              labels={'ano': 'Ano', 'contagem_focos': 'Número de Focos'},
                              markers=True, template="plotly_white")
            st.plotly_chart(fig_ano, use_container_width=True)

            if bioma_selecionado == "Todos":
                st.subheader("Distribuição Total por Bioma")
                focos_por_bioma = df_dashboard.groupby('bioma')['contagem_focos'].sum().sort_values(ascending=False).reset_index()
                fig_bioma = px.bar(focos_por_bioma, x="contagem_focos", y="bioma",
                                   labels={'bioma': 'Bioma', 'contagem_focos': 'Total de Focos'},
                                   text_auto=True, template="plotly_white", orientation='h'
                                  ).update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bioma, use_container_width=True)

        # --- Conteúdo da Aba 2: Heatmap de Sazonalidade ---
        with tab2:
            st.subheader("Mapa de Calor: Intensidade Mensal das Queimadas por Ano")
            st.markdown("Este gráfico mostra em quais meses de cada ano a atividade de queimadas foi mais intensa. Cores mais quentes indicam um maior número de focos.")
            
            # Prepara os dados para o heatmap
            heatmap_data = df_filtrado.groupby(['ano', 'mes'])['contagem_focos'].sum().reset_index()
            heatmap_pivot = heatmap_data.pivot_table(index='ano', columns='mes', values='contagem_focos', fill_value=0)
            
            fig_heatmap = px.imshow(
                heatmap_pivot,
                labels=dict(x="Mês", y="Ano", color="Nº de Focos"),
                title=f"Intensidade de Queimadas para: {bioma_selecionado}",
                color_continuous_scale='YlOrRd'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

        # --- Conteúdo da Aba 3: Padrão Sazonal dos Biomas ---
        with tab3:
            st.subheader("Padrão Sazonal de Queimadas por Bioma")
            st.markdown("Este gráfico compara o comportamento das queimadas ao longo do ano para cada bioma, revelando seus períodos mais críticos.")
            
            # Agrupa por bioma e mês, mesmo que só um bioma esteja selecionado
            sazonalidade_bioma = df_filtrado.groupby(['bioma', 'mes'])['contagem_focos'].sum().reset_index()
            
            fig_sazonalidade_bioma = px.line(
                sazonalidade_bioma,
                x='mes',
                y='contagem_focos',
                color='bioma', # Mesmo com um bioma, 'color' cria a legenda corretamente
                title=f"Ciclo Anual de Queimadas para: {bioma_selecionado}",
                labels={'mes': 'Mês do Ano', 'contagem_focos': 'Número de Focos'},
                markers=True
            )
            fig_sazonalidade_bioma.update_xaxes(dtick=1)
            st.plotly_chart(fig_sazonalidade_bioma, use_container_width=True)


# --- Mapa Interativo ---
elif pagina == "Mapa de Exploração Anual":
    st.title("🗺️ Análise Anual e Comparativa dos Focos de Queimada")
    st.markdown("Use o controle deslizante para selecionar um ano e veja a distribuição dos focos no mapa e no gráfico de resumo.")

    if df_mapa is not None:
        # --- FILTROS ---
        
        # 1. Slider para selecionar um único ano
        anos_disponiveis = sorted(df_mapa['ano'].unique())
        ano_selecionado = st.slider(
            "Selecione o Ano para Análise:",
            min_value=min(anos_disponiveis),
            max_value=max(anos_disponiveis),
            value=max(anos_disponiveis), # Começa com o ano mais recente
            step=1
        )
        
        # Filtro para Biomas continua útil para focar a análise
        biomas_disponiveis = sorted(df_mapa['bioma'].unique())
        biomas_selecionados = st.multiselect(
            "Selecione os biomas para exibir:",
            options=biomas_disponiveis,
            default=biomas_disponiveis
        )

        # --- LÓGICA DE FILTRAGEM ---
        if biomas_selecionados:
            df_filtrado = df_mapa[
                (df_mapa['ano'] == ano_selecionado) &
                (df_mapa['bioma'].isin(biomas_selecionados))
            ]

            # --- CORES E LEGENDA PARA OS BIOMAS (permanece igual) ---
            cores_bioma = {
                'Amazônia': [34, 139, 34],
                'Cerrado': [255, 165, 0],
                'Mata Atlântica': [0, 100, 0],
                'Caatinga': [218, 165, 32],
                'Pantanal': [0, 191, 255],
                'Pampa': [189, 183, 107]
            }
            df_filtrado["color"] = df_filtrado["bioma"].map(cores_bioma)

            # Legenda dinâmica
            legenda_html = "<div style='display:flex; flex-wrap:wrap; gap:15px; align-items:center; margin-bottom:10px;'>"
            legenda_html += "<h4>Legendas por Bioma:</h4>"
            for bioma, cor in cores_bioma.items():
                if bioma in biomas_disponiveis:
                    cor_hex = '#%02x%02x%02x' % tuple(cor)
                    legenda_html += f"<div style='display:flex; align-items:center; gap:5px;'><span style='width:20px; height:20px; background-color:{cor_hex}; border-radius:3px;'></span><span>{bioma}</span></div>"
            legenda_html += "</div>"
            st.markdown(legenda_html, unsafe_allow_html=True)

            # --- LAYOUT COM DUAS COLUNAS: MAPA E GRÁFICO ---
            col_mapa, col_grafico = st.columns([3, 2]) # Mapa ocupa 60%, gráfico 40%

            with col_mapa:
                st.subheader(f"📍 Distribuição de {len(df_filtrado):,} focos em {ano_selecionado}")
                if not df_filtrado.empty:
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=df_filtrado,
                        get_position='[longitude, latitude]',
                        get_fill_color="color",
                        get_radius=15000,
                        pickable=True,
                        opacity=0.6
                    )
                    view_state = pdk.ViewState(latitude=-14, longitude=-55, zoom=3.5, pitch=0)
                    tooltip = {"html": "<b>Bioma:</b> {bioma}<br/><b>Coords:</b> {latitude:.4f}, {longitude:.4f}"}
                    r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
                    st.pydeck_chart(r)
                else:
                    st.info("Nenhum foco de queimada encontrado com os filtros selecionados.")

            with col_grafico:
                st.subheader(f"📊 Resumo por Bioma em {ano_selecionado}")
                if not df_filtrado.empty:
                    # Conta os focos por bioma para o ano selecionado
                    contagem_bioma = df_filtrado['bioma'].value_counts().reset_index()
                    contagem_bioma.columns = ['bioma', 'contagem']
                    
                    # Cria o gráfico de barras com as cores correspondentes
                    fig_resumo = px.bar(
                        contagem_bioma,
                        x='contagem',
                        y='bioma',
                        orientation='h',
                        color='bioma',
                        color_discrete_map={bioma: f'rgb({r},{g},{b})' for bioma, (r,g,b) in cores_bioma.items()},
                        labels={'contagem': 'Número de Focos', 'bioma': 'Bioma'},
                        text='contagem'
                    ).update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                    st.plotly_chart(fig_resumo, use_container_width=True)
                else:
                    st.info("Sem dados para exibir.")
        else:
            st.warning("⚠️ Por favor, selecione pelo menos um bioma.")

# --- COMPARAÇÃO DE MAPAS ---
elif pagina == "Comparativo Anual de Mapas":
    st.title("🗺️ Comparativo Anual de Mapas de Focos de Queimada")
    st.markdown("Selecione dois anos diferentes para comparar a distribuição dos focos lado a lado.")

    if df_mapa is not None:
        # --- SELETORES DE ANOS E BIOMAS ---
        anos_disponiveis = sorted(df_mapa['ano'].unique(), reverse=True)
        
        col_seletores1, col_seletores2 = st.columns([1, 3])
        with col_seletores1:
            # Seletor para o primeiro ano (Ano A)
            ano_a = st.selectbox(
                "Selecione o Ano A (Esquerda):",
                options=anos_disponiveis,
                index=1 # Pega o segundo ano mais recente por padrão (ex: 2024)
            )
            # Seletor para o segundo ano (Ano B)
            ano_b = st.selectbox(
                "Selecione o Ano B (Direita):",
                options=anos_disponiveis,
                index=0 # Pega o ano mais recente por padrão (ex: 2025)
            )

        with col_seletores2:
            # Filtro de Biomas que se aplica a ambos os mapas
            biomas_disponiveis = sorted(df_mapa['bioma'].unique())
            biomas_selecionados = st.multiselect(
                "Filtre por Biomas (para ambos os mapas):",
                options=biomas_disponiveis,
                default=biomas_disponiveis
            )
        
        # --- LEGENDA COMPARTILHADA ---
        cores_bioma = {
            'Amazônia': [34, 139, 34], 'Cerrado': [255, 165, 0], 'Mata Atlântica': [0, 100, 0],
            'Caatinga': [218, 165, 32], 'Pantanal': [0, 191, 255], 'Pampa': [189, 183, 107]
        }
        legenda_html = "<div style='display:flex; flex-wrap:wrap; gap:15px; align-items:center; margin-bottom:10px;'>"
        for bioma, cor in cores_bioma.items():
            if bioma in biomas_disponiveis:
                cor_hex = '#%02x%02x%02x' % tuple(cor)
                legenda_html += f"<div style='display:flex; align-items:center; gap:5px;'><span style='width:20px; height:20px; background-color:{cor_hex}; border-radius:3px;'></span><span>{bioma}</span></div>"
        legenda_html += "</div>"
        st.markdown(legenda_html, unsafe_allow_html=True)
        st.markdown("---")


        # --- CRIAÇÃO DOS MAPAS LADO A LADO ---
        col_mapa1, col_mapa2 = st.columns(2)

        if biomas_selecionados:
            # Filtra os dados para cada ano selecionado
            df_a = df_mapa[(df_mapa['ano'] == ano_a) & (df_mapa['bioma'].isin(biomas_selecionados))]
            df_b = df_mapa[(df_mapa['ano'] == ano_b) & (df_mapa['bioma'].isin(biomas_selecionados))]

            # Adiciona a coluna de cor
            df_a["color"] = df_a["bioma"].map(cores_bioma)
            df_b["color"] = df_b["bioma"].map(cores_bioma)
            
            # Visão de câmera compartilhada para que os mapas fiquem sincronizados
            view_state = pdk.ViewState(latitude=-14, longitude=-55, zoom=3.5, pitch=0)
            tooltip = {"html": "<b>Bioma:</b> {bioma}<br/><b>Coords:</b> {latitude:.4f}, {longitude:.4f}"}

            # Renderiza o Mapa A (Esquerda)
            with col_mapa1:
                st.subheader(f"Mapa para {ano_a} ({len(df_a):,} focos)")
                layer_a = pdk.Layer(
                    "ScatterplotLayer", data=df_a, get_position='[longitude, latitude]',
                    get_fill_color="color", get_radius=15000, pickable=True, opacity=0.6
                )
                r_a = pdk.Deck(layers=[layer_a], initial_view_state=view_state, tooltip=tooltip)
                st.pydeck_chart(r_a)

            # Renderiza o Mapa B (Direita)
            with col_mapa2:
                st.subheader(f"Mapa para {ano_b} ({len(df_b):,} focos)")
                layer_b = pdk.Layer(
                    "ScatterplotLayer", data=df_b, get_position='[longitude, latitude]',
                    get_fill_color="color", get_radius=15000, pickable=True, opacity=0.6
                )
                r_b = pdk.Deck(layers=[layer_b], initial_view_state=view_state, tooltip=tooltip)
                st.pydeck_chart(r_b)

        else:
            st.warning("⚠️ Por favor, selecione pelo menos um bioma.")

# --- PREVISÃO DE RISCO---
elif pagina == "Previsão de Risco de Fogo":
    st.title("🤖 Previsão de Risco de Fogo")

    if modelo is not None:
        with st.form("formulario_previsao"):
            st.markdown("##### Preencha os dados para a simulação:")
            col1, col2 = st.columns(2)
            
            with col1:
                dias_sem_chuva = st.slider("Dias sem chuva", 0, 100, 15)
                precipitacao = st.number_input("Precipitação (mm)", 0.0, 200.0, 0.0, step=0.1)
                mes = st.selectbox("Mês", list(range(1, 13)), 8)
                
                # Lógica para gerar as opções de satélite dinamicamente
                colunas_satelite_modelo = [c for c in colunas_do_modelo if c.startswith("satelite_")]
                opcoes_satelite = [c.replace("satelite_", "") for c in colunas_satelite_modelo]
                if "AQUA_M" not in opcoes_satelite: # Adiciona o satélite removido pelo drop_first=True
                    opcoes_satelite.insert(0, "AQUA_M")
                satelite = st.selectbox("Satélite", sorted(opcoes_satelite))

            with col2:
                latitude = st.number_input("Latitude", -34.0, 5.0, -10.0, format="%.4f")
                longitude = st.number_input("Longitude", -74.0, -34.0, -55.0, format="%.4f")
                
                # Lógica para gerar as opções de bioma dinamicamente
                colunas_bioma_modelo = [c for c in colunas_do_modelo if c.startswith("bioma_")]
                opcoes_bioma = [c.replace("bioma_", "") for c in colunas_bioma_modelo]
                if "Amazônia" not in opcoes_bioma: # Adiciona o bioma removido pelo drop_first=True
                    opcoes_bioma.insert(0, "Amazônia")
                bioma = st.selectbox("Bioma", sorted(opcoes_bioma))

            submit = st.form_submit_button("🔮 Realizar Previsão")

        # --- LÓGICA DE PREVISÃO E EXIBIÇÃO DOS RESULTADOS ---
        # Esta parte agora fica fora do "with st.form(...)" para que os resultados persistam
        if submit:
            # Prepara o DataFrame para o modelo
            input_df = pd.DataFrame(0, index=[0], columns=colunas_do_modelo)
            input_df['dias_sem_chuva'] = dias_sem_chuva
            input_df['precipitacao'] = precipitacao
            input_df['mes'] = mes
            input_df['latitude'] = latitude
            input_df['longitude'] = longitude
            if f'bioma_{bioma}' in input_df.columns:
                input_df[f'bioma_{bioma}'] = 1
            if f'satelite_{satelite}' in input_df.columns:
                input_df[f'satelite_{satelite}'] = 1

            previsao = modelo.predict(input_df)[0]

            # --- EXIBIÇÃO DOS RESULTADOS (TEXTO E MAPA) ---
            st.markdown("---")
            st.subheader("Resultado da Previsão:")
            
            # Layout com duas colunas para o resultado e o mapa
            col_resultado, col_mapa = st.columns([1, 2]) # Resultado ocupa 1/3, mapa 2/3

            with col_resultado:
                # Mostra o resultado com a cor apropriada
                if previsao >= 0.75:
                    st.error(f"🔥 Risco MUITO ALTO")
                elif previsao >= 0.5:
                    st.warning(f"⚠️ Risco MODERADO")
                else:
                    st.success(f"✅ Risco BAIXO")
                
                st.markdown(f"Risco de fogo: {previsao:.2%}")
                st.progress(previsao)

            with col_mapa:
                # --- NOVO: Função para criar a cor do marcador ---
                def calcular_cor_risco(risco):
                    """Cria um gradiente de verde para vermelho baseado no risco (0 a 1)."""
                    # Interpolação linear: R = 255 * risco, G = 255 * (1 - risco)
                    red = int(255 * risco)
                    green = int(255 * (1 - risco))
                    return [red, green, 0]

                cor_marcador = calcular_cor_risco(previsao)

                # --- NOVO: Criação do Mapa com o Ponto da Previsão ---
                df_ponto_mapa = pd.DataFrame({
                    'latitude': [latitude],
                    'longitude': [longitude],
                    'cor': [cor_marcador],
                    'risco_texto': [f"Risco: {previsao:.2%}"]
                })

                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=df_ponto_mapa,
                    get_position='[longitude, latitude]',
                    get_fill_color="cor", # Usa a cor que calculamos
                    get_radius=20000,     # Raio do marcador em metros
                    pickable=True,
                    opacity=0.8
                )

                # Centraliza o mapa na coordenada prevista
                view_state = pdk.ViewState(
                    latitude=latitude,
                    longitude=longitude,
                    zoom=6,
                    pitch=0
                )

                tooltip = {"text": "{risco_texto}"}

                r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip, map_style='mapbox://styles/mapbox/satellite-streets-v11')
                st.pydeck_chart(r)

# --- NOVA PÁGINA DE CONCLUSÕES ---
elif pagina == "Conclusões":
    st.title("💡 Conclusões e Insights Principais")

    st.markdown("""
    A análise dos dados de queimadas do INPE, abrangendo o período de 2003 a 2025, revela padrões marcantes e confirma que os incêndios florestais no Brasil, embora complexos, não são eventos aleatórios. Eles seguem tendências e são influenciados por fatores geográficos e sazonais bem definidos.

    Abaixo estão os principais insights derivados deste projeto:
    """)

    st.markdown("---")

    st.subheader("Principais Observações da Análise Exploratória")
    st.markdown("""
    - ** sazonalidade no 'Arco do Desmatamento'**: Como observado, há uma concentração massiva de focos de queimada nos meses de **Agosto, Setembro e Outubro**. Este período corresponde ao final da estação seca em grande parte do centro do país, especialmente nos biomas Amazônia e Cerrado, onde a vegetação seca se torna altamente inflamável.

    - **Concentração Geográfica nos Biomas Amazônia e Cerrado**: A grande maioria dos focos de incêndio registrados no Brasil ocorre nesses dois biomas. Isso destaca a pressão constante sobre essas áreas, seja por fatores naturais ou, mais significativamente, por atividades humanas como desmatamento e práticas agrícolas.

    - **Variação Anual Significativa**: O número de focos de queimada não é constante e varia muito de um ano para o outro. O **aumento expressivo observado entre 2023 e 2024**, por exemplo, pode estar ligado a fatores complexos como fenômenos climáticos (ex: El Niño, que causa secas mais severas) e mudanças em políticas de fiscalização ambiental.

    - **Padrões Sazonais Distintos por Bioma**: Embora o pico nacional ocorra no final do inverno, a análise detalhada revela que cada ecossistema tem sua própria "personalidade de fogo". Biomas como o Pampa, no sul, ou áreas específicas como o estado de Roraima (que segue um ciclo climático diferente), apresentam picos em outras épocas do ano, evidenciando a necessidade de estratégias de combate regionalizadas.
    """)

    st.markdown("---")

    st.subheader("A Previsibilidade do Risco de Fogo")
    st.markdown("""
    O sucesso do modelo de Machine Learning (`RandomForestRegressor`), que alcançou uma alta performance (R² > 90%), é talvez a conclusão mais poderosa deste projeto. Ele demonstra que o risco de fogo **não é um evento imprevisível**.

    Com um conjunto limitado de variáveis, o modelo conseguiu prever o risco com alta precisão. Isso confirma que os principais impulsionadores do risco de fogo são:
    1.  **Condições Meteorológicas:** Dias sem chuva e precipitação são preditores extremamente fortes.
    - **Localização Geográfica:** A latitude e a longitude são cruciais, pois representam o tipo de vegetação e o clima local.
    3.  **Época do Ano:** O mês é um indicador poderoso da posição na estação seca ou chuvosa.
    """)

    st.markdown("---")

    st.subheader("Limitações e Próximos Passos")
    st.markdown("""
    Como todo projeto de dados, este também tem suas limitações, que abrem portas para trabalhos futuros:
    - **Qualidade dos Dados:** A análise revelou que dados meteorológicos detalhados e consistentes para todos os biomas ainda são um desafio, o que nos levou a focar o modelo em dados mais recentes.
    - **Próximos Passos Sugeridos:**
        - Enriquecer o modelo com outras variáveis, como velocidade do vento, umidade do ar e dados de desmatamento em tempo real.
        - Desenvolver modelos especialistas para outros biomas, à medida que mais dados de qualidade se tornem disponíveis.
        - Criar um modelo de séries temporais para tentar prever o *volume* total de queimadas para os próximos meses.

    Em suma, este projeto demonstra o poder da ciência de dados para transformar dados brutos em insights acionáveis, essenciais para o monitoramento e combate às queimadas no Brasil.
    """)
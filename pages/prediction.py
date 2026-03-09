import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
import utils.BioethanolOptimizer as bioopt
# from pages.data import select_dataset
import pages.data as data
from pathlib import Path
from utils.bucket_connect import BucketUtils
from utils.utils_datas import list_files, handle_existing_dataset, load_model
from config import DATASET_DIR, DEFAULT_DATA
from utils.utils_models_trained import UtilsModelsTrained

FIELDS = {'input_c': 0.0, 'input_h': 0.0, 'input_l': 0.0, 'acid': 2.5, 'time': 45}

class PredictionPage:
    """"
    A class to encapsulate the prediction page logic and state management.
    """

    def __init__(self, model_path=None, bucket=None):
        """"
        Initializes the PredictionPage class by loading the model and dataset.
        """
        try:

            training_data = BucketUtils.load_model_from_bucket(bucket, model_path)

            # Extract the components
            self.model = training_data['model']
            self.model_name = training_data['model_name']
            self.columns_input = training_data['columns_input']
            self.columns_output = training_data['columns_output']
            self.dataset = training_data['dataset']
            self.filename = training_data['filename']

            st.success(f"Modelo '{training_data.get('model_name')}' carregado com sucesso!")
            # st.write(training_data)
        except Exception as e:
            st.error(f"Erro ao inicializar a página de predição: {e}")

    
    def simulate_results_old(self, X_new):
        optimizer = bioopt.BioethanolOptimizer(st.session_state.current_dataset)

        scaler = StandardScaler()
        X_new_scaled = scaler.transform(X_new)


        # Relações básicas de conversão
        glucose_base = ( (X_new['Acid Conc (%)'] * 0.5) + 
                    (X_new['S- Time (min)'] * 0.1) ) * (1 - X_new['L (%)']/100)
        
        ethanol_conversion = 0.51  # Fator teórico máximo de conversão glicose->etanol
        
        # Cálculos simulados com fatores aleatórios controlados
        simulated = {
            'Glicose (g/L)': max(10, glucose_base * 5 + np.random.normal(2, 0.5)),
            'Etanol (g/L)': max(5, (glucose_base * ethanol_conversion) * 0.9 + np.random.normal(3, 0.3)),
            'Efficiency': min(0.95, ( (X_new['C (%)']/40) * 0.3 + 
                                (X_new['H (%)']/25) * 0.2 +
                                (1 - X_new['L (%)']/100) * 0.5 ) + np.random.uniform(-0.1, 0.1)),
            'Yield': min(100, ( (X_new['Acid Conc (%)']/3) * 25 + 
                            (X_new['S- Time (min)']/60) * 25 +
                            (1 - X_new['L (%)']/100) * 50 ) + np.random.normal(0, 5))
        }
        
        # Ajustes de consistência
        simulated['Etanol (g/L)'] = min(simulated['Etanol (g/L)'], simulated['Glicose (g/L)'] * ethanol_conversion)
        simulated['Efficiency'] = max(0.35, simulated['Efficiency'])
        
        # Formatação numérica
        simulated = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in simulated.items()}
        
        return simulated

    def simulate_results(self, X_new):
        try:
            model = self.model
            X_cols = self.columns_input
            y_cols = self.columns_output
            dataset = self.dataset

            
            # Converte o dicionário de entrada para um DataFrame
            X_new_df = pd.DataFrame([X_new])
            
            # Identifica colunas numéricas para normalização (mesma lógica do treinamento)
            # Como o scaler não foi salvo, recriamos com base no dataset original
            numeric_cols = [col for col in X_cols if pd.api.types.is_numeric_dtype(dataset[col])]
            
            scaler = StandardScaler()
            scaler.fit(dataset[numeric_cols])

            # Prepara dados para predição
            X_processed = X_new_df[numeric_cols]
            X_scaled = scaler.transform(X_processed)

            # Realiza a predição
            y_pred = model.predict(X_scaled)

            # Formata a saída em um dicionário, como na função de simulação antiga
            # Assumindo que y_pred é um array com as predições na ordem de y_cols
            results = {label: round(value, 2) for label, value in zip(y_cols, y_pred[0])}
            
            # Adiciona outras métricas se necessário, como na função antiga
            # Exemplo:
            if 'Glicose (g/L)' in results and 'Etanol (g/L)' not in results:
                results['Etanol (g/L)'] = round(results['Glicose (g/L)'] * 0.51 * 0.9, 2) # Conversão teórica

            return results

        except Exception as e:
            # st.error(f"Erro ao simular resultados: {e}")
            st.exception(e) # Mostra o stack trace completo na tela
            return None

    def params_simulate(self):
        """
        Show the input parameters for the simulation and allow the user to adjust them.
        """
        
        dataset = self.dataset
        # bioethanol_optimizer = bioopt.BioethanolOptimizer(dataset)
        biomass_options = dataset.iloc[:, 0].drop_duplicates().tolist()

        # Inicializa os valores padrão
        for key, default in FIELDS.items():
            if key not in st.session_state:
                st.session_state[key] = default

        # Divisão em colunas para organização
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                'Celulose (C %)', 
                min_value=0.0, 
                max_value=100.0, 
                # value=42.5,
                step=0.1,
                key='input_c',
                on_change=lambda: st.session_state.__setitem__('input_c', st.session_state.input_c),
                help="Percentual de celulose na biomassa"
            )
        with col2:
            st.number_input(
                'Hemicelulose (H %)', 
                min_value=0.0,
                max_value=100.0, 
                # value=25.0,
                step=0.1,
                key='input_h',
                on_change=lambda: st.session_state.__setitem__('input_h', st.session_state.input_h),
                help="Percentual de hemicelulose na biomassa"
            )
        with col3:
            st.number_input(
                'Lignina (L %)', 
                min_value=0.0,
                max_value=100.0, 
                # value=14.2,
                step=0.1,
                key='input_l',
                on_change=lambda: st.session_state.__setitem__('input_l', st.session_state.input_l),
                help="Percentual de lignina na biomassa"
            )

        st.selectbox(
            label="Selecione o tipo de biomassa",
            options=biomass_options,
            help="Escolha a biomassa base para a simulação",
            key='selected_biomass',
            on_change=lambda: st.session_state.__setitem__('selected_biomass', st.session_state.selected_biomass),
            index=0
        )

        if st.toggle("Parâmetros Avançados", False, help="Habilita ajustes avançados para otimização"):
            with st.expander("⚙️ Parâmetros de Sacarificação (hidrólise enzimática)", expanded=False):
                acid_col, stime_col = st.columns(2)
                with acid_col:
                    st.number_input(
                        'Concentração Ácida (pH)', 
                        min_value=0.0,
                        max_value=100.0, 
                        # value=2.5,
                        step=0.1,
                        key='acid',
                        on_change=lambda: st.session_state.__setitem__('acid', st.session_state.acid),
                        help="Concentração de ácido na solução"
                        )
                with stime_col:
                    st.number_input(
                    'Tempo de Sacarificação (horas)', 
                    min_value=0,
                    # value=45,
                    step=1,
                    key='time',
                    on_change=lambda: st.session_state.__setitem__('time', st.session_state.time),
                    help="Tempo de reação da sacarificação"
                    )
                
                temp_col, rpm_col = st.columns(2)
                with temp_col:
                    st.number_input(
                    'Temperatura (°C)',
                    min_value=0.0,
                    value=30.0,
                    step=0.5,
                    key='s_temp',
                    on_change=lambda: st.session_state.__setitem__('s_temp', st.session_state.s_temp),
                    help="Temperatura do processo de sacarificação"
                    )
                with rpm_col:
                    st.number_input(
                    'Velocidade de Agitação (RPM)',
                    min_value=0,
                    value=150,
                    step=10,
                    key='s_rpm',
                    on_change=lambda: st.session_state.__setitem__('s_rpm', st.session_state.s_rpm),
                    help="Velocidade de agitação durante a sacarificação"
                    )
            
            with st.expander("⚙️ Parâmetros de Fermentação", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.number_input(
                        'Concentração Ácida (pH)', 
                        min_value=0.0,
                        max_value=100.0, 
                        # value=2.5,
                        step=0.1,
                        key='f_acid',
                        on_change=lambda: st.session_state.__setitem__('f_acid', st.session_state.f_acid),
                        help="Concentração de ácido na solução"
                        )
                    st.number_input(
                        'Tempo de Sacarificação (horas)', 
                        min_value=0,
                        # value=45,
                        step=1,
                        key='f_time',
                        on_change=lambda: st.session_state.__setitem__('f_time', st.session_state.f_time),
                        help="Tempo de reação da sacarificação"
                        )
                with col2:
                    st.number_input(
                        'Temperatura (°C)',
                        min_value=0.0,
                        value=30.0,
                        step=0.5,
                        key='f_temp',
                        on_change=lambda: st.session_state.__setitem__('f_temp', st.session_state.f_temp),
                        help="Temperatura do processo de sacarificação"
                        )
            
                    st.number_input(
                        'Velocidade de Agitação (RPM)',
                        min_value=0,
                        value=150,
                        step=10,
                        key='f_rpm',
                        on_change=lambda: st.session_state.__setitem__('f_rpm', st.session_state.f_rpm),
                        help="Velocidade de agitação durante a sacarificação"
                        )
        
        sum = st.session_state.input_c + st.session_state.input_h + st.session_state.input_l
        if sum > 100 or sum <= 0:
            st.error("❌ A soma dos percentuais de C, H e L não pode exceder 100% ou ser menor que 0%")
        elif sum < 100:
            st.warning("⚠️ A soma dos percentuais de C, H e L está abaixo de 100%")
        else:
            st.success("✅ A soma dos percentuais de C, H e L está correta")
        
        st.button(
            label='▶️ Executar Simulação',
            key='submit_simulation',
            disabled=sum > 100 or sum <= 0  # Desabilita se inválido
        )

    def run_simulation(self):
        """
        Executa a simulação com os parâmetros definidos pelo usuário.
        """
        if st.session_state.submit_simulation:
            with st.spinner('🔍 Otimizando parâmetros...'):
                try:
                    # Construção do input para o modelo
                    X_new = {
                        'Biomass': st.session_state.selected_biomass,
                        'C (%)': st.session_state.input_c,
                        'H (%)': st.session_state.input_h,
                        'L (%)': st.session_state.input_l,
                        'Acid Conc (%)': st.session_state.acid,
                        'S- Time (min)': st.session_state.s_time if st.session_state.get('s_time') is not None else 45,
                        'S- Temp (h)': st.session_state.s_temp if st.session_state.get('s_temp') is not None else 30.0,
                    }

                    # st.write(X_new)

                    # Execução da otimização
                    results = self.simulate_results(X_new)
                    st.divider()
                    # Exibição dos resultados
                    st.success("✅ Otimização concluída com sucesso!")
                    
                    # Métricas principais
                    st.markdown("### 📊 Resultados da Otimização")
                    cols = st.columns(3)
                    cols[0].metric("Glicose Otimizada (g/L)", 
                                    f"{results['Glicose (g/L)']:.2f}")
                    cols[1].metric("Etanol Produzido (g/L)", 
                                    f"{results['Etanol (g/L)']:.2f}", 
                                    delta_color="off")
                    cols[2].metric("Eficiência", 
                                    f"{results['Efficiency']:.1%}" if 'Efficiency' in results else "N/A")
                    
                    # Detalhes da simulação
                    with st.expander("📝 Detalhes Completos da Simulação"):
                        st.markdown("""
                        **Parâmetros Utilizados:**
                        - Biomassa: {Biomass}
                        - Celulose (C): {c}%
                        - Hemicelulose (H): {h}%
                        - Lignina (L): {l}%
                        - Concentração Ácida: {Acid}%
                        - Tempo de Sacarificação: {Time} min
                        """.format(**X_new, c=X_new['C (%)'], h=X_new['H (%)'], l=X_new['L (%)'], Acid=X_new['Acid Conc (%)'], Time=X_new['S- Time (min)']))

                        st.markdown("""
                        **Resultados:**
                        - Concentração de Glicose: {glicose} g/L
                        - Produção de Etanol: {etanol} g/L
                        - Rendimento Teórico Máximo: {rendimento}%
                        - Eficiência: {eficiencia}%
                        """.format(**results, glicose=results['Glicose (g/L)'], etanol=results['Etanol (g/L)'], rendimento=results['Yield'], eficiencia=results['Efficiency']))
                        # """.format(**results))

                    # Visualização gráfica (exemplo)
                    if 'Yield' in results:
                        st.markdown("### 📈 Progresso do Rendimento")
                        progress = min(int(results['Yield']), 100)
                        st.progress(progress)
                        st.caption(f"Rendimento estimado: {progress}%")

                except Exception as e:
                    st.error(f"❌ Erro durante a otimização: {str(e)}")

            # Seção de ajuda
            st.markdown("---")
            with st.expander("ℹ️ Como interpretar os resultados?"):
                st.markdown("""
                **Guia de Interpretação:**
                - **Glicose Otimizada:** Quantidade ideal de glicose liberada durante a hidrólise
                - **Etanol Produzido:** Quantidade estimada de etanol produzido na fermentação
                - **Eficiência:** Razão entre produção real e teórica máxima
                - **Rendimento:** Percentual da conversão teórica máxima alcançada
                
                **Dicas:**
                1. Valores de eficiência acima de 85% são considerados excelentes
                2. Ajuste os parâmetros avançados para melhorar o rendimento
                3. Verifique a compatibilidade da biomassa com os parâmetros químicos
                """)

    def custom_data(self, list_train):
        col1, col2 = st.columns([2, 2])
        with st.container(border=True):
            col1, col2 = st.columns([2, 2])
            with col1:
                    # data.select_dataset()
                op = data.list_files()
                dataset_option = st.selectbox(
                        label="Selecione o conjunto de dados",
                        options=op,
                        help="Escolha o conjunto de dados para a simulação"
                    )
            with col2:
                selected_option = st.selectbox(
                        label="Selecione o conjunto de treino",
                        options=list_train,
                        help="Escolha o conjunto de treino para a simulação"
                        )
        
            if st.button("Carregar"):
                try:
                    handle_existing_dataset(dataset_option)
                    load_model(selected_option)
                    st.info(f"Modelo de treinamento carregado!")
                    # st.write(st.session_state.filename)
                    # st.write(st.session_state.current_train)
                except Exception as e:
                    st.error(f"Erro ao carregar: {str(e)}")
                # params_simulate(dataset)
                return

if __name__ == "__main__":
# Início da página
    st.subheader("🔮 Predição de Rendimento de Bioetanol")
    bucket = st.session_state.get('bucket')
    
    model_select = UtilsModelsTrained.load_model_selector(bucket=bucket)
    
    if model_select != " ":
        model = model_select
    else:
        st.info("Nenhum modelo selecionado. Por favor, escolha um modelo para iniciar a simulação.")
        st.stop()
    
    try:
        prediction = PredictionPage(model, bucket=bucket)
        prediction.params_simulate()
        prediction.run_simulation()
        
    except Exception as e:
        st.error(f"Erro ao carregar modelo ou dados: {e}")
    
    # if st.toggle("Dados Personalizados", False, key="custom_data_toggle", 
                # help="Habilita a utilização de dados treinados pelo usuário"):
        # custom_data(list_train)
            
    # else:
    #     # Carrega o dataset padrão
    #     if 'current_dataset' not in st.session_state or st.session_state.current_dataset.empty:
    #         data.handle_existing_dataset(DEFAULT_DATA)
            
    # dataset = st.session_state.current_dataset 
    
    # with st.expander("🔍 Visualizar dados Carregados", expanded=False):
    #     st.write(dataset)
    

    # if st.session_state.submit_simulation:
    #     X_new = {
    #             # 'Biomass': st.session_state.selected_biomass,
    #             'C (%)': st.session_state.input_c,
    #             'H (%)': st.session_state.input_h,
    #             'L (%)': st.session_state.input_l,
    #             'Acid Conc (%)': st.session_state.acid,
    #             'S- Time (min)': st.session_state.time,
                # 'S- Temp (h)': st.session_state.temp,
            # }
        # run_simulation()
        # st.write(X_new)
        # simulate_results(trained_model, X_new)

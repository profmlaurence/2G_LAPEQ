import joblib
import os
import time
import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import altair as alt
import utils.BioethanolOptimizer as bioopt
from utils.bucket_connect import BucketUtils
import utils.utils_datas as data
from utils.utils_models_trained import UtilsModelsTrained

class SimulationPlots:
    """
    A class to encapsulate the simulation data and plotting logic.
    """
    
    def __init__(self, filepath, bucket=None):
        """Initialize the SimulationPlots class by loading the model and data from a file."""
        try:
            # Load the data from the specified file
            if bucket:
                training_data = BucketUtils.load_model_from_bucket(bucket, filepath)
            else:
                training_data = joblib.load("trained_models/"+filepath)

            # Extract the components
            self.model = training_data['model']
            self.model_name = training_data['model_name']
            self.columns_input = training_data['columns_input']
            self.columns_output = training_data['columns_output']
            self.dataset = training_data['dataset']
            self.filename = training_data['filename']

            st.success(f"Modelo '{self.model_name}' carregado com sucesso!")

            # return model, model_name, columns_input, columns_output

        except FileNotFoundError:
            st.error(f"Erro: O arquivo não foi encontrado em `{filepath}`.")
            return None, None, None, None
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar o modelo: {e}")
            return None, None, None, None
        
    def data_prepare(self, X_test=None, y_test=None, y_pred=None, model_name="Modelo"):
        """
        Initializes the simulation data.
        """
        try:
         # Obter predições se o modelo estiver carregado
            if hasattr(self, 'model') and self.model is not None:
                optimizer = bioopt.BioethanolOptimizer(self.dataset)
                X_train_scaled, X_test_scaled, y_train, y_test_actual = optimizer.preparation_data(self.columns_input, self.columns_output)
                
                if X_test_scaled is not None:
                    self.X_test = X_test_scaled
                    self.y_true = y_test_actual
                    self.y_pred = self.model.predict(X_test_scaled)
            # self.X_test = X_test
            # self.y_true = y_test
            # self.y_pred = y_pred
            # self.model_name = model_name
            
            # Fallback data if none provided (for testing layout)
            if self.y_true is None:
                self.size = 100
                self.y_true = np.random.choice([0, 1], size=self.size)
                self.y_pred = np.random.choice([0, 1], size=self.size)
                self.y_scores = np.random.rand(self.size)
                self.X_test = np.random.rand(self.size, 2)
            else:
                self.size = len(self.y_true)
                self.y_scores = self.y_pred
        except Exception as e:
            st.error(f"Erro ao preparar os dados para visualização: {e}")
            self.y_true = None
            self.y_pred = None
            self.X_test = None
            self.y_scores = None
    
    def plot_prediction_scatter(self):
        """
        Scatter plot of the simulation data (Real vs Predicted).
        """
        fig, ax = plt.subplots()
        ax.scatter(self.y_true, self.y_pred, alpha=0.5)

        # Add identity line
        min_val = min(np.min(self.y_true), np.min(self.y_pred))
        max_val = max(np.max(self.y_true), np.max(self.y_pred))
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)

        ax.set_xlabel('Valores Reais')
        ax.set_ylabel('Valores Previstos')
        ax.set_title(f'Gráfico de Dispersão - {self.model_name}')
        return fig  

    def plot_3d_surface(self):
        """
        Plots a 3D surface plot of the simulation data using Altair.
        """
        try:
            if self.X_test is None:
                st.warning("Dados X_test não disponíveis.")
                return

            # Ensure X_test is accessible as array
            X_vis = self.X_test.values if isinstance(self.X_test, pd.DataFrame) else self.X_test

            if X_vis.shape[1] < 2:
                st.warning("⚠️ Não há features suficientes para gráfico 3D.")
                return

            df_plot = pd.DataFrame(X_vis, columns=[f'Feature_{i+1}' for i in range(X_vis.shape[1])])
            
            # Flatten arrays
            y_t = self.y_true.values.flatten() if hasattr(self.y_true, 'values') else np.array(self.y_true).flatten()
            y_p = self.y_pred.flatten() if hasattr(self.y_pred, 'flatten') else np.array(self.y_pred).flatten()

            df_plot['Actual'] = y_t
            df_plot['Predicted'] = y_p

            feature_x = df_plot.columns[0]
            feature_y = df_plot.columns[1]

            chart = alt.Chart(df_plot).mark_circle(size=60).encode(
                x=feature_x,
                y=feature_y,
                color='Actual',
                tooltip=['Actual', 'Predicted']
            ).properties(
                title=f'Gráfico 3D - {self.model_name}'
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao gerar gráfico 3D: {e}")

    def plot_roc_curve(self):
        """
        Computes and plots the Receiver Operating Characteristic (ROC) curve.
        """
        try:
            # Check for binary classification
            if len(np.unique(self.y_true)) != 2:
                st.info("Curva ROC disponível apenas para classificação binária.")
                return None

            fpr, tpr, _ = roc_curve(self.y_true, self.y_scores)
            roc_auc = auc(fpr, tpr)

            fig, ax = plt.subplots()
            ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (área = {roc_auc:.2f})')
            ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            ax.set_xlim([0.0, 1.0])
            ax.set_ylim([0.0, 1.05])
            ax.set_xlabel('Taxa de Falsos Positivos')
            ax.set_ylabel('Taxa de Verdadeiros Positivos')
            ax.set_title('Receiver Operating Characteristic')
            ax.legend(loc="lower right")
            return fig
        except Exception as e:
            st.error(f"Erro ao gerar ROC: {e}")
            return None

    def plot_confusion_matrix(self):
        """
        Computes and plots the confusion matrix.
        """
        try:
            # Heuristic check for regression
            if len(np.unique(self.y_true)) > 20:
                st.info("Matriz de confusão não recomendada para regressão contínua.")
                return None

            cm = confusion_matrix(self.y_true, np.round(self.y_pred))
            fig, ax = plt.subplots()
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
            ax.set_xlabel('Valores Previstos')
            ax.set_ylabel('Valores Reais')
            ax.set_title('Matriz de Confusão')
            return fig
        except Exception as e:
            st.error(f"Erro ao gerar Matriz de Confusão: {e}")
            return None

    def run(self):

        """
        Runs the Streamlit application to display the plots in tabs.
        """
        st.header("Visualizações da Simulação")
        tab1, tab2, tab3, tab4 = st.tabs(["Dispersão", "Visualização 3D", "Curva ROC", "Matriz de Confusão"])

        with tab1:
            st.subheader("Gráfico de Dispersão (Real vs Previsto)")
            fig_scatter = self.plot_prediction_scatter()
            st.pyplot(fig_scatter)

        with tab2:
            st.subheader("Visualização 3D")
            self.plot_3d_surface()

        with tab3:
            st.subheader("Outras métricas")
            

if __name__ == "__main__":
    # filename = st.session_state.current_dataset 
    bucket = st.session_state.get("bucket")

    # utils_models = UtilsModelsTrained(bucket)
    modelo_select = UtilsModelsTrained.load_model_selector(bucket=bucket)

    if modelo_select != " ":
        try:
            simulation = SimulationPlots(modelo_select, bucket=bucket)
            simulation.data_prepare(model_name=simulation.model_name)
            
            
            # Run the simulation plots
            simulation.run()
        except Exception as e:
            st.error(f"Erro ao carregar modelo ou dados: {e}")
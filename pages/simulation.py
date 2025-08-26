import streamlit as st
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import utils.BioethanolOptimizer as bioopt
import utils.utils_datas as data

class SimulationPlots:
    """
    A class to encapsulate the simulation data and plotting logic for ROC and confusion matrix.
    """
    # modelo_select = None
    
    def __init__(self, size=100):
        """
        Initializes the simulation data.
        """
        self.size = size
        self.y_true = np.random.choice([0, 1], size=self.size)
        self.y_pred = np.random.choice([0, 1], size=self.size)
        self.y_scores = np.random.rand(self.size)

    def plot_roc_curve(self):
        """
        Computes and plots the Receiver Operating Characteristic (ROC) curve.
        """
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

    def plot_confusion_matrix(self):
        """
        Computes and plots the confusion matrix.
        """
        cm = confusion_matrix(self.y_true, self.y_pred)
        fig, ax = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
        ax.set_xlabel('Valores Previstos')
        ax.set_ylabel('Valores Reais')
        ax.set_title('Matriz de Confusão')
        return fig

    def plot_scatter(self):
        """
        Plots a scatter plot of true values against scores.
        """
        fig, ax = plt.subplots()
        ax.scatter(self.y_true, self.y_scores, alpha=0.5)
        ax.set_xlabel('Valores Reais')
        ax.set_ylabel('Scores de Predição')
        ax.set_title('Gráfico de Dispersão')
        return fig

    def run(self):
        """
        Runs the Streamlit application to display the plots in tabs.
        """
        st.header("Visualizações da Simulação")
        tab1, tab2, tab3 = st.tabs(["Curva ROC", "Matriz de Confusão", "Gráfico de Dispersão"])

        with tab1:
            st.subheader("Curva ROC")
            fig_roc = self.plot_roc_curve()
            st.pyplot(fig_roc)

        with tab2:
            st.subheader("Matriz de Confusão")
            fig_cm = self.plot_confusion_matrix()
            st.pyplot(fig_cm)

        with tab3:
            st.subheader("Gráfico de Dispersão")
            fig_scatter = self.plot_scatter()
            st.pyplot(fig_scatter)

if __name__ == "__main__":
    simulation = SimulationPlots()
    optimizer = bioopt.BioethanolOptimizer(st.session_state.filename)

    modelo_select = st.selectbox("Selecione o modelo treinado", [" "] +data.list_files("trained_models"),index=0)
    
    if modelo_select != " ":
        model, model_name, columns_input, columns_output = optimizer.load_model(modelo_select)
        
        simulation.run()
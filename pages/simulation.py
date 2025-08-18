import streamlit as st
import numpy as np
import seaborn as sns
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc

import matplotlib.pyplot as plt

# Simulate data
y_true = np.random.choice([0, 1], size=100)
y_pred = np.random.choice([0, 1], size=100)

# Compute confusion matrix
y_scores = np.random.rand(100)

# Create tabs for the plots
tab1, tab2 = st.tabs(["Curva ROC", "Matriz de Confusão"])

with tab1:
    # Compute ROC curve and ROC area
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    # Plot ROC curve
    st.header("Receiver Operating Characteristic (ROC) Curve")
    fig_roc, ax_roc = plt.subplots()
    ax_roc.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (área = {roc_auc:.2f})')
    ax_roc.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    ax_roc.set_xlim([0.0, 1.0])
    ax_roc.set_ylim([0.0, 1.05])
    ax_roc.set_xlabel('Taxa de Falsos Positivos')
    ax_roc.set_ylabel('Taxa de Verdadeiros Positivos')
    ax_roc.set_title('Receiver Operating Characteristic')
    ax_roc.legend(loc="lower right")
    st.pyplot(fig_roc)

with tab2:
    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Plot confusion matrix
    st.header("Matriz de Confusão")
    fig_cm, ax_cm = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax_cm)
    ax_cm.set_xlabel('Valores Previstos')
    ax_cm.set_ylabel('Valores Reais')
    ax_cm.set_title('Matriz de Confusão')
    st.pyplot(fig_cm)
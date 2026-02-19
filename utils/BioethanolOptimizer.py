from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
import streamlit as st
import pandas as pd
import numpy as np
import scipy.stats as stats
import altair as alt
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_squared_error,r2_score
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from config import DATASET_DIR
import joblib
import os

class BioethanolOptimizer:
    def __init__(self, dataset):
        if 'current_dataset' in st.session_state:
            self.df = st.session_state.current_dataset
        else:
            self.df = pd.read_csv(DATASET_DIR  /dataset)
            st.session_state.current_dataset = self.df
        # self.df = dataset
        self.models = {
            "SVM (Vinitha23)": SVR(),
            "Rede Neural": MLPRegressor(),
            "Modelo Proposto (Freitas, Gramacho, Guarda, 2024)": MLPRegressor(hidden_layer_sizes=(30, 30), max_iter=100000, random_state=42),
            "Random Forest": RandomForestRegressor(random_state=42),
            "Regressão Linear":  LinearRegression(),
            "Deep Learning": "Deep Learning",
            "My model": "My model"
            
        }

    def preparation_data(self, columns_input, columns_output):
        
        try:
            df_cleaned = self.df.copy()
            
            # Verifica se as colunas de entrada existem no dataset atual
            missing_cols = [col for col in columns_input if col not in df_cleaned.columns]
            if missing_cols:
                st.error(f"Erro de Compatibilidade: O modelo espera as colunas {missing_cols}, mas elas não estão no dataset atual.")
                return None, None, None, None

            missing_out = [col for col in columns_output if col not in df_cleaned.columns]
            if missing_out:
                st.error(f"Erro de Compatibilidade: As colunas de saída {missing_out} não estão no dataset atual.")
                return None, None, None, None

            X = df_cleaned[columns_input]
            Y = df_cleaned[columns_output]

            string_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
            X = X.drop(columns=string_cols)
            
            # st.write(X)
            X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            return X_train_scaled, X_test_scaled, y_train, y_test
        except Exception as e:
            st.error(f"Erro na preparação dos dados: {e}")
            return None, None, None, None
        
    def best_params(self, model_name, X_train, y_train):
        
        return None
    
    def best_model(self, model_name, X_train, y_train):
                
        return None
    
    def fit_model_optimized(self, model_name, columns_input, columns_output):
        try:
            param_grid = {}
            X_train, X_test, y_train, y_test = self.preparation_data(columns_input, columns_output)
            model = self.models[model_name]
        
            if model_name == 'SVM (Vinitha23)':
                param_grid = {
                    'kernel': ['linear', 'rbf'],
                    'C': [0.1, 1, 10, 50],
                    'epsilon': [0.1, 0.2, 0.3]
                }
            elif model_name == 'Rede Neural':
                # param_grid = {
                #     'hidden_layer_sizes': [(50,50), (100,100)],
                #     'activation': ['tanh', 'relu'],
                #     'alpha': [0.0001, 0.05]
                # }
                pass
            elif model_name == 'Random Forest':
                param_grid = {
                    'n_estimators': [100, 200],
                    'max_depth': [None, 10],
                    'min_samples_split': [2, 5]
                }
            elif model_name == 'Regressão Linear':
                param_grid = {
                    'fit_intercept': [True, False],
                    'copy_X': [True, False]
                }
            
            if param_grid:
                grid = GridSearchCV(
                    estimator=model,
                    param_grid=param_grid,
                    cv=5,
                    scoring='r2',
                    n_jobs=-1
                )
                
                st.write(f"🔍 Otimizando hiperparâmetros para {param_grid}...")
                grid.fit(X_train, y_train)
                
                # Usa o melhor modelo encontrado
                best_model = grid.best_estimator_
                st.success(f"Melhores parâmetros: {grid.best_params_}")
            else:
                best_model = model
                best_model.fit(X_train, y_train)
                
                # Previsões e métricas
                y_pred = best_model.predict(X_test)
                r2 = r2_score(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                quadratic_error = mse ** 0.5

                # Exibe resultados
                st.success(f"Modelo treinado com sucesso! {model}🎯")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("R² Score", f"{r2:.4f}")
                with col2:
                    st.metric("MSE", f"{mse:.4f}")
                with col3:
                    st.metric("RMSE", f"{quadratic_error:.4f}")
        except Exception as e:
            st.error(f"Erro ao treinar o modelo: {e}")
            
        return 0.0,0.0,0.0,None,None

    def fit_model(self, model_name, columns_input, columns_output):
        
        if model_name == 'Deep Learning':
            st.warning("⚠️Modelo em construção...")
            return 0.0,0.0,0.0,None,None
        elif model_name == 'My model':

            X_train, X_test, y_train, y_test = self.preparation_data(columns_input, columns_output)

            # Normalizar os dados
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # 1. Redução de dimensionalidade com PCA
            pca = PCA(n_components=0.95) # Manter 95% da variância
            X_train_pca = pca.fit_transform(X_train_scaled)
            X_test_pca = pca.transform(X_test_scaled)

            # 2. Treinamento de uma Rede Neural Artificial (ANN) sobre os componentes principais
            mlp_pca = MLPRegressor(hidden_layer_sizes=(100, 100), max_iter=2000, random_state=42)
            mlp_pca.fit(X_train_pca, y_train) # Treinando para glicose como exemplo

            # Obter as saídas da ANN para usar como entrada para o SVM
            X_train_ann_output = mlp_pca.predict(X_train_pca).reshape(-1, 1)
            X_test_ann_output = mlp_pca.predict(X_test_pca).reshape(-1, 1)


            # 3. Aplicação de uma Máquina de Vetores de Suporte (SVM) sobre as saídas da ANN
            svr_ann = SVR(kernel='rbf', C=1.0, epsilon=0.1) # Exemplo de parâmetros
            svr_ann.fit(X_train_ann_output, y_train) # Treinando o SVM com as saídas da ANN

            # Previsões combinadas (ANN + SVM)
            y_pred_combined_glucose = svr_ann.predict(X_test_ann_output)

            # Avaliar o modelo combinado
            mse = mean_squared_error(y_test, y_pred_combined_glucose)
            r2 = r2_score(y_test, y_pred_combined_glucose)

            print("MSE Combined (Glucose):", mse)
            print("R2 Combined (Glucose):", r2)
        
            return r2, mse, mse**0.5, None, None
        
        try:
            X_train, X_test, y_train, y_test = self.preparation_data(columns_input, columns_output)
            
            model = self.models[model_name]

            st.write(f"Treinando o modelo {model_name}...")
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            r2 = r2_score(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            quadratic_error = mse ** 0.5
            params = model.get_params()
            st.success("Modelo treinado com sucesso! 🎯")

            return r2, mse, quadratic_error, params, model
            # return None, None, None, None, None
            
        except Exception as e:
            st.error(f"Erro ao treinar o modelo (fit_model): {e}")
        
        # self.graficos(model_name, model, X_test, y_test, y_pred)

        return None, None, None, None, None
        
    def simulate_mode(self,model,columns_input,columns_output):
        
        X_train, X_test, y_train, y_test = self.preparation_data(columns_input, columns_output)

        y_pred = model.predict(X_test)

        cm = confusion_matrix(y_train, y_pred)

        st.write("y_test:", y_test)
        st.write("y_pred:", y_pred)
        
        # Calcula a matriz de confusão
        confusion_matrix = pd.crosstab(y_test.values.flatten(), y_pred.flatten(), rownames=['Actual'], colnames=['Predicted'], margins=True)
        st.write("Matriz de Confusão:")
        st.write(confusion_matrix)

        pass

    def save_model(self, filename, model, model_name, columns_input, columns_output, dataset):
        """Saves the trained model and its metadata to a serialized file on disk."""

        try:
            # Directory to save models
            save_dir = "trained_models"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            # Data to be saved
            training_data = {
                'model': model,
                'model_name': model_name,
                'columns_input': columns_input,
                'columns_output': columns_output,
                'dataset': dataset,
                'filename': filename,
            }

            # Sanitize model_name for use as a filename
            safe_filename = filename + "_" + "".join(x for x in model_name if x.isalnum() or x in "._- ").replace(" ", "_")
            filepath = os.path.join(save_dir, f"{safe_filename}.joblib")

            # Serialize and save the data to disk
            joblib.dump(training_data, filepath)

            st.success(f"Modelo '{model_name}' salvo com sucesso em: `{filepath}`")

        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o modelo: {e}")
    
    def graf_3d_curve(self, model_name, X_test, y_test, y_pred):
        try:
            df_plot = pd.DataFrame(X_test, columns=[f'Feature_{i+1}' for i in range(X_test.shape[1])])
            df_plot['Actual'] = y_test
            df_plot['Predicted'] = y_pred

            if X_test.shape[1] < 2:
                st.warning("⚠️ Não há features suficientes para gráfico 3D.")
                return

            feature_x = df_plot.columns[0]
            feature_y = df_plot.columns[1]

            chart = alt.Chart(df_plot).mark_circle(size=60).encode(
                x=feature_x,
                y=feature_y,
                color='Actual',
                tooltip=['Actual', 'Predicted']
            ).properties(
                title=f'Gráfico 3D - {model_name}'
            ).interactive()

            st.altair_chart(chart, use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao gerar gráfico 3D: {e}")
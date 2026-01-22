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
            "Deep Learning": "Deep Learning"
            
        }

    def preparation_data(self, columns_input, columns_output):
        
        df_cleaned = self.df.copy()
        
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
                
                st.write(f"🔍 Otimizando hiperparâmetros para 111 {param_grid}...")
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

    def save_model(self, filename, model, model_name, columns_input, columns_output):
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
            }

            # Sanitize model_name for use as a filename
            safe_filename = filename + "_" + "".join(x for x in model_name if x.isalnum() or x in "._- ").replace(" ", "_")
            filepath = os.path.join(save_dir, f"{safe_filename}.joblib")

            # Serialize and save the data to disk
            joblib.dump(training_data, filepath)

            st.success(f"Modelo '{model_name}' salvo com sucesso em: `{filepath}`")

        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar o modelo: {e}")
    
    def load_model(self, filepath):
        """Loads a trained model and its metadata from a serialized file."""
        try:
            # Load the data from the specified file
            training_data = joblib.load("trained_models/"+filepath)

            # Extract the components
            model = training_data['model']
            model_name = training_data['model_name']
            columns_input = training_data['columns_input']
            columns_output = training_data['columns_output']

            st.success(f"Modelo '{model_name}' carregado com sucesso de: `{filepath}`")

            return model, model_name, columns_input, columns_output

        except FileNotFoundError:
            st.error(f"Erro: O arquivo não foi encontrado em `{filepath}`.")
            return None, None, None, None
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar o modelo: {e}")
            return None, None, None, None
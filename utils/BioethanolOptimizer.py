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
# import matplotlib.pyplot as plt
# import seaborn as sns

class BioethanolOptimizer:
    def __init__(self, dataset):
        # self.df = pd.read_csv(data_path)
        self.df = dataset
        self.models = {
            "SVM (Vinitha23)": SVR(),
            "Rede Neural": MLPRegressor(),
            "Modelo Proposto (Freitas, Gramacho, Guarda, 2024)": MLPRegressor(hidden_layer_sizes=(30, 30), max_iter=1000, random_state=42),
            "Random Forest": RandomForestRegressor(random_state=42),
            "Regressão Linear":  LinearRegression(),
            "Deep Learning": "Deep Learning"
            
        }

    def preparation_data(self, columns_input, columns_output):
        df_cleaned = self.df.copy()
        # st.write("Colunas do DataFrame:", df_cleaned.columns.tolist())
        # X = df_cleaned[['C (%)', 'H \n(%)', 'L (%)', 'Acid Conc\n(%)', 'S- Time (min)', 'S- Temp (ᵒC)', 'F- Time (h)', 'F-Temp (ᵒC)']]
        # y_glucose = df_cleaned['Glucose (g/L)']
        # X_train, X_test, y_train, y_test = train_test_split(X, y_glucose, test_size=0.2, random_state=42)
        
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
            return 0.0,0.0,0.0,None
        try:
            X_train, X_test, y_train, y_test = self.preparation_data(columns_input, columns_output)
            model = self.models[model_name]

            print(model)


            # st.write(f"Treinando o modelo {model_name}...")
            # model.fit(X_train, y_train)
            
            # y_pred = model.predict(X_test)
            # r2 = r2_score(y_test, y_pred)
            # mse = mean_squared_error(y_test, y_pred)
            # quadratic_error = mse ** 0.5
            # params = model.get_params()
            # # st.success("Modelo treinado com sucesso! 🎯")

            # return r2, mse, quadratic_error, params, model
            return None, None, None, None, None
            
        except Exception as e:
            st.error(f"Erro ao treinar o modelo: {e}")
            # return 0.0,0.0,0.0,None
        
        # self.graficos(model_name, model, X_test, y_test, y_pred)

        return 0.0,0.0,0.0,None
    
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

    def save_model(self,model, model_name, columns_input, columns_output):
        st.session_state['model_training'] = model
        st.session_state['model_name'] = model_name
        st.session_state['columns_input'] = columns_input
        st.session_state['columns_output'] = columns_output
        # st.session_state['BioethanolOptimizer'] = self.bioethanol_optimizer
        # st.session_state['current_name_dataset'] = self.df.name
        pass
import streamlit as st
# import pages.data as dt
from utils.utils_datas import handle_existing_dataset

DATASET_DIR = 'dataset'
DEFAULT_DATA = 'dados_salvos.csv'

col1, col2, col3, col4 = st.columns([1,2,2,1])

def verified_dataset():
    if 'current_dataset' not in st.session_state:
        handle_existing_dataset(DEFAULT_DATA)
    
    if 'current_dataset' in st.session_state:
        print(st.session_state.filename)
    
def main():
    verified_dataset()
    
    if col2.button("Treinar um novo modelo", key="new_model"):
        st.session_state.menu = True
        st.divider()
        # dt.select_dataset()
        # dt.show_data_interface()
        st.switch_page("pages/data.py")


    if col3.button("Fazer Predições", key="predict_model"):
        st.session_state.menu = False
        st.switch_page("pages/prediction.py")
    


if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("f1_1950s_race_results.csv")
    df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date"])

races_df = load_data()

# Título de la app
st.title("Grand Prix de los años 50 en tu cumpleaños 🎉")

# Input del usuario
birth_input = st.date_input("Selecciona tu fecha de cumpleaños (ignora el año):", value=datetime(1955, 7, 2))

# Buscar carreras en el mismo día y mes
birth_day = birth_input.day
birth_month = birth_input.month

matching_races = races_df[(races_df["Date"].dt.day == birth_day) & (races_df["Date"].dt.month == birth_month)]

if not matching_races.empty:
    st.success("¡Sí hubo Grand Prix en tu cumpleaños!")
    st.dataframe(matching_races[["Year", "Grand Prix", "Winner", "Team"]].sort_values("Year"))
else:
    st.warning("No hubo ningún Grand Prix en ese día durante los años 50 😢")

# Mostrar tabla completa opcionalmente
with st.expander("Ver todos los resultados de los 50s"):
    st.dataframe(races_df)

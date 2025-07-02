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
st.title("Los Grand Prix de los años 50")

# Input del usuario
col1, col2 = st.columns(2)

birth_day = col1.selectbox("Día", list(range(1, 32)), index=1)
birth_month = col2.selectbox("Mes", [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
], index=6)

# Convertir el mes a número
month_number = list(range(1, 13))[["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"].index(birth_month)]

# Buscar carreras en el mismo día y mes
birth_day = birth_input.day
birth_month = birth_input.month

matching_races = races_df[
    (races_df["Date"].dt.day == birth_day) &
    (races_df["Date"].dt.month == month_number)
]

if not matching_races.empty:
    st.success("¡Sí hubo Grand Prix en tu cumpleaños!")
    st.dataframe(matching_races[["Year", "Grand Prix", "Winner", "Team"]].sort_values("Year"))
else:
    st.warning("No hubo ningún Grand Prix en ese día durante los años 50 😢")

# Mostrar tabla completa opcionalmente
with st.expander("Ver todos los resultados de los 50s"):
    st.dataframe(races_df)

import streamlit as st
import pandas as pd
from datetime import datetime

# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("f1_1950s_race_results.csv")  # Asegúrate que el nombre coincida
    df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date"])

races_df = load_data()

# Título de la app
st.title("🏁 Grand Prix de los años 50")

# Input del usuario (día y mes, sin año)
st.subheader("¿Hubo una carrera de F1 en tu cumpleaños durante los años 50?")

col1, col2 = st.columns(2)

birth_day = col1.selectbox("Día", list(range(1, 32)), index=1)
birth_month_name = col2.selectbox("Mes", [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
], index=6)

# Convertir nombre del mes a número
month_number = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
].index(birth_month_name) + 1

# Buscar carreras en el mismo día y mes
matching_races = races_df[
    (races_df["Date"].dt.day == birth_day) &
    (races_df["Date"].dt.month == month_number)
]

# Mostrar resultados
if not matching_races.empty:
    st.success("🎉 ¡Sí hubo Grand Prix en tu cumpleaños!")
    st.dataframe(matching_races[["Year", "Grand Prix", "Date", "Winner", "Team"]].sort_values("Year"))
else:
    st.warning("😢 No hubo ningún Grand Prix en ese día durante los años 50.")

#Tabla
with st.expander("📋 Ver todos los resultados de los 50s"):
    st.dataframe(races_df, use_container_width=True, height=600)



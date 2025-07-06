import streamlit as st
import pandas as pd
from datetime import datetime
import time  # 👈 Importar para usar sleep

# 🚗 Animación de auto F1 antes de mostrar el contenido
car_animation = """
<div style="position:relative; height:80px; overflow:hidden;">
    <div style="
        position:absolute;
        left:-200px;
        top:20px;
        animation: drive 3s linear forwards;
        font-size: 40px;">
        🏎️💨
    </div>
</div>

<style>
@keyframes drive {
    0% { left: -200px; }
    100% { left: 100%; }
}
</style>
"""
st.markdown(car_animation, unsafe_allow_html=True)
time.sleep(3.2)  # Esperar que termine la animación

# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("F1_1950s_Race_Results_FULL.csv")
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date_Parsed"])

races_df = load_data()

# Título de la app
st.title("🏁 Grand Prix de los años 50")

# Input del usuario (día y mes)
st.subheader("¿Hubo una carrera de F1 en tu cumpleaños durante los años 50?")

col1, col2 = st.columns(2)
birth_day = col1.selectbox("Día", list(range(1, 32)), index=1)
birth_month_name = col2.selectbox("Mes", [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
], index=6)

# Convertir mes a número
month_number = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
].index(birth_month_name) + 1

# Filtrar carreras que coincidan con día y mes
matching_races = races_df[
    (races_df["Date_Parsed"].dt.day == birth_day) &
    (races_df["Date_Parsed"].dt.month == month_number)
]

# Mostrar resultados
if not matching_races.empty:
    st.success("🎉 ¡Sí hubo Grand Prix en tu cumpleaños!")
    st.dataframe(matching_races[["Year", "Grand Prix", "Date", "Winner", "Team"]].sort_values("Year"))
else:
    st.warning("😢 No hubo ningún Grand Prix en ese día durante los años 50.")

# Ver todos los resultados
with st.expander("📋 Ver todos los resultados de los 50s"):
    st.dataframe(races_df[["Year", "Grand Prix", "Date", "Winner", "Team"]], use_container_width=True, height=600)


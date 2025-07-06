import streamlit as st
import pandas as pd
from datetime import datetime
import time  # 👈 Importar para usar sleep

# 🚗 Animación de auto F1 antes de mostrar el contenido
car_animation = """
<div style="position:relative; height:160px; overflow:hidden;">
    <div style="
        position:absolute;
        right:-500px;
        top:20px;
        animation: drive 3s linear forwards;
        font-size: 120px;">
        🏎️💨
    </div>
</div>

<style>
@keyframes drive {
    0% { right: -500px; }
    100% { right: 100%; }
}
</style>
"""
st.markdown(car_animation, unsafe_allow_html=True)
time.sleep(4.2)



# Cargar los datos
@st.cache_data
def load_data():
    df = pd.read_csv("F1_1950s_Race_Results_FULL.csv")
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date_Parsed"])

races_df = load_data()

# Título de la app
st.title("🏁 La fórmula de los 50s")

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
    
gp_name = gp_translation.get(closest_race["Grand Prix"], f"el GP de {closest_race['Grand Prix']}")

st.subheader("🏁 Carrera más cercana a tu cumpleaños:")
st.info(f"""
{gp_name} en {closest_race['Date']} fue la carrera más cercana a tu cumple.
Ganó **{closest_race['Winner']}** con **{closest_race['Team']}**.
""")

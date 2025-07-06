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
races_df = load_data()

# ✅ Diccionario de traducción de Grand Prix
gp_translation = {
    "British": "el GP de Gran Bretaña",
    "French": "el GP de Francia",
    "Italian": "el GP de Italia",
    "German": "el GP de Alemania",
    "Monaco": "el GP de Mónaco",
    "Belgian": "el GP de Bélgica",
    "Dutch": "el GP de los Países Bajos",
    "Swiss": "el GP de Suiza",
    "Argentine": "el GP de Argentina",
    "Indianapolis 500": "las 500 Millas de Indianápolis",
    "Spanish": "el GP de España",
    "Portuguese": "el GP de Portugal",
    "Moroccan": "el GP de Marruecos",
    # Agrega más si los ves en tu CSV
}

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
    
# 🏁 ¿Cuál fue la carrera más cercana a tu cumpleaños?

# Fecha del usuario sin año
birth_date_str = f"{birth_day:02d}-{month_number:02d}"

# Calcular diferencia con cada carrera
races_df["Birthday_Diff"] = races_df["Date_Parsed"].dt.strftime("%d-%m").apply(
    lambda x: abs(datetime.strptime(x, "%d-%m") - datetime.strptime(birth_date_str, "%d-%m")).days
)

# Carrera más cercana
closest_race = races_df.sort_values("Birthday_Diff").iloc[0]

# Traducción del nombre del GP
gp_name = gp_translation.get(closest_race["Grand Prix"], f"el GP de {closest_race['Grand Prix']}")

# ✅ Formatear fecha en español
fecha = closest_race["Date_Parsed"]
month_translation = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}
fecha_formateada = f"{fecha.day} de {month_translation[fecha.month]} de {fecha.year}"

# Frase final
texto = f"{gp_name} en {fecha_formateada} fue la carrera más cercana a tu cumple."
texto = texto[0].upper() + texto[1:]

# Mostrar resultado
st.subheader("📅 Carrera más cercana a tu cumpleaños:")
st.info(f"""
{texto}
Ganó **{closest_race['Winner']}** con **{closest_race['Team']}**.
""")
# 📜 ¿Cuál fue el primer GP de los años 50?

# Buscar la primera carrera por fecha
first_race = races_df.sort_values("Date_Parsed").iloc[0]

# Traducir nombre del Grand Prix
gp_name = gp_translation.get(first_race["Grand Prix"], f"el GP de {first_race['Grand Prix']}")

# Traducir la fecha al español
fecha = first_race["Date_Parsed"]
month_translation = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}
fecha_formateada = f"{fecha.day} de {month_translation[fecha.month]} de {fecha.year}"

# Armar texto final con capitalización
texto = f"{gp_name} abrió la década el {fecha_formateada}."
texto = texto[0].upper() + texto[1:]

# Mostrar resultado
st.subheader("📜 Primer GP de los años 50:")
st.info(f"""
{texto}
Ganó **{first_race['Winner']}** con **{first_race['Team']}**.
""")


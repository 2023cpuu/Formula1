import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import time
from datetime import datetime

# ANIMACIÓN AUTO F1
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

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="GPs de los años 50", page_icon="🏁")
st.title("🏁 Grand Prix de los años 50")

# CARGA DE DATOS
@st.cache_data
def load_data():
    df = pd.read_csv("F1_1950s_Race_Results_FULL.csv")
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date_Parsed"])

races_df = load_data()

# DICCIONARIOS
gp_to_country = {
    "British": "Reino Unido", "French": "Francia", "Italian": "Italia", "German": "Alemania",
    "Monaco": "Mónaco", "Belgian": "Bélgica", "Dutch": "Países Bajos", "Swiss": "Suiza",
    "Argentine": "Argentina", "Indianapolis 500": "Estados Unidos", "Spanish": "España",
    "Portuguese": "Portugal", "Moroccan": "Marruecos"
}

gp_to_circuits = {
    "Argentine": ["Autódromo Juan y Oscar Gálvez"],
    "Belgian": ["Spa-Francorchamps"],
    "British": ["Silverstone", "Aintree"],
    "Dutch": ["Zandvoort"],
    "French": ["Reims-Gueux", "Rouen-Les-Essarts"],
    "German": ["Nürburgring", "AVUS"],
    "Indianapolis 500": ["Indianapolis Motor Speedway"],
    "Italian": ["Autodromo Nazionale Monza"],
    "Monaco": ["Circuit de Monaco"],
    "Moroccan": ["Ain-Diab Circuit"],
    "Portuguese": ["Boavista", "Monsanto Park"],
    "Spanish": ["Pedralbes"],
    "Swiss": ["Bremgarten"]
}

month_translation = {
    "Jan": "Enero", "Feb": "Febrero", "Mar": "Marzo", "Apr": "Abril", "May": "Mayo", "Jun": "Junio",
    "Jul": "Julio", "Aug": "Agosto", "Sep": "Septiembre", "Oct": "Octubre", "Nov": "Noviembre", "Dec": "Diciembre"
}

country_coords = {
    "Reino Unido": [51.5, -0.1], "Francia": [48.85, 2.35], "Italia": [41.9, 12.5],
    "Alemania": [52.52, 13.4], "Mónaco": [43.73, 7.42], "Bélgica": [50.85, 4.35],
    "Países Bajos": [52.37, 4.89], "Suiza": [46.95, 7.45], "Argentina": [-34.6, -58.38],
    "Estados Unidos": [39.8, -86.1], "España": [40.42, -3.7], "Portugal": [38.72, -9.14],
    "Marruecos": [33.58, -7.62]
}

races_df["País"] = races_df["Grand Prix"].map(gp_to_country)

# ¿HUBO GP EN TU CUMPLE?
st.subheader("🎂 ¿Hubo una carrera de F1 en tu cumpleaños durante los años 50?")
col1, col2 = st.columns(2)
birth_day = col1.selectbox("Día", [""] + list(range(1, 32)))
birth_month_name = col2.selectbox("Mes", [""] + list(month_translation.values()))

if birth_day and birth_month_name:
    month_number = list(month_translation.values()).index(birth_month_name)
    matching_races = races_df[
        (races_df["Date_Parsed"].dt.day == int(birth_day)) &
        (races_df["Date_Parsed"].dt.month == month_number + 1)
    ]
    if not matching_races.empty:
        st.success("🎉 ¡Sí hubo Grand Prix en tu cumpleaños!")
        df = matching_races[["Year", "Grand Prix", "Date", "Winner", "Team"]].sort_values("Year").reset_index(drop=True)
        df.index += 1
        st.table(df)
    else:
        st.warning("😢 No hubo ningún Grand Prix en ese día durante los años 50.")
        # Carrera más cercana
        st.subheader("📅 Carrera más cercana a tu cumpleaños")
        ref_date = datetime(1955, month_number + 1, int(birth_day))
        races_df["Diff"] = races_df["Date_Parsed"].apply(lambda x: abs((x - ref_date).days))
        closest_race = races_df.loc[races_df["Diff"].idxmin()]
        fecha_gp = closest_race["Date_Parsed"]
        mes_es = month_translation[fecha_gp.strftime("%b")]
        fecha_str = f"{fecha_gp.day} {mes_es} {fecha_gp.year}"
        gp_name = gp_to_country.get(closest_race["Grand Prix"], closest_race["Grand Prix"])
        mensaje_cercano = f"El GP de {gp_name} en {fecha_str} fue la carrera más cercana a tu cumple. Ganó {closest_race['Winner']} con {closest_race['Team']}."
        st.info(mensaje_cercano[0].upper() + mensaje_cercano[1:])

# PILOTO TOP 5
st.subheader("🏆 Piloto con más victorias en los 50s")
top5 = races_df["Winner"].value_counts().head(5).reset_index()
top5.index += 1
top5.columns = ["Piloto", "Victorias"]
st.table(top5)

# ESCUDERÍA TOP 5
st.subheader("🔧 Escudería más dominante de los 50s")
top_teams = races_df["Team"].value_counts().head(5).reset_index()
top_teams.index += 1
top_teams.columns = ["Escudería", "Victorias"]
st.table(top_teams)

# PAÍSES TOP
st.subheader("🌍 País con más carreras en los 50s")
country_counts = races_df["País"].value_counts()
top_count = country_counts.max()
top_countries = country_counts[country_counts == top_count].index.tolist()
if len(top_countries) == 1:
    texto = f"{top_countries[0]} fue el país con más Grandes Premios: {top_count} en total."
else:
    if len(top_countries) == 2:
        conj = "e" if top_countries[1].lower().startswith("i") else "y"
        texto = f"{top_countries[0]} {conj} {top_countries[1]} fueron los países con más Grandes Premios: {top_count} cada uno."
    else:
        texto = ", ".join(top_countries[:-1]) + f" y {top_countries[-1]} fueron los países con más Grandes Premios: {top_count} cada uno."
st.success(texto[0].upper() + texto[1:])

with st.expander("📊 Ver el top 5 de países con más carreras"):
    top5_paises = country_counts.head(5).reset_index()
    top5_paises.index += 1
    top5_paises.columns = ["País", "Cantidad de carreras"]
    st.table(top5_paises)

# MAPA INTERACTIVO
st.subheader("🗺️ Mapa de países con carreras en los años 50")
map_data = [{"País": c, "Lat": lat, "Lon": lon, "Carreras": country_counts[c]}
            for c, (lat, lon) in country_coords.items() if c in country_counts]
map_df = pd.DataFrame(map_data)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position="[Lon, Lat]",
    get_radius="Carreras * 50000",
    get_fill_color="[200, 30, 0, 160]",
    pickable=True
)
view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state,
                         tooltip={"text": "{País}: {Carreras} carreras"}))
# CIRCUITOS POR PAÍS
with st.expander("🏟️ Ver los circuitos usados en cada país"):
    circuitos_por_pais = {}
    for gp, pais in gp_to_country.items():
        if gp in gp_to_circuits:
            circuitos_por_pais.setdefault(pais, set()).update(gp_to_circuits[gp])
    for pais, circuitos in circuitos_por_pais.items():
        st.markdown(f"**{pais}**: {', '.join(sorted(circuitos))}")
    st.caption("📝 *Nota: Se muestran todos los circuitos usados por país en los años 50.*")

# 🔍 Explora pilotos y escuderías
st.subheader("🔍 Explora pilotos y escuderías")

# PILOTOS
pilotos_unicos = sorted(races_df["Winner"].dropna().unique())
piloto_seleccionado = st.selectbox("Selecciona un piloto", pilotos_unicos, index=None, placeholder="Elige un piloto...")

if piloto_seleccionado:
    piloto_df = races_df[races_df["Winner"] == piloto_seleccionado]
    if not piloto_df.empty:
        piloto_top = piloto_df["Team"].value_counts().reset_index()
        piloto_top.index += 1
        piloto_top.columns = ["Escudería", "Victorias"]
        st.table(piloto_top)

# ESCUDERÍAS
equipos_unicos = sorted(races_df["Team"].dropna().unique())
equipo_seleccionado = st.selectbox("Selecciona una escudería", equipos_unicos, index=None, placeholder="Elige una escudería...")

if equipo_seleccionado:
    team_df = races_df[races_df["Team"] == equipo_seleccionado]
    if not team_df.empty:
        team_top = team_df["Winner"].value_counts().reset_index()
        team_top.index += 1
        team_top.columns = ["Piloto", "Victorias"]
        st.table(team_top)


# PILOTOS QUE CORRIERON PARA MÁS DE UNA ESCUDERÍA
st.subheader("👨‍🔧 Pilotos que corrieron para más de una escudería")

multi_team_df = races_df.groupby(["Winner", "Team"]).size().reset_index().groupby("Winner").size()
pilotos_varios_equipos = multi_team_df[multi_team_df > 1].index.tolist()

for piloto in pilotos_varios_equipos:
    equipos = races_df[races_df["Winner"] == piloto]["Team"].dropna().unique()
    equipos = [e for e in equipos if e.strip() != ""]
    if len(equipos) > 1:
        st.markdown(f"- **{piloto}** corrió para: {', '.join(sorted(equipos))}")

# PILOTOS CON MÚLTIPLES VICTORIAS EN UN MISMO CIRCUITO
st.subheader("🏟️ Pilotos que ganaron varias veces en un mismo circuito")

# Suponiendo que Grand Prix + país → circuito
circuito_df = races_df.copy()
circuito_df["Circuito"] = circuito_df["Grand Prix"].apply(lambda gp: gp_to_circuits.get(gp, ["Desconocido"])[0])
circuito_df["País"] = circuito_df["Grand Prix"].map(gp_to_country)
circuito_df["Lugar"] = circuito_df["Circuito"] + ", " + circuito_df["País"]

wins_por_lugar = circuito_df.groupby(["Winner", "Lugar"]).size().reset_index(name="Victorias")
repetidos = wins_por_lugar[wins_por_lugar["Victorias"] > 1].sort_values(by="Victorias", ascending=False)
repetidos.index += 1

if not repetidos.empty:
    st.table(repetidos.rename(columns={
        "Winner": "Piloto",
        "Lugar": "Circuito",
        "Victorias": "Veces que ganó"
    }))
else:
    st.info("Ningún piloto ganó más de una vez en el mismo circuito.")

import random

# ===================== TRIVIA =====================
st.subheader("🧠 Trivia")

# Lista de preguntas de trivia
preguntas_trivia = [
    {
        "pregunta": "¿Cuál fue el primer país fuera de Europa en albergar un Grand Prix en los años 50?",
        "opciones": ["Argentina", "Estados Unidos", "Marruecos", "India"],
        "respuesta": "Argentina",
        "explicacion": "Argentina fue sede del GP en 1953, siendo el primer país no europeo en hacerlo."
    },
    {
        "pregunta": "¿Qué piloto ganó más Grandes Premios durante los años 50?",
        "opciones": ["Stirling Moss", "Alberto Ascari", "Juan Manuel Fangio", "Luigi Musso"],
        "respuesta": "Juan Manuel Fangio",
        "explicacion": "Fangio ganó 24 carreras y 5 campeonatos mundiales en esa década."
    },
    {
        "pregunta": "¿Qué escudería obtuvo más victorias en los años 50?",
        "opciones": ["Ferrari", "Mercedes", "Maserati", "Alfa Romeo"],
        "respuesta": "Ferrari",
        "explicacion": "Ferrari fue la escudería con más victorias en la década de los 50."
    },
    {
        "pregunta": "¿Dónde se disputó el famoso GP de Mónaco?",
        "opciones": ["Silverstone", "Spa-Francorchamps", "Monaco", "Zandvoort"],
        "respuesta": "Monaco",
        "explicacion": "El GP de Mónaco siempre se ha celebrado en el Circuit de Monaco, en Monte Carlo."
    }
]

# Inicializar estados
if "trivia_respondidas" not in st.session_state:
    st.session_state.trivia_respondidas = []
if "trivia_puntos" not in st.session_state:
    st.session_state.trivia_puntos = 0
if "trivia_actual" not in st.session_state:
    preguntas_disponibles = [p for p in preguntas_trivia if p["pregunta"] not in st.session_state.trivia_respondidas]
    if preguntas_disponibles:
        st.session_state.trivia_actual = random.choice(preguntas_disponibles)
    else:
        st.session_state.trivia_actual = None
if "trivia_mostrada" not in st.session_state:
    st.session_state.trivia_mostrada = False

# Mostrar pregunta actual
pregunta = st.session_state.trivia_actual
if pregunta:
    st.markdown(f"""
    <div style='font-size:20px; font-weight: bold; margin-bottom:10px;'>
        {pregunta['pregunta']}
    </div>
    """, unsafe_allow_html=True)

    with st.form("trivia_form"):
        respuesta_usuario = st.radio("Elige una opción:", pregunta["opciones"])
        submit = st.form_submit_button("Comprobar respuesta")

    if submit and not st.session_state.trivia_mostrada:
        st.session_state.trivia_mostrada = True
        st.session_state.trivia_respondidas.append(pregunta["pregunta"])
        if respuesta_usuario == pregunta["respuesta"]:
            st.success("✅ ¡Correcto!")
            st.session_state.trivia_puntos += 1
        else:
            st.error(f"❌ Incorrecto. La respuesta correcta era: {pregunta['respuesta']}")
        st.info(f"🧠 {pregunta['explicacion']}")

        st.markdown("---")
        st.markdown(f"**Puntaje actual:** {st.session_state.trivia_puntos} de {len(st.session_state.trivia_respondidas)}")

        # Botón para pasar a la siguiente
        if st.button("Siguiente pregunta"):
            preguntas_restantes = [p for p in preguntas_trivia if p["pregunta"] not in st.session_state.trivia_respondidas]
            if preguntas_restantes:
                st.session_state.trivia_actual = random.choice(preguntas_restantes)
                st.session_state.trivia_mostrada = False
                st.rerun()
            else:
                st.success("🎉 ¡Has respondido todas las preguntas de trivia!")
else:
    st.success("🎉 ¡Has respondido todas las preguntas de trivia!")
    st.markdown(f"**Puntaje final:** {st.session_state.trivia_puntos} de {len(preguntas_trivia)}")


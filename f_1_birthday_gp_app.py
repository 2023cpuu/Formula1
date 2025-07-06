import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime
import time
import random

# Configurar página
st.set_page_config(page_title="GPs de los años 50", page_icon="🏁")
st.markdown("""
    <style>
    .stApp {
        background-image: repeating-conic-gradient(#000 0% 25%, white 0% 50%);
        background-size: 80px 80px;
        color: #000;
    }
    .contenedor-blanco {
        background-color: rgba(255, 255, 255, 0.94);
        padding: 3rem;
        border-radius: 15px;
        max-width: 1000px;
        margin: auto;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
    }
    .contenedor-blanco h1, .contenedor-blanco h2, .contenedor-blanco h3,
    .contenedor-blanco h4, .contenedor-blanco h5, .contenedor-blanco h6,
    .contenedor-blanco p {
        color: #111 !important;
    }
    </style>
""", unsafe_allow_html=True)


# 🎨 Fondo tipo bandera a cuadros
st.markdown("""
    <style>
    .stApp {
        background-image: repeating-conic-gradient(#000 0% 25%, white 0% 50%);
        background-size: 60px 60px;
    }
    .main-container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 15px;
        max-width: 1000px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Animación de auto
st.markdown("""
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
""", unsafe_allow_html=True)
time.sleep(4.2)
st.markdown('<div class="contenedor-blanco">', unsafe_allow_html=True)


with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Cargar datos
    @st.cache_data
    def load_data():
        df = pd.read_csv("F1_1950s_Race_Results_FULL.csv")
        df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
        return df.dropna(subset=["Date_Parsed"])

    races_df = load_data()

    gp_to_country = {
        "British": "Reino Unido", "French": "Francia", "Italian": "Italia", "German": "Alemania",
        "Monaco": "Mónaco", "Belgian": "Bélgica", "Dutch": "Países Bajos", "Swiss": "Suiza",
        "Argentine": "Argentina", "Indianapolis 500": "Estados Unidos", "Spanish": "España",
        "Portuguese": "Portugal", "Moroccan": "Marruecos"
    }

    month_translation = {
        "Jan": "Enero", "Feb": "Febrero", "Mar": "Marzo", "Apr": "Abril", "May": "Mayo", "Jun": "Junio",
        "Jul": "Julio", "Aug": "Agosto", "Sep": "Septiembre", "Oct": "Octubre", "Nov": "Noviembre", "Dec": "Diciembre"
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

    # Traducción país
    races_df["País"] = races_df["Grand Prix"].map(gp_to_country)

    # 🎂 ¿Hubo carrera en tu cumpleaños?
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
            st.dataframe(matching_races[["Year", "Grand Prix", "Date", "Winner", "Team"]])
        else:
            st.warning("😢 No hubo ningún Grand Prix ese día.")
            # Carrera más cercana
            st.subheader("📅 Carrera más cercana a tu cumpleaños")
            ref_date = datetime(1955, month_number + 1, int(birth_day))
            races_df["Diff"] = races_df["Date_Parsed"].apply(lambda x: abs((x - ref_date).days))
            closest = races_df.loc[races_df["Diff"].idxmin()]
            fecha_gp = closest["Date_Parsed"]
            mes_es = month_translation[fecha_gp.strftime("%b")]
            fecha_str = f"{fecha_gp.day} {mes_es} {fecha_gp.year}"
            gp_name = gp_to_country.get(closest["Grand Prix"], closest["Grand Prix"])
            mensaje = f"El GP de {gp_name} en {fecha_str} fue la carrera más cercana a tu cumple. Ganó {closest['Winner']} con {closest['Team']}."
            st.info(mensaje[0].upper() + mensaje[1:])
    # 🏆 Piloto con más victorias
    st.subheader("🏆 Piloto con más victorias en los 50s")
    top5_winners = races_df["Winner"].value_counts().head(5).reset_index()
    top5_winners.index += 1
    top5_winners.columns = ["Piloto", "Victorias"]
    st.table(top5_winners)

    # 🔧 Escudería más dominante
    st.subheader("🔧 Escudería más dominante de los 50s")
    top5_teams = races_df["Team"].value_counts().head(5).reset_index()
    top5_teams.index += 1
    top5_teams.columns = ["Escudería", "Victorias"]
    st.table(top5_teams)

    # 🌍 País con más carreras
    st.subheader("🌍 País con más carreras en los 50s")
    country_counts = races_df["País"].value_counts()
    top_count = country_counts.max()
    top_countries = country_counts[country_counts == top_count].index.tolist()

    if len(top_countries) == 1:
        pais_texto = f"{top_countries[0]} fue el país con más Grandes Premios: {top_count} en total."
    else:
        if len(top_countries) == 2:
            pais1, pais2 = top_countries
            conjuncion = "e" if pais2.strip().lower().startswith("i") else "y"
            lista_paises = f"{pais1} {conjuncion} {pais2}"
        else:
            lista_paises = ", ".join(top_countries[:-1]) + f" y {top_countries[-1]}"
        pais_texto = f"{lista_paises} fueron los países con más Grandes Premios: {top_count} cada uno."

    st.success(pais_texto[0].upper() + pais_texto[1:])

    with st.expander("📊 Ver el top 5 de países con más carreras"):
        top5_countries = country_counts.head(5).reset_index()
        top5_countries.index += 1
        top5_countries.columns = ["País", "Carreras"]
        st.table(top5_countries)

    # 🏟️ Circuitos por país
    with st.expander("🏟️ Ver los circuitos usados en cada país"):
        circuitos_por_pais = {}
        for gp, pais in gp_to_country.items():
            if gp in gp_to_circuits:
                circuitos_por_pais.setdefault(pais, set()).update(gp_to_circuits[gp])
        for pais, circuitos in circuitos_por_pais.items():
            st.markdown(f"**{pais}**: {', '.join(sorted(circuitos))}")
        st.caption("📝 *Nota: Se muestran todos los circuitos usados por país en los años 50.*")

    # 🌐 Mapa interactivo
    st.subheader("🌐 Mapa de circuitos o países con carreras en los 50s")
    map_mode = st.selectbox("¿Qué quieres ver en el mapa?", ["Por país", "Por circuito"])

    if map_mode == "Por país":
        country_coords = {
            "Reino Unido": [51.5, -0.1], "Francia": [48.85, 2.35], "Italia": [41.9, 12.5],
            "Alemania": [52.52, 13.4], "Mónaco": [43.73, 7.42], "Bélgica": [50.85, 4.35],
            "Países Bajos": [52.37, 4.89], "Suiza": [46.95, 7.45], "Argentina": [-34.6, -58.38],
            "Estados Unidos": [39.8, -86.1], "España": [40.42, -3.7], "Portugal": [38.72, -9.14],
            "Marruecos": [33.58, -7.62]
        }
        map_data = []
        for country, count in country_counts.items():
            if country in country_coords:
                lat, lon = country_coords[country]
                map_data.append({"País": country, "Lat": lat, "Lon": lon, "Carreras": count})
        map_df = pd.DataFrame(map_data)

    else:  # Por circuito
        circuito_coords = {
            "Silverstone": [52.0786, -1.0169], "Aintree": [53.475, -2.941],
            "Spa-Francorchamps": [50.4372, 5.9714], "Zandvoort": [52.3883, 4.5409],
            "Reims-Gueux": [49.247, 3.945], "Rouen-Les-Essarts": [49.398, 1.034],
            "Nürburgring": [50.3356, 6.9475], "AVUS": [52.4725, 13.2761],
            "Circuit de Monaco": [43.7347, 7.4206], "Pedralbes": [41.391, 2.119],
            "Boavista": [41.158, -8.630], "Monsanto Park": [38.7169, -9.1952],
            "Bremgarten": [46.948, 7.447], "Ain-Diab Circuit": [33.578, -7.625],
            "Autódromo Juan y Oscar Gálvez": [-34.671, -58.471],
            "Indianapolis Motor Speedway": [39.795, -86.234],
            "Autodromo Nazionale Monza": [45.6156, 9.2811]
        }

        circuito_counts = races_df["Grand Prix"].map(gp_to_circuits).explode().value_counts()
        map_data = []
        for circuito, count in circuito_counts.items():
            if circuito in circuito_coords:
                lat, lon = circuito_coords[circuito]
                map_data.append({"Circuito": circuito, "Lat": lat, "Lon": lon, "Carreras": count})
        map_df = pd.DataFrame(map_data)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[Lon, Lat]",
        get_radius="Carreras * 50000",
        get_fill_color="[200, 30, 0, 160]",
        pickable=True
    )
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2, pitch=0)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{País}: {Carreras} carreras}" if map_mode == "Por país" else "{Circuito}: {Carreras} carreras"}))

    # 📚 Trivia
    st.subheader("❓ Trivia")
    if "trivia_idx" not in st.session_state:
        st.session_state.trivia_idx = 0

    preguntas = [
        {
            "pregunta": "¿Quién fue el piloto con más títulos en los 50s?",
            "opciones": ["Alberto Ascari", "Juan Manuel Fangio", "Stirling Moss"],
            "respuesta": "Juan Manuel Fangio"
        },
        {
            "pregunta": "¿En qué país se realizó el GP de Mónaco?",
            "opciones": ["Francia", "Mónaco", "Italia"],
            "respuesta": "Mónaco"
        },
        {
            "pregunta": "¿Cuál fue el único GP estadounidense en los 50s?",
            "opciones": ["Watkins Glen", "Daytona", "Indianapolis 500"],
            "respuesta": "Indianapolis 500"
        }
    ]

    idx = st.session_state.trivia_idx
    if idx < len(preguntas):
        q = preguntas[idx]
        st.markdown(f"### {q['pregunta']}")
        opcion = st.radio("Elige una opción:", q["opciones"], key=f"trivia_{idx}")
        if st.button("Comprobar respuesta", key=f"check_{idx}"):
            if opcion == q["respuesta"]:
                st.success("¡Correcto!")
            else:
                st.error(f"Incorrecto. La respuesta era: {q['respuesta']}")
            st.session_state.trivia_idx += 1
    else:
        st.info("¡Has completado la trivia!")

st.markdown("</div>", unsafe_allow_html=True)



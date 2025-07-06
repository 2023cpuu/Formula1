import streamlit as st
import time

# Configurar página
st.set_page_config(page_title="La Fórmula de los 50s", page_icon="🏁")

# Fondo a cuadros blanco y negro
st.markdown("""
    <style>
        body {
            background-image: repeating-linear-gradient(
                45deg,
                #ffffff 0,
                #ffffff 20px,
                #000000 20px,
                #000000 40px
            );
            background-size: 40px 40px;
        }
        /* Para el contenido principal */
        .stApp {
            background-color: rgba(255,255,255,0.95);
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ANIMACIÓN del carrito (una sola vez)
car_animation = """
<div style="position:relative; height:120px; overflow:hidden;">
    <div style="
        position:absolute;
        left:-200px;
        top:20px;
        animation: drive 3s linear forwards;
        font-size: 100px;">
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
time.sleep(3.2)

# TÍTULO con carrito decorativo
st.markdown("""
<h1 style='text-align: center; font-size: 3em; margin-bottom: 0.3em; color: black;'>La Fórmula de los 50s</h1>
<div style='text-align:center; font-size:100px; margin-top:-10px;'>🏎️</div>
""", unsafe_allow_html=True)



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

# ======================= COORDENADAS DE PAÍSES =======================
country_coords = {
    "Reino Unido": [51.5, -0.1], "Francia": [48.85, 2.35], "Italia": [41.9, 12.5],
    "Alemania": [52.52, 13.4], "Mónaco": [43.73, 7.42], "Bélgica": [50.85, 4.35],
    "Países Bajos": [52.37, 4.89], "Suiza": [46.95, 7.45], "Argentina": [-34.6, -58.38],
    "Estados Unidos": [39.8, -86.1], "España": [40.42, -3.7], "Portugal": [38.72, -9.14],
    "Marruecos": [33.58, -7.62]
}

# ======================= MAPA INTERACTIVO (mejorado) =======================
st.subheader("🗺️ Mapa de países con carreras en los años 50")

map_data = []
for country, count in country_counts.items():
    if country in country_coords:
        lat, lon = country_coords[country]
        map_data.append({
            "País": country,
            "Lat": lat,
            "Lon": lon,
            "Carreras": count
        })
map_df = pd.DataFrame(map_data)

# Capa de puntos más discretos
layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[Lon, Lat]',
    get_radius="Carreras * 30000",
    get_fill_color=[255, 0, 0, 180],
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2, pitch=0)
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{País}: {Carreras} carreras"}
))

st.subheader("🔍 Explora desempeño de pilotos y escuderías")

st.markdown("Selecciona **una sola opción** para ver el historial de victorias de un piloto o una escudería:")

tab1, tab2 = st.tabs(["🏎️ Ver por piloto", "🔧 Ver por escudería"])

# ==== Por piloto ====
with tab1:
    pilotos_unicos = sorted(races_df["Winner"].dropna().unique())
    piloto = st.selectbox("Selecciona un piloto ganador", ["--"] + pilotos_unicos)

    if piloto != "--":
        st.markdown(f"### 🏁 Victorias de **{piloto}** en los años 50")
        victorias_piloto = races_df[races_df["Winner"] == piloto][["Year", "Grand Prix", "Date", "Team"]].sort_values("Year")
        victorias_piloto.reset_index(drop=True, inplace=True)
        victorias_piloto.index += 1
        victorias_piloto.index.name = "N°"
        st.dataframe(victorias_piloto, use_container_width=True)

# ==== Por escudería ====
with tab2:
    escuderias_unicas = sorted(races_df["Team"].dropna().unique())
    escuderia = st.selectbox("Selecciona una escudería ganadora", ["--"] + escuderias_unicas)

    if escuderia != "--":
        st.markdown(f"### 🏆 Victorias de **{escuderia}** en los años 50")
        victorias_escuderia = races_df[races_df["Team"] == escuderia][["Year", "Grand Prix", "Date", "Winner"]].sort_values("Year")
        victorias_escuderia.reset_index(drop=True, inplace=True)
        victorias_escuderia.index += 1
        victorias_escuderia.index.name = "N°"
        st.dataframe(victorias_escuderia, use_container_width=True)


st.subheader("🧠 Trivia")

# ---------- Preguntas ampliadas ----------
trivia_preguntas = [
    {
        "pregunta": "¿Qué piloto ganó más carreras en la década de 1950?",
        "opciones": ["Juan Manuel Fangio", "Alberto Ascari", "Stirling Moss", "Mike Hawthorn"],
        "respuesta": "Juan Manuel Fangio"
    },
    {
        "pregunta": "¿En qué circuito se corrió el primer GP en 1950?",
        "opciones": ["Monza", "Silverstone", "Indianápolis", "Zandvoort"],
        "respuesta": "Silverstone"
    },
    {
        "pregunta": "¿Qué país sudamericano albergó Grandes Premios en los años 50?",
        "opciones": ["Brasil", "Argentina", "Chile", "Perú"],
        "respuesta": "Argentina"
    },
    {
        "pregunta": "¿Qué piloto argentino fue cinco veces campeón del mundo en los 50s?",
        "opciones": ["Carlos Reutemann", "Juan Manuel Fangio", "Ricardo Zunino", "José Froilán González"],
        "respuesta": "Juan Manuel Fangio"
    },
    {
        "pregunta": "¿Cuál fue la escudería más ganadora en los 50s?",
        "opciones": ["Ferrari", "Mercedes", "Maserati", "Alfa Romeo"],
        "respuesta": "Ferrari"
    },
    {
        "pregunta": "¿En qué país se encuentra el circuito de Spa-Francorchamps?",
        "opciones": ["Francia", "Bélgica", "Países Bajos", "Suiza"],
        "respuesta": "Bélgica"
    }
]

# ---------- Estado ----------
if "trivia_index" not in st.session_state:
    st.session_state.trivia_index = 0
if "trivia_opcion" not in st.session_state:
    st.session_state.trivia_opcion = None
if "trivia_respondida" not in st.session_state:
    st.session_state.trivia_respondida = False
if "trivia_resultado" not in st.session_state:
    st.session_state.trivia_resultado = False
if "trivia_puntaje" not in st.session_state:
    st.session_state.trivia_puntaje = 0

# ---------- Funciones ----------
def comprobar_respuesta():
    if st.session_state.trivia_opcion == "Selecciona una opción" or st.session_state.trivia_opcion is None:
        st.warning("Selecciona una opción válida.")
    else:
        correcta = trivia_preguntas[st.session_state.trivia_index]["respuesta"]
        st.session_state.trivia_resultado = st.session_state.trivia_opcion == correcta
        st.session_state.trivia_respondida = True
        if st.session_state.trivia_resultado:
            st.session_state.trivia_puntaje += 1

def siguiente_pregunta():
    st.session_state.trivia_index += 1
    st.session_state.trivia_opcion = None
    st.session_state.trivia_respondida = False
    st.session_state.trivia_resultado = False

# ---------- Mostrar Pregunta ----------
if st.session_state.trivia_index < len(trivia_preguntas):
    q = trivia_preguntas[st.session_state.trivia_index]
    opciones = ["Selecciona una opción"] + q["opciones"]

    st.markdown(f"**{q['pregunta']}**")
    st.session_state.trivia_opcion = st.radio(
        "Opciones:",
        opciones,
        index=0,
        key=f"radio_{st.session_state.trivia_index}"
    )

    if not st.session_state.trivia_respondida:
        st.button("Comprobar respuesta", on_click=comprobar_respuesta)
    else:
        if st.session_state.trivia_resultado:
            st.success("✅ ¡Correcto!")
        else:
            st.error(f"❌ Incorrecto. La respuesta correcta era: {q['respuesta']}")
        st.button("Siguiente pregunta", on_click=siguiente_pregunta)

else:
    st.success(f"🎉 ¡Has terminado la trivia! Obtuviste {st.session_state.trivia_puntaje} de {len(trivia_preguntas)} puntos.")

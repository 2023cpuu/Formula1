import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt
from datetime import datetime
import time
import random

# ======================= ESTILO CSS =======================
st.markdown(
    """
    <style>
    html, body, .stApp {
        height: 100%;
        margin: 0;
        padding: 0;
        background-color: white;
        background-image: repeating-conic-gradient(#fff 0% 25%, #000 0% 50%);
        background-size: 40px 40px;
    }
    .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.3);
    }
    .block-container * {
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ======================= ANIMACIÓN DE AUTO =======================
car_animation = """
<div style="position:relative; height:160px; overflow:hidden;">
    <div style="
        position:absolute;
        left: 100%;
        top:20px;
        animation: drive 3s linear forwards;
        font-size: 120px;">
        🏎️💨
    </div>
</div>
<style>
@keyframes drive {
    0% { left: 100%; }
    100% { left: -500px; }
}
</style>
"""
st.markdown(car_animation, unsafe_allow_html=True)
time.sleep(3.5)

# ======================= TÍTULO PRINCIPAL =======================
st.markdown("<h1 style='text-align: center;'>La Fórmula de los 50s</h1>", unsafe_allow_html=True)
st.image("https://i.imgur.com/tXsjOO5.png", caption="Alfa Romeo 158 en el GP de Gran Bretaña, 1950", use_container_width=True)

# ======================= INTRO TEXTO =======================
st.markdown("""
<div style="background-color: rgba(255, 255, 255, 0.92); padding: 1.5rem; border-radius: 12px; margin-top: 1rem;">
    <h4 style="color: black;">🏁 Bienvenido a la era dorada de la F1</h4>
    <p style="color: black; font-size: 16px; line-height: 1.6;">
        Antes de los autos híbridos, de los cascos ultratecnológicos y de las radios con estrategias complicadas, la Fórmula 1 era puro corazón, instinto y gasolina. Los años 50 fueron el inicio de una leyenda: pilotos temerarios, escuderías míticas y circuitos que hacían historia vuelta a vuelta.
    </p>
    <p style="color: black; font-size: 16px; line-height: 1.6;">
        Esta página no es solo una base de datos: es un viaje interactivo a la década donde todo comenzó. ¿Hubo una carrera en tu cumpleaños? ¿Qué equipo de los 50s te representa más? ¿Cuánto sabes realmente sobre Fangio, Ascari o los peligrosos circuitos de la época?
    </p>
    <p style="color: black; font-size: 16px; font-weight: bold;">
        Hoy muchos conocen a Verstappen o Hamilton, pero pocos a Fangio o Ascari. Esta web busca cambiar eso.<br>
        Explora, juega, descubre. Porque entender el presente de la F1 también es rendir homenaje a su pasado más bravo. 🏎️✨
    </p>
</div>
""", unsafe_allow_html=True)

# ======================= DATOS Y MAPEOS =======================
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

races_df["País"] = races_df["Grand Prix"].map(gp_to_country)

# ======================= ¿Por qué volver a los 50s? =======================
st.subheader("⏳ ¿Por qué volver a los 50s?")
st.markdown("""
<p style="font-size: 16px; line-height: 1.6;">
En la era del streaming, las estadísticas y los monoplazas futuristas, a veces olvidamos cómo empezó todo. 
Los años 50 fueron más que una introducción: fueron una época donde cada victoria era una hazaña y cada circuito, un riesgo real. 
Pocos conocen esta parte de la historia. Esta plataforma te invita a redescubrirla, interactuar con ella y hacerla tuya.
</p>
""", unsafe_allow_html=True)

# ======================= Top 5 pilotos con más victorias =======================
st.subheader("🏆 Piloto con más victorias en los 50s")
top5_winners = races_df["Winner"].value_counts().head(5).reset_index()
top5_winners.columns = ["Piloto", "Victorias"]
top5_winners.index += 1

chart_winners = alt.Chart(top5_winners).mark_bar(color='crimson').encode(
    x=alt.X("Victorias:Q", axis=alt.Axis(title="Victorias", format="d")),
    y=alt.Y("Piloto:N", sort='-x', title=""),
    tooltip=["Piloto", "Victorias"]
).properties(width=600, height=250)

st.altair_chart(chart_winners, use_container_width=True)

# ======================= Escudería más dominante =======================
st.subheader("🔧 Escudería más dominante de los 50s")
top5_teams = races_df["Team"].value_counts().head(5).reset_index()
top5_teams.columns = ["Escudería", "Victorias"]
top5_teams.index += 1

chart_teams = alt.Chart(top5_teams).mark_bar(color='steelblue').encode(
    x=alt.X("Victorias:Q", axis=alt.Axis(title="Victorias", format="d")),
    y=alt.Y("Escudería:N", sort='-x', title=""),
    tooltip=["Escudería", "Victorias"]
).properties(width=600, height=250)

st.altair_chart(chart_teams, use_container_width=True)

# ======================= Línea del tiempo =======================
st.subheader("📜 Línea del tiempo interactiva: Fórmula 1 en los años 50")

eventos_f1_50s = {
    1950: "🏁 Primer campeonato oficial de F1. Farina vence a Fangio y gana el primer título.",
    1951: "🇦🇷 Fangio gana su primer campeonato con Alfa Romeo. Se convierte en una figura dominante.",
    1952: "🔧 Ferrari domina tras la salida de Alfa Romeo. Ascari gana 6 carreras.",
    1953: "🏎️ Ascari repite título con Ferrari. Temporada marcada por su consistencia.",
    1954: "⚙️ Fangio empieza con Maserati, termina con Mercedes… ¡y gana el título!",
    1955: "☠️ Tragedia en Le Mans (80 muertos). Mercedes se retira. Fangio vuelve a campeonar.",
    1956: "🔄 Fangio gana con Ferrari. Cede su auto a Collins para asegurar el título.",
    1957: "🔥 Fangio gana en Nürburgring tras remontar 48 segundos. Su quinto campeonato.",
    1958: "🧠 Se establece el campeonato de constructores. Mike Hawthorn gana el título.",
    1959: "🧪 Cooper innova con motor trasero. Brabham gana su primer título mundial."
}

for año, evento in eventos_f1_50s.items():
    with st.expander(f"📅 {año}"):
        st.markdown(f"<div style='font-size:16px'>{evento}</div>", unsafe_allow_html=True)

# ======================= ¿Hubo carrera en tu cumpleaños? =======================
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

# ======================= Mapa por país con carreras =======================
st.subheader("🌍 País con más carreras en los 50s")
country_counts = races_df["País"].value_counts()
top_count = country_counts.max()
top_countries = country_counts[country_counts == top_count].index.tolist()

if len(top_countries) == 1:
    pais_texto = f"{top_countries[0]} fue el país con más Grandes Premios: {top_count} en total."
elif len(top_countries) == 2:
    pais1, pais2 = top_countries
    conjuncion = "e" if pais2.strip().lower().startswith("i") else "y"
    lista_paises = f"{pais1} {conjuncion} {pais2}"
    pais_texto = f"{lista_paises} fueron los países con más Grandes Premios: {top_count} cada uno."
else:
    lista_paises = ", ".join(top_countries[:-1]) + f" y {top_countries[-1]}"
    pais_texto = f"{lista_paises} fueron los países con más Grandes Premios: {top_count} cada uno."

st.success(pais_texto[0].upper() + pais_texto[1:])

with st.expander("📊 Ver el top 5 de países con más carreras"):
    top5_countries = country_counts.head(5).reset_index()
    top5_countries.index += 1
    top5_countries.columns = ["País", "Carreras"]
    st.table(top5_countries)

# ======================= Mapa de países con circuitos =======================
st.subheader("🗺️ Mapa de países con carreras en los años 50")

map_data = []
for country, count in country_counts.items():
    if country in country_coords:
        lat, lon = country_coords[country]
        circuitos = sorted(circuitos_por_pais.get(country, []))
        tooltip_text = f"{country}: {count} carreras\nCircuitos: {', '.join(circuitos)}"
        map_data.append({
            "País": country,
            "Lat": lat,
            "Lon": lon,
            "Carreras": count,
            "Tooltip": tooltip_text
        })

map_df = pd.DataFrame(map_data)

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
    tooltip={"text": "{Tooltip}"}
))

# ======================= Desempeño por piloto o escudería =======================
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

# ======================= Test: ¿Qué escudería usarías? =======================
st.subheader("🛠️ ¿Qué escudería usarías?")
st.markdown("Responde este breve test y descubre qué escudería de los 50s te representa mejor.")

preguntas = {
    "¿Cuál es tu estilo de conducción?": {
        "Conservador, prefiero la estrategia": "estratega",
        "A la ofensiva, siempre al límite": "agresivo",
        "Equilibrado, me adapto": "equilibrado"
    },
    "¿Qué valoras más en una escudería?": {
        "Innovación y tecnología": "innovador",
        "Pasión y tradición": "tradicional",
        "Precisión y eficiencia": "preciso"
    },
    "¿Qué tipo de piloto te identificas más?": {
        "Líder calmado y analítico": "calculador",
        "Carismático y arriesgado": "valiente",
        "Constante y técnico": "disciplinado"
    }
}

respuestas = []
todo_listo = True

for i, (pregunta, opciones) in enumerate(preguntas.items()):
    st.markdown(f"**{i+1}. {pregunta}**")
    opciones_con_placeholder = ["Selecciona una opción..."] + list(opciones.keys())
    seleccion = st.selectbox("", opciones_con_placeholder, key=f"preg_{i}")
    
    if seleccion == "Selecciona una opción...":
        todo_listo = False
    else:
        respuestas.append(opciones[seleccion])

if st.button("Descubrir mi escudería ideal"):
    if not todo_listo:
        st.warning("Por favor responde todas las preguntas antes de continuar.")
    else:
        conteo = pd.Series(respuestas).value_counts()
        resultado = conteo.idxmax()

        perfil_to_team = {
            "agresivo": "Maserati",
            "estratega": "Ferrari",
            "equilibrado": "Vanwall",
            "tradicional": "Alfa Romeo",
            "innovador": "Cooper",
            "preciso": "Mercedes",
            "valiente": "BRM",
            "calculador": "Ferrari",
            "disciplinado": "Gordini"
        }

        escuderia = perfil_to_team.get(resultado, "Ferrari")
        st.success(f"🏁 ¡Tu escudería ideal es **{escuderia}**!")

# ======================= Trivia F1 de los 50s =======================
st.subheader("🧠 Trivia")

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


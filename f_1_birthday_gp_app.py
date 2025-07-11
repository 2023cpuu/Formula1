# Importo las librerías necesarias para que funcione la app
import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt
from datetime import datetime
import time
import random

# ====================== ESTILO GENERAL: fondo blanco con patrón de bandera a cuadros ======================
# Acá le doy estilo a toda la página para que tenga un fondo de banderita a cuadros y los contenedores se vean bien legibles

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

    .block-container h1, .block-container h2, .block-container h3,
    .block-container h4, .block-container h5, .block-container h6,
    .block-container p, .block-container label, .block-container div {
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ====================== ANIMACIÓN INICIAL: auto corriendo de derecha a izquierda ======================
# Esta parte hace que un autito 🏎️ pase al principio para que la app tenga más personalidad y enganche
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

# Muestro la animación y espero 3.5 segundos para que termine antes de mostrar el resto
st.markdown(car_animation, unsafe_allow_html=True)
time.sleep(3.5)

# ====================== TÍTULO Y PRESENTACIÓN ======================
# Este es el título principal que estará siempre arriba. Debajo, una imagen icónica y un texto que introduce la idea de la app

st.markdown("<h1 style='text-align: center;'>La Fórmula de los 50s</h1>", unsafe_allow_html=True)

st.image("https://i.imgur.com/tXsjOO5.png", caption="Alfa Romeo 158 en el GP de Gran Bretaña, 1950", use_container_width=True)

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

# ===================== CARGA DE DATOS =====================
# Cargo el archivo CSV con los resultados de todas las carreras de los 50s
# También convierto la fecha a formato datetime para poder usarla luego

@st.cache_data
def load_data():
    df = pd.read_csv("F1_1950s_Race_Results_FULL.csv")
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date_Parsed"])

# Llamo a la función y guardo el DataFrame como races_df
races_df = load_data()

# ===================== TRADUCCIÓN DE NOMBRES =====================
# Para que se entienda mejor, traduzco los nombres de los GP a países, y también los meses a español

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

# Traducción de GP a circuito específico (esto me sirve más adelante para el mapa y los tooltips)
gp_to_circuits = {
    "Argentine": ["Autódromo Juan y Oscar Gálvez"],
    "Belgian": ["Spa-Francorchamps"],
    "British": ["Silverstone", "Aintree"],
    "Dutch": ["Zandvoort"],
    "French": ["Reims-Gueux", "Rouen-Les-Essarts"],
    "German": ["Nürburgring", "AVUS"],
    "Indianapolis 500": ["Indianapolis Motor Speedway"],
    "Italian": ["Autodromo Nazionale Monza", "Circuito di Pescara"],
    "Monaco": ["Circuit de Monaco"],
    "Moroccan": ["Ain-Diab Circuit"],
    "Portuguese": ["Boavista", "Monsanto Park"],
    "Spanish": ["Pedralbes"],
    "Swiss": ["Bremgarten"]
}

# 🔧 Normalizo cualquier nombre que sea Indianápolis a una sola forma
races_df.loc[races_df["Grand Prix"].str.contains("indianapolis", case=False, na=False), "Grand Prix"] = "Indianapolis 500"

# 🗺️ Ahora mapeo correctamente los países
races_df["País"] = races_df["Grand Prix"].map(gp_to_country)

# 🔁 Reafirmo que "Indianapolis 500" pertenece a Estados Unidos
races_df.loc[races_df["Grand Prix"] == "Indianapolis 500", "País"] = "Estados Unidos"



# ===================== SECCIÓN: ¿POR QUÉ LOS 50S? =====================
# En vez de decir "justificación", hago esta sección donde implícitamente explico por qué vale la pena mirar esa década

st.subheader("⏳ ¿Por qué volver a los 50s?")
st.markdown("""
<p style="font-size: 16px; line-height: 1.6;">
En la era del streaming, las estadísticas y los monoplazas futuristas, a veces olvidamos cómo empezó todo. 
Los años 50 fueron más que una introducción: fueron una época donde cada victoria era una hazaña y cada circuito, un riesgo real. 
Pocos conocen esta parte de la historia. Esta plataforma te invita a redescubrirla, interactuar con ella y hacerla tuya.
</p>
""", unsafe_allow_html=True)

# ===================== TOP 5 PILOTOS CON MÁS VICTORIAS =====================
# Armo una tabla con los 5 pilotos que más ganaron en la década. Le sumo un gráfico con Altair para hacerlo visual

st.subheader("🏆 Piloto con más victorias en los 50s")

top5_winners = races_df["Winner"].value_counts().head(5).reset_index()
top5_winners.columns = ["Piloto", "Victorias"]
top5_winners.index += 1  # Para que el ranking empiece desde 1

# Hago el gráfico de barras
chart_winners = alt.Chart(top5_winners).mark_bar(color='crimson').encode(
    x=alt.X("Victorias:Q", axis=alt.Axis(title="Victorias", format="d")),
    y=alt.Y("Piloto:N", sort='-x', title=""),
    tooltip=["Piloto", "Victorias"]
).properties(width=600, height=250)

# Lo muestro
st.altair_chart(chart_winners, use_container_width=True)

# ===================== TOP 5 ESCUDERÍAS CON MÁS VICTORIAS =====================
# Igual que con los pilotos, pero ahora muestro las escuderías más exitosas

st.subheader("🔧 Escudería más dominante de los 50s")

top5_teams = races_df["Team"].value_counts().head(5).reset_index()
top5_teams.columns = ["Escudería", "Victorias"]
top5_teams.index += 1  # Empiezo desde 1 también

# Hago el gráfico de barras
chart_teams = alt.Chart(top5_teams).mark_bar(color='steelblue').encode(
    x=alt.X("Victorias:Q", axis=alt.Axis(title="Victorias", format="d")),
    y=alt.Y("Escudería:N", sort='-x', title=""),
    tooltip=["Escudería", "Victorias"]
).properties(width=600, height=250)

# Lo muestro
st.altair_chart(chart_teams, use_container_width=True)

# ===================== LÍNEA DEL TIEMPO INTERACTIVA =====================
# Quise resumir los momentos más importantes de cada año en una especie de línea del tiempo simple con expanders

st.subheader("📜 Línea del tiempo interactiva: Fórmula 1 en los años 50")

eventos_f1_50s = {
    1950: "🏁 Se da el primer campeonato oficial de F1. Farina vence a Fangio y gana el título.",
    1951: "🔥 Fangio gana su primer campeonato con Alfa Romeo, convirtiéndose en una figura dominante. Pero, por falta de apoyo financiero del gobierno italiano, su equipo decide retirarse de la competencia ese año",
    1952: "🔧 Ferrari domina tras la salida de Alfa Romeo. Ascari gana 6 carreras.",
    1953: "🏎️ Ascari repite título con Ferrari, la temporada es marcada por su consistencia.",
    1954: "⚙️ Fangio empieza con Maserati, termina con Mercedes… ¡y gana su segundo título!",
    1955: "☠️ Un Mercedes-Benz 300 SLR se estrella contra la tribuna en la competencia 24 horas de Le Mans, matando a más de 80 espectadores y al piloto Pierre Levegh. Esto ocasiona que, aunque era una competencia distinta, Mercedes se retire también de la F1. Fangio vuelve a campeonar.",
    1956: "🔄 Fangio gana su cuarto título con un Ferrari, gracias a que su compañero Collins le cedió su auto durante un pit-stop. Collins priorizó el título del argentino por sobre sus propias posibilidades de ganar la carrera.",
    1957: "🕊️ Fallece Eugenio Castellotti durante una sesión privada de pruebas de Ferrari en el Autódromo de Módena. Fangio gana su quinto campeonato en un Maserati, lamentando la pérdida de su compañero de equipo de 1956.",
    1958: "🧠 Se establece el campeonato de constructores, el cual se otorga a la escudería que acumule más puntos a lo largo de la temporada, considerando los resultados de todos sus pilotos. Gana la escudería Vanwall y Mike Hawthorn gana el campeonato de pilotos en un Ferrari. Fangio es secuestrado por 26 horas el 23 de febrero por el Movimiento 26 de Julio, el Gran Premio de Cuba no sale en las bases de datos pero se habría celebrado para atraer a turistas estadounidenses por lo que el secuestro se realizó en protesta. Este mismo año, Fangio se retira de la Fórmula 1 después del Gran Premio de Francia en Reims.",
    1959: "🧪 Jack Brabham, piloto de Cooper, se quedó sin combustible en la última vuelta, pero logró empujar su carro hasta la meta para asegurar su primer título mundial."
}

# Cada año aparece como expander para que el usuario vaya abriéndolos como quiera
for año, evento in eventos_f1_50s.items():
    with st.expander(f"📅 {año}"):
        st.markdown(f"<div style='font-size:16px'>{evento}</div>", unsafe_allow_html=True)

# ===================== ¿HUBO UNA CARRERA EN TU CUMPLEAÑOS? =====================
st.subheader("🎂 ¿Hubo una carrera de F1 en tu cumpleaños durante los años 50?")

# Uso dos columnas para seleccionar día y mes
col1, col2 = st.columns(2)
birth_day = col1.selectbox("Día", [""] + list(range(1, 32)))
birth_month_name = col2.selectbox("Mes", [""] + list(month_translation.values()))

if birth_day and birth_month_name:
    # Convierto el mes de texto a número
    month_number = list(month_translation.values()).index(birth_month_name)

    # Filtro las carreras que coinciden exactamente con ese día
    matching_races = races_df[
        (races_df["Date_Parsed"].dt.day == int(birth_day)) &
        (races_df["Date_Parsed"].dt.month == month_number + 1)
    ]

    if not matching_races.empty:
        st.success("🎉 ¡Sí hubo Grand Prix en tu cumpleaños!")
        st.dataframe(matching_races[["Year", "Grand Prix", "Date", "Winner", "Team"]])
    else:
        st.warning("😢 No hubo ningún Grand Prix ese día.")

        # Como extra, muestro la carrera más cercana al cumpleaños
        st.subheader("📅 Carrera más cercana a tu cumpleaños")
        ref_date = datetime(1955, month_number + 1, int(birth_day))
        races_df["Diff"] = races_df["Date_Parsed"].apply(lambda x: abs((x - ref_date).days))
        closest = races_df.loc[races_df["Diff"].idxmin()]

        # Traducción del mes al español
        fecha_gp = closest["Date_Parsed"]
        mes_es = month_translation[fecha_gp.strftime("%b")]
        fecha_str = f"{fecha_gp.day} {mes_es} {fecha_gp.year}"

        # 🔧 Corrección robusta al traducir el GP
        gp_raw = closest["Grand Prix"]
        gp_name = gp_to_country[gp_raw] if gp_raw in gp_to_country else gp_raw

        mensaje = f"El GP de {gp_name} en {fecha_str} fue la carrera más cercana a tu cumple. Ganó {closest['Winner']} con {closest['Team']}."
        st.info(mensaje[0].upper() + mensaje[1:])



# ===================== ¿QUÉ PAÍS TUVO MÁS CARRERAS? =====================
st.subheader("🌍 País con más carreras en los 50s")

# Ajustamos la cantidad de carreras para Indianápolis, que tuvo 10 (una por año entre 1950 y 1959)
# Aseguramos que esté correctamente registrado como "Estados Unidos"
races_df["País"] = races_df["País"].replace({
    "USA": "Estados Unidos",
    "U.S.A.": "Estados Unidos",
    "EEUU": "Estados Unidos"
})

# Validamos que cada edición de Indianápolis esté bien etiquetada
indy_filter = races_df["Grand Prix"] == "Indianapolis 500"
races_df.loc[indy_filter, "País"] = "Estados Unidos"

# Cuento cuántas carreras hubo por país
country_counts = races_df["País"].value_counts()
top_count = country_counts.max()
top_countries = country_counts[country_counts == top_count].index.tolist()

# Acá controlo cómo se muestra el texto dependiendo de si hay empate entre países
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

# Mostramos el top 5. Si Estados Unidos no está, lo agregamos manualmente al final
with st.expander("📊 Ver el top 5 de países con más carreras"):
    top5_countries = country_counts.head(5).reset_index()
    top5_countries.columns = ["País", "Carreras"]
    top5_countries.index += 1

    if "Estados Unidos" not in top5_countries["País"].values:
        us_row = country_counts.loc[["Estados Unidos"]].reset_index()
        us_row.columns = ["País", "Carreras"]
        top5_countries = pd.concat([top5_countries, us_row], ignore_index=True)
        top5_countries.index = range(1, len(top5_countries)+1)

    st.table(top5_countries)

# ===================== MAPA INTERACTIVO (por país con circuitos en tooltip) =====================

# Antes que nada, armamos las coordenadas manualmente (esto no lo sacamos del CSV)
country_coords = {
    "Reino Unido": [51.5, -0.1], "Francia": [48.85, 2.35], "Italia": [41.9, 12.5],
    "Alemania": [52.52, 13.4], "Mónaco": [43.73, 7.42], "Bélgica": [50.85, 4.35],
    "Países Bajos": [52.37, 4.89], "Suiza": [46.95, 7.45], "Argentina": [-34.6, -58.38],
    "Estados Unidos": [39.8, -86.1], "España": [40.42, -3.7], "Portugal": [38.72, -9.14],
    "Marruecos": [33.58, -7.62]
}

# Armamos un diccionario que relacione país con sus circuitos usados
circuitos_por_pais = {}
for gp, pais in gp_to_country.items():
    if gp in gp_to_circuits:
        circuitos_por_pais.setdefault(pais, set()).update(gp_to_circuits[gp])

# Título de la sección
st.subheader("🗺️ Mapa de países con carreras en los años 50")

# Ahora armamos los datos para el mapa
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

# Convertimos la lista en un DataFrame para usar en el mapa
map_df = pd.DataFrame(map_data)

# Creamos la capa de puntos del mapa
layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[Lon, Lat]',  # cada punto se ubica en su lat/lon
    get_radius="Carreras * 30000",  # cuanto más carreras, más grande el círculo
    get_fill_color=[255, 0, 0, 180],  # color rojo translúcido
    pickable=True,  # para que tenga tooltip
    auto_highlight=True
)

# Vista inicial del mapa (centrada en el mundo)
view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2, pitch=0)

# Mostramos el mapa
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{Tooltip}"}  # el tooltip se muestra cuando paso el mouse
))
# ===================== EXPLORAR DESEMPEÑO DE PILOTOS Y ESCUDERÍAS =====================

# Título general de esta sección
st.subheader("🔍 Explora desempeño de pilotos y escuderías")

# Instrucción para el usuario
st.markdown("Selecciona **una sola opción** para ver el historial de victorias de un piloto o una escudería:")

# Creamos dos pestañas (tabs): una para pilotos, otra para escuderías
tab1, tab2 = st.tabs(["🏎️ Ver por piloto", "🔧 Ver por escudería"])

# ==== TAB 1: Por piloto ====
with tab1:
    # Extraigo la lista de pilotos únicos que hayan ganado al menos una carrera
    pilotos_unicos = sorted(races_df["Winner"].dropna().unique())
    # Agrego opción por defecto "--"
    piloto = st.selectbox("Selecciona un piloto ganador", ["--"] + pilotos_unicos)

    if piloto != "--":
        # Mostramos tabla con todas sus victorias
        st.markdown(f"### 🏁 Victorias de **{piloto}** en los años 50")
        victorias_piloto = races_df[races_df["Winner"] == piloto][["Year", "Grand Prix", "Date", "Team"]].sort_values("Year")
        # Resetear índice para que la tabla se vea ordenada
        victorias_piloto.reset_index(drop=True, inplace=True)
        victorias_piloto.index += 1
        victorias_piloto.index.name = "N°"
        st.dataframe(victorias_piloto, use_container_width=True)

# ==== TAB 2: Por escudería ====
with tab2:
    # Lista de escuderías únicas que hayan ganado al menos una carrera
    escuderias_unicas = sorted(races_df["Team"].dropna().unique())
    escuderia = st.selectbox("Selecciona una escudería ganadora", ["--"] + escuderias_unicas)

    if escuderia != "--":
        st.markdown(f"### 🏆 Victorias de **{escuderia}** en los años 50")
        victorias_escuderia = races_df[races_df["Team"] == escuderia][["Year", "Grand Prix", "Date", "Winner"]].sort_values("Year")
        # Ordenamos bien el índice para que se vea claro
        victorias_escuderia.reset_index(drop=True, inplace=True)
        victorias_escuderia.index += 1
        victorias_escuderia.index.name = "N°"
        st.dataframe(victorias_escuderia, use_container_width=True)
# ===================== TEST: ¿QUÉ ESCUDERÍA USARÍAS? =====================

# Título de la sección
st.subheader("🛠️ ¿Qué escudería usarías?")

# Texto introductorio
st.markdown("Responde este breve test y descubre qué escudería de los 50s te representa mejor.")

# Diccionario con las preguntas y opciones. Cada opción tiene un perfil asociado
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

# Lista para guardar las respuestas del usuario
respuestas = []
todo_listo = True  # Flag para comprobar que no falte ninguna pregunta

# Itero sobre cada pregunta y sus opciones
for i, (pregunta, opciones) in enumerate(preguntas.items()):
    st.markdown(f"**{i+1}. {pregunta}**")
    # Agrego una opción por defecto al inicio
    opciones_con_placeholder = ["Selecciona una opción..."] + list(opciones.keys())
    # Usamos un selectbox con clave distinta para cada pregunta
    seleccion = st.selectbox("", opciones_con_placeholder, key=f"preg_{i}")
    
    # Si el usuario no responde una pregunta, marcamos que no está todo listo
    if seleccion == "Selecciona una opción...":
        todo_listo = False
    else:
        respuestas.append(opciones[seleccion])  # Guardamos el perfil

# Botón para ver el resultado
if st.button("Descubrir mi escudería ideal"):
    if not todo_listo:
        st.warning("Por favor responde todas las preguntas antes de continuar.")
    else:
        # Contamos cuántas veces se repite cada perfil en las respuestas
        conteo = pd.Series(respuestas).value_counts()
        resultado = conteo.idxmax()  # Nos quedamos con el perfil dominante

        # Diccionario que relaciona perfil con escudería
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

        # Buscamos la escudería final
        escuderia = perfil_to_team.get(resultado, "Ferrari")
        # Mostramos el resultado al usuario
        st.success(f"🏁 ¡Tu escudería ideal es **{escuderia}**!")
# ===================== TRIVIA INTERACTIVA =====================

# Título
st.subheader("🧠 Trivia")

# 📋 Lista de preguntas tipo test. Cada una tiene una pregunta, opciones y respuesta correcta.
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

# 👉 Variables de estado para guardar progreso y puntaje (uso st.session_state)
if "trivia_index" not in st.session_state:
    st.session_state.trivia_index = 0  # índice actual
if "trivia_opcion" not in st.session_state:
    st.session_state.trivia_opcion = None  # opción seleccionada
if "trivia_respondida" not in st.session_state:
    st.session_state.trivia_respondida = False  # si ya se respondió
if "trivia_resultado" not in st.session_state:
    st.session_state.trivia_resultado = False  # si fue correcta
if "trivia_puntaje" not in st.session_state:
    st.session_state.trivia_puntaje = 0  # puntaje total

# 👉 Función para comprobar si la opción elegida es correcta
def comprobar_respuesta():
    if st.session_state.trivia_opcion == "Selecciona una opción" or st.session_state.trivia_opcion is None:
        st.warning("Selecciona una opción válida.")
    else:
        correcta = trivia_preguntas[st.session_state.trivia_index]["respuesta"]
        st.session_state.trivia_resultado = st.session_state.trivia_opcion == correcta
        st.session_state.trivia_respondida = True
        if st.session_state.trivia_resultado:
            st.session_state.trivia_puntaje += 1  # suma punto si acierta

# 👉 Función para pasar a la siguiente pregunta
def siguiente_pregunta():
    st.session_state.trivia_index += 1
    st.session_state.trivia_opcion = None
    st.session_state.trivia_respondida = False
    st.session_state.trivia_resultado = False

# 👉 Mostrar pregunta actual
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

    # Mostrar botón para responder o siguiente pregunta según el caso
    if not st.session_state.trivia_respondida:
        st.button("Comprobar respuesta", on_click=comprobar_respuesta)
    else:
        if st.session_state.trivia_resultado:
            st.success("✅ ¡Correcto!")
        else:
            st.error(f"❌ Incorrecto. La respuesta correcta era: {q['respuesta']}")
        st.button("Siguiente pregunta", on_click=siguiente_pregunta)

else:
    # Cuando se termina la trivia, mostrar puntaje final
    st.success(f"🎉 ¡Has terminado la trivia! Obtuviste {st.session_state.trivia_puntaje} de {len(trivia_preguntas)} puntos.")

# ===================== CIERRE REFLEXIVO / CONTEXTO FINAL =====================

# Esta sección cierra la web dándole sentido a todo el recorrido sin necesidad de decir “esta es una justificación”.

st.markdown("## 📦 ¿Qué nos deja volver al pasado?")

st.markdown("""
<div style="background-color: #ffffffdd; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;">
    <p style="color: black; font-size: 16px; line-height: 1.7;">
        A lo largo de esta página vimos que los años 50 no fueron una simple etapa temprana de la Fórmula 1. 
        Fueron un laboratorio de riesgo, de ingenio y de pasión desmedida. 
        Sus protagonistas no tenían simuladores ni telemetría, pero sí una voluntad inquebrantable.
    </p>
    <p style="color: black; font-size: 16px; line-height: 1.7;">
        Quizá al principio te preguntabas por qué mirar tan atrás. Ahora sabes que Fangio no es solo una calle 
        o una estatua, que los circuitos no eran simples pistas y que cada escudería tenía algo que decir.
        Explorar esta década es también entender de dónde venimos, por qué la F1 es lo que es hoy y a quiénes 
        les debemos cada vuelta de rueda.
    </p>
    <p style="color: black; font-size: 16px; line-height: 1.7; font-weight: bold;">
        Hoy más que nunca, conocer la historia no es nostalgia: es memoria, es homenaje, es conexión.
    </p>
</div>
""", unsafe_allow_html=True)



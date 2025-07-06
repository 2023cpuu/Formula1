import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

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

# ======================= CONFIGURACIÓN =======================
st.set_page_config(page_title="GPs de los años 50", page_icon="🏁")
st.title("🏁 Grand Prix de los años 50")

# ======================= CARGA DE DATOS =======================
@st.cache_data
def load_data():
    df = pd.read_csv("F1_1950s_Race_Results_FULL.csv")
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date_Parsed"])

races_df = load_data()

# ======================= DICCIONARIOS =======================
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

# ======================= ¿HUBO GP EN TU CUMPLE? =======================
st.subheader("🎂 ¿Hubo una carrera de F1 en tu cumpleaños durante los años 50?")

dias = ["Selecciona un día"] + list(range(1, 32))
meses = ["Selecciona un mes"] + list(month_translation.values())

col1, col2 = st.columns(2)
birth_day = col1.selectbox("Día", dias)
birth_month_name = col2.selectbox("Mes", meses)

if isinstance(birth_day, int) and birth_month_name in month_translation.values():
    month_number = list(month_translation.values()).index(birth_month_name) + 1

    matching_races = races_df[
        (races_df["Date_Parsed"].dt.day == birth_day) &
        (races_df["Date_Parsed"].dt.month == month_number)
    ]

    if not matching_races.empty:
        st.success("🎉 ¡Sí hubo Grand Prix en tu cumpleaños!")
        st.dataframe(matching_races[["Year", "Grand Prix", "Date", "Winner", "Team"]].sort_values("Year"))
    else:
        st.warning("😢 No hubo ningún Grand Prix en ese día durante los años 50.")

        # ========== SOLO SI NO HUBO CARRERA EN LA FECHA EXACTA ==========
        st.subheader("📅 Carrera más cercana a tu cumpleaños")
        ref_date = datetime(1955, month_number, birth_day)
        races_df["Diff"] = races_df["Date_Parsed"].apply(lambda x: abs((x - ref_date).days))
        closest_race = races_df.loc[races_df["Diff"].idxmin()]
        fecha_gp = closest_race["Date_Parsed"]
        mes_es = month_translation[fecha_gp.strftime("%b")]
        fecha_str = f"{fecha_gp.day} {mes_es} {fecha_gp.year}"
        gp_name = gp_to_country.get(closest_race["Grand Prix"], closest_race["Grand Prix"])
        mensaje_cercano = f"El GP de {gp_name} en {fecha_str} fue la carrera más cercana a tu cumple. Ganó {closest_race['Winner']} con {closest_race['Team']}."
        st.info(mensaje_cercano[0].upper() + mensaje_cercano[1:])
else:
    st.info("👆 Selecciona tu día y mes de cumpleaños para ver si hubo una carrera.")

# ======================= PILOTO MÁS GANADOR =======================
st.subheader("🏆 Piloto con más victorias en los 50s")
top5_winners = races_df["Winner"].value_counts().head(5).reset_index()
top5_winners.index += 1
top5_winners.columns = ["Piloto", "Victorias"]
st.table(top5_winners)

# ======================= ESCUDERÍA MÁS GANADORA =======================
st.subheader("🔧 Escudería más dominante de los 50s")
top5_teams = races_df["Team"].value_counts().head(5).reset_index()
top5_teams.index += 1
top5_teams.columns = ["Escudería", "Victorias"]
st.table(top5_teams)

# ======================= PAÍS CON MÁS CARRERAS =======================
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
    top5_countries.columns = ["País", "Cantidad de carreras"]
    st.table(top5_countries)

# ======================= CIRCUITOS POR PAÍS =======================
with st.expander("🏟️ Ver los circuitos usados en cada país"):
    circuitos_por_pais = {}
    for gp, pais in gp_to_country.items():
        if gp in gp_to_circuits:
            circuitos_por_pais.setdefault(pais, set()).update(gp_to_circuits[gp])
    for pais, circuitos in circuitos_por_pais.items():
        st.markdown(f"**{pais}**: {', '.join(sorted(circuitos))}")
    st.caption("📝 *Nota: Se muestran todos los circuitos usados por país en los años 50.*")

# ======================= MAPA INTERACTIVO =======================
st.subheader("🗺️ Mapa de países con carreras en los años 50")
map_data = []
for country, count in country_counts.items():
    if country in country_coords:
        lat, lon = country_coords[country]
        map_data.append({"País": country, "Lat": lat, "Lon": lon, "Carreras": count})
map_df = pd.DataFrame(map_data)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position="[Lon, Lat]",
    get_radius="Carreras * 50000",
    get_fill_color="[200, 30, 0, 160]",
    pickable=True,
    auto_highlight=True
)
view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2, pitch=0)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{País}: {Carreras} carreras"}))

st.subheader("🏟️ Pilotos que ganaron varias veces en el mismo circuito")

multi_winners = races_df.groupby(["Winner", "Grand Prix"]).size().reset_index(name="Victorias")
multi_winners = multi_winners[multi_winners["Victorias"] > 1].sort_values(by="Victorias", ascending=False)

if multi_winners.empty:
    st.info("Ningún piloto ganó más de una vez en el mismo circuito durante los 50s.")
else:
    multi_winners.index += 1
    multi_winners.columns = ["Piloto", "Grand Prix", "Victorias"]
    st.table(multi_winners)

st.subheader("🕰️ Primer y último Grand Prix de los años 50")

primer_gp = races_df.loc[races_df["Date_Parsed"].idxmin()]
ultimo_gp = races_df.loc[races_df["Date_Parsed"].idxmax()]

for label, gp in [("Primer", primer_gp), ("Último", ultimo_gp)]:
    pais = gp_to_country.get(gp["Grand Prix"], gp["Grand Prix"])
    fecha = gp["Date_Parsed"]
    mes_es = month_translation[fecha.strftime("%b")]
    fecha_str = f"{fecha.day} {mes_es} {fecha.year}"
    st.write(f"**{label} GP:** El GP de {pais} el {fecha_str}, ganado por {gp['Winner']} con {gp['Team']}.")

st.subheader("🔄 Pilotos que corrieron para más de una escudería")

pilotos_por_escuderia = races_df.groupby("Winner")["Team"].nunique()
pilotos_multiteam = pilotos_por_escuderia[pilotos_por_escuderia > 1].sort_values(ascending=False)

if pilotos_multiteam.empty:
    st.info("Todos los pilotos compitieron con una sola escudería.")
else:
    pilotos_multiteam = pilotos_multiteam.reset_index()
    pilotos_multiteam.index += 1
    pilotos_multiteam.columns = ["Piloto", "Escuderías distintas"]
    st.table(pilotos_multiteam)


# ======================= PILOTO INTERACTIVO =======================
st.subheader("🎯 ¿Qué Grandes Premios ganó tu piloto favorito?")

pilotos_unicos = sorted(races_df["Winner"].dropna().unique())
piloto_seleccionado = st.selectbox("Selecciona un piloto", [""] + pilotos_unicos)

if piloto_seleccionado:
    victorias_piloto = races_df[races_df["Winner"] == piloto_seleccionado].sort_values("Date_Parsed")
    
    if not victorias_piloto.empty:
        st.success(f"{piloto_seleccionado} ganó {len(victorias_piloto)} carrera(s) en los años 50.")
        st.dataframe(victorias_piloto[["Year", "Grand Prix", "Date", "Team"]])

        # Mostrar gráfico por año
        victorias_por_año = victorias_piloto["Year"].value_counts().sort_index()
        st.bar_chart(victorias_por_año)
    else:
        st.warning(f"{piloto_seleccionado} no ganó ningún GP en los años 50.")


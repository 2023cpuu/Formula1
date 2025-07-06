import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

# ========== ANIMACIÓN ==========
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

# ========== CONFIGURACIÓN ==========
st.set_page_config(page_title="GPs de los años 50", page_icon="🏁")
st.title("🏁 Grand Prix de los años 50")

# ========== CARGA DE DATOS ==========
@st.cache_data
def load_data():
    df = pd.read_csv("F1_1950s_Race_Results_FULL.csv")
    df["Date_Parsed"] = pd.to_datetime(df["Date"], format="%d %b %Y", errors='coerce')
    return df.dropna(subset=["Date_Parsed"])

races_df = load_data()

# ========== DICCIONARIOS ==========
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

# ========== ¿HUBO GP EN TU CUMPLE? ==========
st.subheader("🎂 ¿Hubo una carrera de F1 en tu cumpleaños durante los años 50?")

col1, col2 = st.columns(2)
birth_day = col1.selectbox("Día", [""] + list(range(1, 32)))
birth_month_name = col2.selectbox("Mes", [""] + list(month_translation.values()))

if birth_day and birth_month_name:
    month_number = list(month_translation.values()).index(birth_month_name)
    matching_races = races_df[
        (races_df["Date_Parsed"].dt.day == birth_day) &
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
        ref_date = datetime(1955, month_number + 1, birth_day)
        races_df["Diff"] = races_df["Date_Parsed"].apply(lambda x: abs((x - ref_date).days))
        closest_race = races_df.loc[races_df["Diff"].idxmin()]
        fecha_gp = closest_race["Date_Parsed"]
        mes_es = month_translation[fecha_gp.strftime("%b")]
        fecha_str = f"{fecha_gp.day} {mes_es} {fecha_gp.year}"
        gp_name = gp_to_country.get(closest_race["Grand Prix"], closest_race["Grand Prix"])
        mensaje_cercano = f"El GP de {gp_name} en {fecha_str} fue la carrera más cercana a tu cumple. Ganó {closest_race['Winner']} con {closest_race['Team']}."
        st.info(mensaje_cercano[0].upper() + mensaje_cercano[1:])

# ========== TOP PILOTOS ==========
st.subheader("🏆 Piloto con más victorias en los 50s")
top5 = races_df["Winner"].value_counts().head(5).reset_index()
top5.index += 1
top5.columns = ["Piloto", "Victorias"]
st.table(top5)

# ========== TOP ESCUDERÍAS ==========
st.subheader("🔧 Escudería más dominante de los 50s")
top_teams = races_df["Team"].value_counts().head(5).reset_index()
top_teams.index += 1
top_teams.columns = ["Escudería", "Victorias"]
st.table(top_teams)

# ========== PAÍSES CON MÁS CARRERAS ==========
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

# ========== CIRCUITOS USADOS ==========
with st.expander("🏟️ Ver los circuitos usados en cada país"):
    for gp, pais in gp_to_country.items():
        if gp in gp_to_circuits:
            circuitos = gp_to_circuits[gp]
            st.markdown(f"**{pais}**: {', '.join(sorted(circuitos))}")
    st.caption("📝 *Nota: Se muestran todos los circuitos usados por país en los años 50.*")

# ========== MAPA ==========
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

# ========== INTERACTIVO: PILOTO ==========
st.subheader("🎯 ¿Qué Grandes Premios ganó tu piloto favorito?")
piloto = st.selectbox("Selecciona un piloto", [""] + sorted(races_df["Winner"].dropna().unique()))
if piloto:
    victorias = races_df[races_df["Winner"] == piloto].sort_values("Date_Parsed")
    df = victorias[["Year", "Grand Prix", "Date", "Team"]].reset_index(drop=True)
    df.index += 1
    df.columns = ["Año", "Grand Prix", "Fecha", "Escudería"]
    st.table(df)

    chart_df = victorias["Year"].value_counts().sort_index().reset_index()
    chart_df.columns = ["Año", "Victorias"]
    chart = alt.Chart(chart_df).mark_bar(color="#C00000").encode(
        x=alt.X("Año:O", scale=alt.Scale(paddingInner=0.1), axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Victorias:Q", axis=alt.Axis(format="d"))
    ).properties(width=40 * len(chart_df), height=400)
    st.altair_chart(chart, use_container_width=True)

# ========== INTERACTIVO: ESCUDERÍA ==========
st.subheader("🏢 ¿Qué Grandes Premios ganó tu escudería favorita?")
team = st.selectbox("Selecciona una escudería", [""] + sorted(races_df["Team"].dropna().unique()))
if team:
    victorias = races_df[races_df["Team"] == team].sort_values("Date_Parsed")
    df = victorias[["Year", "Grand Prix", "Date", "Winner"]].reset_index(drop=True)
    df.index += 1
    df.columns = ["Año", "Grand Prix", "Fecha", "Piloto"]
    st.table(df)

    chart_df = victorias["Year"].value_counts().sort_index().reset_index()
    chart_df.columns = ["Año", "Victorias"]
    chart = alt.Chart(chart_df).mark_bar(color="#0066CC").encode(
        x=alt.X("Año:O", scale=alt.Scale(paddingInner=0.1), axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Victorias:Q", axis=alt.Axis(format="d"))
    ).properties(width=40 * len(chart_df), height=400)
    st.altair_chart(chart, use_container_width=True)

# ========== MULTI-ESCUDERÍA ==========
st.subheader("🔄 Pilotos que corrieron para más de una escudería")
multiteam = races_df.groupby("Winner")["Team"].agg(lambda x: sorted(set(x)))
multiteam = multiteam[multiteam.apply(len) > 1].reset_index()
multiteam["Escuderías"] = multiteam["Team"].apply(lambda x: " 🚗 ".join(x))
multiteam = multiteam[["Winner", "Escuderías"]]
multiteam.index += 1
multiteam.columns = ["Piloto", "Escuderías por las que compitió"]
st.table(multiteam)

# ========== PILOTOS DOMINANTES POR CIRCUITO ==========
st.subheader("🏟️ Pilotos que ganaron varias veces en el mismo circuito")
victorias = races_df.groupby(["Winner", "Grand Prix"]).size().reset_index(name="Victorias")
victorias = victorias[victorias["Victorias"] > 1]

rows = []
for _, row in victorias.iterrows():
    piloto, gp, victs = row["Winner"], row["Grand Prix"], row["Victorias"]
    pais = gp_to_country.get(gp, gp)
    for circuito in gp_to_circuits.get(gp, [gp]):
        rows.append((piloto, f"{circuito}, {pais}", victs))

df = pd.DataFrame(rows, columns=["Piloto", "Circuito, País", "Victorias"])
df = df.sort_values("Victorias", ascending=False).drop_duplicates()
df.index += 1
st.table(df)

st.altair_chart(chart, use_container_width=True)
    else:
        st.warning(f"{piloto_seleccionado} no ganó ningún GP en los años 50.")


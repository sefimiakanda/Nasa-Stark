import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import plotly.graph_objs as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="NASA Asteroid Impact Simulator", layout="wide")

# --- Titre principal ---
st.title("☄️ Simulateur NASA : Suivi des Astéroïdes Géocroiseurs")
st.markdown("Visualisation 3D interactive des astéroïdes proches de la Terre selon les données de la NASA (NeoWs API).")

# --- Sélection de la durée d'observation ---
st.sidebar.header("⚙️ Paramètres d'observation")
days = st.sidebar.slider("Durée (en jours)", min_value=1, max_value=7, value=3, step=1)
rotation_speed = st.sidebar.slider("Vitesse de rotation 3D", 0.1, 5.0, 1.5, 0.1)

# --- Calcul de la période ---
today = datetime.date.today()
start_date = (today - datetime.timedelta(days=days - 1)).isoformat()
end_date = today.isoformat()
st.markdown(f"🗓️ **Période d'observation :** du `{start_date}` au `{end_date}`")

# --- Fonction de récupération des données NASA ---
@st.cache_data
def load_nasa_data(start_date, end_date):
    API_KEY = "DEMO_KEY"  # Remplace par ta clé perso : "ETcNg5fUT9TCgGEZSPZixiGKsiot33jfqxl5I3k7"
    url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={API_KEY}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()

# --- Chargement des données ---
with st.spinner("Chargement des données NASA..."):
    data = load_nasa_data(start_date, end_date)

# --- Traitement des données ---
asteroids = []
for date in data["near_earth_objects"]:
    for neo in data["near_earth_objects"][date]:
        avg_diameter = (neo["estimated_diameter"]["meters"]["estimated_diameter_min"] +
                        neo["estimated_diameter"]["meters"]["estimated_diameter_max"]) / 2
        asteroids.append({
            "nom": neo["name"],
            "date": date,
            "vitesse (km/s)": float(neo["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"]),
            "distance (km)": float(neo["close_approach_data"][0]["miss_distance"]["kilometers"]),
            "diamètre moyen (m)": avg_diameter,
            "dangereux": neo["is_potentially_hazardous_asteroid"]
        })

df = pd.DataFrame(asteroids)
df.sort_values(by="distance (km)", inplace=True)
st.success(f"✅ {len(df)} astéroïdes détectés entre le {start_date} et le {end_date}")

# --- Affichage du tableau ---
st.subheader("🪐 Données des astéroïdes détectés")
st.dataframe(df, use_container_width=True)

# --- Visualisation 3D interactive ---
st.subheader("🌍 Visualisation 3D interactive des orbites d'astéroïdes")

# Génération de couleurs et tailles dynamiques
colors = ["#FF4B4B" if h else "#4B9EFF" for h in df["dangereux"]]
sizes = np.interp(df["diamètre moyen (m)"], (df["diamètre moyen (m)"].min(), df["diamètre moyen (m)"].max()), (4, 20))

fig = go.Figure()

# Tracé de chaque astéroïde avec couleur et taille différentes
for i, row in df.iterrows():
    fig.add_trace(go.Scatter3d(
        x=[np.random.uniform(-1, 1) * row["distance (km)"] / 1e6],
        y=[np.random.uniform(-1, 1) * row["distance (km)"] / 1e6],
        z=[np.random.uniform(-0.3, 0.3) * row["distance (km)"] / 1e6],
        mode="markers+text",
        text=[row["nom"]],
        textposition="top center",
        marker=dict(size=sizes[i], color=colors[i], opacity=0.8, line=dict(width=1, color="white")),
        name=row["nom"]
    ))

# Terre au centre
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode="markers+text",
    text=["🌍 Terre"],
    textposition="top center",
    marker=dict(size=25, color="green"),
    name="Terre"
))

# Mise en page 3D
fig.update_layout(
    scene=dict(
        xaxis_title="X (millions de km)",
        yaxis_title="Y (millions de km)",
        zaxis_title="Z (millions de km)",
        aspectmode="data",
        camera=dict(eye=dict(x=2, y=0, z=0.3))
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    showlegend=False
)

# --- Animation de rotation automatique ---
rotation_frames = []
for angle in np.linspace(0, 360, 60):
    camera_eye = dict(
        x=2 * np.cos(np.radians(angle / rotation_speed)),
        y=2 * np.sin(np.radians(angle / rotation_speed)),
        z=0.3
    )
    rotation_frames.append(go.Frame(layout={"scene": {"camera": {"eye": camera_eye}}}))

fig.update(frames=rotation_frames)

# --- Affichage ---
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
    **ℹ Interprétation :**
    - Les sphères **rouges** indiquent des astéroïdes *potentiellement dangereux*.
    - Les sphères **bleues** sont inoffensives.
    - La **taille** de la sphère dépend du diamètre estimé.
    - Le graphique tourne automatiquement pour une meilleure visualisation.
    """
)

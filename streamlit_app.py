import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Immobilier Togo", layout="wide")
st.title("Visualisation des donnees immobilieres")

# Sidebar - Filtres
st.sidebar.header("Filtres")
source_option = st.sidebar.selectbox(
    "Source",
    ["all", "Coin-Afrique", "igoe-immobilier", "intendance-tg", "Immoask"]
)
per_page = st.sidebar.slider("Resultats par page", 1, 100, 20)

min_price, max_price = st.sidebar.slider(
    "Intervalle de prix (FCFA)", 0, 500000000, (0, 500000000), step=1000000
)
min_surface, max_surface = st.sidebar.slider(
    "Surface (m²)", 0, 2000, (0, 2000), step=50
)
property_type_filter = st.sidebar.text_input("Type de bien (Villa, Appartement, Terrain...)")
q = st.sidebar.text_input("Recherche (description ou localisation)")

# Pagination
if 'page' not in st.session_state:
    st.session_state.page = 1

params = {"per_page": per_page, "page": st.session_state.page}
if source_option != "all":
    params["source"] = source_option
params["min_price"] = min_price
params["max_price"] = max_price
params["min_surface"] = min_surface if min_surface > 0 else None
params["max_surface"] = max_surface if max_surface < 2000 else None
if property_type_filter:
    params["property_type"] = property_type_filter
if q:
    params["q"] = q

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["Annonces", "Prix au m² par quartier", "Indice Immobilier", "Statistiques"])

with tab1:
    if st.button("Charger les annonces"):
        resp = requests.get(f"{API_URL}/announcements", params=params)
        if resp.status_code == 200:
            result = resp.json()
            total = result.get("total", 0)
            page = result.get("page", 1)
            per_page_resp = result.get("per_page", per_page)
            items = result.get("items", [])
            df = pd.DataFrame(items)
            if df.empty:
                st.info("Aucune annonce trouvee pour ces filtres.")
            else:
                st.write(f"Page {page} / {max(1, (total-1)//per_page_resp+1)} (total: {total})")
                cols_display = [c for c in df.columns if c not in ('citations', 'images')]
                st.dataframe(df[cols_display] if 'citations' in df.columns else df, use_container_width=True)
                if "price_numeric" in df.columns:
                    st.subheader("Distribution des prix")
                    st.bar_chart(df["price_numeric"].dropna())
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Telecharger CSV", csv, "annonces.csv", "text/csv")
                col1, col2, col3 = st.columns(3)
                if col1.button("<< Premiere") and page > 1:
                    st.session_state.page = 1
                    st.experimental_rerun()
                if col2.button("< Precedent") and page > 1:
                    st.session_state.page = page - 1
                    st.experimental_rerun()
                if col3.button("Suivant >") and page * per_page_resp < total:
                    st.session_state.page = page + 1
                    st.experimental_rerun()
        else:
            st.error(f"Erreur API: {resp.status_code}")

with tab2:
    st.header("Prix moyen au m² par quartier")
    if st.button("Charger prix/m²"):
        resp = requests.get(f"{API_URL}/analytics/price-per-m2")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("quartiers"):
                df = pd.DataFrame(data["quartiers"])
                st.dataframe(df, use_container_width=True)
                st.metric("Moyenne globale (FCFA/m²)", data.get("moyenne_globale"))
                st.bar_chart(df.set_index("quartier")["prix_m2_moyen"])
            else:
                st.info("Pas de donnees avec prix et surface. Importez des annonces.")
        else:
            st.error("Erreur API")

with tab3:
    st.header("Indice Immobilier (ID Immobilier)")
    st.caption("Base 100. < 100 = sous-evalue, > 100 = surevalue")
    if st.button("Charger indice immobilier"):
        resp = requests.get(f"{API_URL}/analytics/indice-immobilier")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("indices"):
                df = pd.DataFrame(data["indices"])
                st.dataframe(df, use_container_width=True)
                st.bar_chart(df.set_index("quartier")["indice"])
            else:
                st.info("Pas de donnees. Importez des annonces avec surface.")
        else:
            st.error("Erreur API")

with tab4:
    st.header("Statistiques globales")
    if st.button("Afficher statistiques"):
        resp = requests.get(f"{API_URL}/statistics")
        if resp.status_code == 200:
            st.json(resp.json())
        else:
            st.error("Erreur API")

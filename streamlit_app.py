import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.title("Visualisation des données immobilières")

col1, col2 = st.columns(2)
with col1:
    source_option = st.selectbox("Choisir une source", ["all", "Coin-Afrique", "igoe-immobilier", "intendance-tg"])
with col2:
    per_page = st.slider("Résultats par page", 1, 100, 20)

# option prix min/max
min_price, max_price = st.slider("Intervalle de prix (CFA)", 0, 500000000, (0, 500000000), step=1000000)

# recherche textuelle
q = st.text_input("Recherche (description ou localisation)")

# pagination state
if 'page' not in st.session_state:
    st.session_state.page = 1

# reset page when filters change
if st.button("Réinitialiser filtres"):
    st.session_state.page = 1

params = {"per_page": per_page, "page": st.session_state.page}
if source_option != "all":
    params["source"] = source_option
params["min_price"] = min_price
params["max_price"] = max_price
if q:
    params["q"] = q

# perform request when user clicks
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
            st.info("Aucune annonce trouvée pour ces filtres.")
        else:
            st.write(f"Affichage page {page} / {((total-1)//per_page_resp)+1} (total {total} annonces)")
            st.dataframe(df)
            # show price distribution
            st.subheader("Distribution des prix")
            st.bar_chart(df["price_numeric"].dropna())
            # allow export to CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Télécharger CSV", csv, "annonces.csv", "text/csv")
        # pagination controls
        st.write("")
        cols = st.columns(3)
        if cols[0].button("<< Première") and page > 1:
            st.session_state.page = 1
            st.experimental_rerun()
        if cols[1].button("< Précédent") and page > 1:
            st.session_state.page = page - 1
            st.experimental_rerun()
        if cols[2].button("> Suivant") and page * per_page_resp < total:
            st.session_state.page = page + 1
            st.experimental_rerun()
    else:
        st.error(f"Erreur API: {resp.status_code}")

st.header("Statistiques globales")
if st.button("Afficher statistiques"):
    resp = requests.get(f"{API_URL}/statistics")
    if resp.status_code == 200:
        st.json(resp.json())
    else:
        st.error("Impossible de récupérer les statistiques")

st.header("Images")
if st.button("Charger images"):
    resp = requests.get(f"{API_URL}/images")
    if resp.status_code == 200:
        imgs = resp.json()
        if not imgs:
            st.info("Aucune image disponible")
        else:
            df = pd.DataFrame(imgs)
            st.dataframe(df)
            # show first 5 thumbnails if possible
            st.subheader("Aperçu des URLs")
            for row in imgs[:5]:
                url = row.get('url')
                if url:
                    st.write(url)
    else:
        st.error("Erreur chargement images")

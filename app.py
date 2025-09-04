import streamlit as st
import pandas as pd
import plotly.express as px
from modules import carica_excel, rinomina_nomi_lunghi, aggiungi_area,filtra_scaduti, filtra_short, esporta_excel, grafico_device_per_area, carica_indirizzi

st.set_page_config(page_title="Analisi Device", layout="centered")

st.title("📦 Hub Gestione TS")

tab1, tab2, = st.tabs(["Analisi TS", "Indirizzi spedizione"])

with tab1:
    
    st.header("Analisi TS")
    uploaded_file = st.file_uploader("Carica il file Excel", type=["xlsx", "xls"])
    if uploaded_file:
        
        # Carico file Excel, rinomino alcuni nomi lunghi con Fermo DHL in mezzo, assegno a ogni città un'area
        
        df = carica_excel(uploaded_file)
        df = rinomina_nomi_lunghi(df)
        df = aggiungi_area(df)
        
        # Aggiungo nella sidebar dei filtri per Area, per codice Device, per seriale, per Nome Persona, e toggle per gli short nella pagina principale
        
        st.sidebar.header("🔎 Filtri")
        selected_area = st.sidebar.multiselect("Area", sorted(df["Area"].dropna().unique().astype(int).tolist())
        )
        selected_name = st.sidebar.multiselect("Nome", sorted(df["Name"].dropna().unique()))
        selected_device = st.sidebar.multiselect("Device", sorted(df["Device"].dropna().unique()))
        selected_serial = st.sidebar.multiselect("Seriale", sorted(df["Batch"].dropna().unique()))
        filtro_short = st.toggle("Mostra device short", value=False)
        
        # Fa in modo che 
        
        mask = pd.Series([True] * len(df))

        if selected_area:
            mask &= df["Area"].isin(selected_area)
        if selected_device:
            mask &= df["Device"].isin(selected_device)
        if selected_serial:
            mask &= df["Batch"].isin(selected_serial)
        if selected_name:
            mask &= df["Name"].isin(selected_name)

        df = df[mask]
        
        # Filtro pezzi che sono già scaduti
        df = filtra_scaduti (df)
        
        # Filtro short per scadenza < 120gg (4 mesi)
        if filtro_short:
            df = filtra_short(df, giorni_short=120)
        
        # Toggle di visualizzazione colonne aggiuntive (Seriali, Units, Area)
        
        mostra_batch = st.sidebar.toggle("Mostra colonna Batch", value=False)
        mostra_units = st.sidebar.toggle("Mostra colonna Units", value=False)
        mostra_area = st.sidebar.toggle("Mostra colonna Area", value=False)
        
        colonne_vis = ["Name", "Device", "Expiration", "Weeks"]
        if mostra_area:
            colonne_vis.insert(0, "Area")
        if mostra_units:
            colonne_vis.insert(3, "Units")
        if mostra_batch:
            colonne_vis.insert(2, "Batch")
        
        df_vis = df[colonne_vis].copy()
        df_vis = df_vis.sort_values(by='Expiration', ascending=True)
        
        # Visualizzazione tabella con data editor (più veloce ma la tabella diventa editabile)
        
        st.subheader("Tabella filtrata")
        st.data_editor(
            df_vis,
            column_config={
                "Expiration": st.column_config.DateColumn("Expiration", format="DD/MM/YYYY"),
                "Area": st.column_config.NumberColumn("Area", format="%d")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Pulsante download per esportare file Excel
        
        st.download_button(
            "💾 Scarica Excel filtrato",
            data=esporta_excel(df),
            file_name="Materiale_filtrato.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )
        
        # Grafico di distribuzione dei device per area e toggle per normalizzazione per numero di persone in area con quel device
        
        st.subheader("Distribuzione device per Area")
        
        device_grafico = st.sidebar.multiselect(
            "Seleziona i Device per il grafico",
            options=sorted(df['Device'].unique()),
            default=[]
        
        )
        normalizza_toggle = st.sidebar.toggle("Normalizza per numero di persone per Area", value=False)
        
        grafico_device_per_area(df, device_selezionati=device_grafico, normalizza=normalizza_toggle)
        

with tab2:
    
    st.header("📍 Indirizzi di Spedizione")
    
    indirizzi_df = carica_indirizzi()
    
    # Filtro per Area
    aree_disponibili = sorted(indirizzi_df["Area"].unique())
    selected_area = st.multiselect("Filtra per Area", aree_disponibili)
    
    if selected_area:
        indirizzi_df = indirizzi_df[indirizzi_df["Area"].isin(selected_area)]

    # Ricerca per Nome
    search_name = st.text_input("Cerca per Nome")
    if search_name:
        indirizzi_df = indirizzi_df[indirizzi_df["Nome"].str.contains(search_name, case=False, na=False)]

    # Mostra tabella
    st.data_editor(
        indirizzi_df,
        column_config={
            "Area": st.column_config.NumberColumn("Area", format="%d"),
            "Nome": "Nome",
            "Via": "Via",
            "Città": "Città",
            "CAP": "CAP",
            "Corriere": "Corriere",
            "Telefono": "Telefono"
        },
        hide_index=True,
        use_container_width=True,
        disabled=True  # solo visualizzazione
    )
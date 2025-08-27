import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(page_title="Analisi Device", layout="centered")

st.title("📊 Analisi Device")

# Caricamento file Excel
uploaded_file = st.file_uploader("Carica il file Excel", type=["xlsx", "xls"])

if uploaded_file:
    # Leggi solo il primo foglio, header alla seconda riga e ignora la prima colonna vuota
    df = pd.read_excel(uploaded_file, sheet_name=0, header=1, usecols = lambda x: x not in ['Unnamed: 0'])

    # Tengo solo le colonne utili: Nome, Città, Unità, Codice Device, Seriale, Scadenza, TS o LT, Settimane di Giacenza
    colonne_da_tenere = [
        "Stock-Customer Name",
        "Stock-Customer City",
        "Total Invntry Units",
        "Material Hier 5 Number",
        "Batch Num",
        "Expiration Date",
        #"Legal Status",
        "Weeks"
    ]
    df = df[colonne_da_tenere]        

    # Sidebar con filtri
    st.sidebar.header("🔎 Filtri")
    
    # Rinomino le colonne per renderle più leggibili
    df = df.rename(columns={
        'Stock-Customer Name':'Name', 
        'Stock-Customer City':'City', 
        'Total Invntry Units':'Units', 
        'Material Hier 5 Number':'Device', 
        'Batch Num':'Batch', 
        'Expiration Date': 'Expiration'
    })
    
    # Expiration Date da stringa a data in formato gg/mm/aaaa e cancello quelle prima di OGGI
    if "Expiration" in df.columns:
        df["Expiration"] = pd.to_datetime(df["Expiration"], errors="coerce")
        today = pd.Timestamp(datetime.today().date())
        df = df[df['Expiration'] >= today]
    
    # Creo una colonna dedicata all'area
    df.insert(0, 'Area', '')
    
    # Assegno a ogni persona della colonna "Name" un'area
    mappa_aree = {
    
        "BARI": 3,
        "BARLETTA": 3,
        "BELLIZZI": 4,
        "BOLOGNA": 1,
        "BORGIA": 4,        
        "BRESCIA": 2,    
        "BUSTO ARSIZIO": 2,
        "CALVI RISORTA": 4,
        "Caselle Torinese": 1,
        "CASELLE TORINESE": 1,
        "CASSANO MAGNAGO": 2,
        "CATANIA": 4,
        "CAVENAGO DI BRIANZA": 2,
        "CHIETI": 3,
        "CIVITANOVA MARCHE": 1,
        "COLOGNO AL SERIO": 2,
        "DECIMOPUTZU": 1,
        "FIRENZE": 1,
        "GALATINA": 3,
        "GENOVA": 1,
        "IMOLA": 1,
        "LISSONE": 2,
        "MARANO DI NAPOLI": 4,
        "MASATE": 2,
        "MESSINA": 4,
        "MODENA": 1,
        "MONSUMMANO TERME": 1,
        "MONTERONI DI LECCE": 3,
        "MUGGIÒ": 2,
        "NAPOLI": 4,
        "OPERA": 2,
        "PADOVA": 2,
        "PALERMO": 4,
        "PISA": 1,
        "REGGIO CALABRIA": 4,
        "ROMA": 3,
        "SAN GIOVANNI ROTONDO": 3,
        "SASSARI": 1,
        "SCHIO": 2,
        "SEGRATE": 2,
        "SPARANISE": 4,
        "TORINO": 1    
    }

    df['Area'] = df['City'].map(mappa_aree)
    
    
    # Filtro Aree
    area_options = sorted(df["Area"].dropna().unique().tolist())
    selected_area = st.sidebar.multiselect("Area", area_options)
    if selected_area:
        df = df[df["Area"].isin(selected_area)]
    
    # Filtro Device
    device_options = sorted(df["Device"].dropna().unique().tolist())
    selected_device = st.sidebar.multiselect("Device", device_options)
    if selected_device:
        df = df[df["Device"].isin(selected_device)]

    # Filtro Seriali
    serial_options = sorted(df["Batch"].dropna().unique().tolist())
    selected_serial = st.sidebar.multiselect("Seriale", serial_options)
    if selected_serial:
        df = df[df["Batch"].isin(selected_serial)]

    # Filtro Nome persona
    name_options = sorted(df["Name"].dropna().unique().tolist())
    selected_name = st.sidebar.multiselect("Nome", name_options)
    if selected_name:
        df = df[df["Name"].isin(selected_name)]
        
        
    # Filtro Short (scadenza < 120gg)
    if "Expiration" in df.columns:
        df["Expiration"] = pd.to_datetime(df["Expiration"], errors="coerce")
        today = pd.Timestamp(datetime.today().date())
        short = today + timedelta(days=120)
        filtro_short = st.toggle("Mostra device short", value=False)
        if filtro_short:
            df = df[(df["Expiration"] >= today) & (df["Expiration"] < short)]
            
    # Cancello la colonna City e ordino il tutto per data di scadenza di default
    df = df.drop(columns=["City"])
    df = df.sort_values(by='Expiration', ascending=True)
    
    # Toggle nella sidebar
    mostra_batch = st.sidebar.toggle("Mostra colonna Batch", value=False)
    mostra_units = st.sidebar.toggle("Mostra colonna Units", value=False)
    
    # Colonne da mostrare in tabella
    colonne_da_mostrare = df.columns.tolist()

    if not mostra_batch and 'Batch' in colonne_da_mostrare:
        colonne_da_mostrare.remove('Batch')
    if not mostra_units and 'Units' in colonne_da_mostrare:
        colonne_da_mostrare.remove('Units')
        
    # Dataframe solo per visualizzazione
    df_vis = df[colonne_da_mostrare].copy()  
    
    # Mostra tabella
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
    

    # Pulsante per scaricare Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        processed_data = output.getvalue()
        return processed_data

    st.download_button(
        label="💾 Scarica Excel filtrato",
        data=to_excel(df),
        file_name="Materiale_filtrato.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

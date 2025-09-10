import streamlit as st
import pandas as pd
import plotly.express as px
from modules import carica_excel, rinomina_nomi_lunghi, aggiungi_area,filtra_scaduti, filtra_short, esporta_excel, grafico_device_per_area, carica_indirizzi, aggiungi_categorie_device

st.set_page_config(page_title="Analisi Device", layout="wide")

st.title("📦 Hub Gestione TS")

tab1, tab2, tab3 = st.tabs(["Analisi TS", "Indirizzi spedizione", "Grafici"])

#Inizializzo il dataframe df

df = None

device_mapping = {
    
    "0662": {"Categoria": "Lead", "Famiglia": "Ty"},
    "0663": {"Categoria": "Lead", "Famiglia": "Ty"},
    "0665": {"Categoria": "Lead", "Famiglia": "Ty"},
    "0672": {"Categoria": "Lead", "Famiglia": "Ty"},
    "0673": {"Categoria": "Lead", "Famiglia": "Ty"},
    "0675": {"Categoria": "Lead", "Famiglia": "Ty"},
    "0676": {"Categoria": "Lead", "Famiglia": "Ty"},
    "3501": {"Categoria": "Lead", "Famiglia": "S"},
    "4457": {"Categoria": "Lead", "Famiglia": "By"},
    "4480": {"Categoria": "Lead", "Famiglia": "By"},
    "4592": {"Categoria": "Lead", "Famiglia": "CRT"},
    "4671": {"Categoria": "Lead", "Famiglia": "CRT"},
    "4672": {"Categoria": "Lead", "Famiglia": "CRT"},
    "4674": {"Categoria": "Lead", "Famiglia": "CRT"},
    "4675": {"Categoria": "Lead", "Famiglia": "CRT"},
    "4677": {"Categoria": "Lead", "Famiglia": "CRT"},
    "4678": {"Categoria": "Lead", "Famiglia": "CRT"},
    "7732": {"Categoria": "Lead", "Famiglia": "By"},
    "7736": {"Categoria": "Lead", "Famiglia": "By"},
    "7841": {"Categoria": "Lead", "Famiglia": "By"},
    "7842": {"Categoria": "Lead", "Famiglia": "By"},
    
    "4712": {"Categoria": "Tunnellizzatore", "Famiglia": "S"},
    
    "A219": {"Categoria": "Device", "Famiglia": "S", "Da sostituzione": "No"},
    "D120": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "Si"},
    "D121": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "Si"},
    "D140": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D141": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "Si"},
    "D142": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D143": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "Si"},
    "D232": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D233": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D332": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D333": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D400": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "Si"},
    "D401": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "Si"},
    "D412": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D413": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D432": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    "D433": {"Categoria": "Device", "Famiglia": "Ty", "Da sostituzione": "No"},
    
    "G125": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G126": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G138": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G140": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G141": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G146": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G148": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "No"},
    "G224": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G247": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "No"},
    "G324": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G347": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "No"},
    "G424": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "Si"},
    "G447": {"Categoria": "Device", "Famiglia": "CRTd", "Da sostituzione": "No"},
    
    "L110": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    "L111": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    "L131": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    "L210": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    "L211": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    "L231": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    "L310": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    "L311": {"Categoria": "Device", "Famiglia": "PMK", "Da sostituzione": "No"},
    
    "U125": {"Categoria": "Device", "Famiglia": "CRTp", "Da sostituzione": "Si"},
    "U128": {"Categoria": "Device", "Famiglia": "CRTp", "Da sostituzione": "No"},
    "U225": {"Categoria": "Device", "Famiglia": "CRTp", "Da sostituzione": "Si"},
    "U226": {"Categoria": "Device", "Famiglia": "CRTp", "Da sostituzione": "Si"},
    "U228": {"Categoria": "Device", "Famiglia": "CRTp", "Da sostituzione": "No"},
    }

with tab1:
    
    st.header("📑 Analisi TS")
    uploaded_file = st.file_uploader("Carica il file Excel", type=["xlsx", "xls"])
    
    if uploaded_file:
        
        # Carico file Excel, rinomino alcuni nomi lunghi con Fermo DHL in mezzo, assegno a ogni città un'area
        
        df_raw = carica_excel(uploaded_file)
        df = rinomina_nomi_lunghi(df_raw.copy())
        df = aggiungi_area(df)
        df = aggiungi_categorie_device (df, device_mapping)
        
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
        
        
        

with tab2:
    
    st.header("🗺️ Indirizzi di Spedizione")
    
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
    
with tab3:
    
    st.header("📊 Grafici")
    
    if uploaded_file:    

        # Filtri centrali nel Tab3
        col1, col2, col3 = st.columns(3)
        
        # filtro i NA dai valori univoci
        devices = sorted(df["Device"].dropna().unique())
        categories = sorted(df["Categoria"].dropna().unique())

        with col1:
            device_grafico = st.multiselect(
                "Seleziona i Device",
                options = devices, # uso la lista filtrata
                default=[],  # vuoto all'apertura
            )
        with col2:
            selected_categoria = st.multiselect(
                "Categoria",
                categories, # uso la lista filtrata
                default=[],
            )
        
        # Vede se il filtro Famiglia deve essere disabilitato
        disable_famiglia = not selected_categoria
        
        df_filtered_for_dependencies = df.copy()
        if selected_categoria:
            df_filtered_for_dependencies = df_filtered_for_dependencies[df_filtered_for_dependencies["Categoria"].isin(selected_categoria)]
            
        famiglie = sorted(df_filtered_for_dependencies["Famiglia"].dropna().unique())
        
        with col3:
            selected_famiglia = st.multiselect(
                "Famiglia",
                famiglie,
                default=[],
                disabled=disable_famiglia # Disabilita se non è stata scelta la Categoria
            )
        
        # Toggle Device da sostituzione (pezzi rari, DF1, DF4-IS1)
        selected_sostituzione = st.toggle(
            "Device da sostituzione",
            value=False
        )

        # Toggle normalizzazione
        normalizza_toggle = st.toggle(
            "Normalizza per numero di persone per Area", value=False
        )

        # Applica i filtri
        df_grafico = df.copy()
        if device_grafico:
            df_grafico = df_grafico[df_grafico["Device"].isin(device_grafico)]
        if selected_categoria:
            df_grafico = df_grafico[df_grafico["Categoria"].isin(selected_categoria)]
        if selected_famiglia:
            df_grafico = df_grafico[df_grafico["Famiglia"].isin(selected_famiglia)]
            
        # Applica il filtro dei device Da Sostituzione
        if selected_sostituzione:
            df_grafico = df_grafico[df_grafico["Da sostituzione"] == "Si"]

        # Crea il grafico solo se ci sono dati
        if not df_grafico.empty:
            import plotly.express as px
            import plotly.graph_objects as go

            if normalizza_toggle:
                counts = (
                    df_grafico.groupby(["Area", "Device"]).size().reset_index(name="Count")
                )
                persone_per_area = (
                    df_grafico.groupby("Area")["Name"]
                    .nunique()
                    .reset_index(name="NumPeople")
                )
                counts = counts.merge(persone_per_area, on="Area")
                counts["CountNormalized"] = counts["Count"] / counts["NumPeople"]

                fig = px.bar(
                    counts,
                    x="Area",
                    y="CountNormalized",
                    color="Device",
                    barmode="group",
                    title="Numero Device per Area (Normalizzato per persone)",
                    labels={"CountNormalized": "Device per persona", "Area": "Area"},
                )

            else:
                counts = (
                    df_grafico.groupby(["Area", "Device"]).size().reset_index(name="Count")
                )
                fig = px.bar(
                    counts,
                    x="Area",
                    y="Count",
                    color="Device",
                    barmode="group",
                    title="Numero di Device per Area",
                    labels={"Count": "Numero dispositivi", "Area": "Area"},
                )
            
            # Sull'asse delle x voglio solo vedere i numeri di area, non i decimali
            x_labels = ['1', '2', '3', '4']
            fig.update_xaxes(
                tickvals=[1, 2, 3, 4], # These are the actual values from your data
                ticktext=x_labels,     # These are the labels you want to display
                type='category'        # Important to treat the x-axis as categories
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Seleziona almeno un filtro per visualizzare il grafico")
    
    else: st.info("⚠️ Carica prima un file nella sezione **Analisi TS** per vedere i grafici.")

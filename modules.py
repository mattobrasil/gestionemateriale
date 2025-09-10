# modules.py
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from io import BytesIO

def carica_excel(file):
    
    # Carica file Excel, tiene solo le colonne utili (Nome, Città, Unità, Modello device, Seriale, Scadenza e settimane di giacenza. Rinomino le colonne
    
    colonne_da_tenere = [
        "Stock-Customer Name",
        "Stock-Customer City",
        "Total Invntry Units",
        "Material Hier 5 Number",
        "Batch Num",
        "Expiration Date",
        "Weeks"
    ]
    df = pd.read_excel(file, sheet_name=0, header=1, usecols=lambda x: x not in ['Unnamed: 0'])
    df = df[colonne_da_tenere]
    df = df.rename(columns={
        'Stock-Customer Name':'Name', 
        'Stock-Customer City':'City', 
        'Total Invntry Units':'Units', 
        'Material Hier 5 Number':'Device', 
        'Batch Num':'Batch', 
        'Expiration Date': 'Expiration'
    })
    return df

def rinomina_nomi_lunghi(df):
    
    # Rinomino i nomi lunghi con Fermo DHL di mezzo
    
    mappa_nomi = {
        'DE MICHELE DANILO - DHL POINT': 'DANILO DE MICHELE',
        'FERMO DHL - FEDERICA BALDAN': 'FEDERICA BALDAN',
        'FRANCESCA FRANCESE - FERMO DHL': 'FRANCESCA FRANCESE',
        'INNOVABEAT-UMBERTO RIVA': 'UMBERTO RIVA',
        'LEONARDO PERON - FERMO DHL': 'LEONARDO PERON',
        'LUCA PALLOTTA - FERMO DHL': 'LUCA PALLOTTA',
        'MEDISI-LUCA ARIOTA': 'LUCA ARIOTA',
        'PIERGUIDI-GIULIA LUSINI': 'GIULIA LUSINI',    
    }
    df['Name'] = df['Name'].replace(mappa_nomi)
    return df

def aggiungi_area(df):
    
    # Assegna a ogni città la sua area (1: Valle D'Aosta, Piemonte, Liguria, Emilia Romagna, Marche, Toscana, Sardegna; 2: Lombardia, Veneto, Friuli Venezia Giulia, Trentino Alto Adige; 3: Lazio, Umbria, Abruzzo, Molise, Basilicata, Puglia; 4: Campania, Calabria, Sicilia
    
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
    df.insert(0, 'Area', df['City'].map(mappa_aree))
    return df

def filtra_scaduti (df):
    
    # Prende i device già scaduti e li toglie dalla lista
    
    df["Expiration"] = pd.to_datetime(df["Expiration"], errors="coerce")
    today = pd.Timestamp(datetime.today().date())
    df = df[df['Expiration'] >= today]
    return df

def filtra_short(df, giorni_short=None):
    
    # Attiva il filtro short con scadenza = giorni_short (messo come input)
    
    df["Expiration"] = pd.to_datetime(df["Expiration"], errors="coerce")
    today = pd.Timestamp(datetime.today().date())
    df = df[df['Expiration'] >= today]
    if giorni_short:
        short = today + timedelta(days=giorni_short)
        df = df[(df["Expiration"] >= today) & (df["Expiration"] < short)]
    return df

def esporta_excel(df):
    
    # Esporta il file Excel
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()
    
def grafico_device_per_area(df, device_selezionati=None, normalizza=False):
    
    # Crea un bar plot in cui mostra quanti device di un certo modello ci sono per ogni area. Toggle per mostrare i device anche normalizzati per numero di persone che li possiedono per valutare le eccedenze
    
    if device_selezionati is None:
        device_selezionati = df["Device"].unique()
    
    # Filtra per device selezionati da sidebar
    
    df_grafico = df[df["Device"].isin(device_selezionati)].copy()
    
    # Assicura che le Aree siano numeri interi
    
    df_grafico["Area"] = df_grafico["Area"].astype(int)
    
    if df_grafico.empty:
        st.info("Seleziona almeno un Device per visualizzare il grafico")
        return
    
    if normalizza:
        
        # Conteggio e normalizzazione per numero di persone per Area
        
        counts = df_grafico.groupby(["Area", "Device"]).size().reset_index(name="Count")
        persone_per_area = df_grafico.groupby("Area")["Name"].nunique().reset_index(name="NumPeople")
        counts = counts.merge(persone_per_area, on="Area")
        counts["CountNormalized"] = counts["Count"] / counts["NumPeople"]
        
        fig = px.bar(
            counts,
            x="Area",
            y="CountNormalized",
            color="Device",
            barmode="group",
            title="Numero Device per Area (Normalizzato per persone)",
            labels={"CountNormalized": "Device per persona", "Area": "Area"}
        )
        
    else:
        counts = df_grafico.groupby(["Area", "Device"]).size().reset_index(name="Count")
        fig = px.bar(
            counts,
            x="Area",
            y="Count",
            color="Device",
            barmode="group",
            title="Numero di Device per Area",
            labels={"Count": "Numero dispositivi", "Area": "Area"}
        )
    
    # Ordina le Aree da 1 a 4
    
    fig.update_xaxes(type='category', categoryorder='array', categoryarray=sorted(df_grafico["Area"].unique()))
    fig.update_layout(xaxis_title="Area", yaxis_title="Conteggio")
    
    st.plotly_chart(fig, use_container_width=True)
    
def carica_indirizzi():
    
    # Funzione per caricare tutti gli indirizzi di spedizione dei colleghi in Italia
    
    data = [
    {"Area": 1, "Nome": "Federica Staunovo Polacco", "Via": "Via Niccolò Paganini, 14", "Città": "Settimo Torinese TO", "CAP": "10036", "Corriere": "DHL", "Telefono": " 3483348221"},
    {"Area": 1, "Nome": "Giorgia Odasso", "Via": "Via Niccolò Paganini, 14", "Città": "Settimo Torinese TO", "CAP": "10036", "Corriere": "DHL", "Telefono": " 3452529230"},
    {"Area": 1, "Nome": "Matteo Donno", "Via": "Piazza Gianbattista Bodoni, 1", "Città": "Torino", "CAP": "10123", "Corriere": "DHL", "Telefono": " 3471119312"},
    {"Area": 1, "Nome": "Roberta Angheleddu", "Via": "Via Niccolò Paganini, 14", "Città": "Decimoputzu SU", "CAP": "09010", "Corriere": "ind", "Telefono": " 3351678593"},
    {"Area": 1, "Nome": "Eugenio Capotorti", "Via": "Viale Francesco Bonaini 37", "Città": "Pisa", "CAP": "56125", "Corriere": "DHL", "Telefono": " 3492241644"},
    {"Area": 1, "Nome": "Stefano Pinciroli", "Via": "Aeroporto di Milano-Malpensa, Cargo City Sud, Edificio 236", "Città": "Lonate Pozzolo VA", "CAP": "21015", "Corriere": "DHL", "Telefono": " 3386623891"},
    {"Area": 1, "Nome": "Alessio Luciano", "Via": "Via Yuri Gagarin 165/B", "Città": "Monsummano Terme (PT)", "CAP": "51015", "Corriere": "ind", "Telefono": " 3384351379"},
    {"Area": 1, "Nome": "Giulia Lusini", "Via": "Via Pietro Nenni 112", "Città": "Monteriggioni (SI)", "CAP": "53035", "Corriere": "DHL", "Telefono": " 3313274113"},
    {"Area": 1, "Nome": "Luca Pallotta", "Via": "V. della Salute 95/8", "Città": "Bologna (BO)", "CAP": "40132", "Corriere": "DHL", "Telefono": "3426251080"},
    {"Area": 1, "Nome": "Elena Caroli", "Via": "Viale Dante 12/c", "Città": "Imola (BO)", "CAP": "40026", "Corriere": "DHL", "Telefono": "3492788049"},
    {"Area": 1, "Nome": "Jacopo Camilletti", "Via": "Via Germania 16", "Città": "Modena (MO)", "CAP": "41122", "Corriere": "DHL", "Telefono": "3456158764"},
    
    {"Area": 2, "Nome": "Lorenzo Alloni", "Via": "Via Dei Chiosi, 18", "Città": "Cavenago di Brianza (MB)", "CAP": "20873", "Corriere": "DHL", "Telefono": " 3425213747"},
    {"Area": 2, "Nome": "Isabella Brosadola", "Via": "Via Lombardia 2/A", "Città": "Peschiera Borromeo (MI)", "CAP": "20068", "Corriere": "DHL", "Telefono": " 3440407167"},
    {"Area": 2, "Nome": "Silvia Cutuli", "Via": "Via XX Settembre 4B", "Città": "Brescia", "CAP": "25122", "Corriere": "DHL", "Telefono": " 3402954109"},
    {"Area": 2, "Nome": "Clara Nozza", "Via": "Via Grassobbio, 2", "Città": "Azzano San Paolo (BG)", "CAP": "24052", "Corriere": "DHL", "Telefono": " 3477854192"},
    {"Area": 2, "Nome": "Matteo Saporiti", "Via": "Malpensa Cargo City Sud", "Città": "Lonate Pozzolo (VA)", "CAP": "21015", "Corriere": "DHL", "Telefono": "3357064038"},
    {"Area": 2, "Nome": "Mariachiara Ullo", "Via": "Via Cuneo, 3", "Città": "Segrate (MI)", "CAP": "20054", "Corriere": "DHL", "Telefono": "3488934332"},
    {"Area": 2, "Nome": "Maria Vittoria Gavazzi", "Via": "Via Pavia 24/26", "Città": "Muggiò (MB)", "CAP": "20835", "Corriere": "DHL", "Telefono": "3458378945"},
    {"Area": 2, "Nome": "Ilaria Monaco", "Via": "Via Pavia 24/26", "Città": "Muggiò (MB)", "CAP": "20835", "Corriere": "DHL", "Telefono": "3472221716"},
    {"Area": 2, "Nome": "Federica Baldan", "Via": "Via Inghilterra 16, complesso C", "Città": "Padova (PD)", "CAP": "35127", "Corriere": "DHL", "Telefono": "3401263039"},
    {"Area": 2, "Nome": "Leonardo Peron", "Via": "Via Inghilterra 16, complesso C", "Città": "Padova (PD)", "CAP": "35127", "Corriere": "DHL", "Telefono": "3485442477"},
    {"Area": 2, "Nome": "Mirco Ponzin", "Via": "Via Roma, 199", "Città": "Vigodarzere (PD)", "CAP": "35010", "Corriere": "DHL", "Telefono": "3387957014"},
    {"Area": 2, "Nome": "Andrea Galvagni", "Via": "Via Ca' Masotta 30", "Città": "Schio (VI)", "CAP": "36015", "Corriere": "ind", "Telefono": "3481323498"},
    {"Area": 2, "Nome": "Alice De Pietri", "Via": "Piazza Donatori di Sangue 1", "Città": "Cerea (VR)", "CAP": "37053", "Corriere": "DHL", "Telefono": "3482659757"},
    
    {"Area": 3, "Nome": "Matteo de Feo", "Via": "Via delle Moratelle 150", "Città": "Roma (RM)", "CAP": "00148", "Corriere": "DHL", "Telefono": "3451612282"},
    {"Area": 3, "Nome": "Iacopo Scandurra", "Via": "Via delle Moratelle 150", "Città": "Roma (RM)", "CAP": "00148", "Corriere": "DHL", "Telefono": "3426809246"},
    {"Area": 3, "Nome": "Chiara Baratta", "Via": "Via delle Moratelle 150", "Città": "Roma (RM)", "CAP": "00148", "Corriere": "DHL", "Telefono": "3482576085"},
    {"Area": 3, "Nome": "Francesca Francese", "Via": "Via delle Moratelle 150", "Città": "Roma (RM)", "CAP": "00148", "Corriere": "DHL", "Telefono": "3391015890"},
    {"Area": 3, "Nome": "Arianna Casini", "Via": "Viale Regina Margherita 40 (Negozio Caponnetto)", "Città": "Roma (RM)", "CAP": "00198", "Corriere": "ind", "Telefono": "3402203991"},
    {"Area": 3, "Nome": "Andrea Gigliati", "Via": "Via Gaspare Stampa 67", "Città": "Roma (RM)", "CAP": "00137", "Corriere": "ind", "Telefono": "3477535504"},
    {"Area": 3, "Nome": "Luigi Placentino", "Via": "Via Isonzo 73", "Città": "S. Giovanni Rotondo (FG)", "CAP": "71013", "Corriere": "ind", "Telefono": "3387912142"},
    {"Area": 3, "Nome": "Giuliano Micciullo", "Via": "Via Giovanni Paolo II", "Città": "Lecce (LE)", "CAP": "73100", "Corriere": "DHL", "Telefono": "3476147470"},
    {"Area": 3, "Nome": "Roberto Musarò", "Via": "Via Teano 35", "Città": "Galatina (LE)", "CAP": "73013", "Corriere": "ind", "Telefono": "3440413825"},
    
    {"Area": 4, "Nome": "Pierluigi De Felice", "Via": "Via Aniello Falcone 290/A", "Città": "Napoli (NA)", "CAP": "80127", "Corriere": "ind", "Telefono": "3491731241"},
    {"Area": 4, "Nome": "Alessandra Cantone", "Via": "Via Raffaele Morghen 36", "Città": "Napoli (NA)", "CAP": "80129", "Corriere": "ind", "Telefono": "3493595315"},
    {"Area": 4, "Nome": "Francesco Vistocco", "Via": "Viale colli aminei 10, Parco dei Gerani", "Città": "Napoli (NA)", "CAP": "80131", "Corriere": "ind", "Telefono": "3492431736"},
    {"Area": 4, "Nome": "Danilo De Michele", "Via": "Via Francesco Blundo 54", "Città": "Napoli (NA)", "CAP": "80128", "Corriere": "ind", "Telefono": "3386641827"},
    {"Area": 4, "Nome": "Simone Porcaro", "Via": "Via Norvegia 11", "Città": "Marano (NA)", "CAP": "80016", "Corriere": "ind", "Telefono": "3402150140"},
    {"Area": 4, "Nome": "Francesco Ricca", "Via": "", "Città": "", "CAP": "", "Corriere": "DHL", "Telefono": "3456499655"},
    {"Area": 4, "Nome": "Francesco Scarpinati", "Via": "Via Volturno 4", "Città": "Bellizzi (SA)", "CAP": "84092", "Corriere": "ind", "Telefono": "3397894334"},
    {"Area": 4, "Nome": "Giuseppe Gatti", "Via": "Via IV Novembre 7 c/o Lavanderia Primavera", "Città": "Calvi Risorta (CE)", "CAP": "81042", "Corriere": "ind", "Telefono": "3472496417"},
    {"Area": 4, "Nome": "Elisa Martello", "Via": "Via Passo Gravina, 183 A", "Città": "Catania", "CAP": "95125", "Corriere": "ind", "Telefono": "3408463474"},
    {"Area": 4, "Nome": "Luigi Valentino", "Via": "Zona industriale XIII strada", "Città": "Catania", "CAP": "95121", "Corriere": "DHL", "Telefono": "3491950982"},
    {"Area": 4, "Nome": "Federico Scicchitano", "Via": "Contrada serramonda", "Città": "Marcellinara (CZ)", "CAP": "88044", "Corriere": "DHL", "Telefono": "3429928617"},
    {"Area": 4, "Nome": "Claudio Lombardo", "Via": "Via Siracusa, 27", "Città": "Palermo", "CAP": "90141", "Corriere": "DHL", "Telefono": "3489696966"},
    {"Area": 4, "Nome": "Michele Rigano", "Via": "Via Vincenzo Leanza, 5", "Città": "Messina-Torre faro", "CAP": "98165", "Corriere": "ind", "Telefono": "3316476574"},
    {"Area": 4, "Nome": "Davide Tornabene", "Via": "Via De Nava, 32", "Città": "Reggio Calabria", "CAP": "89129", "Corriere": "DHL", "Telefono": "3429930110"},
    {"Area": 4, "Nome": "Davide Tornabene", "Via": "Campo Calabro", "Città": "Reggio Calabria", "CAP": "80127", "Corriere": "TNT", "Telefono": "3429930110"},
        
    ]
    return pd.DataFrame(data)

    
def aggiungi_categorie_device(df, device_mapping):
    df = df.copy()
    df["Categoria"] = df["Device"].map(
        lambda d: device_mapping.get(d, {}).get("Categoria", "NA")
    )
    df["Famiglia"] = df["Device"].map(
        lambda d: device_mapping.get(d, {}).get("Famiglia", "NA")
    )
    df["Da sostituzione"] = df["Device"].map(
        lambda d: device_mapping.get(d, {}).get("Da sostituzione", "NA")
    )
    return df

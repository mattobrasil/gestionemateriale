# modules.py
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

def carica_excel(file):
    """Carica Excel e mantiene solo colonne utili"""
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
    """Rinomina nomi lunghi nella colonna Name"""
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
    """Assegna un'area in base alla città"""
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
    df["Expiration"] = pd.to_datetime(df["Expiration"], errors="coerce")
    today = pd.Timestamp(datetime.today().date())
    df = df[df['Expiration'] >= today]
    return df

def filtra_short(df, giorni_short=None):
    """Filtra solo le date future, opzionalmente solo short"""
    df["Expiration"] = pd.to_datetime(df["Expiration"], errors="coerce")
    today = pd.Timestamp(datetime.today().date())
    df = df[df['Expiration'] >= today]
    if giorni_short:
        short = today + timedelta(days=giorni_short)
        df = df[(df["Expiration"] >= today) & (df["Expiration"] < short)]
    return df

def esporta_excel(df):
    """Esporta DataFrame in Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()



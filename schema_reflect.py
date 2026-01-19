# schema_reflect.py
# -----------------------------------------------------------------------------
# IN QUESTO FILE SI CARICA LO SCHEMA DEL DATABASE TRAMITE REFLECTION SQLALCHEMY
# PER POTER UTILIZZARE DIRETTAMENTE LE TABELLE SENZA DEFINIRE CLASSI ORM
# -----------------------------------------------------------------------------
#

from sqlalchemy import MetaData
from database import engine

# Carica tutte le tabelle del database usando la reflection di SQLAlchemy.
# Ritorna un oggetto MetaData con lo schema completo.

def schema_riflesso():
    meta = MetaData()
    meta.reflect(bind=engine)
    return meta

# Ritorna una tabella dallo schema riflesso.
# Se la tabella non esiste, mostra un errore e l’elenco di quelle presenti.

def ottieni_tabella(meta: MetaData, name: str):
    if name not in meta.tables:
        raise RuntimeError(f"Tabella '{name}' non trovata nel Database. Ho Trovato: {list(meta.tables.keys())}")
    return meta.tables[name]

# Controlla che nel database siano presenti tutte le tabelle richieste
# per il corretto funzionamento dell’applicativo.

def controllo_tabelle_richieste(meta: MetaData):
    required = [
        "Cliente", "ClientePrivato", "ClienteBusiness",
        "Dispositivo", "Riparazione", "Appuntamento",
        "Tecnico", "Intervento",
        "Ricambio", "Preventivo", "DettaglioPreventivo",
        "Pagamento", "Fornitore", "Fornitura",
        "Ordine", "DettaglioOrdine",
        "DocumentoFiscale", "Garanzia",
    ]
    missing = [t for t in required if t not in meta.tables] # Individua esventuali tabelle mancanti
    if missing:
        raise RuntimeError(
            "Nel Database mancano le tabelle richieste: "
            + ", ".join(missing)
            + "\nTabelle presenti: "
            + ", ".join(sorted(meta.tables.keys()))
        )

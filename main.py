# main.py
# -----------------------------------------------------------
# FILE PRINCIPALE DELL'APPLICATIVO
# Gestisce il menu, le operazioni CRUD e il collegamento al database.
# -----------------------------------------------------------
#

from __future__ import annotations
from datetime import datetime
from typing import Any
from sqlalchemy import select, func
from database import engine
from schema_reflect import schema_riflesso, controllo_tabelle_richieste
import queries

# -------------------------
# FUNZIONI DI SUPPORTO
# -------------------------


# Esegue una query SELECT e stampa tutte le righe ottenute.
# Serve solo per visualizzare i risultati a schermo.
def stampa_risultato(conn, stmt):
    rows = conn.execute(stmt).fetchall()
    if not rows:
        print("(nessun risultato)")
        return
    for r in rows:
        print(dict(r._mapping))

# Controlla se una colonna ha un valore di default
def colonna_ha_default(col) -> bool:
    return (col.default is not None) or (col.server_default is not None)

# Verifica se la PK è autoincrement
def pk_autoincrementa(col) -> bool:
    try:
        return bool(getattr(col, "autoincrement", False))
    except Exception:
        return False

# Calcola e inserisce la PK se non autoincrementa
def id_successivo(conn, table, pk_name: str) -> int:
    stmt = select(func.coalesce(func.max(table.c[pk_name]), 0) + 1)
    return int(conn.execute(stmt).scalar_one())

# converte l’input stringa dell’utente nel tipo corretto
def interprete(raw: str, col):
    raw = raw.strip()
    if raw == "":
        return None

# DateTime
    try:
        coltype = col.type.__class__.__name__.lower()
        if "datetime" in coltype:
            if len(raw) == 16:  # "YYYY-MM-DD HH:MM"
                raw = raw + ":00"
            return raw
    except Exception:
        pass

    py = getattr(col.type, "python_type", None)
    if py is None:
        return raw

    try:
        if py is int:
            return int(raw)
        if py is float:
            return float(raw)
        return raw
    except Exception:
        return raw

# inserisce una riga chiedendo solo i campi obbligatori
def inserisci_campi_richiesti(conn, table, preset: dict | None = None, pk_name: str | None = None):

    preset = dict(preset or {})
    cols = list(table.c)

# PK singola (se non fornita)
    if pk_name is None:
        pks = [c.name for c in cols if c.primary_key]
        pk_name = pks[0] if len(pks) == 1 else None

# se PK singola e non autoincrement, genero valore
    if pk_name and pk_name not in preset:
        pk_col = table.c[pk_name]
        if (not pk_autoincrementa(pk_col)) and (not colonna_ha_default(pk_col)):
            preset[pk_name] = id_successivo(conn, table, pk_name)

    data: dict[str, Any] = dict(preset)

    for col in cols:
        name = col.name

        if name in data:
            continue

# PK autoincrement o default => non richiesto
        if col.primary_key and pk_autoincrementa(col):
            continue
        if colonna_ha_default(col):
            continue

# nullable => si può lasciare vuoto
        if col.nullable:
            continue

# NOT NULL senza default => necessario
        prompt = f"Inserisci valore per {table.name}.{name} ({col.type}) [OBBLIGATORIO]: "
        raw = input(prompt)
        while raw.strip() == "":
            raw = input(prompt)
        data[name] = interprete(raw, col)

    if not data:
        raise RuntimeError(f"Insert vuoto su {table.name}: impossibile.")

    res = conn.execute(table.insert().values(**data))

    if pk_name:
        return data.get(pk_name, getattr(res, "lastrowid", None))
    return getattr(res, "lastrowid", None)


# --------------------------------------------------------------------------------
# INTERFACCIA UTENTE (lavora su riga di comando), non è prevista una GUI (per ora)
# --------------------------------------------------------------------------------

# Stampa il menu
def menu():
    print("\n=== ETIVITY 4 - collegata al DB MySQL tramite reflection ===")
    print("1) Dispositivi di un cliente (Privato o Business)")
    print("2) Riparazioni con appuntamento (JOIN, ordinate per data)")
    print("3) Appuntamenti di un cliente (Privato o Business)")
    print("4) Riparazioni con almeno un appuntamento (EXISTS)")
    print("5) Update stato riparazione")
    print("6) INSERT guidato (Cliente Privato/Business + Dispositivo + Riparazione + opz. Appuntamento)")
    print("0) Esci")

# punto centrale dell'applicativo
def main():
    meta = schema_riflesso()
    controllo_tabelle_richieste(meta)

# tabelle base
    Cliente = meta.tables["Cliente"]
    Dispositivo = meta.tables["Dispositivo"]
    Riparazione = meta.tables["Riparazione"]
    Appuntamento = meta.tables["Appuntamento"]

    while True:
        menu()
        scelta = input("Scelta: ").strip()

        if scelta == "0":
            print("Ciao, alla prossima!.")
            break

        try:
            with engine.begin() as conn:

                if scelta == "1":
                    print("\nTipo cliente per ricerca dispositivi:")
                    print("1) Privato (indicare nome+cognome)")
                    print("2) Business (indicare ragione sociale)")
                    t = input("Scelta (1/2): ").strip()

                    if t == "1":
                        nome = input("Nome: ").strip()
                        cognome = input("Cognome: ").strip()
                        stmt = queries.q_dispositivi_cliente_privato(meta, nome, cognome)
                        stampa_risultato(conn, stmt)
                    elif t == "2":
                        ragione = input("Ragione Sociale: ").strip()
                        stmt = queries.q_dispositivi_cliente_business(meta, ragione_sociale)
                        stampa_risultato(conn, stmt)
                    else:
                        print("Scelta non valida.")

                elif scelta == "2":
                    stmt = queries.q_riparazioni_con_appuntamento(meta)
                    stampa_risultato(conn, stmt)

                elif scelta == "3":
                    print("\nTipo cliente per ricerca appuntamenti:")
                    print("1) Privato (nome+cognome)")
                    print("2) Business (ragione sociale)")
                    t = input("Scelta (1/2): ").strip()

                    if t == "1":
                        nome = input("Nome: ").strip()
                        cognome = input("Cognome: ").strip()
                        stmt = queries.q_appuntamenti_cliente_privato(meta, nome, cognome)
                        stampa_risultato(conn, stmt)
                    elif t == "2":
                        ragione = input("Ragione Sociale: ").strip()
                        stmt = queries.q_appuntamenti_cliente_business(meta, ragione_sociale)
                        stampa_risultato(conn, stmt)
                    else:
                        print("Scelta non valida.")

                elif scelta == "4":
                    stmt = queries.q_riparazioni_con_appuntamento_exists(meta)
                    stampa_risultato(conn, stmt)

                elif scelta == "5":
                    idr = int(input("idRiparazione: ").strip())
                    stato = input("Nuovo stato: ").strip()
                    stmt = queries.update_stato_riparazione(meta, idr, stato)
                    res = conn.execute(stmt)
                    print("OK" if res.rowcount == 1 else "Nessuna riga aggiornata")

                elif scelta == "6":
                    print("\n--- INSERT GUIDATO (popola tutti i campi obbligatori dal tuo DB) ---")

                    # ----- scelta tipo cliente -----
                    print("\nTipo cliente:")
                    print("1) Privato")
                    print("2) Business")
                    tipo_sel = input("Scelta (1/2): ").strip()
                    if tipo_sel not in ("1", "2"):
                        raise RuntimeError("Tipo cliente non valido.")

                    tipo_cliente = "Privato" if tipo_sel == "1" else "Business"

                    # ----- 1) INSERT Cliente (padre) -----
                    preset_cliente = {}

                    # colonna tipoCliente
                    if "tipoCliente" in Cliente.c:
                        preset_cliente["tipoCliente"] = tipo_cliente


                    print("\n>> Inserimento Cliente")
                    id_cliente = inserisci_campi_richiesti(conn, Cliente, preset=preset_cliente, pk_name="idCliente")
                    print(f"Creato Cliente n. idCliente={id_cliente}")

                    # ----- 2) INSERT ClientePrivato / ClienteBusiness -----
                    if tipo_cliente == "Privato":
                        if "ClientePrivato" not in meta.tables:
                            raise RuntimeError("Tabella 'ClientePrivato' non trovata nel DB.")
                        ClienteSpec = meta.tables["ClientePrivato"]
                        print("\n>> Inserimento Cliente Privato")
                        preset_spec = {"idCliente": id_cliente}

                        # campi esempio
                        if "nome" in ClienteSpec.c:
                            v = input("Nome: ").strip()
                            if v:
                                preset_spec["nome"] = v
                        if "cognome" in ClienteSpec.c:
                            v = input("Cognome: ").strip()
                            if v:
                                preset_spec["cognome"] = v
                        if "codiceFiscale" in ClienteSpec.c:
                            v = input("Codice Fiscale (invio per saltare): ").strip()
                            if v:
                                preset_spec["codiceFiscale"] = v
                        if "telefono" in ClienteSpec.c:
                            v = input("numero di telefono (invio per saltare): ").strip()
                            if v:
                                preset_spec["telefono"] = v

                        inserisci_campi_richiesti(conn, ClienteSpec, preset=preset_spec, pk_name="idCliente")
                        print("Creato Cliente Privato")

                    else:
                        if "ClienteBusiness" not in meta.tables:
                            raise RuntimeError("Tabella 'ClienteBusiness' non trovata nel DB.")
                        ClienteSpec = meta.tables["ClienteBusiness"]
                        print("\n>> Inserimento ClienteBusiness")
                        preset_spec = {"idCliente": id_cliente}

                        if "ragioneSociale" in ClienteSpec.c:
                            v = input("Ragione Sociale: ").strip()
                            if v:
                                preset_spec["ragioneSociale"] = v
                        if "partitaIVA" in ClienteSpec.c:
                            v = input("Partita IVA (invio per saltare): ").strip()
                            if v:
                                preset_spec["partitaIVA"] = v
                        if "telefono" in ClienteSpec.c:
                            v = input("numero di telefono (invio per saltare): ").strip()
                            if v:
                                preset_spec["telefono"] = v

                        inserisci_campi_richiesti(conn, ClienteSpec, preset=preset_spec, pk_name="idCliente")
                        print("Creato ClienteBusiness")

                    # ----- 3) INSERT Dispositivo -----
                    print("\n>> Inserimento Dispositivo")
                    preset_disp = {"idCliente": id_cliente}

                    # tipo dispositivo: può chiamarsi tipo o tipoDispositivo
                    v_tipo = input("Tipo dispositivo (es. Smartphone/PC) [invio per saltare]: ").strip()
                    if v_tipo:
                        if "tipoDispositivo" in Dispositivo.c:
                            preset_disp["tipoDispositivo"] = v_tipo
                        elif "tipo" in Dispositivo.c:
                            preset_disp["tipo"] = v_tipo

                    if "marca" in Dispositivo.c:
                        v = input("Marca [invio per saltare]: ").strip()
                        if v:
                            preset_disp["marca"] = v
                    if "modello" in Dispositivo.c:
                        v = input("Modello [invio per saltare]: ").strip()
                        if v:
                            preset_disp["modello"] = v
                    if "numeroSerie" in Dispositivo.c:
                        v = input("Seriale [invio per saltare]: ").strip()
                        if v:
                            preset_disp["numeroSerie"] = v

                    id_disp = inserisci_campi_richiesti(conn, Dispositivo, preset=preset_disp, pk_name="idDispositivo")
                    print(f"Creato Dispositivo idDispositivo={id_disp}")

                    # ----- 4) INSERT Riparazione -----
                    print("\n>> Inserimento Riparazione")
                    preset_rip = {"idDispositivo": id_disp}

                    if "stato" in Riparazione.c:
                        preset_rip["stato"] = "Aperta"
                    if "dataIngresso" in Riparazione.c:
                        preset_rip["dataIngresso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    id_rip = inserisci_campi_richiesti(conn, Riparazione, preset=preset_rip, pk_name="idRiparazione")
                    print(f"Creata Riparazione idRiparazione={id_rip}")

                    # ----- 5) INSERT Appuntamento (opzionale) -----
                    add_app = input("Vuoi inserire un Appuntamento? (s/n): ").strip().lower()
                    if add_app == "s":
                        print("\n>> Inserimento Appuntamento")
                        preset_app = {"idRiparazione": id_rip}

                        if "dataOra" in Appuntamento.c:
                            dt_str = input("DataOra (YYYY-MM-DD HH:MM oppure YYYY-MM-DD HH:MM:SS): ").strip()
                            if len(dt_str) == 16:
                                dt_str += ":00"
                            preset_app["dataOra"] = dt_str

                        id_app = inserisci_campi_richiesti(conn, Appuntamento, preset=preset_app, pk_name="idAppuntamento")
                        print(f"Creato Appuntamento idAppuntamento={id_app}")

                    print("INSERT completato (transazione OK).")

                else:
                    print("Scelta non valida.")

        except Exception as e:
            print(f"ERRORE: {e}")


if __name__ == "__main__":
    main()

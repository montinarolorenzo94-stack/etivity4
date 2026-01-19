# queries.py
# -----------------------------------------------
# IN QUESTO FILE DEFINIAMO LE QUERIES
# -----------------------------------------------
#
from sqlalchemy import select, and_, exists, delete

# Restituisce i dispositivi (id, marca, modello) associati a un cliente business,
# filtrando per ragione sociale.

def q_dispositivi_cliente_business(meta, ragione_sociale):
    ClienteBusiness = meta.tables["ClienteBusiness"]
    Cliente = meta.tables["Cliente"]
    Dispositivo = meta.tables["Dispositivo"]

    stmt = (
        select(
            Dispositivo.c.idDispositivo,
            Dispositivo.c.marca,
            Dispositivo.c.modello
        )
        .select_from(
            ClienteBusiness
            .join(Cliente, ClienteBusiness.c.idCliente == Cliente.c.idCliente)
            .join(Dispositivo, Cliente.c.idCliente == Dispositivo.c.idCliente)
        )
        .where(ClienteBusiness.c.ragioneSociale == ragione_sociale)
    )
    return stmt

# Restituisce le date degli appuntamenti associati a un cliente business,
# ordinati per data, filtrando per ragione sociale.

def q_appuntamenti_cliente_business(meta, ragione_sociale):
    ClienteBusiness = meta.tables["ClienteBusiness"]
    Cliente = meta.tables["Cliente"]
    Dispositivo = meta.tables["Dispositivo"]
    Riparazione = meta.tables["Riparazione"]
    Appuntamento = meta.tables["Appuntamento"]

    stmt = (
        select(Appuntamento.c.dataOra)
        .select_from(
            ClienteBusiness
            .join(Cliente, ClienteBusiness.c.idCliente == Cliente.c.idCliente)
            .join(Dispositivo, Cliente.c.idCliente == Dispositivo.c.idCliente)
            .join(Riparazione, Dispositivo.c.idDispositivo == Riparazione.c.idDispositivo)
            .join(Appuntamento, Riparazione.c.idRiparazione == Appuntamento.c.idRiparazione)
        )
        .where(ClienteBusiness.c.ragioneSociale == ragione_sociale)
        .order_by(Appuntamento.c.dataOra.asc())
    )
    return stmt

# Restituisce i dispositivi (id, marca, modello) di un cliente privato,
# identificato tramite nome e cognome.

def q_dispositivi_cliente_privato(meta, nome, cognome):
    Dispositivo = meta.tables["Dispositivo"]
    ClientePrivato = meta.tables["ClientePrivato"]

    stmt = (
        select(Dispositivo.c.idDispositivo, Dispositivo.c.marca, Dispositivo.c.modello)
        .select_from(Dispositivo.join(ClientePrivato, Dispositivo.c.idCliente == ClientePrivato.c.idCliente))
        .where(and_(ClientePrivato.c.nome == nome, ClientePrivato.c.cognome == cognome))
    )
    return stmt

# Restituisce le riparazioni che hanno un appuntamento,
# mostrando i dati del cliente privato, del dispositivo e della riparazione,
# con ordinamento per data dell’appuntamento.

def q_riparazioni_con_appuntamento(meta):
    ClientePrivato = meta.tables["ClientePrivato"]
    Dispositivo = meta.tables["Dispositivo"]
    Riparazione = meta.tables["Riparazione"]
    Appuntamento = meta.tables["Appuntamento"]

    stmt = (
        select(
            ClientePrivato.c.nome,
            ClientePrivato.c.cognome,
            Dispositivo.c.marca,
            Dispositivo.c.modello,
            Riparazione.c.idRiparazione,
            Riparazione.c.stato,
            Appuntamento.c.dataOra
        )
        .select_from(
            ClientePrivato
            .join(Dispositivo, ClientePrivato.c.idCliente == Dispositivo.c.idCliente)
            .join(Riparazione, Dispositivo.c.idDispositivo == Riparazione.c.idDispositivo)
            .join(Appuntamento, Riparazione.c.idRiparazione == Appuntamento.c.idRiparazione)
        )
        .order_by(Appuntamento.c.dataOra.asc())
    )
    return stmt

# Restituisce le date degli appuntamenti associati a un cliente privato,
# identificato tramite nome e cognome, ordinate per data.

def q_appuntamenti_cliente_privato(meta, nome, cognome):
    ClientePrivato = meta.tables["ClientePrivato"]
    Cliente = meta.tables["Cliente"]
    Dispositivo = meta.tables["Dispositivo"]
    Riparazione = meta.tables["Riparazione"]
    Appuntamento = meta.tables["Appuntamento"]

    stmt = (
        select(Appuntamento.c.dataOra)
        .select_from(
            ClientePrivato
            .join(Cliente, ClientePrivato.c.idCliente == Cliente.c.idCliente)
            .join(Dispositivo, Cliente.c.idCliente == Dispositivo.c.idCliente)
            .join(Riparazione, Dispositivo.c.idDispositivo == Riparazione.c.idDispositivo)
            .join(Appuntamento, Riparazione.c.idRiparazione == Appuntamento.c.idRiparazione)
        )
        .where(and_(ClientePrivato.c.nome == nome, ClientePrivato.c.cognome == cognome))
        .order_by(Appuntamento.c.dataOra.asc())
    )
    return stmt

# Restituisce tutte le riparazioni che hanno almeno un appuntamento,
# utilizzando una sottoquery con EXISTS.

def q_riparazioni_con_appuntamento_exists(meta):
    Riparazione = meta.tables["Riparazione"]
    Appuntamento = meta.tables["Appuntamento"]

    sub = (
        select(1)
        .select_from(Appuntamento)
        .where(Appuntamento.c.idRiparazione == Riparazione.c.idRiparazione)
    )

    stmt = select(Riparazione).where(exists(sub))
    return stmt

# Aggiorna lo stato di una riparazione specifica,
# identificata tramite idRiparazione.

def update_stato_riparazione(meta, idRiparazione, nuovo_stato):
    Riparazione = meta.tables["Riparazione"]
    return (
        Riparazione.update()
        .where(Riparazione.c.idRiparazione == idRiparazione)
        .values(stato=nuovo_stato)
    )

# Elimina una riparazione e tutti i suoi appuntamenti associati
def delete_riparazione(meta, idRiparazione):
    Riparazione = meta.tables["Riparazione"]
    Appuntamento = meta.tables["Appuntamento"]

    # prima elimina gli appuntamenti
    stmt_app = delete(Appuntamento).where(
        Appuntamento.c.idRiparazione == idRiparazione
    )

    # poi elimina la riparazione
    stmt_rip = delete(Riparazione).where(
        Riparazione.c.idRiparazione == idRiparazione
    )

    return stmt_app, stmt_rip

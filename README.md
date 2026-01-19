# E-tivity 4 – Basi di Dati
Applicativo Python con database relazionale (SQLAlchemy)

---

## Scopo dell’E-tivity
Questa E-tivity consiste nello sviluppo di un applicativo Python che utilizza una base di dati
relazionale progettata nelle E-tivity precedenti (1, 2 e 3).  
L’obiettivo è mettere insieme **modellazione**, **SQL** e **programmazione**, usando
**SQLAlchemy** come ORM.

Il caso di studio scelto è un **Centro Riparazioni**, con gestione di:

 clienti privati
- clienti business
- dispositivi
- riparazioni
- appuntamenti

---

## Struttura del progetto

```
main.py              # Menu e logica principale
database.py          # Connessione al database MySQL
schema_reflect.py    # Reflection dello schema DB
queries.py           # Query SQLAlchemy
README.md            # Questo file
```

---

## Descrizione generale

L’applicativo è a **menu testuale** e permette di interrogare e modificare il database.
Non ci sono classi ORM, ma si lavora direttamente sulle tabelle tramite **reflection**,
come richiesto dall’E-tivity.

Il sistema gestisce clienti **Privati** e **Business** tramite una struttura ISA
(entità padre Cliente + entità figlie).

---

## Funzionalità disponibili

Dal menu principale è possibile:

1. Visualizzare i dispositivi di un cliente  
   - cliente privato (nome e cognome)  
   - cliente business (ragione sociale)

2. Visualizzare le riparazioni che hanno un appuntamento  
   - uso di JOIN  
   - risultati ordinati per data

3. Visualizzare gli appuntamenti di un cliente  
   - privato o business

4. Visualizzare le riparazioni che hanno almeno un appuntamento  
   - uso di EXISTS

5. Aggiornare lo stato di una riparazione  
   - operazione UPDATE

6. Inserimento guidato dei dati  
   - cliente (privato o business)  
   - dispositivo  
   - riparazione  
   - appuntamento (opzionale)

---

## Operazioni CRUD

- **Create**: inserimento guidato di tutte le entità principali  
- **Read**: interrogazioni con JOIN ed EXISTS  
- **Update**: modifica dello stato di una riparazione  
- **Delete**: gestita a livello ORM (non esposta nel menu)

---

## Avvio dell’applicativo

1. Configurare i parametri di connessione in `database.py`
2. Avviare il database MySQL
3. Eseguire:

```bash
python main.py
```

---

## Autore
Studente: Montinaro Lorenzo  

E-tivity 4 – Basi di Dati  

# Jobbot AI
## Assistente IA per la ricerca di lavoro

### Introduzione
**Jobbot AI** è un progetto realizzato al termine di un percorso didattico incentrato sullo sviluppo tramite linguaggio Python e, in particolare, su concetti di *data automation*. 
In quanto tale, questo programma ha il mero scopo didattico e di apprendimento.

  
### Descrizione del codice
Il codice si basa su un utilizzo combinato delle librerie Selenium e OpenAI, oltre che dei tools di openAI, ed implementa una conversazione
dinamica e interattiva tra l'utente e un assistente virtuale (Jobbot) per la ricerca di lavoro.  
La conversazione è suddivisa in più fasi:  
- **Fase 1. Caricamento del CV in formato PDF:** Inizialmente, il programma richiederà l'inserimento di un CV in formato PDF (che, tuttavia, non è obbligatorio ai fini della conversazione).  
- **Fase 2. Lettura del CV da parte dell'IA:** Se caricato, si potrà chiedere la lettura, da parte dell'IA, delle informazioni contenute nel CV (primo tool), oppure si potrà avviare
la chat con Jobbot partendo direttamente dalla fase successiva.  
- **Fase 3. Web scraping degli annunci su Linkedin:** A questo punto, l'utente potrà chiedere a Jobbot di generare due parole chiave, necessarie per il secondo tool,
inerenti il ruolo e la località desiderati per la ricerca di lavoro. Queste possono essere generate indifferentemente tramite input dell'utente, che fornisce all'IA le informazioni necessarie,
o tramite le informazioni contenute nel CV stesso.  
Le due parole chiave verranno utilizzate dal secondo tool, che sfrutta Selenium per raccogliere le informazioni 
relative a tutti gli annunci di lavoro trovati su Linkedin utilizzando il ruolo e la località generati in questa fase.  
- **Fase 4. Secondo web scraping su Linkedin per la raccolta delle descrizioni:** Ora che l'utente conosce la lista di annunci, può decidere di approfondirne uno in particolare
richiamando il terzo tool, che utilizza Selenium per ottenere l'intera descrizione dell'offerta di lavoro. Avendo memoria dei messaggi precedenti, è possibile chiedere ulteriori
informazioni su qualunque annuncio trovato.  
- **Fase 5. Calcolo dell'affinità:** L'ultimo tool permette, sulla base delle informazioni contenute nel CV e sulla base dei requisiti dell'annuncio di lavoro, di valutare
l'affinità del proprio profilo con la figura richiesta dall'annuncio.

### Requisiti
- Python 3.10+
- Librerie Python: selenium, python-dotenv, openai, os, time, json, random, re, pypdf, tkinter, shutil
- Chrome WebDriver installato e compatibile con la tua versione di Chrome
  
### Configurazione
- Crea un file .env con la tua API key: "OPENAI_API_KEY=your_api_key"
- Installa le dipendenze: "pip install selenium python-dotenv openai"
- Assicurati che ChromeDriver sia nel PATH.

  
### Possibili sviluppi  
Sono molteplici i possibili sviluppi e migliorie, tra cui:  
- Sviluppo di un front-end,  con una GUI che renda la conversazione più intuitiva.
- Integrazione di più piattaforme per il lavoro (Indeed, Glassdoors, etc.) per estendere la ricerca.
- Una fase di valutazione dell'affinità del profilo utente più articolata (che includa, ad esempio, esperienze lavorative, soft-skills, percorso di studi, certificazioni) e più robusta.
- Diminuzione del costo computazionale dei processi per rendere la conversazione più fluida.
- Generazione di lettere di presentazione personalizzate in base al profilo utente e al ruolo scelto.


### Contatti  
Per qualunque informazione, contattare: stemallus97@gmail.com



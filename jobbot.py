from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from openai import OpenAI
import os
from dotenv import load_dotenv
import time as t
import json
import random
import re
import pypdf
from tkinter import filedialog
import shutil
import os


def upload_cv(cv_path):
    """"
    Funzione che carica il documento PDF contenente il CV e lo salva nella repo indicata.
    """
    file_path = filedialog.askopenfilename(
        title="Carica il tuo CV",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not file_path:
        print("Nessun file selezionato")
        return None

    shutil.copy(file_path, cv_path)
    print(f"CV salvato in: {cv_path}")


def extract_pdf (cv_path):
    """
    Funzione che estrae le informazioni contenute in un documento in formato PDF e restituisce una stringa
    """
    cv_str = ""
    try:
        with open(cv_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                cv_str += page.extract_text() + "\n"
    except:
        pass
    finally:
        return cv_str


def init_driver():
    """
    Funzione che inizializza il driver.
    """
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver


def site_preparation(driver, wait):
    """
    Funzione che prepara il sito (Linkedin) per poter inserire i parametri di ricerca.
    """
    deny_button = wait.until(ec.element_to_be_clickable((By.XPATH,'//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[2]')))
    deny_button.click()

    cerca_lavoro_button = wait.until(ec.element_to_be_clickable((
        By.CSS_SELECTOR,
        'a[data-tracking-control-name="guest_homepage-basic_guest_nav_menu_jobs"]'
        )))
    cerca_lavoro_button.click()
    dismiss_icon = wait.until(ec.element_to_be_clickable((By.CLASS_NAME,'contextual-sign-in-modal__modal-dismiss-icon')))
    dismiss_icon.click()

    #Occorre fare un primo Submit perchè altrimenti non è impossibile settare la località
    submit_button = wait.until(ec.element_to_be_clickable((By.XPATH,'//*[@id="jobs-search-panel"]/form/button')))
    submit_button.click()


def set_search_parameters(ruolo, luogo, driver, wait):
    """
    Funzione che setta i parametri di ricerca: ruolo e location
    """
    #Barra di ricerca: parole chiave ruolo
    search_bar = wait.until(ec.element_to_be_clickable((By.ID, 'job-search-bar-keywords')))
    search_bar.click()
    search_bar.clear()
    for elem in ruolo:
        search_bar.send_keys(elem)
        t.sleep(random.uniform(0.1,0.3))       #Simula un input "umano"
    t.sleep(1)

    #Barra di ricerca: località
    location_bar = driver.find_element(By.ID,'job-search-bar-location')
    location_bar.click()
    t.sleep(1)
    location_bar.clear()
    location_bar.click()
    t.sleep(1)
    for el in luogo:
        location_bar.send_keys(el)
        t.sleep(random.uniform(0.1,0.3))    #Simula un input "umano"
    t.sleep(2)
    location_bar.send_keys(Keys.ENTER)
    t.sleep(2)


def get_adv_cards_info(driver,wait):
    """
    Funzione che raccoglie le informazioni di ogni annuncio e restituisce una lista di dizionari con: 
    - Codice
    - Titolo annuncio
    - Azienda
    - Location
    - Quando è stato pubblicato l'annuncio
    - Descrizione dell'annuncio
    """
    lista_annunci = []
    try:
        lista_cards_annunci = wait.until(ec.presence_of_element_located((By.CLASS_NAME,'jobs-search__results-list')))
        cards_annunci = lista_cards_annunci.find_elements(By.CLASS_NAME,'base-card')
        for i,annuncio in enumerate(cards_annunci, start=1):
            info_annuncio = {}
            info_card = annuncio.find_element(By.CLASS_NAME,'base-search-card__info')
            info_annuncio_str = info_card.text    #Trova le informazioni testuali della card
            info_annuncio = {}
            info_annuncio['codice'] = i
            info_annuncio_list = info_annuncio_str.split("\n")
            info_annuncio['titolo'] = info_annuncio_list[0]
            info_annuncio['azienda'] = info_annuncio_list[1]
            info_annuncio['localita'] = info_annuncio_list[2]
            regex = '[0-9]'
            if re.match(regex,info_annuncio_list[3]) is None:
                info_annuncio['pubblicato'] = info_annuncio_list[4]
            else:
                info_annuncio['pubblicato'] = info_annuncio_list[3]
            t.sleep(0.5)
            #Append del dizionario alla lista degli annunci
            lista_annunci.append(info_annuncio)
        
        return lista_annunci    
    except Exception as e:
        pass


def get_description (driver,wait):
    """
    Funzione che ottiene la descrizione completa dell'annuncio di lavoro cercato.
    """
    lista_cards_annunci = wait.until(ec.presence_of_element_located((By.CLASS_NAME,'jobs-search__results-list')))
    cards_annunci = lista_cards_annunci.find_elements(By.CLASS_NAME,'base-card')
    cards_annunci[0].click()
    sezione_pagina_annuncio = driver.find_element(By.CLASS_NAME,"two-pane-serp-page__detail-view")
    t.sleep(0.5)
    driver.execute_script(
        "arguments[0].scrollBy(0, 500);", sezione_pagina_annuncio
    )
    t.sleep(0.5)
    show_more_button = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, 'show-more-less-html__button')))
    show_more_button.click()
    job_description = driver.find_element(By.CLASS_NAME,'show-more-less-html__markup')
    job_description_str = job_description.text
    t.sleep(0.5)
    return job_description_str


def start_scraping(ruolo, luogo):
    """
    Questa funzione esegue lo scraping delle offerte di lavoro su Linkedin. 
    Restituisce una lista di dizionari con tutte le informazioni delle card relative agli annunci.
    """
    URL = "https://it.linkedin.com/"
    driver = init_driver()
    try:
        driver.get(URL)
        wait = WebDriverWait(driver,5)
        t.sleep(2)

        #Preparazione di Linkedin
        site_preparation(driver,wait)

        #Settaggio dei parametri
        set_search_parameters(ruolo,luogo,driver,wait)

        #Raccolta informazioni
        lista_annunci = get_adv_cards_info(driver,wait)

        t.sleep(2)
    except Exception as e:
        print(f"Si è verificato un errore: {e}")  # Stampa l'errore se qualcosa va storto
    finally:
        driver.quit()  # Chiude il browser e termina il WebDriver
        return lista_annunci


def find_adv_description (ruolo,azienda,luogo):
    """
    Questa funzione esegue lo scraping delle offerte di lavoro su Linkedin. 
    Restituisce la descrizione di una specifica offerta di lavoro.
    """
    URL = "https://it.linkedin.com/"
    driver = init_driver()
    job_description_str = ""
    try:
        driver.get(URL)
        wait = WebDriverWait(driver,5)
        t.sleep(2)

        #Preparazione di Linkedin
        site_preparation(driver,wait)

        #Settaggio dei parametri
        posizione = ruolo + " " + azienda
        set_search_parameters(posizione,luogo,driver,wait)

        #Lettura descrizione
        job_description_str = get_description(driver,wait)

    except Exception as e:
        print(f"Si è verificato un errore: {e}")  # Stampa l'errore se qualcosa va storto
    finally:
        driver.quit()  # Chiude il browser e termina il WebDriver
        return job_description_str


def check_affinity(skills_cv, skills_job):
    """
    Funzione che interroga l'IA per confrontare l'elenco di skills dell'utente e quello richiesto dall'annuncio
    per valutare l'affinità del profilo.
    """
    risposta = client.responses.create(
        model="gpt-4.1-nano",
        input=f"Fai un confronto tra {skills_cv} e {skills_job}, che sono liste di skill dell'utente e di skill richieste dall'annuncio di lavoro, rispettivamente."
                "Valuta quante skill richieste dall'annuncio vengono matchate dalle skill dell'utente." 
                "Non valutare in maniera letterale. Ad esempio: Se il CV dice 'Python' e l'annuncio dice 'Linguaggo Python'" \
                "allora il match si avvera. Quindi il match vale anche per sinonimi o espressioni semanticamente affini." \
                "Se ottieni più match per la stessa skill_job, considerane solo una. Non devi ottenere più del 100percento di affinita-"
                "L'output deve essere la percentuale di skill_job matchate sul totale."
    ).output_text

    return risposta

# ============================================================================
# CONVERSAZIONE CON IA
# ============================================================================
# ----------------------------------------------------------------------------
# DEFINIZIONE DEI TOOLS PER OPENAI
# ----------------------------------------------------------------------------
tools = [
    {
        "type": "function",
        "name": "extract_pdf",  #Estrae le informazioni contenute nel PDF
        "description": "Legge il file PDF contenente il CV e restituisce una stringa con le informazioni contenute nel PDF",
        "parameters": {
            "type": "object",
            "properties": {
                "cv_path": {
                    "type": "string",
                    "description": "Percorso nel quale è salvato il file PDF col CV",
                },
            },
            "required": ["cv_path"],  # Tutti obbligatori
            "additionalProperties": False,  # Non accetta parametri extra
        },
        "strict": True,  # Abilita "Structured Outputs" per garantire formato corretto
    },
    {
        "type": "function",
        "name": "start_scraping",  #Cerca gli annunci di lavoro per quella posizione e località
        "description": "Esegue lo scraping di offerte di lavoro su Linkedin sulla base di parametri inerenti ruolo e location.",
        "parameters": {
            "type": "object",
            "properties": {
                "ruolo": {
                    "type": "string",
                    "description": "Ruolo o posizione da cercare. Assicurati che sia un ruolo sensato",
                },
                "luogo": {
                    "type": "string",
                    "description": "Luogo in cui si desidera trovare le offerte di lavoro. Assicurati che sia un luogo sensato",
                },
            },
            "required": ["ruolo", "luogo"],  # Tutti obbligatori
            "additionalProperties": False,  # Non accetta parametri extra
        },
        "strict": True,  # Abilita "Structured Outputs" per garantire formato corretto
    },
    {
        "type": "function",
        "name": "find_adv_description",  #Cerca la descrizione di uno specifico annuncio di lavoro
        "description": "Sulla base della lista di dizionari inerenti lavori ottenuta, esegue lo scraping"
                        "dell'offerta data dalla chiave titolo dell'annuncio, azienda e location, per andare"
                        "a trovare la descrizione dell'annuncio di lavoro",
        "parameters": {
            "type": "object",
            "properties": {
                "ruolo": {
                    "type": "string",
                    "description": "Cerca la chiave 'titolo' dell' elemento della lista di annunci desiderato",
                },
                "azienda": {
                    "type": "string",
                    "description": "Cerca la chiave 'azienda' dell' elemento della lista di annunci desiderato",
                },
                "luogo": {
                    "type": "string",
                    "description": "Cerca la chiave 'localita' dell' elemento della lista di annunci desiderato",
                },
            },
            "required": ["ruolo","azienda","luogo"],  # Tutti obbligatori
            "additionalProperties": False,  # Non accetta parametri extra
        },
        "strict": True,  # Abilita "Structured Outputs" per garantire formato corretto
    },
    {
        "type": "function",
        "name": "check_affinity", 
        "description": "Sulla base della lista di skill del profilo utente e la lista di skill richieste dall'annuncio,"
                        "valuta l'affinita del profilo utente e dell'annuncio di lavoro desiderato.",
        "parameters": {
            "type": "object",
            "properties": {
                "skills_cv": {
                    "type": "array",
                    "items":{
                        "type":"string"
                    },
                    "description": "Lista di stringhe corrispondenti alle skill del profilo utente",
                },
                "skills_job": {
                    "type": "array",
                    "items":{
                        "type":"string"
                    },
                    "description": "Lista di stringhe corrispondenti alle skill richieste dall'annuncio",
                },
            },
            "required": ["skills_cv","skills_job"],  # Tutti obbligatori
            "additionalProperties": False,  # Non accetta parametri extra
        },
        "strict": True,  # Abilita "Structured Outputs" per garantire formato corretto
    },
]


# ----------------------------------------------------------------------------
# GESTIONE DELLA CONVERSAZIONE CON TOOL
# ----------------------------------------------------------------------------
def ask_jobbot(messages):
    response = client.responses.create(
        model="gpt-4.1-nano",  # Modello veloce ed economico (puoi usare anche "gpt-4o")
        input=messages,  # Messaggi della conversazione
        tools=tools,  # Tool disponibili (lo scraping)
    )

    if not response.output or response.output[0].type != "function_call":
        return response.output_text

    tool_call = response.output[0]
    print("=================================================================")
    print(f"[DEBUG] Ha chiamato il tool: {tool_call.name}")
    print(f"[DEBUG] Argomenti grezzi: {tool_call.arguments}")
    print("=================================================================")

    args = json.loads(tool_call.arguments)

    if tool_call.name == 'extract_pdf':
        tool_result = extract_pdf(**args)
    elif tool_call.name == "start_scraping":
        tool_result = start_scraping(**args)  # **args "spacchetta" il dizionario
    elif tool_call.name == "find_adv_description":
        tool_result = find_adv_description(**args)
    elif tool_call.name == "check_affinity":
        tool_result = check_affinity(**args)
    else:
        tool_result = {"error": f"Tool {tool_call.name} non implementato nel backend."}

    messages.append(
        {
            "type": "function_call",
            "name": tool_call.name,
            "arguments": tool_call.arguments,
            "call_id": tool_call.call_id,  # ID univoco per tracciare la chiamata
        }
    )

    messages.append(
        {
            "type": "function_call_output",    #function_call_output
            "call_id": tool_call.call_id,  # Deve corrispondere alla chiamata
            "output": json.dumps(tool_result),  # Convertiamo il risultato in JSON
        },
    )
    
    final_response = client.responses.create(
        model="gpt-4.1-nano",
        input=messages,  # Conversazione completa con tool call e risultato
        tools=tools,
    )
    
    return final_response.output_text


cv_path = "Stefano_Mallus/CV.pdf"

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================================
# PUNTO DI INGRESSO: INTERFACCIA A LINEA DI COMANDO
# ============================================================================
if __name__ == "__main__":
    """
    Crea un semplice loop interattivo dove l'utente può fare domande
    e ricevere risposte dall'assistente.
    """
    print("=====================================================================")
    print("                            ASK JOBBOT")
    print("=====================================================================")
    print("Per trovare il lavoro dei tuoi sogni, prima carica il tuo CV!\n")
    upload_cv(cv_path)
    print("\nStai parlando con l'assistente Jobbot (digita 'esci' per uscire).\n")
    messages = [
        {
            "role": "system",
            "content": "Sei un consulente del lavoro. Per prima cosa, leggi il CV caricato (se presente) "
                        f"dal path {cv_path} e cerchi due parole chiave"
                        "inerenti 'ruolo' da cercare e 'località' e mostrale all'utente. "
                        "Se nessuna informazione viene ottenuta dal CV, chiedi all'utente di inserire "
                        "manualmente i dati. "
                        "Estratte le informazioni del CV, fai un riepilogo del profilo descritto dal CV e stampa"
                        "le due parole chiave, chiedendo all'utente se è soddisfatto."
                        "Ogni volta che ottieni dei nuovi dati devi fare un riepilogo con quei dati."
        }
    ]
    # Loop infinito finché l'utente non digita 'exit'
    while True:
        user_msg = input("Tu: ")

        # Controlla se l'utente vuole uscire
        if user_msg.lower().strip() in {"exit", "quit", "esci"}:
            break
        
        messages.append({
            "role": "user",
            "content": user_msg
            })

        # Chiama l'assistente e stampa la risposta
        answer = ask_jobbot(messages)

        messages.append({
            "role": "assistant",
            "content": answer
            })

        print(f"\nJobbot: {answer}\n")
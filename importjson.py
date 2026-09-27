import cloudscraper
import xml.etree.ElementTree as ET
import json
import time

URL_RSS = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
FILE_OUTPUT = "avvisi_richiami_osa.json"

def scarica_modalita_stealth():
    print("🚀 Avvio di CloudScraper (simulatore di browser avanzato)...")
    
    # Questo crea una sessione che imita matematicamente Google Chrome su Windows
    # Inganna il sistema Cloudflare/Akamai facendogli credere che siamo un utente reale
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    try:
        # Aggiungiamo un timestamp per forzare il server a non darci file vecchi
        url_dinamico = f"{URL_RSS}?_={int(time.time())}"
        print(f"🌐 Infiltrazione nel server del Ministero in corso: {URL_RSS}")
        
        response = scraper.get(url_dinamico, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Il server ha risposto con un codice di errore HTTP: {response.status_code}")
            return
            
        raw_data = response.content.decode('utf-8-sig', errors='ignore').strip()
        
        # Verifica se ci hanno scoperto e bloccato lo stesso
        if raw_data.lower().startswith("<!doctype html") or "<html" in raw_data.lower()[:50]:
            print("❌ BLOCCO ESTREMO: Il Ministero ha riconosciuto l'IP del datacenter di GitHub nonostante CloudScraper.")
            print("Risposta ricevuta dal server (HTML):")
            print(raw_data[:200])
            return
            
        # Pulisce l'inizio dell'XML
        inizio_xml = raw_data.find("<?xml")
        if inizio_xml == -1:
            inizio_xml = raw_data.find("<rss")
        if inizio_xml > 0:
            raw_data = raw_data[inizio_xml:]
            
        print("🔍 Decodifica XML in corso...")
        root = ET.fromstring(raw_data)
        
        notifiche = []
        for item in root.findall(".//item"):
            notifica = {
                "title": item.findtext("title", default="").strip(),
                "link": item.findtext("link", default="").strip(),
                "description": item.findtext("description", default="").strip(),
                "pubDate": item.findtext("pubDate", default="").strip(),
                "guid": item.findtext("guid", default="").strip()
            }
            notifiche.append(notifica)
            
        print(f"📊 Trovati {len(notifiche)} avvisi nel feed RSS!")
        
        output = {"notifiche_italia": notifiche}
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        print(f"✅ File '{FILE_OUTPUT}' creato e salvato con successo!")
        
    except ET.ParseError as e:
        print(f"❌ Errore durante la conversione XML: {e}")
    except Exception as e:
        print(f"❌ Errore di connessione o esecuzione: {e}")

if __name__ == "__main__":
    scarica_modalita_stealth()

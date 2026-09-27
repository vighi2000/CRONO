import requests
import xml.etree.ElementTree as ET
import json
import os

URL_RSS = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
FILE_OUTPUT = "avvisi_richiami_osa.json"

def scarica_e_converti_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, come Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*;q=0.9",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }

    try:
        print(f"🌐 Connessione in corso a: {URL_RSS}")
        response = requests.get(URL_RSS, headers=headers, timeout=30)
        response.raise_for_status()

        # 1. RISOLUZIONE DELL'ERRORE LINE 1, COLUMN 0:
        # Decodifica forzata per rimuovere il BOM (Byte Order Mark) e tagliare spazi o a capo iniziali
        raw_data = response.content.decode('utf-8-sig', errors='ignore').strip()

        if not raw_data:
            print("❌ Errore: Il server del Ministero ha risposto, ma ha inviato un file completamente vuoto.")
            return

        # 2. CONTROLLO FIREWALL/BLOCCO IP:
        # Se la risposta inizia con un tag HTML anziché XML, GitHub è bloccato
        if raw_data.lower().startswith("<!doctype html") or "<html" in raw_data.lower()[:50]:
            print("❌ BLOCCO FIREWALL: Il server del Ministero sta bloccando l'IP di GitHub Actions.")
            print("Invece del feed RSS XML, ha restituito questa pagina web:")
            print(f"---\n{raw_data[:300]}...\n---")
            return

        # 3. FORZA LA LETTURA DALL'INIZIO DELL'XML:
        # Trova esattamente dove inizia il codice XML saltando ogni spazzatura iniziale
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

        print(f"📊 Trovati {len(notifiche)} avvisi nel feed RSS.")

        output = {"notifiche_italia": notifiche}
        
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ File '{FILE_OUTPUT}' creato e salvato con successo!")

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore HTTP o di Connessione: {e}")
    except ET.ParseError as e:
        print(f"❌ Errore di parsing XML: {e}")
        # Stampa i primi 200 caratteri per farti vedere COSA ha causato l'errore se dovesse ripetersi
        print(f"🔍 Il parser è andato in errore leggendo questo contenuto:\n{raw_data[:200]}")
    except Exception as e:
        print(f"❌ Errore generico: {e}")

if __name__ == "__main__":
    scarica_e_converti_rss()

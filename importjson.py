import requests
import xml.etree.ElementTree as ET
import json
import os

# URL del feed RSS ufficiale del Ministero della Salute
URL_RSS = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
FILE_OUTPUT = "avvisi_richiami_osa.json"

def scarica_e_converti_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*"
    }

    try:
        print(f"🌐 Connessione a: {URL_RSS}")
        response = requests.get(URL_RSS, headers=headers, timeout=30)
        response.raise_for_status()

        # Verifica che il contenuto non sia vuoto
        if not response.text.strip():
            print("❌ Errore: Il server ha restituito una risposta vuota.")
            return

        print("🔍 Decodifica XML in corso...")
        # Parsing dell'XML direttamente dal testo scaricato
        root = ET.fromstring(response.content)

        notifiche = []

        # Scansione di ciascun elemento <item> presente nel canale RSS
        for item in root.findall(".//item"):
            notifica = {
                "title": item.findtext("title", default="").strip(),
                "link": item.findtext("link", default="").strip(),
                "description": item.findtext("description", default="").strip(),
                "pubDate": item.findtext("pubDate", default="").strip(),
                "guid": item.findtext("guid", default="").strip()
            }
            notifiche.append(notifica)

        print(f"📊 Trovati {len(notifiche)} avvisi/richiami nel feed RSS.")

        # Struttura output JSON per l'applicazione
        output = {
            "notifiche_italia": notifiche
        }

        # Salvataggio nel file JSON
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ File '{FILE_OUTPUT}' creato e salvato con successo!")

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore durante il download del feed RSS: {e}")
    except ET.ParseError as e:
        print(f"❌ Errore di parsing XML (il file scaricato non è XML valido): {e}")
    except Exception as e:
        print(f"❌ Errore generico: {e}")

if __name__ == "__main__":
    scarica_e_converti_rss()

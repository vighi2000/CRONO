import requests
import json
import time

# Usiamo il servizio gratuito rss2json per fare da "ponte" e aggirare il firewall del Ministero
URL_RSS = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
API_URL = f"https://api.rss2json.com/v1/api.json?rss_url={URL_RSS}"
FILE_OUTPUT = "avvisi_richiami_osa.json"

def scarica_tramite_proxy():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, come Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        print(f"🌐 Connessione al proxy rss2json per aggirare il blocco IP...")
        # Aggiungiamo un timestamp casuale per forzare il server a darci i dati più recenti (evitare la cache)
        url_dinamico = f"{API_URL}&_={int(time.time())}"
        
        response = requests.get(url_dinamico, headers=headers, timeout=30)
        response.raise_for_status()

        dati = response.json()

        # Controllo se rss2json è riuscito a leggere il feed
        if dati.get("status") != "ok":
            print(f"❌ Errore del proxy: Impossibile leggere l'RSS. Dettagli: {dati.get('message', 'Sconosciuto')}")
            return

        items = dati.get("items", [])
        print(f"📊 Trovati {len(items)} avvisi tramite il proxy.")

        # Adattiamo i dati alla struttura che ti serve (stessi nomi del vecchio script)
        notifiche = []
        for item in items:
            notifica = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "description": item.get("description", ""),
                "pubDate": item.get("pubDate", ""),
                "guid": item.get("guid", "")
            }
            notifiche.append(notifica)

        output = {"notifiche_italia": notifiche}
        
        # Salviamo il file
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ File '{FILE_OUTPUT}' creato e salvato con successo!")

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore di connessione al proxy: {e}")
    except json.JSONDecodeError:
        print("❌ Errore: Il proxy ha risposto, ma non con un formato JSON valido.")
    except Exception as e:
        print(f"❌ Errore generico: {e}")

if __name__ == "__main__":
    scarica_tramite_proxy()

import json
import time
import xml.etree.ElementTree as ET
import requests

RSS_URL = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
OUTPUT_JSON = "avvisi_richiami_osa.json"
INTERVALLO_ORE = 24  # Frequenza di aggiornamento automatico


def aggiorna_json():
  print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Tentativo di connessione...")

  # Header completi per simulare un browser reale ed evitare i blocchi del ministero
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
      "Accept": (
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
      ),
      "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
      "Referer": "https://www.salute.gov.it/",
      "Connection": "keep-alive",
  }

  try:
    # Eseguiamo la richiesta HTTP con un timeout di 15 secondi
    response = requests.get(RSS_URL, headers=headers, timeout=15)

    # Verifica se il server ha bloccato la richiesta (es. errore 403 o 503)
    if response.status_code != 200:
      print(
          f"Errore HTTP: Il server ha risposto con il codice"
          f" {response.status_code}. Impossibile scaricare il feed."
      )
      return

    xml_data = response.content

    # Controllo di sicurezza se il contenuto è vuoto
    if not xml_data.strip():
      print("Errore: Il contenuto ricevuto è vuoto.")
      return

    # Parsing dell'XML
    root = ET.fromstring(xml_data)
    items = []

    for item in root.iter("item"):
      item_data = {}
      for child in item:
        tag_name = child.tag.split("}")[-1]  # Pulisce i namespace XML
        item_data[tag_name] = child.text.strip() if child.text else ""
      items.append(item_data)

    # Salvataggio del file JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
      json.dump({"items": items}, f, ensure_ascii=False, indent=4)

    print(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successo! Aggiornati"
        f" {len(items)} elementi in '{OUTPUT_JSON}'."
    )

  except requests.exceptions.RequestException as e:
    print(f"Errore di rete durante la connessione: {e}")
  except ET.ParseError as e:
    print(
        f"Errore di parsing XML: Il sito ha probabilmente restituito una pagina"
        f" di blocco HTML anziché l'RSS. Dettagli: {e}"
    )
  except Exception as e:
    print(f"Errore imprevisto: {e}")


if __name__ == "__main__":
  print(
      "Avvio del demone automatico per i richiami del Ministero della Salute..."
  )

  while True:
    aggiorna_json()
    print(
        f"In attesa del prossimo controllo tra {INTERVALLO_ORE} ore...\n"
        "------------------------------------------------------------"
    )
    time.sleep(INTERVALLO_ORE * 3600)

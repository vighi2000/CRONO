import json
import xml.etree.ElementTree as ET
import requests

RSS_URL = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
OUTPUT_JSON = "avvisi_richiami_osa.json"


def aggiorna_json():
  print("Tentativo di connessione e scaricamento RSS...")

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
    response = requests.get(RSS_URL, headers=headers, timeout=15)

    if response.status_code != 200:
      print(
          f"Errore HTTP: Il server ha risposto con il codice"
          f" {response.status_code}."
      )
      return

    xml_data = response.content

    if not xml_data.strip():
      print("Errore: Il contenuto ricevuto è vuoto.")
      return

    root = ET.fromstring(xml_data)
    items = []

    for item in root.iter("item"):
      item_data = {}
      for child in item:
        tag_name = child.tag.split("}")[-1]
        item_data[tag_name] = child.text.strip() if child.text else ""
      items.append(item_data)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
      json.dump({"items": items}, f, ensure_ascii=False, indent=4)

    print(
        f"Successo! Aggiornati {len(items)} elementi nel file '{OUTPUT_JSON}'."
    )

  except requests.exceptions.RequestException as e:
    print(f"Errore di rete durante la connessione: {e}")
  except ET.ParseError as e:
    print(f"Errore di parsing XML: {e}")
  except Exception as e:
    print(f"Errore imprevisto: {e}")


# --- ESECUZIONE SINGOLA (senza loop infiniti) ---
if __name__ == "__main__":
  aggiorna_json()

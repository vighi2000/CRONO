import requests
import json

url = "https://www.salute.gov.it/new/page-data/it/avvisi/avvisi-e-richiami-di-prodotti-alimentari/page-data.json"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

print("Scaricando i dati dal Ministero...")
try:
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        dati = response.json()
        
        # Salva il contenuto in un file locale
        with open("richiami_ministero.json", "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=4)
            
        print("✅ Successo! Il file è stato salvato come 'richiami_ministero.json'.")
    else:
        print(f"❌ Errore del server. Codice: {response.status_code}")
except Exception as e:
    print(f"❌ Errore di connessione: {e}")
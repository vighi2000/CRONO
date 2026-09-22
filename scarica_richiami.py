import requests
import json

def fetch_rasff_data_italy(limit=100):
    url = "https://webgate.ec.europa.eu/rasff-window/backend/public/notification/search"
    
    # Payload aggiornato con il filtro per "Paesi coinvolti: Italia"
    payload = {
        "parameters": {
            "countries": {
                "type": "LIST",
                "name": "countries",
                "value": [
                    {"id": "IT", "label": "Italy"}
                ]
            }
        },
        "itemsPerPage": limit,
        "pageNumber": 1
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    print("Scaricamento delle allerte relative all'Italia in corso...")
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    return response.json()

def main():
    try:
        # Recupera le ultime 100 allerte che riguardano l'Italia
        data = fetch_rasff_data_italy(limit=100)
        
        # Estrai le allerte (la lista si trova dentro la chiave "notifications")
        allerte = {"notifiche_italia": data.get("notifications", [])}
        
        # Conta quante ne ha trovate e stampalo a schermo
        numero_allerte = len(allerte["notifiche_italia"])
        print(f"Trovate {numero_allerte} allerte per l'Italia.")
        
        # Salvataggio in formato JSON
        with open("allerte_rasff_italia.json", "w", encoding="utf-8") as json_file:
            json.dump(allerte, json_file, indent=4, ensure_ascii=False)
            
        print("✅ File 'allerte_rasff_italia.json' creato con successo!")

    except requests.exceptions.RequestException as e:
        print(f"❌ Errore durante la comunicazione con il server RASFF: {e}")
    except Exception as e:
        print(f"❌ Si è verificato un errore: {e}")

if __name__ == "__main__":
    main()
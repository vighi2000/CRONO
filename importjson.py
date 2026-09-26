import requests
import json
from datetime import datetime, timedelta
import sys

def fetch_rasff_all_pages():
    base_url = "https://api.datalake.sante.service.ec.europa.eu/rasff/irasff-general-info-view"
    
    params = {
        "api-version": "v1.1",
        "format": "json",
        "NETWORK_DESC": "RASFF"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    all_records = []
    next_link = base_url
    page = 1
    
    print("🚀 Inizio scaricamento del database iRASFF...")
    
    while next_link:
        try:
            if page == 1:
                response = requests.get(next_link, params=params, headers=headers, timeout=25)
            else:
                response = requests.get(next_link, headers=headers, timeout=25)
                
            response.raise_for_status()
            data = response.json()
            
            records = data.get("value", data.get("data", []))
            if not records:
                break
                
            all_records.extend(records)
            
            data_corrente = str(records[-1].get("NOTIF_DATE", "Sconosciuta"))[:10]
            sys.stdout.write(f"\r📥 Pagina {page} | Record totali: {len(all_records)} | Data corrente: {data_corrente}")
            sys.stdout.flush()
            
            next_link = data.get("@odata.nextLink") or data.get("nextLink")
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"\n⚠️ Errore durante la richiesta alla pagina {page}: {e}")
            break
            
    print("\n✅ Download dal database europeo completato!")
    return all_records

def main():
    try:
        records = fetch_rasff_all_pages()
        if not records:
            print("❌ Nessun record recuperato dal server.")
            return

        print("\n📊 Filtraggio delle notifiche collegate all'Italia...")
        
        # Ampliato il margine di ricerca a 60 giorni per evitare che ritardi di pubblicazione escludano dati
        limite_data = datetime.now() - timedelta(days=60)
        allerte_italia = []

        for item in records:
            # Estraggo la data di notifica
            notif_date_str = str(item.get("NOTIF_DATE", ""))[:10]
            
            # Se è presente una data valida, verifico la finestra temporale
            if len(notif_date_str) == 10:
                try:
                    notif_date = datetime.strptime(notif_date_str, "%Y-%m-%d")
                    if notif_date < limite_data:
                        # Poiché i dati arrivano in ordine cronologico decrescente, 
                        # possiamo interrompere la scansione se superiamo la data limite
                        continue
                except ValueError:
                    pass

            # Controllo paesi coinvolti
            dist = str(item.get("DISTRIBUTION_COUNTRY_DESC", ""))
            orig = str(item.get("ORIGIN_COUNTRY_DESC", ""))
            notif = str(item.get("NOTIFYNG_COUNTRY_DESC", ""))

            if "Italy" in dist or "Italy" in orig or "Italy" in notif:
                allerte_italia.append(item)

        print(f"🇮🇹 Trovate {len(allerte_italia)} allerte collegate all'Italia negli ultimi 60 giorni.")

        # NOME FILE ALLINEATO CON IL WORKFLOW GITHUB ACTIONS
        NOME_FILE_OUTPUT = "avvisi_richiami_osa.json"

        output = {"notifiche_italia": allerte_italia}
        with open(NOME_FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ File '{NOME_FILE_OUTPUT}' salvato correttamente con successo!")

    except Exception as e:
        print(f"\n❌ Errore generale durante l'esecuzione: {e}")

if __name__ == "__main__":
    main()

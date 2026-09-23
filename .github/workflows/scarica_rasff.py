import requests
import json
from datetime import datetime, timedelta
import sys

def fetch_rasff_all_pages():
    base_url = "https://api.datalake.sante.service.ec.europa.eu/rasff/irasff-general-info-view"
    
    # Usiamo SOLO i parametri permessi dal server UE per evitare che ci blocchi
    params = {
        "api-version": "v1.1",
        "format": "json",
        "NETWORK_DESC": "RASFF"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    all_records = []
    next_link = base_url
    page = 1
    
    print("🚀 Inizio scaricamento del database iRASFF...")
    print("⏳ Il server UE ci costringe a sfogliare l'archivio storico pagina per pagina. Attendi...")
    
    while next_link:
        try:
            # Se è la prima pagina usiamo 'params', se è una successiva usiamo il link completo fornito dal server
            if page == 1:
                response = requests.get(next_link, params=params, headers=headers, timeout=20)
            else:
                response = requests.get(next_link, headers=headers, timeout=20)
                
            response.raise_for_status()
            data = response.json()
            
            # Estrae i record (OData V4 usa la chiave 'value')
            records = data.get("value", data.get("data", []))
            if not records:
                break
                
            all_records.extend(records)
            
            # Feedback visivo sulla stessa riga per farti vedere a che data è arrivato lo script
            data_corrente = records[-1].get("NOTIF_DATE", "Sconosciuta")[:10]
            sys.stdout.write(f"\r📥 Pagina {page} scaricata | Totale record: {len(all_records)} | Data in lettura: {data_corrente} ")
            sys.stdout.flush()
            
            # Cerca il link alla pagina successiva generato dal server UE
            next_link = data.get("@odata.nextLink") or data.get("nextLink")
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"\n⚠️ Errore di connessione alla pagina {page}: {e}")
            break
            
    print("\n✅ Download completo dal database europeo!")
    return all_records

def main():
    try:
        records = fetch_rasff_all_pages()
        
        if not records:
            print("❌ Nessun record scaricato.")
            return
            
        print(f"\n📊 Avvio filtro per l'Italia sugli ultimi 30 giorni...")
        
        oggi = datetime.now()
        trenta_giorni_fa = oggi - timedelta(days=30)
        
        allerte_italia = []
        for item in records:
            # 1. Filtro per data (solo ultimi 30 giorni)
            notif_date_str = str(item.get("NOTIF_DATE", ""))
            try:
                if len(notif_date_str) >= 10:
                    notif_date = datetime.strptime(notif_date_str[:10], "%Y-%m-%d")
                    if notif_date < trenta_giorni_fa:
                        continue 
            except ValueError:
                pass 
                
            # 2. Filtro per l'Italia (Distribuzione, Origine o Notifica)
            dist = str(item.get("DISTRIBUTION_COUNTRY_DESC", ""))
            orig = str(item.get("ORIGIN_COUNTRY_DESC", ""))
            notif = str(item.get("NOTIFYNG_COUNTRY_DESC", ""))
            
            if "Italy" in dist or "Italy" in orig or "Italy" in notif:
                allerte_italia.append(item)
                
        print(f"🇮🇹 Trovate {len(allerte_italia)} allerte recentissime collegate all'Italia!")
        
        # Salvataggio nel file per l'App
        output = {"notifiche_italia": allerte_italia}
        with open("allerte_rasff_italia.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)
            
        print("✅ File 'allerte_rasff_italia.json' salvato con successo e pronto per GitHub!")

    except Exception as e:
        print(f"\n❌ Errore generale: {e}")

if __name__ == "__main__":
    main()
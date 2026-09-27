import requests
import xml.etree.ElementTree as ET
import json

URL_RSS = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
FILE_OUTPUT = "avvisi_richiami_osa.json"

# Lista di 3 proxy (ponti) gratuiti diversi. Se uno viene bloccato, proviamo il successivo.
PROXY_LIST = [
    f"https://api.allorigins.win/raw?url={URL_RSS}",
    f"https://api.codetabs.com/v1/proxy?quest={URL_RSS}",
    f"https://corsproxy.io/?{URL_RSS}"
]

def scarica_multi_proxy():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    raw_data = None

    print("🌐 Avvio aggiramento del firewall del Ministero...")
    
    # 1. TENTA LA CONNESSIONE CON I PROXY A ROTAZIONE
    for proxy_url in PROXY_LIST:
        nome_proxy = proxy_url.split('/')[2]
        print(f"🔄 Provo a passare dal proxy: {nome_proxy}...")
        
        try:
            response = requests.get(proxy_url, headers=headers, timeout=25)
            
            # Se scarica correttamente e trova le parole chiave dell'XML
            if response.status_code == 200 and ("<rss" in response.text.lower() or "<?xml" in response.text.lower()):
                raw_data = response.content.decode('utf-8-sig', errors='ignore').strip()
                print(f"✅ BINGO! Connessione riuscita aggirando il firewall tramite: {nome_proxy}")
                break # Esce dal ciclo, abbiamo i dati!
            else:
                print(f"⚠️ {nome_proxy} è stato bloccato dal Ministero. Passo al prossimo...")
                
        except Exception as e:
            print(f"⚠️ Errore di connessione a {nome_proxy}: {e}")

    # 2. CONTROLLO FINALE DEL DOWNLOAD
    if not raw_data:
        print("❌ TUTTI I PROXY SONO STATI BLOCCATI. Il Ministero ha bloccato tutte le vie d'accesso.")
        return

    # 3. PULIZIA E CONVERSIONE DELL'XML IN JSON
    try:
        # Pulisce l'XML da eventuali schifezze inserite all'inizio
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

        # 4. SALVATAGGIO DEL FILE
        output = {"notifiche_italia": notifiche}
        with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ File '{FILE_OUTPUT}' creato e salvato con successo!")

    except ET.ParseError as e:
        print(f"❌ Errore durante la conversione XML: {e}")
    except Exception as e:
        print(f"❌ Errore generico: {e}")

if __name__ == "__main__":
    scarica_multi_proxy()

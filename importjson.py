import json
import xml.etree.ElementTree as ET
import requests

RSS_URL = "https://www.salute.gov.it/new/rss/RSS_avvisi_richiami_osa.xml"
OUTPUT_JSON = "avvisi_richiami_osa.json"


def aggiorna_json():
  print("Tentativo di connessione e scaricamento RSS...")

  headers = {
      "User-Agent": (

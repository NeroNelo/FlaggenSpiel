import json
import requests
import os
from urllib.parse import urlparse

#Prüfen ob zielordner existiert, wenn nicht erstellen
ziel_ordner = "src/assets/flags"
if not os.path.exists(ziel_ordner):
    os.mkdir(ziel_ordner)
    print("Directory " , ziel_ordner , " Created ")

variable = open("countries.json","r",encoding="utf-8")
loaded_flags = json.load(variable)

# Flaggen url und Namen finden
for country in loaded_flags:
    url=country["flags"]["png"]
    cca3=country["cca3"]
    print(cca3,url)

    #nimmt name von png aus der url
    dateiname = os.path.basename(urlparse(url).path)
    dateiname = cca3 + ".png"
    #setzt order pfad mit dateinamen zusammen
    ziel_pfad = os.path.join(ziel_ordner, dateiname)
    response = requests.get(url)

    #prüft ob der download erfolgreich war
    if response.status_code == 200:
        with open(ziel_pfad, 'wb') as f:
            f.write(response.content)
        print(f"Erfolgreich gespeichert unter: {ziel_ordner}")
    else:
        print(f"Fehler beim Download. Status-Code: {response.status_code}{dateiname}")




import json
import requests

url="https://restcountries.com/v3.1/all?fields=name,flags,borders,capital,continents,translations,languages,population,cca3"

response = requests.get(url)

if response.status_code == 200:
    countries = response.json()
    with open('countries.json', 'w',encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False,indent=4)








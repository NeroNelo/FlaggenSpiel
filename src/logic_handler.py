import json


from country import Country

def load_country_file(country_file):
    with open(country_file,encoding="utf-8") as f:
        country_dict = json.load(f)
    return country_dict

def load_countries(country_dict):
    countries = []
    for country in country_dict:
        cca3 = country["cca3"]
        name = country["translations"]["deu"]["official"]
        capital = country["capital"]
        borders = country["borders"]
        continent = country["continents"]
        population = country["population"]
        languages = country["languages"]
        countries.append(Country(name,cca3,capital,borders,continent,languages,population))
    return countries



class Country:

    def __init__(self, name: str, cca3_code: str,capital:list[str], borders: list[str],continent:list[str], languages:list[str],population: int):

        self.name = name
        self.cca3_code = cca3_code
        self.capital = capital
        self.borders = borders
        self.continent = continent
        self.languages = languages
        self.population = population

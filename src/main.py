import flet as ft
from flet import View, Text, Button, Image
from src.logic_handler import load_country_file,load_countries

from country import Country

def init_game():
    countries_json = load_country_file("countries.json")
    countries = load_countries(countries_json)
    return countries


def main(page: ft.Page):
    counter = ft.Text("0", size=50, data=0)
    loaded_countries:list[Country] = init_game()
    print(loaded_countries[0].name)


    def decrement_click(e):
        counter.data -= 1
        counter.value = str(counter.data)
        page.update()

    def start_game(e):
        print("Game started")


    page.views.append(View(route="/", controls=[
        Text(value=loaded_countries[0].name,size=30),
        Text(value="Population  Guess", size=30),
        Button(content="Continent Guess",on_click=start_game, color="red"),




    ]))
    page.update()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")

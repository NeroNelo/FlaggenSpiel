from unidecode import unidecode
import flet as ft
import os, random
from src.logic_handler import load_country_file, load_countries
from country import Country


def load_game_data():
    countries_json = load_country_file("countries.json")
    return load_countries(countries_json)


def get_random_country(loaded_countries: list):
    x = random.randint(0, len(loaded_countries) - 1)
    return loaded_countries.pop(x)


def get_wrong_answers(all_countries: list, correct: Country, count=3):
    others = [c for c in all_countries if c.cca3_code != correct.cca3_code]
    return random.sample(others, min(count, len(others)))


def build_buttons(country, country_list):
    wrong = get_wrong_answers(country_list, country)
    options = wrong + [country]
    random.shuffle(options)
    return [
        {"text": c.name, "color": "blue", "width": 300, "visible": True, "country": c}
        for c in options
    ]


@ft.component
def Home():
    return ft.View(
        route="/",
        can_pop=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Flaggen Spiel", size=32),
            ft.Button(
                "Leicht",
                on_click=lambda _: ft.context.page.navigate("/leicht"),
            ),
            ft.Button(
                "Schwer",
                on_click=lambda _: ft.context.page.navigate("/schwer"),
            ),
            ft.Button("Exit", on_click=ft.context.page.window.close, ),

        ],
    )


@ft.component
def Leicht():

    def create_initial_state():
        all_countries = load_game_data()
        current = get_random_country(all_countries)
        btns = build_buttons(current, all_countries)
        return {
            "countries": all_countries,
            "current_country": current,
            "points": 0,
            "buttons": btns,
        }

    game, set_game = ft.use_state(create_initial_state())

    def on_click(index):
        def handler(e):
            clicked = game["buttons"][index]["country"]
            new_buttons = [b.copy() for b in game["buttons"]]

            if clicked.cca3_code == game["current_country"].cca3_code:
                new_buttons[index] = {**new_buttons[index], "color": "green"}
                new_countries = game["countries"].copy()
                new_country = get_random_country(new_countries)
                new_game = {
                    "countries": new_countries,
                    "current_country": new_country,
                    "points": game["points"] + 1,
                    "buttons": build_buttons(new_country, new_countries),
                }
            else:
                new_buttons[index] = {**new_buttons[index], "color": "red"}
                new_game = {**game, "buttons": new_buttons}

            set_game(new_game)
        return handler


    flag_path = os.path.join("flags", game["current_country"].cca3_code + ".png")
    if not os.path.isfile(flag_path):
        print("flagg not found")
        pass

    return ft.View(
        route="/leicht",
        appbar=ft.AppBar(title=ft.Text("Leicht")),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                value="Punkte: " + str(game["points"]),
                text_align=ft.TextAlign.CENTER,
                size=30,
            ),
            ft.Image(
                src=flag_path,
                width=300,
                height=300,
                repeat=ft.ImageRepeat.NO_REPEAT,
            ),
            *[
                ft.Button(
                    content=ft.Text(value=btn["text"]),
                    color=btn["color"],
                    width=btn["width"],
                    visible=btn["visible"],
                    on_click=on_click(i),
                )
                for i, btn in enumerate(game["buttons"])
            ],
            ft.Button("Home",on_click=lambda _: ft.context.page.navigate("/"),
            ),
            ft.Button("Exit", on_click=ft.context.page.window.close, ),
        ],
    )


@ft.component
def Schwer():



    def create_initial_state():
        all_countries = load_game_data()
        current = get_random_country(all_countries)
        return {
            "countries": all_countries,
            "current_country": current,
            "points": 0,
            "input_text": "",
            "feedback": "",
            "show_next": False,
        }

    game, set_game = ft.use_state(create_initial_state())
    versuche,set_versuche = ft.use_state(5)

    def pruefen(e):
        antwort = unidecode(game["input_text"].strip().lower())
        richtig = unidecode(game["current_country"].name.strip().lower())

        if antwort == richtig:
            set_game({
                **game,
                "feedback": "✅ Richtig!",
                "input_text": "",
                "show_next": True,
            })
        elif versuche > 1:
            set_versuche(versuche - 1)
            set_game({**game, "feedback": f"❌ Noch {versuche - 1} Versuche übrig!"})
        else:
            set_game({
                **game,
                "feedback": "❌ Falsch! Richtig wäre: " + game["current_country"].name,
                "show_next": True,
            })
            set_versuche(0)

    def naechstes_land(e):
        new_countries = game["countries"].copy()
        if len(new_countries) == 0:
            ft.context.page.navigate("/")
            return
        new_country = get_random_country(new_countries)
        set_versuche(5)
        set_game({
            "countries": new_countries,
            "current_country": new_country,
            "points": game["points"] + (1 if "✅" in game["feedback"] else 0),
            "input_text": "",
            "feedback": "",
            "show_next": False,
        })

    flag_path = os.path.join("flags", game["current_country"].cca3_code + ".png")

    return ft.View(
        route="/schwer",
        appbar=ft.AppBar(title=ft.Text("Schwer")),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,

        controls=[

            ft.Text(

                value="Punkte: " + str(game["points"]),
                text_align=ft.TextAlign.CENTER,
                size=30,
            ),

            ft.Image(
                src=flag_path,
                width=300,
                height=300,
                repeat=ft.ImageRepeat.NO_REPEAT,
            ),
            ft.Text(value=game["current_country"].name, size=20),
            ft.TextField(
                value=game["input_text"],
                hint_text="Land eingeben...",
                width=300,
                disabled=game["show_next"],
                on_change=lambda e: set_game({**game, "input_text": e.control.value}),
            ),
            ft.Button(
                "Prüfen",
                width=300,
                disabled=game["show_next"],
                on_click=pruefen,
            ),
            ft.Text(value=game["feedback"], size=20),
            ft.Button(
                "Nächstes Land ➡",
                width=300,
                visible=game["show_next"],
                on_click=naechstes_land,
            ),
            ft.Button("Home", on_click=lambda _: ft.context.page.navigate("/"),
            ),
            ft.Button("Exit",on_click=ft.context.page.window.close),
        ],
    )


@ft.component
def App():
    return ft.Router(
        routes=[
            ft.Route(index=True, component=Home),
            ft.Route(path="leicht", component=Leicht),
            ft.Route(path="schwer", component=Schwer),
            ft.Button("Exit", on_click=ft.context.page.window.close ),
        ],
        manage_views=True,

    )


def main(page: ft.Page):
    page.title = "Flaggen Spiel"
    page.window.width = 400
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.render_views(App)


ft.run(main)
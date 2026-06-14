#todo
import copy

import flet as ft
import os, random, json
from datetime import datetime
from logic_handler import load_country_file, load_countries
from country import Country
import logging
import unicodedata

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

def normalisieren(text):
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8").lower().strip()

def is_mobile():
    platform = ft.context.page.platform
    return platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)

def load_game_data():
    try:
        countries_json = load_country_file("countries.json")
        return load_countries(countries_json)
    except FileNotFoundError:
        logging.critical("countries.json nicht gefunden!")
        return []
    except Exception as e:
        logging.critical(f"Fehler beim Laden der Länderdaten: {e}")
        return []


def get_random_country(loaded_countries: list):
    if not loaded_countries:
        logging.error("get_random_country: Liste ist leer!")
        return None
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


def highscore_speichern(name, punkte, schwierigkeitsgrad):
    datum = datetime.now().strftime("%d.%m.%Y")
    datei = "highscore_leicht.json" if schwierigkeitsgrad == "Leicht" else "highscore_schwer.json"
    try:
        with open(datei, encoding="utf-8") as f:
            daten = json.load(f)
    except FileNotFoundError:
        logging.warning(f"{datei} nicht gefunden, wird neu erstellt")
        daten = []
    except json.JSONDecodeError as e:
        logging.error(f"{datei} ist beschädigt: {e}")
        daten = []
    try:
        daten.append({"name": name, "points": punkte, "date": datum})
        with open(datei, "w", encoding="utf-8") as f:
            json.dump(daten, f, ensure_ascii=False)
        logging.info(f"Highscore gespeichert: {name} - {punkte} Punkte ({schwierigkeitsgrad})")
    except Exception as e:
        logging.error(f"Fehler beim Speichern des Highscores: {e}")


@ft.component
def Home():

    async def exit_handler(e):
        await ft.context.page.window.close()

    return ft.View(
        route="/",
        appbar=ft.AppBar(title=ft.Text("Home")),
        can_pop=False,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Flaggen Spiel", size=32),
            ft.Text("", size=32),
            ft.Button("Leicht", on_click=lambda _: ft.context.page.navigate("/leicht")),
            ft.Button("Schwer", on_click=lambda _: ft.context.page.navigate("/schwer")),
            ft.Button("Highscore", on_click=lambda _: ft.context.page.navigate("/highscore")),
            *([ft.Button("Exit", on_click=exit_handler)] if not is_mobile() else []),
        ],
    )


@ft.component
def Leicht():

    def create_initial_state():
        all_countries = load_game_data()
        all_countries_backup = copy.deepcopy(all_countries)
        current = get_random_country(all_countries)
        btns = build_buttons(current, all_countries_backup)
        return {
            "countries": all_countries,
            "all_countries_backup": all_countries_backup,
            "current_country": current,
            "points": 0,
            "buttons": btns,
            "show_next": False,
        }

    game, set_game = ft.use_state(create_initial_state())
    dialog_aktion, set_dialog_aktion = ft.use_state(None)
    name_text, set_name_text = ft.use_state("")

    def on_click(index):
        def handler(e):
            clicked = game["buttons"][index]["country"]
            new_buttons = [b.copy() for b in game["buttons"]]

            if clicked.cca3_code == game["current_country"].cca3_code:
                new_countries = game["countries"].copy()
                new_points = game["points"] + 1

                if len(new_countries) == 0:
                    set_game({**game, "points":new_points, "show_next":False,
                              "current_country": game["all_countries_backup"][0]}) # Platzhalter statt NONE sonst error
                    set_dialog_aktion("home")
                    return

                new_country = get_random_country(new_countries)
                set_game({
                    "countries": new_countries,
                    "all_countries_backup": game["all_countries_backup"],
                    "current_country": new_country,
                    "points": new_points,
                    "buttons": build_buttons(new_country, game["all_countries_backup"]),
                    "show_next": False,
                })
            else:
                for i, btn in enumerate(new_buttons):
                    if btn["country"].cca3_code == game["current_country"].cca3_code:
                        new_buttons[i] = {**new_buttons[i], "color": "green"}
                    else:
                        new_buttons[i] = {**new_buttons[i], "color": "red"}
                set_game({**game, "buttons": new_buttons, "show_next": True})

        return handler

    def naechste_flagge(e):
        new_countries = game["countries"].copy()
        if len(new_countries) == 0:
            set_dialog_aktion("home")
            return
        new_country = get_random_country(new_countries)
        set_game({
            "countries": new_countries,
            "current_country": new_country,
            "all_countries_backup": game["all_countries_backup"],
            "points": game["points"],
            "buttons": build_buttons(new_country, game["all_countries_backup"]),
            "show_next": False,
        })

    async def dialog_bestaetigen(e):
        name = name_text.strip() or "Unbekannt"
        highscore_speichern(name, game["points"],"Leicht")
        aktion = dialog_aktion
        set_dialog_aktion(None)
        set_name_text("")
        if aktion == "home":
            ft.context.page.navigate("/")
        else:
            await ft.context.page.window.close()

    async def dialog_ablehnen(e):
        aktion = dialog_aktion
        set_dialog_aktion(None)
        set_name_text("")
        if aktion == "home":
            ft.context.page.navigate("/")
        else:
            await ft.context.page.window.close()

    async def exit_handler(e):
        if game["points"] > 0:
            set_dialog_aktion("exit")
        else:
            await ft.context.page.window.close()


    if game["current_country"] is None:
        return ft.View(route="/leicht", controls=[])

    flag_path = os.path.join("flags", game["current_country"].cca3_code + ".png")
    if not os.path.isfile(flag_path):
        logging.warning(f"Flagge nicht gefunden: {flag_path}")

    dialog = ft.AlertDialog(
        modal=True,
        open=dialog_aktion is not None,
        title=ft.Text("🎉 Spiel beendet!" if len(game["countries"]) == 0 else "Highscore speichern?"),
        content=ft.Column(
            [
                ft.Text(f"Deine Punkte: {game['points']}"),
                ft.TextField(
                    value=name_text,
                    label="Dein Name",
                    keyboard_type=ft.KeyboardType.NAME,
                    on_change=lambda e: set_name_text(e.control.value),
                ),
            ],
            tight=True,
        ),
        actions=[
            ft.TextButton("Nein", on_click=dialog_ablehnen),
            ft.TextButton("Ja", on_click=dialog_bestaetigen),
        ],
    )

    return ft.View(
        route="/leicht",
        appbar=ft.AppBar(title=ft.Text("Leicht")),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            dialog,
            ft.Text(value="Punkte: " + str(game["points"]), text_align=ft.TextAlign.CENTER, size=30),
            ft.Text(value="Länder übrig: " + str(len(game["countries"])), text_align=ft.TextAlign.CENTER, size=16),
            ft.Image(src=flag_path, width=300, height=250, repeat=ft.ImageRepeat.NO_REPEAT),
            *[
                ft.Button(
                    content=ft.Text(value=btn["text"]),
                    color=btn["color"],
                    width=btn["width"],
                    visible=btn["visible"],
                    disabled=game["show_next"],
                    on_click=on_click(i),
                )
                for i, btn in enumerate(game["buttons"])
            ],
            ft.Button(
                "Nächste Flagge ➡",
                width=300,
                opacity=1 if game["show_next"] else 0,
                disabled=not game["show_next"],
                on_click=naechste_flagge,
            ),
            ft.Button("Home", on_click=lambda _: set_dialog_aktion("home") if game["points"] > 0 else ft.context.page.navigate("/")),
            *([ft.Button("Exit", on_click=exit_handler)] if not is_mobile() else []),
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
    versuche, set_versuche = ft.use_state(5)
    dialog_aktion, set_dialog_aktion = ft.use_state(None)
    name_text, set_name_text = ft.use_state("")

    def pruefen(e):
        antwort = normalisieren(game["input_text"])
        richtig = normalisieren(game["current_country"].name)
        if antwort == richtig:
            set_game({**game, "feedback": "✅ Richtig!", "input_text": "", "show_next": True, "points": game["points"] + 1})
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
            set_dialog_aktion("home")
            return
        new_country = get_random_country(new_countries)
        set_versuche(5)
        set_game({
            **game,
            "countries": new_countries,
            "current_country": new_country,
            "input_text": "",
            "feedback": "",
            "show_next": False,
        })

    async def dialog_bestaetigen(e):
        name = name_text.strip() or "Unbekannt"
        highscore_speichern(name, game["points"],"Schwer")
        aktion = dialog_aktion
        set_dialog_aktion(None)
        set_name_text("")
        if aktion == "home":
            ft.context.page.navigate("/")
        else:
            await ft.context.page.window.close()

    async def dialog_ablehnen(e):
        aktion = dialog_aktion
        set_dialog_aktion(None)
        set_name_text("")
        if aktion == "home":
            ft.context.page.navigate("/")
        else:
            await ft.context.page.window.close()

    async def exit_handler(e):
        if game["points"] > 0:
            set_dialog_aktion("exit")
        else:
            await ft.context.page.window.close()

    flag_path = os.path.join("flags", game["current_country"].cca3_code + ".png")
    if not os.path.isfile(flag_path):
        logging.warning(f"Flagge nicht gefunden: {flag_path}")

    def versuche_als_sterne(versuche):
        return "❤️" * versuche + "🖤" * (5 - versuche)

    dialog = ft.AlertDialog(
        modal=True,
        open=dialog_aktion is not None,
        title=ft.Text("🎉 Spiel beendet!" if len(game["countries"]) == 0 else "Highscore speichern?"),
        content=ft.Column(
            [
                ft.Text(f"Deine Punkte: {game['points']}"),
                ft.TextField(
                    value=name_text,
                    label="Dein Name",
                    keyboard_type=ft.KeyboardType.NAME,
                    on_change=lambda e: set_name_text(e.control.value),
                ),
            ],
            tight=True,
        ),
        actions=[
            ft.TextButton("Nein", on_click=dialog_ablehnen),
            ft.TextButton("Ja", on_click=dialog_bestaetigen),
        ],
    )

    return ft.View(
        route="/schwer",
        appbar=ft.AppBar(title=ft.Text("Schwer")),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            dialog,

            ft.Text(value="Punkte: " + str(game["points"]), text_align=ft.TextAlign.CENTER, size=30),
            ft.Text(value="Länder übrig: " + str(len(game["countries"])), text_align=ft.TextAlign.CENTER, size=16),
            ft.Image(src=flag_path, width=300, height=200, repeat=ft.ImageRepeat.NO_REPEAT),
            ft.Text(value=versuche_als_sterne(versuche), size=24, text_align=ft.TextAlign.CENTER),
            ft.Text(value=game["current_country"].name, size=20),
            ft.TextField(
                value=game["input_text"],
                hint_text="Land eingeben...",
                width=300,
                disabled=game["show_next"],
                on_change=lambda e: set_game({**game, "input_text": e.control.value}),
            ),
            ft.Button("Prüfen", width=300, disabled=game["show_next"], on_click=pruefen),
            ft.Text(value=game["feedback"], size=20),
            ft.Button("Nächstes Land ➡", width=300,opacity=1 if game["show_next"] else 0, disabled=not game["show_next"], on_click=naechstes_land),
            ft.Button("Home", on_click=lambda _: set_dialog_aktion("home") if game["points"] > 0 else ft.context.page.navigate("/")),
            *([ft.Button("Exit", on_click=exit_handler)] if not is_mobile() else []),
        ],
    )


@ft.component
def Highscore():

    score_leicht, set_score_leicht = ft.use_state([])
    score_schwer, set_score_schwer = ft.use_state([])

    def get_score(datei, set_fn):
        highscore_ls = []
        try:
            with open(datei, encoding="utf-8") as f:
                score_dict = json.load(f)
            for data in score_dict:
                highscore_ls.append([
                    data.get("name", "Unbekannt"),
                    data.get("points", 0),
                    data.get("date", "-")
                ])
        except FileNotFoundError:
            logging.error(f"{datei} nicht gefunden")
        except json.JSONDecodeError as e:
            logging.error(f"{datei} beschädigt: {e}")
        highscore_ls.sort(key=lambda x: x[1], reverse=True)
        highscore_ls = highscore_ls[:10]
        set_fn(highscore_ls)

    ft.use_effect(lambda: get_score("highscore_leicht.json", set_score_leicht), [])
    ft.use_effect(lambda: get_score("highscore_schwer.json", set_score_schwer), [])


    list_items_leicht = []
    for item in score_leicht:
        name, points, date = item
        list_items_leicht.append(
            ft.ListTile(
                title=ft.Text(f"{name} - {points} Punkte", text_align=ft.TextAlign.CENTER),
                subtitle=ft.Text(f"Datum: {date}", text_align=ft.TextAlign.CENTER),
            )
        )
    list_items_schwer = []
    for item in score_schwer:
        name, points, date = item
        list_items_schwer.append(
            ft.ListTile(
                title=ft.Text(f"{name} - {points} Punkte", text_align=ft.TextAlign.CENTER),
                subtitle=ft.Text(f"Datum: {date}", text_align=ft.TextAlign.CENTER),
            )
        )



    async def exit_handler(e):
        await ft.context.page.window.close()

    return ft.View(
        route="/highscore",
        appbar=ft.AppBar(title=ft.Text("")),
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(value="Highscore", text_align=ft.TextAlign.CENTER, size=30),
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("🟢 Leicht", size=18, text_align=ft.TextAlign.CENTER),
                            ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=False,
                                        controls=list_items_leicht)
                        ]
                    ),
                    ft.VerticalDivider(),
                    ft.Column(
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("🔴 Schwer", size=18, text_align=ft.TextAlign.CENTER),
                            ft.ListView(expand=True, spacing=10, padding=10, auto_scroll=False,
                                        controls=list_items_schwer),
                        ]
                    ),
                ],
            ),
            ft.Button("Home", on_click=lambda _: ft.context.page.navigate("/")),
            *([ft.Button("Exit", on_click=exit_handler)] if not is_mobile() else []),
        ],
    )


@ft.component
def App():
    return ft.Router(
        routes=[
            ft.Route(index=True, component=Home),
            ft.Route(path="leicht", component=Leicht),
            ft.Route(path="schwer", component=Schwer),
            ft.Route(path="highscore", component=Highscore),
        ],
        manage_views=True,
    )


def main(page: ft.Page):
    logging.info("App gestartet")
    page.title = "Flaggen Spiel"
    page.window.width = 400
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.render_views(App)


ft.run(main)
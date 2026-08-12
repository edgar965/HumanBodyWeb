# -*- coding: utf-8 -*-
"""Wächter für static/css/theme.css — die Theme-Paletten.

WARUM DIESER TEST EXISTIERT (12.08.2026)
----------------------------------------
Im Datei-Header von theme.css stand ein Sternchen-Platzhalter unmittelbar vor
einem Schrägstrich. Diese Zeichenfolge SCHLIESST einen CSS-Kommentar. Der Header
endete damit mitten im Satz, und der Browser verwarf beim Aufräumen den
kompletten ERSTEN Regelblock — `body, body[data-theme="dark"]`, also die ganze
Dark-Palette.

Aufgefallen ist das monatelang nicht, und genau das macht den Fehler gefährlich:
`style.css :root` hält dieselben Dark-Werte ein zweites Mal, deshalb sah Dark
unverändert aus. Sichtbar wurde es erst an fünf Variablen, die es NUR in
theme.css gibt (`--bg-tertiary`, `--bg-darker`, `--bg-hover`, `--bg-highlight`,
`--text-secondary`) und an `--fg-rgb`, das die Auslastungs-Leiste braucht.

Ein CSS-Syntaxfehler bricht nichts — er wird still geschluckt. Darum diese
Prüfungen: Sie kosten keine Datenbank, laufen in Millisekunden und schlagen an,
BEVOR jemand den Ausfall im Browser sucht.

Aufruf (auch über Hilfe > Tests, DJANGOBASE['test_befehle'] slug "core"):
    python manage.py test core
"""
import re

from django.conf import settings
from django.test import SimpleTestCase


class ThemeCssTest(SimpleTestCase):
    """Prüft theme.css auf Syntax, Vollständigkeit und Gleichstand mit style.css."""

    #: Die fünf Modi, die der Topbar-Umschalter anbietet.
    THEMES = ("dark", "light", "cyber", "forest", "sunset")

    #: Variablen, die es NUR in theme.css gibt (in style.css:root fehlen sie).
    #: Sie waren die Verlierer des Kommentar-Fehlers und sind der Grund, warum
    #: der Dark-Block NICHT einfach gelöscht werden darf.
    NUR_IN_THEME_CSS = ("--bg-tertiary", "--bg-darker", "--bg-hover",
                        "--bg-highlight", "--text-secondary", "--fg-rgb")

    def setUp(self):
        wurzel = settings.BASE_DIR / "static" / "css"
        self.theme = (wurzel / "theme.css").read_text(encoding="utf-8")
        self.style = (wurzel / "style.css").read_text(encoding="utf-8")

    # ------------------------------------------------------------------ Syntax

    def test_kommentar_marker_paarig(self):
        """Kein `*/` ohne offenen Kommentar und kein `/*` im Kommentar.

        DER FEHLER VON 12.08.2026. CSS-Kommentare verschachteln nicht: Das erste
        `*/` beendet den Kommentar, alles danach wird als CSS gelesen — und der
        Parser wirft beim Wiederaufsetzen den nächsten Regelblock weg."""
        offen = False
        fehler = []
        for treffer in re.finditer(r"/\*|\*/", self.theme):
            zeile = self.theme[:treffer.start()].count("\n") + 1
            if treffer.group() == "/*":
                if offen:
                    fehler.append("Zeile %d: `/*` innerhalb eines Kommentars" % zeile)
                offen = True
            else:
                if not offen:
                    fehler.append("Zeile %d: `*/` ohne offenen Kommentar - der "
                                  "Kommentar davor endete zu frueh" % zeile)
                offen = False
        self.assertFalse(offen, "Am Dateiende steht ein nicht geschlossener Kommentar.")
        self.assertEqual(fehler, [], "Unpaarige Kommentar-Marker in theme.css:\n  "
                                     + "\n  ".join(fehler))

    def test_erster_block_ist_der_dark_block(self):
        """Der Dark-Block muss die erste Regel der Datei bleiben.

        EHRLICHE EINORDNUNG (Gegenprobe 12.08.2026 gegen den kaputten Stand):
        Diese Prüfung hat den Kommentar-Fehler NICHT gefunden — nach dem zu
        frühen `*/` blieb der Selektor trotzdem die letzte Zeile vor der ersten
        Klammer. Den Fehler fängt `test_kommentar_marker_paarig`. Hier wird eine
        andere Invariante gesichert: dass niemand die Reihenfolge umstellt und
        damit den `body`-Selektor hinter ein konkretes Theme rutschen lässt."""
        ohne_kommentare = re.sub(r"/\*.*?\*/", "", self.theme, flags=re.S)
        erste_regel = ohne_kommentare.find("{")
        vorlauf = ohne_kommentare[:erste_regel]
        selektor = vorlauf.strip().splitlines()[-1] if vorlauf.strip() else ""
        self.assertIn('body[data-theme="dark"]', selektor,
                      "Erste Regel in theme.css ist nicht mehr der Dark-Block, "
                      "sondern: %r" % selektor)

    # ------------------------------------------------------- Vollstaendigkeit

    def test_alle_themes_definieren_fg_rgb(self):
        """Jeder Modus braucht `--fg-rgb` — sonst steht die Leiste nackt da.

        Das Modul aus djangoBase baut daraus `rgba(var(--fg-rgb),.07)`. Fehlt die
        Variable, ist die Deklaration ungueltig: keine Fuellung, kein Rahmen."""
        for thema in self.THEMES:
            block = self._block(thema)
            self.assertIsNotNone(block, "Theme-Block fuer %r fehlt in theme.css" % thema)
            self.assertRegex(
                block, r"--fg-rgb:\s*\d+\s*,\s*\d+\s*,\s*\d+",
                "Theme %r definiert --fg-rgb nicht als KOMMA-getrenntes Tripel. "
                "Space-separated waere mit dem Komma vor dem Alpha keine gueltige "
                "rgba()-Syntax." % thema)

    def test_topbar_erzwingt_hellen_vordergrund(self):
        """Die Topbar ist in JEDEM Theme dunkel, auch im Light-Theme.

        Ohne diese Regel gilt dort das aus --text abgeleitete --fg-rgb; im
        Light-Theme ist das dunkelgrau und die Leiste war unlesbar."""
        self.assertRegex(
            self.theme, r"\.topbar\s*\{[^}]*--fg-rgb:\s*255\s*,\s*255\s*,\s*255",
            "Die Regel `.topbar { --fg-rgb: 255, 255, 255 }` fehlt.")

    def test_ampelfarben_schlagen_das_modul(self):
        """Die Ampel-Farben brauchen `body` davor, sonst gewinnt das Modul.

        Das Modul haengt sein CSS zur Laufzeit in den <head>, also NACH dieser
        Datei. Ohne die hoehere Spezifitaet bliebe der Override wirkungslos."""
        for zustand, variable in (("", "--success"), (".ss-warn", "--warning"),
                                  (".ss-danger", "--danger")):
            muster = r"body\s+\.ss-pill%s\s+\.ss-fill\s*\{[^}]*var\(%s\)" % (
                re.escape(zustand), variable)
            self.assertRegex(self.theme, muster,
                             "Ampel-Regel fuer %r auf %s fehlt oder hat kein "
                             "vorangestelltes `body`." % (zustand or "normal", variable))

    def test_leiste_hat_absteigende_breakpoints(self):
        """Die Stufen der Auslastungs-Leiste müssen absteigend und vollständig sein.

        Sie sind GEMESSEN, nicht geschätzt (Platzbedarf 1206/1007/641/421/231 px)
        — die erste Fassung war verrechnet, auf einem 1366er-Display brach die
        Leiste weiter um. Wer hier Zahlen ändert, muss neu messen."""
        grenzen = [int(g) for g in re.findall(
            r"@media\s*\(max-width:\s*(\d+)px\)\s*\{\s*body\s+\.ss-pill", self.theme)]
        self.assertEqual(len(grenzen), 4,
                         "Erwartet vier Stufen fuer die Leiste, gefunden: %r" % grenzen)
        self.assertEqual(grenzen, sorted(grenzen, reverse=True),
                         "Die Stufen muessen absteigend stehen, sonst greift die "
                         "spaetere nie: %r" % grenzen)

    def test_nur_in_theme_css_definierte_variablen_bleiben(self):
        """Diese Variablen gibt es nirgends sonst — sie duerfen nicht wegfallen.

        Wer den Dark-Block aus theme.css entfernt (ein naheliegender Vorschlag
        gegen die doppelte Pflege), killt sie. In style.css stehen sie NICHT."""
        for variable in self.NUR_IN_THEME_CSS:
            self.assertIn("%s:" % variable, self.theme,
                          "%s fehlt in theme.css" % variable)
            self.assertNotIn(
                "%s:" % variable, self.style,
                "%s steht jetzt AUCH in style.css - dann gehoert dieser Test "
                "angepasst (und die Pflege an zwei Orten geprueft)." % variable)

    # -------------------------------------------------------- Doppelte Pflege

    def test_dark_werte_stimmen_mit_style_css_ueberein(self):
        """style.css:root und der Dark-Block halten dieselben Werte — im Gleichstand.

        Die Doppelung ist Absicht (`:root` traegt Seiten ohne data-theme), aber
        sie driftet: `body[data-theme="dark"]` ist spezifischer und gewinnt
        immer. Wer nur style.css aendert, sieht im Dark-Theme NICHTS passieren
        und sucht den Fehler woanders. Dieser Test nennt die Abweichung."""
        dark = self._vars(self._block("dark"))
        root_block = re.search(r":root\s*\{(.*?)\}", self.style, re.S)
        self.assertIsNotNone(root_block, ":root-Block in style.css nicht gefunden.")
        root = self._vars(root_block.group(1))

        abweichungen = ["%s: style.css %r vs. theme.css %r" % (name, root[name], wert)
                        for name, wert in dark.items()
                        if name in root and root[name] != wert]
        self.assertEqual(
            abweichungen, [],
            "Dark-Werte laufen auseinander (theme.css gewinnt, style.css ist "
            "wirkungslos):\n  " + "\n  ".join(abweichungen))

    # ----------------------------------------------------------------- Helfer

    def _block(self, thema):
        """Der Inhalt des Regelblocks eines Themes — oder None."""
        if thema == "dark":
            muster = r"body,\s*body\[data-theme=\"dark\"\]\s*\{(.*?)\n\}"
        else:
            muster = r"body\[data-theme=\"%s\"\]\s*\{(.*?)\n\}" % thema
        treffer = re.search(muster, self.theme, re.S)
        return treffer.group(1) if treffer else None

    @staticmethod
    def _vars(block):
        """{'--accent': '#e94560', ...} aus einem Regelblock, Kommentare entfernt."""
        sauber = re.sub(r"/\*.*?\*/", "", block or "", flags=re.S)
        return {name: wert.strip()
                for name, wert in re.findall(r"(--[\w-]+):\s*([^;]+);", sauber)}

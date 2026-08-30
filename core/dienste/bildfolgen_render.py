# -*- coding: utf-8 -*-
"""BildfolgenRender — die Szene im Hintergrundbrowser aufnehmen.

Aus `theatre_render_video` herausgeloest (Umbau 15.08.2026). Der Weg ist
umstaendlich, aber notwendig: Playwright braucht einen eigenen Prozess, weil die
Ereignisschleife des ASGI-Servers kein `subprocess_exec` erlaubt, und der
Browser laeuft in der Python-3.10-Umgebung, weil dort Playwright installiert
ist. Das Skript wird deshalb als Text erzeugt und uebergeben.

Die Werte werden NICHT mehr in den Skripttext interpoliert, sondern als JSON auf
der Standardeingabe uebergeben: Eine Szenen-URL mit einem Anfuehrungszeichen
haette das Skript sonst zerlegt.
"""
import json
import logging
import subprocess

from django.conf import settings

logger = logging.getLogger('core')

#: Das Aufnahmeskript. Es liest seine Werte von stdin — siehe Modulkopf.
SKRIPT = r'''
import json, os, sys
from playwright.sync_api import sync_playwright

cfg = json.load(sys.stdin)
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": cfg["breite"], "height": cfg["hoehe"]})
    page.goto(cfg["url"], wait_until="networkidle", timeout=120000)

    for _ in range(60):
        if page.evaluate("window.__theatreReady === true"):
            break
        page.wait_for_timeout(1000)

    dauer = page.evaluate(
        "window.__theatreGetDuration ? window.__theatreGetDuration() : 0")
    print("Dauer laut Seite: %ss" % dauer, flush=True)

    ausschnitt = cfg.get("ausschnitt")
    for f in range(cfg["frames"]):
        t = cfg["start"] + f / cfg["fps"]
        page.evaluate("window.__theatreSetTime && window.__theatreSetTime(%r)" % t)
        page.wait_for_timeout(30)
        ziel = os.path.join(cfg["ordner"], "%06d.png" % f)
        if ausschnitt:
            page.screenshot(path=ziel, clip=ausschnitt)
        else:
            page.screenshot(path=ziel)
        if f % 50 == 0:
            print("Frame %d/%d (%.1fs)" % (f, cfg["frames"], t), flush=True)
    browser.close()
    print("fertig", flush=True)
'''


class RenderFehler(RuntimeError):
    """Der Browserprozess ist nicht gestartet oder abgebrochen."""


class BildfolgenRender:
    """Nimmt die Studio-Szene Bild fuer Bild auf."""

    ZEITGRENZE = 600
    VORGABE_DAUER = 10

    def __init__(self, ordner, breite=1920, hoehe=1080, fps=30):
        self.ordner = str(ordner)
        self.breite = int(breite)
        self.hoehe = int(hoehe)
        self.fps = int(fps) or 30

    @staticmethod
    def python_mit_playwright():
        from pathlib import Path
        return str(Path(settings.TOOLS_ROOT) / 'python10' / 'Scripts' / 'python.exe')

    @staticmethod
    def vollstaendige_url(url, port):
        """Relative Szenen-URL absolut machen und den Aufnahmemodus anhaengen."""
        if url.startswith('/'):
            url = 'http://127.0.0.1:%s%s' % (port, url)
        trenner = '&' if '?' in url else '?'
        return '%s%srenderMode=server&autoplay=1' % (url, trenner)

    def aufnehmen(self, url, start=0.0, ende=0.0, ausschnitt=None):
        """Bilder in den Ordner schreiben; gibt die Zahl der Bilder zurueck."""
        dauer = (ende - start) if ende > start else self.VORGABE_DAUER
        frames = max(1, int(dauer * self.fps))
        einstellungen = {
            'url': url, 'breite': self.breite, 'hoehe': self.hoehe,
            'fps': self.fps, 'start': start, 'frames': frames,
            'ordner': self.ordner, 'ausschnitt': ausschnitt,
        }
        try:
            ergebnis = subprocess.run(
                [self.python_mit_playwright(), '-c', SKRIPT],
                input=json.dumps(einstellungen), capture_output=True, text=True,
                timeout=self.ZEITGRENZE)
        except subprocess.TimeoutExpired as e:
            raise RenderFehler('Aufnahme hat die Zeitgrenze ueberschritten') from e
        except FileNotFoundError as e:
            raise RenderFehler('Python mit Playwright nicht gefunden: %s'
                               % self.python_mit_playwright()) from e
        if ergebnis.returncode != 0:
            raise RenderFehler('Playwright: %s' % (ergebnis.stderr or '')[-500:])
        logger.info('Bildfolge aufgenommen: %d Bilder nach %s', frames, self.ordner)
        return frames

    @staticmethod
    def ausschnitt(x, y, breite, hoehe):
        """Zuschnitt fuer die Aufnahme — None, wenn keiner gewuenscht ist."""
        if breite > 0 and hoehe > 0:
            return {'x': x, 'y': y, 'width': breite, 'height': hoehe}
        return None

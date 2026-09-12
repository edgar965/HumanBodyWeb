# -*- coding: utf-8 -*-
u"""Kein Einblenden mit `style.display = ''` bei Elementen, die die Vorlage
per Klasse oder ID-Regel versteckt.

WARUM (11.09.2026, Edgar: „suche noch nach anderen stillen Fehlern"): Der
Stil-Umbau 6fbaa7e (17.08.2026) ersetzte `style="display:none"` durch die
Klassen `hb-versteckt` / `hb-display-none*` und ID-Regeln. Wer danach mit
einem LEEREN Inline-Wert einblenden wollte, blendete nichts ein — ein leerer
Wert hebt keine Regel auf. Gefunden wurden 18 solche Stellen in sechs Seiten,
darunter der Kleider-Reiter der Szene, alle Formparameter des
Modellgenerators, Fortschritt und Abbrechen des MP4-Exports, der
Abbrechen-Knopf des Stoff-Exports und die Kontextmenüs des BVH-Studios.

Erlaubt bleibt '' dort, wo dieselbe Stelle auch die Klasse umschaltet
(`classList.toggle('hb-versteckt', …)` in Reichweite) — dann ist der leere
Stil das Zurücksetzen, nicht das Einblenden.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

WURZEL = Path(settings.BASE_DIR)
JS_ORDNER = [WURZEL / 'static' / 'viewer', WURZEL / 'static' / 'js']
HTML = list((WURZEL / 'templates').rglob('*.html'))
CSS = list((WURZEL / 'static' / 'css').rglob('*.css')) + HTML

LEER = re.compile(r"(\w+)\.style\.display\s*=\s*[^;]*?(?<![\w'\"])(''|\"\")")
VERSTECKKLASSEN = ('hb-versteckt', 'hb-display-none', 'hb-display-none-b',
                   'hb-kontextmenue')
REICHWEITE = 3   # Zeilen davor/danach, in denen eine Klassen-Umschaltung zählt


class LeeresDisplayTest(SimpleTestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.html = {p: p.read_text(encoding='utf-8', errors='replace') for p in HTML}
        cls.css = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in CSS)

    # -- Hilfen ---------------------------------------------------------------

    @staticmethod
    def _element_id(zeilen, var, nr):
        kopf = '\n'.join(zeilen[:nr])
        muster = r"%s\s*=\s*[^;\n]*getElementById\(['\"]([^'\"]+)['\"]\)" % re.escape(var)
        treffer = list(re.finditer(muster, kopf))
        if treffer:
            return treffer[-1].group(1)
        inline = re.search(r"getElementById\(['\"]([^'\"]+)['\"]\)", zeilen[nr - 1])
        return inline.group(1) if inline else None

    def _versteckt(self, kennung):
        """Warum die Vorlage das Element versteckt — oder [] wenn gar nicht."""
        gruende = []
        for t in self.html.values():
            for m in re.finditer(r'<[a-z]+[^>]*\bid="%s"[^>]*>' % re.escape(kennung), t):
                k = re.search(r'class="([^"]*)"', m.group(0))
                klassen = k.group(1).split() if k else []
                gruende += ['.' + c for c in klassen if c in VERSTECKKLASSEN]
        if re.search(r'#%s\b[^{]*\{[^}]*display\s*:\s*none' % re.escape(kennung), self.css):
            gruende.append('#' + kennung)
        return gruende

    @staticmethod
    def _klasseUmgeschaltet(zeilen, var, nr):
        fenster = '\n'.join(zeilen[max(0, nr - 1 - REICHWEITE):nr + REICHWEITE])
        return re.search(r"%s\.classList\.(toggle|remove)\(\s*['\"](%s)"
                         % (re.escape(var), '|'.join(VERSTECKKLASSEN)), fenster) is not None

    # -- Test -----------------------------------------------------------------

    def test_leeres_display_zeigt_nichts(self):
        befunde = []
        for ordner in JS_ORDNER:
            for p in ordner.rglob('*.js'):
                if 'vendor' in p.parts:
                    continue
                zeilen = p.read_text(encoding='utf-8', errors='replace').split('\n')
                for nr, zeile in enumerate(zeilen, 1):
                    for m in LEER.finditer(zeile):
                        var = m.group(1)
                        kennung = self._element_id(zeilen, var, nr)
                        if not kennung:
                            continue
                        gruende = self._versteckt(kennung)
                        if not gruende or self._klasseUmgeschaltet(zeilen, var, nr):
                            continue
                        befunde.append('%s:%d  #%s versteckt durch %s'
                                       % (p.relative_to(WURZEL), nr, kennung, ', '.join(gruende)))
        self.assertEqual(befunde, [], '\n' + '\n'.join(befunde))

# -*- coding: utf-8 -*-
u"""BVH Studio: Die Kontextmenüs der Zeitleiste müssen sichtbar werden können.

WARUM (11.09.2026, Edgar: „Es waren doch auch Kontext Menüs verfügbar, z.B.
bei Rechtsklick auf ein item in der Timeline?"): Vom 17.08. bis zum 11.09.2026
öffnete KEIN Kontextmenü der Zeitleiste. Der Umbau 6fbaa7e ersetzte den
Inline-Stil `style="display:none"` der Menüs durch Klassen
(`.hb-kontextmenue`, `.hb-display-none`) — und das Einblenden im Skript
blieb `menue.style.display = ''`. Ein leerer Inline-Wert hebt eine
Klassenregel nicht auf; das Menü blieb unsichtbar, ohne Fehler.

Geprüft wird beides zusammen: Jedes Menü, das die Vorlage über eine Klasse
versteckt, wird im Skript mit einem WERT eingeblendet, nicht mit ''.

Dazu seit 13.09.2026 (Edgar: „Länge einstellen soll auch beim Modell-Eintrag
als Kontextmenü kommen"): Das Untermenü „Länge" steht im Modellmenü mit
denselben Aktionen wie im Clipmenü, `Modellmenue` reicht sie an `fn.clipLaenge`
durch, und `Clipbearbeitung.laenge` lässt `model` zu. Sabotage: `'model'` aus
der Typliste in `clipbearbeitung.js` → rot.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ._studiovorlage import Studiovorlage

WURZEL = Path(settings.BASE_DIR)
VORLAGE = WURZEL / 'templates' / 'bvh_studio.html'
STUDIO = WURZEL / 'static' / 'viewer' / 'bvh_studio'

# Die Module, die Menüs der Zeitleiste einblenden.
ZEIGER = ['zeitleiste_menue.js', 'zeitleiste_kontextmenue.js']
VERSTECKKLASSEN = ('hb-kontextmenue', 'hb-display-none')


class KontextmenueSichtbarTest(SimpleTestCase):

    databases = set()

    def test_menues_werden_per_klasse_versteckt(self):
        """Die Voraussetzung des Fehlers: Verstecken über eine Klasse."""
        html = VORLAGE.read_text(encoding='utf-8')
        menues = re.findall(r'<div id="([a-z-]*context-menu)" class="([^"]+)"', html)
        self.assertTrue(menues, 'keine Kontextmenüs in bvh_studio.html gefunden')
        for kennung, klassen in menues:
            self.assertTrue(any(k in klassen.split() for k in VERSTECKKLASSEN),
                            f'{kennung}: versteckt sich nicht über {VERSTECKKLASSEN}')

    def test_einblenden_setzt_einen_wert(self):
        """Wer ein Menü zeigt, setzt `display` auf einen Wert — '' zeigt nichts."""
        for name in ZEIGER:
            text = (STUDIO / name).read_text(encoding='utf-8')
            leer = re.findall(r"menue\.style\.display\s*=\s*''", text)
            self.assertFalse(leer, f"{name}: style.display = '' blendet nicht ein")
            self.assertIn("menue.style.display = 'block'", text,
                          f'{name}: kein Einblenden mit display: block')


class ModellLaengeTest(SimpleTestCase):

    databases = set()

    def test_laenge_im_modellmenue_wie_im_clipmenue(self):
        html = Studiovorlage.text()
        menues = {}
        for kennung in ('clip-context-menu', 'model-context-menu'):
            anfang = html.index('<div id="%s"' % kennung)
            block = html[anfang:html.index('\n</div>', anfang)]
            menues[kennung] = re.findall(
                r'data-action="(ctx-laenge[a-z-]*)"(?: data-wert="(\d+)")?', block)
        self.assertTrue(menues['clip-context-menu'])
        self.assertEqual(menues['model-context-menu'], menues['clip-context-menu'])
        modellmenue = (STUDIO / 'zeitleiste_modellmenue.js').read_text(encoding='utf-8')
        self.assertIn("aktion === 'ctx-laenge-prozent'", modellmenue)
        self.assertIn("aktion === 'ctx-laenge-sekunden'", modellmenue)
        self.assertIn("classList.toggle('hb-versteckt', !treffer)", modellmenue)
        bearbeitung = (STUDIO / 'clipbearbeitung.js').read_text(encoding='utf-8')
        self.assertIn("['bvh', 'audio', 'model', 'script'].includes(wahl.clip.type)", bearbeitung)
        # Prozent messen sich am Ende der ANDEREN Clips, nie am eigenen.
        self.assertIn('anderer !== clip && anderer.endFrame > ende', bearbeitung)

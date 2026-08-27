# -*- coding: utf-8 -*-
"""Wächter für ProjektTemp — Zwischendateien und ihr Aufräumen.

WARUM (Review 13.08.2026)
-------------------------
Zwei Befunde, beide am echten Code nachgelesen:

1. Sechs Stellen schrieben mit `tempfile.NamedTemporaryFile()` bzw.
   `mkdtemp()` ohne `dir=` nach System-Temp — also nach `C:`. Das ist in
   diesem Projekt ausdrücklich verboten; es hat einmal rund 100 GB Datenmüll
   dort hinterlassen.

2. `theatre_convert_video` hatte einen `finally`-Block, der nur aus `pass` und
   dem Kommentar „Clean up on error (if response wasn't created)" bestand. Auf
   JEDEM Fehlerweg blieben beide Zwischendateien liegen.

Der Fall, den kein `finally` abdeckt: Der Browser bricht das Hochladen ab, die
Antwort wird nie fertig, und der an sie gehängte Löschaufruf läuft deshalb nie.
Dafür gibt es den Hausmeister — und dafür gibt es diesen Test.
"""
import os
import time
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from core.projekt_temp import ProjektTemp


class ProjektTempTest(TestCase):

    def setUp(self):
        self.basis = ProjektTemp.verzeichnis()
        self.eigene = []
        self.addCleanup(lambda: ProjektTemp.weg(*self.eigene))

    def test_liegt_im_projekt_und_nicht_in_system_temp(self):
        """Der Kern der Regel: nichts auf C:\\…\\Temp."""
        import tempfile as _t
        f = ProjektTemp.datei(suffix='.mp4')
        self.eigene.append(f)
        self.assertTrue(f.is_relative_to(Path(settings.MEDIA_ROOT)),
                        '%s liegt nicht unter MEDIA_ROOT' % f)
        # `gettempdir()` steht hier in einer ZUSICHERUNG, es wird nichts
        # dorthin geschrieben — Lehre gilt hier nicht
        # („keine-temp-dateien-im-system"). Der Wächter meldete sonst
        # genau die Prüfung, die seine eigene Lehre durchsetzt.
        system = Path(_t.gettempdir()).resolve()
        self.assertFalse(str(f.resolve()).lower().startswith(str(system).lower()),
                         'Datei liegt in System-Temp: %s' % f)

    def test_ordner_wird_angelegt_und_wieder_entfernt(self):
        d = ProjektTemp.ordner(prefix='test_')
        (d / 'inhalt.txt').write_text('x', encoding='utf-8')
        self.assertTrue(d.is_dir())
        ProjektTemp.weg(d)
        self.assertFalse(d.exists(), 'Verzeichnis mit Inhalt blieb liegen')

    def test_weg_raeumt_vorhandenes_und_uebergeht_fehlendes(self):
        """Für den `finally`-Zweig: Was schon weg ist, ist in Ordnung.

        Der Rumpf behauptete bis zum 27.08.2026 NICHTS — er verliess sich
        darauf, dass keine Ausnahme fliegt. Eine solche Prüfung meldet auch
        dann grün, wenn `weg` gar nichts mehr tut."""
        da = ProjektTemp.datei(suffix='.tmp')
        fehlt = self.basis / 'gibtesnicht.tmp'
        self.assertTrue(da.exists())
        ProjektTemp.weg(da, fehlt, None)
        self.assertFalse(da.exists(), 'vorhandene Datei blieb liegen')
        self.assertFalse(fehlt.exists())

    def test_hausmeister_entfernt_nur_altes(self):
        """DER FALL, DEN KEIN finally ABDECKT: abgebrochener Upload.

        Alt wird hier über die Änderungszeit nachgestellt, statt einen Tag zu
        warten."""
        alt_datei = ProjektTemp.datei(suffix='.png', prefix='alt_')
        alt_ordner = ProjektTemp.ordner(prefix='alt_')
        neu = ProjektTemp.datei(suffix='.png', prefix='neu_')
        self.eigene += [neu]
        vorgestern = time.time() - 48 * 3600
        for p in (alt_datei, alt_ordner):
            os.utime(p, (vorgestern, vorgestern))

        # `erzwingen=True` übergeht die Drosselung (siehe MIN_ABSTAND_S) —
        # hier soll er ja gerade jetzt laufen.
        entfernt = ProjektTemp.hausmeister(erzwingen=True)

        self.assertGreaterEqual(entfernt, 2)
        self.assertFalse(alt_datei.exists(), 'alte Datei blieb liegen')
        self.assertFalse(alt_ordner.exists(), 'alter Ordner blieb liegen')
        self.assertTrue(neu.exists(), 'der Hausmeister hat Frisches mitgenommen')

    def test_anlegen_ruft_den_hausmeister(self):
        """Er soll nebenbei laufen, damit niemand ihn planen muss."""
        ProjektTemp._letzter_lauf = 0.0        # Drosselung zurücksetzen
        alt = ProjektTemp.datei(suffix='.tmp', prefix='alt2_')
        vorgestern = time.time() - 48 * 3600
        os.utime(alt, (vorgestern, vorgestern))
        ProjektTemp._letzter_lauf = 0.0        # das Anlegen oben hat ihn verbraucht
        neu = ProjektTemp.datei(suffix='.tmp', prefix='neu2_')
        self.eigene.append(neu)
        self.assertFalse(alt.exists(),
                         'Anlegen einer neuen Datei hat nicht aufgeräumt')

    def test_hausmeister_ist_gedrosselt(self):
        """NEU 15.08.2026, mit Messung begründet.

        `iterdir()` samt `stat()` je Eintrag kostet gemessen 1,1 ms bei 100,
        19,9 ms bei 2.000 und 138,8 ms bei 10.000 Resten. Er lief bei JEDEM
        Anlegen mit — das zahlt jede Zwischendatei mit. Höchstens alle
        `MIN_ABSTAND_S` Sekunden genügt, die Altersgrenze sind ohnehin 24 h."""
        ProjektTemp._letzter_lauf = 0.0
        self.assertGreaterEqual(ProjektTemp.MIN_ABSTAND_S, 60)

        alt = ProjektTemp.datei(suffix='.tmp', prefix='alt3_')
        vorgestern = time.time() - 48 * 3600
        os.utime(alt, (vorgestern, vorgestern))

        # Erster Lauf räumt, der zweite unmittelbar danach nicht mehr.
        ProjektTemp.hausmeister(erzwingen=True)
        zweiter = ProjektTemp.datei(suffix='.tmp', prefix='alt4_')
        os.utime(zweiter, (vorgestern, vorgestern))
        self.assertEqual(ProjektTemp.hausmeister(), 0,
                         'der Hausmeister lief trotz Drosselung erneut')
        self.assertTrue(zweiter.exists())

        # ... und `erzwingen=True` kommt trotzdem durch.
        self.assertGreaterEqual(ProjektTemp.hausmeister(erzwingen=True), 1)
        self.assertFalse(zweiter.exists())

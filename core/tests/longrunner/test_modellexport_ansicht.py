# -*- coding: utf-8 -*-
u"""Sieht die exportierte Figur aus wie die Figur? (26.09.2026)

Edgar: „mach dir einen besseren Testcase der die Bilder aus dem Charakter
Fenster vergleicht mit dem Meshlab, also auch Augen, schuhe, Haut usw."

WARUM NICHT MESHLAB: `meshlabserver` gibt es seit 2021 nicht mehr, und
`pymeshlab` rendert nur Silhouetten — ohne Kamera, ohne Textur (gemessen:
zwei Farben im Bild). Stattdessen liest BLENDER die `.obj` — ein fremdes
Programm mit eigenem OBJ/MTL/PNG-Leser, headless aufrufbar. Es zeigt nicht
MeshLabs Bild, aber es findet dieselben Datei- und Kartenfehler: alle drei
Fehler dieses Tages waren in Blender genauso zu sehen.

WARUM KEIN PIXELVERGLEICH mit dem Browserbild: zwei Renderer, zwei
Beleuchtungen, zwei Kameras — der Vergleich wäre entweder blind (große
Toleranz) oder dauernd rot. Geprüft wird stattdessen das MERKMAL, das alle
drei Vorfälle teilen: eine Stelle der Figur ist FARBLOS, wo Farbe hingehört.

    hellgraue Flecken an Hals, Knie, Fingern -> Karten standen auf dem Kopf
    weiße Augen ohne Iris                    -> Hornhaut davor
    schneeweiße Brauen                       -> `Kd` ging verloren

Messwerte am echten Modell (Blender, 700x1000, Damira1):

    vor den Berichtigungen:  2,0 % farblos, Kniestreifen 13,7 %
    danach:                  0,0 % farblos, kein Streifen über 1,7 %

DER FALL BRAUCHT EINE EXPORTDATEI. Er erzeugt sie nicht selbst — dafür
müsste eine Genesis-9-Figur im Browser stehen. Liegt keine im Ausgabeordner,
wird er übersprungen und sagt, was zu tun ist. Nach einem Export im Browser
ist er scharf.
"""
import subprocess
import unittest
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.exportbildpruefung import Exportbildpruefung
from core.dienste.exportkartenpruefung import Exportkartenpruefung
from core.projekt_temp import ProjektTemp

SKRIPT = Path(settings.BASE_DIR) / 'core' / 'dienste' / 'blender' / 'exportbild.py'

#: Über dieser Marke gilt die Figur als fehlerhaft. Die berichtigte Ausgabe
#: lag bei 0,0 %, die fehlerhafte bei 2,0 % — die Grenze liegt dazwischen und
#: nicht knapp an einem der beiden Werte.
GRENZE_GESAMT = 0.01
#: Je Höhenstreifen darf es mehr sein: Augenweiß und Zähne sind echtes Weiß.
#: Der Kopfstreifen lag auch berichtigt bei 1,7 %, der Kniestreifen fehlerhaft
#: bei 13,7 %.
GRENZE_STREIFEN = 0.05


def neueste_ausgabe():
    u"""Die zuletzt geschriebene `.obj` im Ausgabeordner — oder None.

    `rglob`, nicht `glob('*/*.obj')` (Fund 27.09.2026): Ein Export mit
    eigenem Zielordner je Format (Edgar: „exportiere blender files in
    …\\Models\\Blender, glb in …\\Models\\glb, obj in …\\Models\\obj") legt die
    Datei unter `Models/obj/<Name>/<Name>.obj` ab — eine Ebene tiefer als der
    normale `Models/<Name>/<Name>.obj`. Der feste Zwei-Ebenen-Glob fand dann
    NICHTS und der Fall übersprang sich still, obwohl frisch exportiert war.
    """
    wurzel = Path(settings.HUMANBODY_MODELLEXPORT_VORGABE_DIR)
    if not wurzel.is_dir():
        return None
    dateien = sorted(wurzel.rglob('*.obj'), key=lambda p: p.stat().st_mtime, reverse=True)
    return dateien[0] if dateien else None


class ModellexportAnsichtTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.obj = neueste_ausgabe()
        cls.bericht = None
        if not cls.obj:
            return
        ziel = Path(ProjektTemp.ordner('test_modellexport')) / 'ansicht.png'
        lauf = subprocess.run(
            [str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python', str(SKRIPT), '--',
             '--obj', cls.obj.as_posix(), '--png', ziel.as_posix(),
             '--breite', '700', '--hoehe', '1000'],
            capture_output=True, text=True, timeout=900,
        )
        if lauf.returncode != 0 or not ziel.is_file():
            raise RuntimeError(f'Blender-Lauf gescheitert:\n{lauf.stdout[-3000:]}\n{lauf.stderr[-2000:]}')
        cls.bild = ziel
        cls.bericht = Exportbildpruefung(ziel).bericht()

    def setUp(self):
        if not self.obj:
            raise unittest.SkipTest(
                'Keine Exportdatei unter %s — erst im Browser exportieren, dann läuft der Fall.'
                % settings.HUMANBODY_MODELLEXPORT_VORGABE_DIR)

    def test_1_die_figur_ist_nicht_farblos(self):
        u"""Der gemeinsame Nenner aller drei Vorfälle."""
        b = self.bericht
        self.assertGreater(b['punkte'], 10000, 'zu wenig Figur im Bild — stimmt die Kamera?')
        self.assertLess(b['anteil'], GRENZE_GESAMT,
                        'farblose Flächen im Export: %s\n%s'
                        % (self.obj, '\n'.join(Exportbildpruefung.zeilen(b))))

    def test_2_keine_einzelne_koerperpartie_faellt_aus(self):
        u"""Der Gesamtwert allein reicht nicht: die weißen Knie waren nur
        2,0 % der Figur, aber 13,7 % ihres Streifens — und genau das hat
        Edgar gesehen."""
        schlimm = self.bericht['schlimmster']
        self.assertIsNotNone(schlimm)
        self.assertLess(schlimm['anteil'], GRENZE_STREIFEN,
                        'Streifen %d ist zu %.1f %% farblos\n%s'
                        % (schlimm['nr'], 100 * schlimm['anteil'],
                           '\n'.join(Exportbildpruefung.zeilen(self.bericht))))

    def test_3_keine_karte_steht_auf_dem_kopf(self):
        u"""Zweite, unabhängige Sicht auf dieselbe Datei: nicht das Bild,
        sondern die Karten. Sie findet auch kleine Stellen (Brauen), die im
        700-Pixel-Bild untergehen."""
        bericht = Exportkartenpruefung(self.obj).bericht()
        self.assertEqual(bericht['verdacht_gespiegelt'], [],
                         'Bildkarten stehen auf dem Kopf:\n%s'
                         % '\n'.join(Exportkartenpruefung.zeilen(bericht)))

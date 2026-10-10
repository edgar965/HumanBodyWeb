# -*- coding: utf-8 -*-
"""Die Bildzahl der Vorstufe bei Containern ohne Zahl, vor allem `.webm` (09.10.2026).

DER ANLASS
==========
Das Kamerabahn-Paket meldete als Nebenbefund: `Vorstufe` liest aus `.webm` 0 Bilder und bricht ab. Gemessen 09.10.2026
(`ProjektTemp/_wegwerf/vorstufe_webm/webm_pruefen.py`): GVHMRs `get_video_lwh` (imageio `improps`) meldet bei einer 3-s-WebM-Datei (VP9) 0 Bilder,
`cv2` und das Dekodieren finden 75; die mp4 daneben meldet 75. Der Lauf sagte dann „Spur hat 75 Bilder, das Video 0". Jetzt zählt `Vorstufenbilder.zaehlen`
durch Dekodieren, wenn die gemeldete Zahl nicht über 0 liegt (`Vorstufe.videomasse`).

WAS DIESE PRÜFUNG NICHT IST
===========================
Kein Video, kein GVHMR: `get_video_lwh` und `av` sind Attrappen. Dass die Zahl mit der übereinstimmt, die `Vorstufenbilder.bloecke` wirklich liefert, zeigt
`ProjektTemp/_wegwerf/vorstufe_webm/vorstufe_masse_pruefen.py` (VP9 75 = 75, VP8 100 = 100, mp4 75 = 75, gemessen 09.10.2026). Geschrieben am 09.10.2026.

BDD - GEGEBEN / DANN
====================
    ein Container, der 0 Bilder nennt   ... `videomasse` zählt durch Dekodieren und gibt Breite und Höhe unverändert weiter
    ein Container mit Bildzahl          ... es wird nicht gezählt (das Dekodieren ganzer Videos ist teuer)
    `zaehlen`                           ... zählt die dekodierten Bilder des ersten Videostroms
Sabotage-Gegenprobe (gelaufen 09.10.2026): `if laenge <= 0` durch `if False` ersetzen → der erste Test wird rot (Länge 0 statt 7).

NACHTRAG (09.10.2026 spät): Der ganze Lauf mit einer `.webm` brach weiter ab — `Personenspur` rief `get_video_lwh` selbst auf. Die Zählung sitzt jetzt in
`Vorstufenbilder.masse`; neu: ein Fall für `masse` und eine Quelltext-Wache (`get_video_lwh(` nur in `vorstufenbilder.py`). GESCHRIEBEN, NICHT GELAUFEN.
"""
import sys
import types
from unittest import mock

from django.test import SimpleTestCase

from ._wrappersuchpfad import WRAPPERS, Wrappersuchpfad

Wrappersuchpfad.setzen()

from vorstufe import Vorstufe  # noqa: E402
from vorstufenbilder import Vorstufenbilder  # noqa: E402


class _Behaelter:
    """Attrappe für `av.open(...)`: ein Videostrom, `decode` liefert n Bilder."""

    def __init__(self, n):
        self.n = n
        self.streams = types.SimpleNamespace(video=[types.SimpleNamespace(thread_type=None)])

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def decode(self, strom):
        return iter(range(self.n))


def _attrappen(gemeldet, dekodiert):
    """`hmr4d.utils.video_io_utils` und `av` als Attrappen, `get_video_lwh` meldet `gemeldet` Bilder."""
    gvhmr = types.ModuleType('hmr4d.utils.video_io_utils')
    gvhmr.get_video_lwh = lambda pfad: (gemeldet, 320, 180)
    av = types.ModuleType('av')
    av.open = mock.Mock(side_effect=lambda pfad: _Behaelter(dekodiert))
    module = {'hmr4d': types.ModuleType('hmr4d'), 'hmr4d.utils': types.ModuleType('hmr4d.utils'),
              'hmr4d.utils.video_io_utils': gvhmr, 'av': av}
    return mock.patch.dict(sys.modules, module), av


class DieBildzahl(SimpleTestCase):
    def test_ein_container_ohne_bildzahl_wird_gezaehlt(self):
        patch, av = _attrappen(gemeldet=0, dekodiert=7)
        with patch:
            laenge, breite, hoehe = Vorstufe('x.webm', 'ziel').videomasse()
        self.assertEqual((laenge, breite, hoehe), (7, 320, 180))
        av.open.assert_called_once_with('x.webm')

    def test_mit_gemeldeter_bildzahl_wird_nicht_gezaehlt(self):
        patch, av = _attrappen(gemeldet=75, dekodiert=3)
        with patch:
            laenge, breite, hoehe = Vorstufe('x.mp4', 'ziel').videomasse()
        self.assertEqual((laenge, breite, hoehe), (75, 320, 180))
        av.open.assert_not_called()

    def test_zaehlen_gibt_die_dekodierten_bilder(self):
        patch, _ = _attrappen(gemeldet=0, dekodiert=12)
        with patch:
            self.assertEqual(Vorstufenbilder.zaehlen('x.webm'), 12)

    def test_masse_nimmt_die_uebergebene_funktion(self):
        """Personenspur und GEM übergeben ihre eigene `get_video_lwh` (GVHMR bzw. GEM) — dieselbe Zählung."""
        patch, av = _attrappen(gemeldet=0, dekodiert=9)
        with patch:
            self.assertEqual(Vorstufenbilder.masse('x.webm', lambda pfad: (0, 640, 360)), (9, 640, 360))
            self.assertEqual(Vorstufenbilder.masse('x.mp4', lambda pfad: (50, 640, 360)), (50, 640, 360))
        av.open.assert_called_once_with('x.webm')

    def test_kein_aufruf_von_get_video_lwh_ausser_in_masse(self):
        """Wache (Ganzlauf 09.10.2026): Die erste Korrektur betraf nur `Vorstufe.videomasse`; die Personenspur
        (`track`, `spurwahl`) rief `get_video_lwh` weiter selbst auf und brach bei einer `.webm` mit 0 Bildern ab.
        Jeder Aufruf `get_video_lwh(` im Wrapperbaum steht in `vorstufenbilder.py`; die anderen übergeben die Funktion."""
        aufrufe = []
        for datei in sorted(WRAPPERS.glob('*.py')):
            if datei.name == 'vorstufenbilder.py':
                continue
            for nummer, zeile in enumerate(datei.read_text(encoding='utf-8').splitlines(), 1):
                if 'get_video_lwh(' in zeile and not zeile.lstrip().startswith('#'):
                    aufrufe.append('%s:%d' % (datei.name, nummer))
        self.assertEqual(aufrufe, [])

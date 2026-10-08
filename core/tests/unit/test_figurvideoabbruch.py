# -*- coding: utf-8 -*-
"""„Abbrechen" beim Video (Edgar, 08.10.2026: „mach einen Button Abbrechen für die Video Erzeugung und brich den
job ab") — `Figurvideoabbruch`, ohne echten Prozess: Der Beendigungsweg ist ersetzt.

Gemessen im Chrome am echten Lauf (Kennung `79679c15824e`, `Bild 13 von 96`, zwei python.exe — der Starter und
sein Kind): Der Abbruch nach einem Autoreload des Servers (Verzeichnis `LaufendeProzesse` leer, PID aus
`prozess.json`) beendete beide, `fortschritt.json` stand danach auf `abgebrochen`.

Sabotage-Gegenprobe: in `abbrechen` die Prüfung `stand.get('fertig')` streichen → Fall 1 rot; die Befehlszeilen-
Prüfung in `_pid` streichen → Fall 4 rot (ein Abbruch träfe dann jede Nummer, die in `prozess.json` stand).
"""
import json
import os
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.figurvideoabbruch import Figurvideoabbruch
from core.dienste.laufende_prozesse import LaufendeProzesse

from ._pruefablage import Pruefablage


def _schreiben(ordner, name, inhalt):
    with open(os.path.join(ordner, name), 'w', encoding='utf-8') as datei:
        json.dump(inhalt, datei)


def _lesen(ordner, name):
    with open(os.path.join(ordner, name), encoding='utf-8') as datei:
        return json.load(datei)


class _Prozess:
    """Was von `subprocess.Popen` gebraucht wird: `pid` und `poll`."""

    def __init__(self, pid, lebt=True):
        self.pid = pid
        self._lebt = lebt

    def poll(self):
        return None if self._lebt else 0


class FigurvideoabbruchTest(SimpleTestCase):
    databases = set()

    def tearDown(self):
        LaufendeProzesse.entfernen('figurvideo_abc123')

    def test_1_fertiges_video_wird_nicht_abgebrochen(self):
        with Pruefablage.ordner('videoabbruch_') as ordner:
            _schreiben(ordner, 'fortschritt.json', {'phase': 'Fertig', 'anteil': 1.0, 'fertig': True, 'fehler': None})
            with mock.patch.object(Figurvideoabbruch, '_beenden') as beenden:
                antwort = Figurvideoabbruch.abbrechen('abc123', ordner)
            self.assertFalse(antwort['abgebrochen'])
            beenden.assert_not_called()
            self.assertIsNone(_lesen(ordner, 'fortschritt.json')['fehler'], 'der Stand bleibt, wie er war')

    def test_2_laufender_prozess_aus_dem_verzeichnis_wird_beendet(self):
        with Pruefablage.ordner('videoabbruch_') as ordner:
            _schreiben(ordner, 'fortschritt.json', {'phase': 'Bild 13 von 96', 'anteil': 0.5, 'fertig': False, 'fehler': None})
            LaufendeProzesse.eintragen('figurvideo_abc123', _Prozess(4711))
            with mock.patch.object(Figurvideoabbruch, '_beenden') as beenden:
                antwort = Figurvideoabbruch.abbrechen('abc123', ordner)
            beenden.assert_called_once_with(4711)
            self.assertEqual(antwort, {'abgebrochen': True, 'prozess_beendet': True, 'grund': ''})
            stand = _lesen(ordner, 'fortschritt.json')
            self.assertEqual(stand['fehler'], Figurvideoabbruch.TEXT)
            self.assertTrue(stand['abgebrochen'])
            self.assertEqual(stand['phase'], 'Bild 13 von 96', 'die Phase, in der abgebrochen wurde, bleibt lesbar')
            self.assertIsNone(LaufendeProzesse.holen('figurvideo_abc123'), 'der Eintrag ist weg')

    def test_3_ohne_prozess_wird_nur_der_stand_geschrieben(self):
        with Pruefablage.ordner('videoabbruch_') as ordner:
            with mock.patch.object(Figurvideoabbruch, '_beenden') as beenden:
                antwort = Figurvideoabbruch.abbrechen('abc123', ordner)
            beenden.assert_not_called()
            self.assertEqual(antwort, {'abgebrochen': True, 'prozess_beendet': False, 'grund': ''})
            stand = _lesen(ordner, 'fortschritt.json')
            self.assertEqual(stand['fehler'], Figurvideoabbruch.TEXT)
            self.assertEqual(stand['phase'], 'Abgebrochen')

    def test_4_pid_aus_der_datei_nur_wenn_die_befehlszeile_die_kennung_nennt(self):
        """Nach einem Autoreload ist nur die PID da; Windows vergibt sie rasch neu — eine fremde Nummer darf nicht sterben."""
        with Pruefablage.ordner('videoabbruch_') as ordner:
            _schreiben(ordner, Figurvideoabbruch.PID_DATEI, {'pid': 4711})
            with mock.patch('core.dienste.figurvideoabbruch.Prozesspruefung.lebt', return_value=True):
                with mock.patch.object(Figurvideoabbruch, '_befehlszeile', return_value='python.exe fremd.py'):
                    self.assertIsNone(Figurvideoabbruch._pid('abc123', ordner))
                with mock.patch.object(
                    Figurvideoabbruch, '_befehlszeile',
                    return_value=r'python.exe filmlauf.py A:\figurvideos\abc123\auftrag.json',
                ):
                    self.assertEqual(Figurvideoabbruch._pid('abc123', ordner), 4711)

    def test_5_beendeter_prozess_im_verzeichnis_zaehlt_nicht(self):
        with Pruefablage.ordner('videoabbruch_') as ordner:
            LaufendeProzesse.eintragen('figurvideo_abc123', _Prozess(4711, lebt=False))
            self.assertIsNone(Figurvideoabbruch._pid('abc123', ordner))

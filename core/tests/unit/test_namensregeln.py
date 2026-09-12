# -*- coding: utf-8 -*-
u"""Namensregeln — die drei Windows-Fallen, jede für sich.

WARUM (12.09.2026, Befund `testdeckung`): `Namensregeln` liegt auf acht
Arbeitswegen (Modelle, Szenen, BVH, Videoexport, Katalogpflege …), wurde aber
in keinem Test beim Namen genannt — `test_safe_paths` prüft die Meldungen nur
durch `SafePath` hindurch. Wer eine Regel in der Klasse ändert, sieht dort
erst spät, welche sie war. Hier steht je Regel ein Fall, und die Meldungstexte
sind Teil der Schnittstelle (sie gehen als Ablehnungsgrund an den Aufrufer).

Sabotage-Gegenprobe: `geraet` ohne `.split('.')[0]` lässt `COM1.txt` durch —
`test_geraet_auch_mit_endung` wird rot; `datei` ohne die Bindestrichregel
macht `test_datei_lehnt_fuehrenden_bindestrich_ab` rot.

Aufruf: python manage.py test core.tests.unit.test_namensregeln
"""
import unittest

from core.namensregeln import Namensregeln, GERAETE, VERBOTEN


class NamensregelnTest(unittest.TestCase):
    databases = set()

    def grund(self, wert):
        u"""Der Ablehnungsgrund — und dass es einen gibt."""
        assert wert is not None, 'kein Ablehnungsgrund'
        return wert

    # -- Gerätenamen ---------------------------------------------------------

    def test_geraet_in_jeder_schreibweise(self):
        for name in ('CON', 'con', 'Com1', 'LPT9', 'nul', 'CLOCK$'):
            self.assertIn('Gerätename', self.grund(Namensregeln.geraet(name)), name)

    def test_geraet_auch_mit_endung(self):
        # `COM1.txt` öffnet unter Windows die serielle Schnittstelle.
        self.assertIsNotNone(Namensregeln.geraet('COM1.txt'))
        self.assertIsNotNone(Namensregeln.geraet('aux.bvh.json'))

    def test_geraet_lehnt_gewoehnliche_namen_nicht_ab(self):
        for name in ('command', 'console', 'nullwert', 'COM10', 'LPT0', 'figur'):
            self.assertIsNone(Namensregeln.geraet(name), name)

    def test_geraet_nennt_die_rolle(self):
        self.assertIn('dateiname', self.grund(Namensregeln.geraet('PRN', 'Dateiname')))
        self.assertIn('pfadteil', self.grund(Namensregeln.geraet('PRN')))

    def test_die_geraeteliste_ist_vollstaendig(self):
        self.assertEqual(len(GERAETE), 5 + 9 + 9)

    # -- Verbotene Zeichen ---------------------------------------------------

    def test_zeichen_lehnt_jedes_verbotene_ab(self):
        for zeichen in '<>:"|?*':
            self.assertIsNotNone(Namensregeln.zeichen('a%sb' % zeichen), zeichen)
        self.assertIsNotNone(Namensregeln.zeichen('a\tb'))
        self.assertIsNotNone(Namensregeln.zeichen('a\x00b'))

    def test_der_doppelpunkt_ist_der_gefaehrliche(self):
        # `video:1.mp4` ist unter NTFS der Datenstrom `1.mp4` der Datei `video`.
        self.assertIsNotNone(Namensregeln.zeichen('video:1.mp4'))

    def test_zeichen_laesst_umlaute_und_leerzeichen_durch(self):
        self.assertIsNone(Namensregeln.zeichen('Körper Größe 1.json'))
        self.assertEqual(len(VERBOTEN), 7 + 32)

    # -- Punkt und Leerzeichen am Ende ---------------------------------------

    def test_endet_sauber(self):
        self.assertIsNotNone(Namensregeln.endet_sauber('name.'))
        self.assertIsNotNone(Namensregeln.endet_sauber('name '))
        self.assertIsNotNone(Namensregeln.endet_sauber('name. .'))
        self.assertIsNone(Namensregeln.endet_sauber('name.json'))
        self.assertIsNone(Namensregeln.endet_sauber(' name'))

    # -- Die zwei Sammelprüfungen --------------------------------------------

    def test_teil_nennt_den_ersten_grund(self):
        self.assertIn('Zeichen', self.grund(Namensregeln.teil('a<b')))
        self.assertIn('Gerätename', self.grund(Namensregeln.teil('COM1')))
        self.assertIn('Punkt', self.grund(Namensregeln.teil('ordner.')))
        self.assertIsNone(Namensregeln.teil('Ordner_1'))

    def test_datei_prueft_alle_drei_regeln(self):
        self.assertIn('Dateinamen', self.grund(Namensregeln.datei('a|b.txt')))
        self.assertIn('dateiname', self.grund(Namensregeln.datei('NUL.txt')))
        self.assertIn('Dateiname', self.grund(Namensregeln.datei('a.txt ')))
        self.assertIsNone(Namensregeln.datei('walk_01.bvh'))

    def test_datei_lehnt_fuehrenden_bindestrich_ab(self):
        # `-i.mp4` läse ffmpeg als OPTION, nicht als Datei.
        self.assertIn('Bindestrich', self.grund(Namensregeln.datei('-i.mp4')))
        # Als PFADteil ist der Bindestrich erlaubt — dort steht er nie allein
        # auf einer Kommandozeile.
        self.assertIsNone(Namensregeln.teil('-ordner'))

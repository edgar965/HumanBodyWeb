# -*- coding: utf-8 -*-
u"""Grundfall der Effekte-Seitenprüfungen: Ablage, Modelle, Client, Start.

Drei Prüfklassen (`test_effekte`, `test_effekte_figur`,
`test_einstellungen_effekte`) bauten dieselbe Umgebung: eine Prüfablage je
Klasse, einen Modellordner mit JSON-Vorlagen, `HUMANBODY_MODELS_DIR`
dorthin umgebogen, `Client(HTTP_HOST='127.0.0.1')`, der Start über
`Effektstart` und die Schleife über abgewiesene Nutzlasten (Befund
`doppelcode`, 17.09.2026). Hier einmal; die Klassen liefern ihre Dateien
über `dateien()` und ihre Nutzlast über `nutzlast()`.
"""
import json
import os

from django.test import Client, TestCase, override_settings

from core.tests.unit._effektstart import Effektstart
from core.tests.unit._pruefablage import Pruefablage


class Effektseite(TestCase):

    #: Präfix des Prüfordners.
    PRAEFIX = 'effekte_'
    #: {Modellname: Vorlage} — als `<name>.json` in `models/`; None = kein Modellordner.
    MODELLE: 'dict[str, dict] | None' = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ablage = Pruefablage.ordner(cls.PRAEFIX)
        cls.ordner = cls._ablage.__enter__()
        cls.modelle = os.path.join(cls.ordner, 'models')
        if cls.MODELLE is not None:
            os.makedirs(cls.modelle)
            for name, vorlage in cls.MODELLE.items():
                cls.schreiben(os.path.join('models', name + '.json'),
                              json.dumps(vorlage))
        cls.dateien()

    @classmethod
    def tearDownClass(cls):
        cls._ablage.__exit__(None, None, None)
        super().tearDownClass()

    @classmethod
    def dateien(cls):
        u"""Die Prüfdateien der Klasse — zum Überschreiben."""

    @classmethod
    def schreiben(cls, name, text):
        u"""Datei `name` (relativ zur Ablage) mit `text`; gibt den Pfad zurück."""
        pfad = os.path.join(cls.ordner, name)
        with open(pfad, 'w', encoding='utf-8') as datei:
            datei.write(text)
        return pfad

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        if self.MODELLE is not None:
            self.enterContext(override_settings(HUMANBODY_MODELS_DIR=self.modelle))

    def nutzlast(self, **extra):
        u"""Die gültige Start-Nutzlast der Klasse, `extra` überschreibt Felder."""
        raise NotImplementedError

    def starten(self, **extra):
        return Effektstart.senden(self.client, self.nutzlast(**extra))

    def abgewiesen(self, faelle):
        u"""Jeder Fall `(extra, erwarteter Fehlertext)` bekommt 400, nichts startet."""
        for extra, erwartet in faelle:
            with self.subTest(**extra):
                antwort, start = self.starten(**extra)
                self.assertEqual(antwort.status_code, 400)
                self.assertIn(erwartet, antwort.json()['error'])
                start.assert_not_called()

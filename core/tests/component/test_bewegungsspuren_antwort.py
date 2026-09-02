# -*- coding: utf-8 -*-
"""Die Retarget-Endpunkte müssen JSON liefern, keinen Datensatz.

WARUM ES DIESEN TEST GIBT
=========================
Seit dem 01.09.2026 geben `retarget_bvh_to_rigify`, `merge_retargeted`
und die Ablage `Retargetdaten.holen()` ein `Bewegungsspuren`-Objekt
zurück statt eines Wörterbuchs — sechs Felder, die vorher an fünf
Stellen von Hand zusammengesetzt wurden.

`JsonResponse` nimmt kein beliebiges Objekt: Wer `als_dict()` an einer
der vier Antwortstellen vergisst, bekommt zur Laufzeit
`TypeError: Object of type Bewegungsspuren is not JSON serializable` —
eine 500 im Betrieb, die kein Import- und kein Namenstest findet, weil
sie erst beim Aufruf entsteht. `test_endpunkte` deckt sie nicht ab: Die
Retarget-Endpunkte stehen dort in der Liste der Wege, die nur auf Route
und Zugriffsschutz geprüft und NICHT ausgelöst werden.

WAS GEPRÜFT WIRD
================
Die sechs Felder der Schnittstelle stehen in der Antwort, und die
Antwort ist wirklich JSON. Gerechnet wird auf einer echten BVH-Datei
aus der Bibliothek — ohne sie wird geprüft, dass der
Endpunkt mit 404 antwortet — übersprungen wird nichts.
"""
import json
import os

from django.test import TestCase
from django.urls import reverse

from core.dienste.bvhverzeichnis import Bvhverzeichnis
from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren


#: Eine kurze Aufnahme aus der Bibliothek. Der Weg über die
#: Kategorie/Name-Adresse ist genau der, den die Weboberfläche geht.
KATEGORIE = 'Aist'
NAME = '01001_ArmeSeitlich'


class BewegungsspurenAntwortTest(TestCase):
    """Der Bibliotheks-Retarget liefert die sechs Felder als JSON.

    OHNE DIE DATEI WIRD NICHT ÜBERSPRUNGEN: „nichts zu prüfen" ist ein
    ERGEBNIS. Ein `skipTest` meldet grün und fällt nie auf — auch dann
    nicht, wenn der Pfad ins Leere zeigt. Fehlt die Aufnahme, wird
    stattdessen geprüft, dass der Endpunkt sauber mit 404 antwortet
    statt mit einer 500.
    """

    @staticmethod
    def bvh_datei():
        """Der Pfad aus `Bvhverzeichnis`, nie ein fester Laufwerksbuchstabe.

        Hier stand `os.path.join('A:', os.sep, '3DTools', …)`. Ein
        fester Pfad wirft nichts: Die Datei ist dann einfach „nicht da",
        der Fall übersprang sich, und niemand merkte es
        (`projektpfade.md`).
        """
        return os.path.join(Bvhverzeichnis().wurzel(), KATEGORIE,
                            NAME + '.bvh')

    def test_bibliotheks_bvh_antwortet_mit_allen_feldern(self):
        adresse = reverse('retarget_bvh', args=[KATEGORIE, NAME])
        if not os.path.isfile(self.bvh_datei()):
            antwort = self.client.get(adresse)
            self.assertEqual(antwort.status_code, 404,
                             'Ohne Datei muss der Endpunkt 404 melden, '
                             'nicht %d' % antwort.status_code)
            return
        antwort = self.client.get(adresse)
        self.assertEqual(antwort.status_code, 200,
                         'Retarget-Endpunkt antwortet nicht: %s'
                         % antwort.content[:200])
        daten = json.loads(antwort.content)
        self.assertEqual(sorted(daten), sorted(Bewegungsspuren.FELDER),
                         'Die Felder der Schnittstelle haben sich geändert')

    def test_antwort_traegt_wirklich_bewegung(self):
        """Eine leere 200 wäre schlimmer als ein Fehler: Der Spieler
        zeigt dann eine Figur, die stillsteht, ohne dass jemand etwas
        merkt."""
        adresse = reverse('retarget_bvh', args=[KATEGORIE, NAME])
        daten = json.loads(self.client.get(adresse).content)
        self.assertGreater(daten['frame_count'], 0, 'keine Bilder')
        self.assertGreater(len(daten['tracks']), 0, 'keine Knochenspuren')
        self.assertEqual(len(daten['times']), daten['frame_count'],
                         'zu jedem Bild gehört ein Zeitpunkt')

    def test_datensatz_und_json_tragen_dasselbe(self):
        """`als_dict` ist die einzige Stelle, an der die Feldnamen der
        Schnittstelle stehen — hier wird sie gegen die echte Antwort
        gehalten."""
        spuren = Bewegungsspuren(duration=2.0, times=[0.0, 1.0, 2.0],
                                 tracks={'DEF-spine': [0, 0, 0, 1] * 3},
                                 frame_count=3, mapped_bones=['DEF-spine'],
                                 position_track=None)
        als_json = json.loads(json.dumps(spuren.als_dict()))
        self.assertEqual(als_json, spuren.als_dict())
        self.assertEqual(Bewegungsspuren.aus_dict(als_json).als_dict(),
                         spuren.als_dict(), 'JSON-Umlauf verliert Felder')

    def test_leerer_datensatz_traegt_alle_felder(self):
        """Der leere Fall (BVH ohne Bilder) muss dieselbe Form haben —
        die Leser prüfen `frame_count == 0`, nicht das Fehlen von
        Feldern."""
        self.assertEqual(sorted(Bewegungsspuren.leer().als_dict()),
                         sorted(Bewegungsspuren.FELDER))

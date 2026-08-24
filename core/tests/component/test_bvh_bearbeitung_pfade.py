# -*- coding: utf-8 -*-
"""Wächter: Die BVH-Bearbeitung darf nur in der Bibliothek schreiben.

WARUM (Review 13.08.2026)
-------------------------
`smooth_bvh` und `save_bvh_effects` bauten ihren Pfad so:

    bvh_root = Path(settings.HUMANBODY_BVH_DIR).resolve().parent
    bvh_path = bvh_root / category / f'{name}.bvh'      # ungeprüft aus dem Request

und schrieben ihn am Ende mit `open(..., 'w')` neu. Nachgerechnet — beide Wege
landen in den Produktivdaten:

    category='../../..'  name='evil'              ->  HumanBody/evil.bvh
    category='Aist'      name='../../../../evil'  ->  HumanBody/evil.bvh

Begrenzt war der Schaden nur dadurch, dass `is_file()` davor stand: Es konnte
also keine neue Datei angelegt, aber JEDE bestehende `.bvh`-Datei auf dem
Rechner überschrieben werden — auch die in `HumanBody/data/`, die laut
Projektregel unantastbar sind.

Am 12.08.2026 wurden vier Datei-Endpunkte auf SafePath umgestellt; diese zwei
wurden dabei übersehen. Genau dasselbe Muster wie damals — deshalb steht der
Fall jetzt als Test da und nicht als Notiz.
"""
import json

from django.test import TestCase
from django.urls import reverse


class BvhBearbeitungPfadeTest(TestCase):
    """Prüft die Absage, nicht die Glättung — die braucht eine echte Datei."""

    FIESE_EINGABEN = [
        {'category': '../../..', 'name': 'evil'},
        {'category': 'Aist', 'name': '../../../../evil'},
        {'category': '..', 'name': '..\\..\\evil'},
        {'category': 'C:/Windows/Temp', 'name': 'evil'},
    ]

    def _post(self, name, nutzlast):
        return self.client.post(reverse(name), data=json.dumps(nutzlast),
                                content_type='application/json')

    def test_smooth_bvh_lehnt_pfade_ausserhalb_ab(self):
        for daten in self.FIESE_EINGABEN:
            with self.subTest(**daten):
                a = self._post('smooth_bvh', {**daten, 'sigma': 2.0})
                self.assertEqual(a.status_code, 403,
                                 'Pfad %r kam durch (%s)' % (daten, a.status_code))

    def test_save_bvh_effects_lehnt_pfade_ausserhalb_ab(self):
        for daten in self.FIESE_EINGABEN:
            with self.subTest(**daten):
                a = self._post('save_bvh_effects', {**daten, 'effects': {}})
                self.assertEqual(a.status_code, 403,
                                 'Pfad %r kam durch (%s)' % (daten, a.status_code))

    def test_gueltige_kategorie_kommt_bis_zur_datei(self):
        """Gegenprobe: Der Schutz darf die Bibliothek nicht aussperren.

        404 heisst „Pfad war in Ordnung, die Datei gibt es nur nicht" — genau
        das soll bei einem erfundenen Namen herauskommen."""
        for name in ('smooth_bvh', 'save_bvh_effects'):
            with self.subTest(name=name):
                a = self._post(name, {'category': 'Aist', 'name': 'gibtesnicht_xyz',
                                      'sigma': 2.0, 'effects': {}})
                self.assertEqual(a.status_code, 404)

    def test_antwort_nennt_den_pfad_nicht(self):
        """Ein voller Pfad in der Antwort ist eine Auskunft über das Dateisystem."""
        a = self._post('smooth_bvh', {'category': 'Aist', 'name': 'gibtesnicht_xyz'})
        self.assertNotIn('3DTools', a.content.decode('utf-8'))

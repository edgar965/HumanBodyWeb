# -*- coding: utf-8 -*-
"""Wächter: Zustandsändernde Job-Ansichten dürfen nicht per GET laufen.

WARUM (13.08.2026)
------------------
`start_processing` startet eine ML-Pipeline auf der Grafikkarte,
`stop_processing` bricht eine laufende ab. Beide waren ohne Methodenschutz —
also per GET auslösbar. Ein `<img src="…/process/<uuid>/start/">` auf einer
beliebigen Webseite, ein Vorschau-Abruf oder ein Lesezeichen hätte gereicht.

Das ist dieselbe Fehlerklasse wie beim Löschlink der Foto-Jobs, der am selben
Tag umgestellt wurde: Die Ursprungsprüfung in der Middleware fasst GET bewusst
nicht an (sonst würde jedes Bild und jede Verknüpfung geprüft) — Schutz gibt es
dort nur über die Methode.

Die Oberfläche ist nicht betroffen: `job_status.html` schickt für Start ein
POST-Formular, und die Stopp-Knöpfe rufen durchweg `api_stop_processing`.
"""
import uuid

from django.test import TestCase
from django.urls import reverse


class JobMethodenTest(TestCase):
    """Kein DB-Eintrag nötig: Der Methodenschutz greift VOR der Ansicht."""

    def setUp(self):
        self.job_id = uuid.uuid4()

    def test_start_per_get_ist_nicht_moeglich(self):
        a = self.client.get(reverse('start_processing', args=[self.job_id]))
        self.assertEqual(a.status_code, 405,
                         'GET startet eine GPU-Pipeline — das darf nicht gehen')

    def test_stop_per_get_ist_nicht_moeglich(self):
        a = self.client.get(reverse('stop_processing', args=[self.job_id]))
        self.assertEqual(a.status_code, 405)

    def test_post_kommt_bis_zur_ansicht(self):
        """Gegenprobe: Der Schutz darf die Oberfläche nicht aussperren.

        404 heisst hier „Ansicht lief, Auftrag gibt es nicht" — genau richtig,
        denn die Kennung ist frei erfunden."""
        for name in ('start_processing', 'stop_processing'):
            with self.subTest(name=name):
                a = self.client.post(reverse(name, args=[self.job_id]))
                self.assertEqual(a.status_code, 404)

    def test_api_stopp_prueft_die_methode_selbst(self):
        """Die AJAX-Fassung hat ihre eigene Prüfung (405) — die bleibt gültig."""
        a = self.client.get(reverse('api_stop_processing', args=[self.job_id]))
        self.assertEqual(a.status_code, 405)

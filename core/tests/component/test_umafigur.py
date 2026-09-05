# -*- coding: utf-8 -*-
u"""UMA-Figur aus dem Figurkatalog: Liste, Datei, Zettel, Regler.

WARUM (05.09.2026): Die Szene-Seite lädt die UMA-GLB und ihre Form-Regler
über diese Endpunkte. Geprüft auf einem Wegwerf-Katalog und einem Wegwerf-
UMA3-Ordner unter `ProjektTemp/` — nichts hier liest oder schreibt den
echten Katalog oder das UMA-Projekt.

Aufruf:  python manage.py test core.tests.component.test_umafigur
"""
import json
import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse

from core.dienste.umaformregler import Umaformregler
from core.dienste.umaskelett import Umaskelett
from ..unit._umaattrappe import Umaattrappe
from ..unit._umareglerattrappe import Umareglerattrappe


class UmafigurTest(TestCase):

    def setUp(self):
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.katalog = Path(tempfile.mkdtemp(prefix='umafigur_', dir=str(basis)))
        self.addCleanup(shutil.rmtree, self.katalog, True)
        (self.katalog / 'uma').mkdir()
        self.uma3 = Umareglerattrappe.anlegen(self.katalog / 'UMA3')
        umschaltung = override_settings(FIGUREN_KATALOG=self.katalog, UMA_UMA3_ORDNER=self.uma3)
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)
        for dienst in (Umaskelett, Umaformregler):
            dienst.vergessen()
            self.addCleanup(dienst.vergessen)

    def _figur(self, name='probe.glb', rasse='Human Female 3.0'):
        gltf, binaer = Umaattrappe.glb_beispiel()
        (self.katalog / 'uma' / name).write_bytes(Umaattrappe.glb_bytes(gltf, binaer))
        (self.katalog / 'uma' / name[:-4]).with_suffix('.json').write_text(
            json.dumps({'name': name[:-4], 'ruhelage': 'A-Pose',
                        'hinweis': 'Rasse %s, 3 Kleidungsstücke' % rasse}),
            encoding='utf-8')

    # -------------------------------------------------------------- Liste

    def test_liste_mit_geschlecht_aus_dem_zettel(self):
        self._figur('frau.glb', 'Human Female 3.0')
        self._figur('mann.glb', 'Human Male 3.0')
        antwort = self.client.get(reverse('uma_figur_liste'))
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        nach_name = {f['name']: f for f in daten['figuren']}
        self.assertEqual(sorted(nach_name), ['frau.glb', 'mann.glb'])
        self.assertEqual(nach_name['frau.glb']['geschlecht'], 'weiblich')
        self.assertEqual(nach_name['mann.glb']['geschlecht'], 'maennlich')
        self.assertEqual(nach_name['frau.glb']['zettel']['ruhelage'], 'A-Pose')
        self.assertGreater(nach_name['frau.glb']['bytes'], 100)
        self.assertIn(daten['aktuell'], ('frau.glb', 'mann.glb'))    # die jüngste

    def test_leerer_katalog_ist_eine_leere_liste(self):
        daten = self.client.get(reverse('uma_figur_liste')).json()
        self.assertEqual(daten['figuren'], [])
        self.assertIsNone(daten['aktuell'])

    # -------------------------------------------------------------- Datei

    def test_datei_mit_last_modified_und_304(self):
        self._figur()
        antwort = self.client.get(reverse('uma_figur', args=['probe.glb']))
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort['Content-Type'], 'model/gltf-binary')
        self.assertTrue(antwort['Last-Modified'])
        inhalt = b''.join(antwort.streaming_content)
        self.assertEqual(inhalt[:4], b'glTF')
        self.assertEqual(int(antwort['Content-Length']), len(inhalt))
        erneut = self.client.get(reverse('uma_figur', args=['probe.glb']),
                                 HTTP_IF_MODIFIED_SINCE=antwort['Last-Modified'])
        self.assertEqual(erneut.status_code, 304)

    def test_falscher_name_400_fehlende_datei_404(self):
        self.assertEqual(self.client.get('/api/character/uma-figur/..%2Fx.glb/').status_code,
                         404)   # Django löst `..` nicht auf eine Route auf
        self.assertEqual(self.client.get(reverse('uma_figur', args=['x.txt'])).status_code, 400)
        self.assertEqual(self.client.get(reverse('uma_figur', args=['nix.glb'])).status_code, 404)

    def test_zettel_kommt_und_fehlt_nach_dem_loeschen_mit_404(self):
        self._figur()
        antwort = self.client.get(reverse('uma_figur_zettel', args=['probe.glb']))
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['ruhelage'], 'A-Pose')
        (self.katalog / 'uma' / 'probe.json').unlink()
        antwort = self.client.get(reverse('uma_figur_zettel', args=['probe.glb']))
        self.assertEqual(antwort.status_code, 404)

    # ------------------------------------------------------------- Regler

    def test_regler_zur_figur(self):
        self._figur()
        antwort = self.client.get(reverse('uma_regler'), {'figur': 'probe.glb'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        daten = antwort.json()
        self.assertEqual(daten['geschlecht'], 'weiblich')
        self.assertEqual([g['name'] for g in daten['gruppen']], ['Körper', 'Gesicht', 'Pose'])
        self.assertEqual(daten['anzahl'], 4)
        self.assertEqual(daten['uebergangen'], ['DNAEffect_SharedColor'])

    def test_regler_ohne_angabe_nimmt_die_aktuelle_figur(self):
        self._figur('mann.glb', 'Human Male 3.0')
        daten = self.client.get(reverse('uma_regler')).json()
        self.assertEqual(daten['geschlecht'], 'maennlich')
        self.assertEqual(daten['anzahl'], 2)

    def test_regler_fehler_in_klartext(self):
        antwort = self.client.get(reverse('uma_regler'), {'geschlecht': 'quatsch'})
        self.assertEqual(antwort.status_code, 400)
        self.assertEqual(self.client.get(reverse('uma_regler'), {'figur': 'nix.glb'}).status_code,
                         404)
        with override_settings(UMA_UMA3_ORDNER=self.katalog / 'gibtsnicht'):
            Umaformregler.vergessen()
            antwort = self.client.get(reverse('uma_regler'), {'geschlecht': 'weiblich'})
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('Kein UMA-Projekt', antwort.json()['error'])

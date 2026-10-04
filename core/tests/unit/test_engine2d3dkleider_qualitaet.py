# -*- coding: utf-8 -*-
"""Die Handwertung „Qualität …" der Liste von „2D3D Kleider" (03.10.2026): `Engine2d3dKleiderqualitaet` (Werte), `Engine2d3dKleiderrang` (die Rangliste),
die Zellen der Tabelle und der Endpunkt.

Edgar: „die qualität soll eindeutig sein, also keine zwei Läufe mit gleicher Qualität. Beste Qualität: 1. falls eine Zahl dazwischenkommt, ändere die
Qualitäten anderer Läufe" und „Qualität Textur, Mesh insgesamt, Kleider, Haar, Gesicht, Körper — ALS NEUE SPALTEN".

Die Prüfung der Werte, das Umordnen und die Zelle der Tabelle rechnen ohne Datenbank; der Endpunkt braucht Aufträge (kein Lauf, keine Grafikkarte, kein
Ordner auf der Platte)."""

import json
from types import SimpleNamespace
import uuid

from django.test import Client, SimpleTestCase, TestCase

from core.dienste.engine2d3dkleiderqualitaet import Engine2d3dKleiderqualitaet
from core.dienste.engine2d3dkleiderrang import Engine2d3dKleiderrang
from core.dienste.engine2d3dkleidertabelle import Engine2d3dKleidertabelle
from core.models import Engine2d3dKleiderauftrag


class Engine2d3dKleiderqualitaetWerteTest(SimpleTestCase):
    def test_gueltig_ist_jede_ganze_zahl_ab_1(self):
        for wert in (1, 2, 7, 36, '3', 4.0):
            self.assertEqual(Engine2d3dKleiderqualitaet.normieren(wert), int(float(wert)))

    def test_null_leer_und_nichts_heissen_nicht_bewertet(self):
        for wert in (0, '0', '', None):
            self.assertIsNone(Engine2d3dKleiderqualitaet.normieren(wert))

    def test_alles_andere_wird_abgelehnt_statt_gerundet(self):
        for wert in (-1, 2.5, 'gut', [], True):
            with self.assertRaises(ValueError, msg=repr(wert)):
                Engine2d3dKleiderqualitaet.normieren(wert)

    def test_acht_felder_je_eine_spalte_im_modell(self):
        namen = [s for s, (_spalte, _label, _frage) in Engine2d3dKleiderqualitaet.FELDER.items()]
        self.assertEqual(namen, ['mesh', '3d', 'textur', 'mesh_gesamt', 'kleider', 'haar', 'gesicht', 'koerper'])
        self.assertIsNone(Engine2d3dKleiderqualitaet.spalte('xyz'))
        vorhanden = {f.name for f in Engine2d3dKleiderauftrag._meta.get_fields()}
        for _schluessel, (spalte, _label, _frage) in Engine2d3dKleiderqualitaet.FELDER.items():
            self.assertIn(spalte, vorhanden)  # sonst speicherte der Endpunkt ins Leere


class Engine2d3dKleiderrangUmordnenTest(SimpleTestCase):
    """Die Rangliste als reine Rechnung auf einer Liste: [bester, …, schlechtester]."""

    def test_ein_neuer_rang_schiebt_die_dahinter_nach_hinten(self):
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b', 'c'], 'x', 2), ['a', 'x', 'b', 'c'])
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b', 'c'], 'x', 1), ['x', 'a', 'b', 'c'])

    def test_ein_rang_hinter_dem_ende_wird_der_naechste_freie(self):
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b'], 'x', 9), ['a', 'b', 'x'])
        self.assertEqual(Engine2d3dKleiderrang.umordnen([], 'x', 5), ['x'])

    def test_ein_bewerteter_lauf_rueckt_an_seine_neue_stelle_und_die_dazwischen_auf(self):
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b', 'c', 'd'], 'a', 3), ['b', 'c', 'a', 'd'])
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b', 'c', 'd'], 'd', 1), ['d', 'a', 'b', 'c'])
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b', 'c'], 'b', 2), ['a', 'b', 'c'])

    def test_nicht_bewertet_nimmt_den_lauf_heraus_und_schliesst_die_luecke(self):
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b', 'c'], 'a', None), ['b', 'c'])
        self.assertEqual(Engine2d3dKleiderrang.umordnen(['a', 'b'], 'x', None), ['a', 'b'])

    def test_die_eingabe_bleibt_unveraendert(self):
        vorher = ['a', 'b', 'c']
        Engine2d3dKleiderrang.umordnen(vorher, 'b', 1)
        self.assertEqual(vorher, ['a', 'b', 'c'])


class Engine2d3dKleiderqualitaetTabelleTest(SimpleTestCase):
    @staticmethod
    def _auftrag(**spalten):
        werte = {s: None for s, _l, _f in Engine2d3dKleiderqualitaet.FELDER.values()}
        werte.update(spalten)
        return SimpleNamespace(id=uuid.uuid4(), auftraege=[], ergebnis={}, **werte)

    def _tabelle(self, *auftraege):
        tabelle = Engine2d3dKleidertabelle(auftraege)
        return tabelle

    def test_die_zelle_waehlt_den_rang_und_reicht_bis_zum_naechsten_freien(self):
        a, b, c = (self._auftrag(qualitaet_mesh=rang) for rang in (1, 2, None))
        tabelle = self._tabelle(a, b, c)
        html = str(tabelle._qualitaet(b, 'mesh'))
        self.assertIn('data-sort="2"', html)
        self.assertIn('<option value="2" selected>2</option>', html)
        self.assertEqual(html.count(' selected'), 1)
        self.assertIn('data-feld="mesh"', html)
        self.assertNotIn('<option value="3"', html)  # ein bewerteter Lauf hat nur Ränge bis zur Zahl der bewerteten
        frei = str(tabelle._qualitaet(c, 'mesh'))
        self.assertIn('<option value="3">3</option>', frei)  # der unbewertete darf auf den nächsten freien (2 bewertet + 1)
        self.assertNotIn('<option value="4"', frei)

    def test_ohne_rang_sortiert_die_zelle_ans_ende_nicht_vor_rang_1(self):
        a = self._auftrag()
        html = str(self._tabelle(a)._qualitaet(a, 'haar'))
        self.assertIn('data-sort="%d"' % Engine2d3dKleiderqualitaet.SORT_OHNE_RANG, html)
        self.assertIn('<option value="0" selected>–</option>', html)
        self.assertIn('<option value="1">1</option>', html)

    def test_die_acht_spalten_stehen_im_kopf_in_der_reihenfolge_der_felder(self):
        labels = [s['label'] for s in Engine2d3dKleidertabelle.SPALTEN]
        erwartet = [label for _spalte, label, _frage in Engine2d3dKleiderqualitaet.FELDER.values()]
        self.assertEqual(len(erwartet), 8)
        start = labels.index(erwartet[0])
        self.assertEqual(labels[start:start + 8], erwartet)
        for neu in ('Qualität Textur', 'Qualität Mesh insgesamt', 'Qualität Kleider', 'Qualität Haar', 'Qualität Gesicht', 'Qualität Körper'):
            self.assertIn(neu, labels)

    def test_jeder_lauf_hat_acht_auswahlfelder_je_eines_pro_spalte(self):
        a = self._auftrag(qualitaet_koerper=1)
        tabelle = self._tabelle(a)
        felder = {s: str(tabelle._qualitaet(a, s)) for s in Engine2d3dKleiderqualitaet.FELDER}
        self.assertEqual([f.count('<select') for f in felder.values()], [1] * 8)
        for schluessel, html in felder.items():
            self.assertIn('data-feld="%s"' % schluessel, html)
        self.assertIn('<option value="1" selected>1</option>', felder['koerper'])  # nur diese Spalte trägt einen Rang


class Engine2d3dKleiderqualitaetEndpunktTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.jobs = [
            Engine2d3dKleiderauftrag.objects.create(kennung='2026.10.03.12.00.0%d' % i, name='Qualitätsprobe %d' % i) for i in range(1, 5)
        ]

    def adresse(self, job):
        return '/api/engine2d3dkleider/%s/qualitaet/' % job.id

    def senden(self, job, daten):
        return self.client.post(self.adresse(job), data=json.dumps(daten), content_type='application/json')

    def raenge(self, spalte='qualitaet_mesh'):
        return {j.name[-1]: getattr(Engine2d3dKleiderauftrag.objects.get(pk=j.pk), spalte) for j in self.jobs}

    def test_ein_rang_wird_gespeichert_und_die_antwort_traegt_die_ganze_rangliste(self):
        antwort = self.senden(self.jobs[0], {'feld': 'mesh', 'wert': 1})
        self.assertEqual((antwort.status_code, antwort.json()['wert']), (200, 1))
        self.assertEqual(antwort.json()['raenge'], {str(self.jobs[0].id): 1})
        self.assertEqual(self.raenge(), {'1': 1, '2': None, '3': None, '4': None})

    def test_ein_vergebener_rang_schiebt_die_anderen_nach_hinten(self):
        for job, rang in zip(self.jobs[:3], (1, 2, 3)):
            self.senden(job, {'feld': 'mesh', 'wert': rang})
        antwort = self.senden(self.jobs[3], {'feld': 'mesh', 'wert': 2})
        self.assertEqual(antwort.json()['wert'], 2)
        self.assertEqual(self.raenge(), {'1': 1, '2': 3, '3': 4, '4': 2})
        self.assertEqual(sorted(v for v in self.raenge().values() if v), [1, 2, 3, 4])  # eindeutig und lückenlos

    def test_ein_rang_hinter_dem_ende_wird_der_naechste_freie_und_die_antwort_sagt_es(self):
        self.senden(self.jobs[0], {'feld': 'mesh', 'wert': 1})
        antwort = self.senden(self.jobs[1], {'feld': 'mesh', 'wert': 9})
        self.assertEqual(antwort.json()['wert'], 2)
        self.assertEqual(self.raenge()['2'], 2)

    def test_umsetzen_eines_bewerteten_laufs_laesst_keine_luecke(self):
        for job, rang in zip(self.jobs, (1, 2, 3, 4)):
            self.senden(job, {'feld': 'mesh', 'wert': rang})
        self.senden(self.jobs[0], {'feld': 'mesh', 'wert': 3})
        self.assertEqual(self.raenge(), {'1': 3, '2': 1, '3': 2, '4': 4})

    def test_nicht_bewertet_nimmt_den_lauf_heraus_und_die_dahinter_ruecken_auf(self):
        for job, rang in zip(self.jobs[:3], (1, 2, 3)):
            self.senden(job, {'feld': 'mesh', 'wert': rang})
        antwort = self.senden(self.jobs[0], {'feld': 'mesh', 'wert': 0})
        self.assertEqual(antwort.json()['wert'], 0)
        self.assertEqual(self.raenge(), {'1': None, '2': 1, '3': 2, '4': None})

    def test_jede_spalte_ist_eine_eigene_rangliste(self):
        self.senden(self.jobs[0], {'feld': 'haar', 'wert': 1})
        self.senden(self.jobs[1], {'feld': 'haar', 'wert': 1})
        self.senden(self.jobs[1], {'feld': 'koerper', 'wert': 1})
        self.assertEqual(self.raenge('qualitaet_haar'), {'1': 2, '2': 1, '3': None, '4': None})
        self.assertEqual(self.raenge('qualitaet_koerper'), {'1': None, '2': 1, '3': None, '4': None})
        self.assertEqual(self.raenge('qualitaet_mesh'), {'1': None, '2': None, '3': None, '4': None})

    def test_falsche_angaben_geben_400_und_aendern_nichts(self):
        for daten in ({'feld': 'mesh', 'wert': -1}, {'feld': 'mesh', 'wert': 'gut'}, {'feld': 'mesh', 'wert': 2.5}, {'feld': 'xyz', 'wert': 3}, {}):
            self.assertEqual(self.senden(self.jobs[0], daten).status_code, 400, daten)
        self.assertEqual(self.raenge(), {'1': None, '2': None, '3': None, '4': None})

    def test_nur_post_und_nur_die_geaenderten_spalten_werden_geschrieben(self):
        self.assertEqual(self.client.get(self.adresse(self.jobs[0])).status_code, 405)
        vorher = {j.pk: Engine2d3dKleiderauftrag.objects.get(pk=j.pk).updated_at for j in self.jobs}
        self.senden(self.jobs[0], {'feld': 'mesh', 'wert': 1})
        self.senden(self.jobs[1], {'feld': 'mesh', 'wert': 1})  # schiebt den ersten nach hinten — auch er behält sein `updated_at`
        for job in self.jobs:
            self.assertEqual(Engine2d3dKleiderauftrag.objects.get(pk=job.pk).updated_at, vorher[job.pk])

    def test_ein_duplikat_bekommt_keine_wertung(self):
        from core.dienste.auftragsduplikat import Auftragsduplikat

        parameter = Auftragsduplikat('engine2d3dkleider').parameter(self.jobs[0])
        for _schluessel, (spalte, _label, _frage) in Engine2d3dKleiderqualitaet.FELDER.items():
            self.assertNotIn(spalte, parameter)

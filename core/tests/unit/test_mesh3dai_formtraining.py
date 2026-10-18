# -*- coding: utf-8 -*-
"""Reiter „Formtraining“ auf /mesh-3D-AI/ (18.10.2026): Trainingsläufe (`Mesh3daiformtraining`), Formvarianten (`Mesh3daiformvarianten`), die Zeilen „Jetzt“ und die Tabellen.
Ohne Datenbank; Ordner und Dateien nur in einem eigenen Ordner unter ProjektTemp (`Pruefablage`), `OBJECTS_ROOT`/`TOOLS_ROOT` je Fall umgebogen.

Sabotage-Gegenprobe (von Hand): in `Mesh3daiformtraining.lauf` die Frist durch 0 ersetzen → Fall 2 rot; in `je_variante` die Bedingung `endswith('_probe')` streichen → Fall 5 rot;
in `Mesh3daiformvarianten._zaehlen` `erste['wolke']` nie setzen → Fall 6 rot; `Mesh3daiformvarianten.alle` ohne `leeren()` zweimal → Fall 7 zeigt die gemerkte Liste (so gewollt).
"""

import json
import os
import time
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.mesh3daiformtraining import Mesh3daiformtraining
from core.dienste.mesh3daiformtrainingjetzt import Mesh3daiformtrainingjetzt
from core.dienste.mesh3daiformtrainingtabelle import Mesh3daiformtrainingtabelle
from core.dienste.mesh3daiformvarianten import Mesh3daiformvarianten
from core.dienste.mesh3daiformvariantentabelle import Mesh3daiformvariantentabelle

from ._pruefablage import Pruefablage


def _schreiben(datei, inhalt):
    datei.parent.mkdir(parents=True, exist_ok=True)
    datei.write_text(inhalt if isinstance(inhalt, str) else json.dumps(inhalt, ensure_ascii=False), encoding='utf-8')
    return datei


class _Ablage:
    """Eine Wurzel mit `3DObjects/mesh3dai/_vorstufe/laeufe` und `ProjektTemp/…/gpu.lock` wie auf der Platte."""

    def __init__(self, wurzel):
        self.wurzel = Path(wurzel)
        self.objekte = self.wurzel / '3DObjects'
        self.laeufe = self.objekte / 'mesh3dai' / '_vorstufe' / 'laeufe'

    def einstellungen(self):
        return override_settings(OBJECTS_ROOT=self.objekte, TOOLS_ROOT=self.wurzel)

    def fertig(self, name, verlauf, formen=None, **mehr):
        _schreiben(self.laeufe / name / 'lauf.log', 'Netz: 1 Parameter, 2 Epochen\nfertig\n')
        _schreiben(self.laeufe / name / 'lauf_ergebnis.json', {'epochen': len(verlauf), 'dauer_s': 120, 'training_daten': ['Ursula1', 'Damira0'], 'verlauf': verlauf, **mehr})
        if formen is not None:
            _schreiben(self.laeufe / name / 'formen_ergebnis.json', formen)

    def laufend(self, name, alter_s=0.0):
        log = _schreiben(self.laeufe / name / 'lauf.log',
                         "Netz: 3 Parameter, 120 Epochen, 14 Schritte; Figuren 2 (Formvarianten 5), Training 62, Prüfung 15; Regler 1323 (Formmaß 2)\n"
                         "Epoche   1  {'epoche': 1, 'pruefung_gelenke_mm': 400.0}  (6 s)\n"
                         "Epoche  20  {'epoche': 20, 'pruefung_gelenke_mm': 33.5}  (300 s)\n")
        if alter_s:
            zeit = time.time() - alter_s
            os.utime(log, (zeit, zeit))


class LaeufeTest(SimpleTestCase):
    def test_1_fertiger_formlauf(self):
        with Pruefablage.ordner('formtraining_') as o:
            a = _Ablage(o)
            a.fertig('2026.10.17.15.43_vorstufe_form78_v3', [{'epoche': 1}, {'epoche': 2, 'pruefung_mm': 11.2}], formkopf=1318, formvarianten=78,
                     proben_alle={'training': 1004, 'pruefung': 192},
                     formen={'zusammen': {Mesh3daiformtraining.PRUEFFORMEN: {'form_mm': 28.4, 'kopf_form_mm': 6.1}}, 'varianten': {}})
            with a.einstellungen():
                (lauf,) = Mesh3daiformtraining.laeufe()
        self.assertEqual((lauf['zustand'], lauf['art'], lauf['kurz'], lauf['epoche']), ('fertig', 'Formkopf', 'vorstufe_form78_v3', 2))
        self.assertEqual((lauf['rig_mm'], lauf['form_mm'], lauf['kopf_mm'], lauf['formvarianten']), (11.2, 28.4, 6.1, 78))
        self.assertEqual(lauf['proben'], {'training': 1004, 'pruefung': 192})
        self.assertIsNotNone(lauf['ende'])

    def test_2_laufender_lauf_aus_dem_log(self):
        with Pruefablage.ordner('formtraining_') as o:
            a = _Ablage(o)
            a.laufend('2026.10.18.22.00_vorstufe_form2')
            with a.einstellungen():
                (lauf,) = Mesh3daiformtraining.laeufe()
        self.assertEqual((lauf['zustand'], lauf['art'], lauf['epoche'], lauf['epochen']), ('läuft', 'Formkopf', 20, 120))
        self.assertEqual((lauf['rig_mm'], lauf['formvarianten'], lauf['dauer_s']), (33.5, 5, 300.0))
        self.assertEqual(lauf['proben'], {'training': 62, 'pruefung': 15})
        self.assertIsNone(lauf['ende'])

    def test_3_stiller_lauf_steht(self):
        with Pruefablage.ordner('formtraining_') as o:
            a = _Ablage(o)
            a.laufend('2026.10.18.10.00_vorstufe_form2', alter_s=3 * 3600)
            with a.einstellungen():
                (lauf,) = Mesh3daiformtraining.laeufe()
        self.assertEqual(lauf['zustand'], 'steht')
        self.assertIn('steht · keine Zeile seit 3 h', Mesh3daiformtrainingtabelle.status(lauf))

    def test_4_probelauf_und_reihenfolge(self):
        with Pruefablage.ordner('formtraining_') as o:
            a = _Ablage(o)
            a.fertig('2026.10.17.01.01_vorstufe_apose_ab_alle4', [{'epoche': 1, 'pruefung_mm': 6.3}])
            a.fertig('2026.10.18.19.00_vorstufe_form2_probe', [{'epoche': 1}], formkopf=1323)
            with a.einstellungen():
                laeufe = Mesh3daiformtraining.laeufe()
        self.assertEqual([lauf['kurz'] for lauf in laeufe], ['vorstufe_form2_probe', 'vorstufe_apose_ab_alle4'])
        self.assertEqual([lauf['probe'] for lauf in laeufe], [True, False])
        self.assertEqual(laeufe[1]['art'], 'Vorstufe')

    def test_5_je_variante_der_juengste_fertige_ohne_probelauf(self):
        with Pruefablage.ordner('formtraining_') as o:
            a = _Ablage(o)
            alt = {'varianten': {'Form001': {'gruppe': 'training', 'form': {'training': {'form_mm': 31.1}}}}}
            neu = {'varianten': {'Form001': {'gruppe': 'training', 'form': {'training': {'form_mm': 12.0}}, 'kopf': {'kopf_form_mm': 5.5}}}}
            probe = {'varianten': {'Form001': {'gruppe': 'training', 'form': {'training': {'form_mm': 99.0}}}}}
            a.fertig('2026.10.17.15.43_vorstufe_form78_v3', [{'epoche': 1}], formen=alt)
            a.fertig('2026.10.18.23.00_vorstufe_form2', [{'epoche': 1}], formen=neu)
            a.fertig('2026.10.19.00.00_vorstufe_form2_probe', [{'epoche': 1}], formen=probe)
            zeit = time.time() - 600
            os.utime(a.laeufe / '2026.10.17.15.43_vorstufe_form78_v3' / 'lauf_ergebnis.json', (zeit, zeit))
            with a.einstellungen():
                v = Mesh3daiformtraining.je_variante()['Form001']
        self.assertEqual((v['lauf'], v['form_mm'], v['kopf_mm'], v['gruppe']), ('2026.10.18.23.00_vorstufe_form2', 12.0, 5.5, 'training'))


class FormvariantenTest(SimpleTestCase):
    def setUp(self):
        Mesh3daiformvarianten.leeren()

    def tearDown(self):
        Mesh3daiformvarianten.leeren()

    def _variante(self, a, name, dateien, kind=False):
        ordner = a.objekte / 'mesh3dai' / name
        regler = {'g1:Kids4': 0.9} if kind else {'body_bs_MassAnkles': 0.1}
        _schreiben(ordner / 'modell.json', {'name': name, 'grundlage': 'Mann1', 'geschlecht': 'maennlich', 'gruppe': 'pruefung', 'figur': {'regler': regler}})
        _schreiben(ordner / 'proben.json', [{'nr': i + 1} for i in range(len(dateien))])
        for i, namen in enumerate(dateien):
            (ordner / 'proben' / ('%04d' % (i + 1))).mkdir(parents=True)
            for n in namen:
                _schreiben(ordner / 'proben' / ('%04d' % (i + 1)) / n, '')
        return ordner

    def test_6_zaehlen_und_zustand(self):
        with Pruefablage.ordner('formvarianten_') as o:
            a = _Ablage(o)
            self._variante(a, 'Form001', [['mia_v1_0.npz', 'apose_v9_0.npz', 'eingabe.npz'], ['mia_v2_0.npz'], ['eingabe.npz']], kind=True)
            self._variante(a, 'Form002', [['mia_v1_0.npz', 'apose_v9_0.npz']])
            (a.objekte / 'mesh3dai' / 'Ursula1').mkdir(parents=True)         # kein FormNNN: kommt nicht in die Liste
            with a.einstellungen():
                jetzt = Mesh3daiformvarianten.alle()
                Mesh3daiformvarianten.leeren()
                spaeter = Mesh3daiformvarianten.alle(time.time() + 7200)
        self.assertEqual([v['name'] for v in jetzt], ['Form001', 'Form002'])
        f1 = jetzt[0]
        self.assertEqual((f1['geplant'], f1['mia'], f1['wolken'], f1['kind'], f1['zustand']), (3, 2, 1, True, 'wird gerechnet'))
        self.assertEqual(jetzt[1]['zustand'], 'fertig')
        self.assertEqual([v['zustand'] for v in spaeter], ['unvollständig', 'fertig'])
        self.assertEqual(Mesh3daiformvarianten.summe(spaeter), {'figuren': 2, 'fertig': 1, 'aktiv': 0, 'geplant': 4, 'mia': 3, 'wolken': 2})

    def test_7_tabelle_der_formvarianten(self):
        with Pruefablage.ordner('formvarianten_') as o:
            a = _Ablage(o)
            self._variante(a, 'Form161', [['mia_v1_0.npz']], kind=True)
            with a.einstellungen():
                tabelle = Mesh3daiformvariantentabelle().tabelle(Mesh3daiformvarianten.alle(time.time() + 7200))
        (zeile,) = tabelle['zeilen']
        self.assertIn('männlich · Kind', zeile['html'])
        self.assertIn('Prüfform', zeile['html'])
        self.assertIn('MIA fertig, Wolken fehlen', zeile['html'])
        self.assertEqual(len(tabelle['spalten']), zeile['html'].count('<td'))
        self.assertNotRegex(zeile['html'], r'data-sort="-?\d+\.\d', 'die djangoBase-Sortierung liest einen Punkt deutsch — Schlüssel als ganze Zahl')


class JetztUndTabelleTest(SimpleTestCase):
    def test_8_gpu_sperre_und_laufender_lauf(self):
        with Pruefablage.ordner('formtraining_') as o:
            a = _Ablage(o)
            a.laufend('2026.10.18.22.00_vorstufe_form2')
            with a.einstellungen():
                laeufe = Mesh3daiformtraining.laeufe()
                frei = Mesh3daiformtraining.gpu()
                _schreiben(a.wurzel.joinpath(*Mesh3daiformtraining.SPERRE), {'name': 'mia_daten', 'seit': time.time() - 120})
                gehalten = Mesh3daiformtraining.gpu()
        self.assertIsNone(frei)
        self.assertEqual(gehalten['name'], 'mia_daten')
        summe = {'figuren': 0, 'fertig': 0, 'aktiv': 0, 'geplant': 0, 'mia': 0, 'wolken': 0}
        zeilen = Mesh3daiformtrainingjetzt.zeilen(laeufe, summe, gehalten)
        self.assertIn('„mia_daten“', zeilen[0])
        self.assertIn('Training läuft: vorstufe_form2 (Formkopf) — Epoche 20 von 120', zeilen[1])
        self.assertEqual(Mesh3daiformtrainingjetzt.zeilen([], summe, None), ['GPU-Sperre: frei.', 'Kein Trainingslauf läuft.'])
        (zeile,) = Mesh3daiformtrainingtabelle().tabelle(laeufe)['zeilen']
        self.assertIn('mesh3dai-laeuft', zeile['klasse'])
        self.assertIn('läuft · Epoche 20 von 120', zeile['html'])
        self.assertIn('data-sort="335"', zeile['html'])        # Gelenke Prüfung 33,5 mm → 335 (mm × 10)
        self.assertEqual(len(Mesh3daiformtrainingtabelle.SPALTEN), zeile['html'].count('<td'))

# -*- coding: utf-8 -*-
"""Seite je Trainingslauf /mesh-3D-AI/formtraining/<lauf>/ und Reiter „Lauf Aktuell“ (18.10.2026): `Mesh3daiformlauf`, `…gruppen`, `…figuren`, `…kurve`, `Mesh3daigpuprozesse`,
`Mesh3dailaufprozesse` (nur die reinen Rechnungen, keine Prozessliste), `Mesh3dailaufaktuell` (Fortschritt). Ohne Datenbank; Läufe nur in einem eigenen Ordner (`Pruefablage`).

Sabotage-Gegenprobe (von Hand): in `Mesh3daiformlauf.finden` die Namensprüfung streichen → Fall 1 rot; in `vorgaenger` die Bedingung `andere['probe']` streichen → Fall 2 rot;
`Mesh3daiformlaufnamen.fehler` immer True → Fall 3 rot (Bezugsgröße gefärbt); in `vergleich` den Rückfall auf `_je_figur` streichen → Fall 4 rot; in `Mesh3daigpuprozesse.auswerten`
`max` durch `sum` ersetzen → Fall 9 rot; in `Mesh3dailaufaktuell._daten` `>= job['start']` streichen → Fall 12 rot (Restzeit aus allen Proben).
"""

import json
import re
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.mesh3daiformlauf import Mesh3daiformlauf
from core.dienste.mesh3daiformlauffiguren import Mesh3daiformlauffiguren
from core.dienste.mesh3daiformlaufgruppen import Mesh3daiformlaufgruppen
from core.dienste.mesh3daiformlaufkurve import Mesh3daiformlaufkurve
from core.dienste.mesh3daigpuprozesse import Mesh3daigpuprozesse
from core.dienste.mesh3dailaufaktuell import Mesh3dailaufaktuell
from core.dienste.mesh3dailaufprozesse import Mesh3dailaufprozesse

from ._pruefablage import Pruefablage

LOG_LAEUFT = ("Netz: 3 Parameter, 200 Epochen, 14 Schritte; Figuren 2 (Formvarianten 5), Training 62, Prüfung 15; Regler 1323 (Formmaß 2)\n"
              "Epoche   1  {'epoche': 1, 'training_form_mm': 150.0, 'pruefung_gelenke_mm': 400.0}  (6 s)\n"
              "Epoche  20  {'epoche': 20, 'training_form_mm': 40.0, 'pruefung_gelenke_mm': 33.5}  (300 s)\n")


class LaufseiteTest(SimpleTestCase):
    @staticmethod
    def _schreiben(datei, inhalt):
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_text(inhalt if isinstance(inhalt, str) else json.dumps(inhalt, ensure_ascii=False), encoding='utf-8')

    def _ablage(self, o):
        wurzel = Path(o)
        laeufe = wurzel / '3DObjects' / 'mesh3dai' / '_vorstufe' / 'laeufe'
        for name, probe in (('2026.10.17.15.43_vorstufe_form78_v3', False), ('2026.10.18.19.00_vorstufe_form2_probe', True)):
            self._schreiben(laeufe / name / 'lauf.log', 'Netz: 1 Parameter, 2 Epochen; Regler 1318\nfertig\n')
            self._schreiben(laeufe / name / 'lauf_ergebnis.json', {'formkopf': 1318, 'epochen': 2, 'verlauf': [{'epoche': 2, 'pruefung_mm': 11.0}], 'probe': probe})
        self._schreiben(laeufe / '2026.10.18.21.00_vorstufe_form2' / 'lauf.log', LOG_LAEUFT)
        return override_settings(OBJECTS_ROOT=wurzel / '3DObjects', TOOLS_ROOT=wurzel)

    def test_1_finden_nur_direkte_unterordner(self):
        with Pruefablage.ordner('formlauf_') as o, self._ablage(o):
            self.assertIsNotNone(Mesh3daiformlauf.finden('2026.10.17.15.43_vorstufe_form78_v3'))
            for name in ('', '..', '../laeufe', '..\\x', 'a/b', '.versteckt', 'gibtsnicht'):
                self.assertIsNone(Mesh3daiformlauf.finden(name), name)

    def test_2_laufender_lauf_liest_den_verlauf_aus_dem_log_und_vergleicht_ohne_probelauf(self):
        with Pruefablage.ordner('formlauf_') as o, self._ablage(o):
            d = Mesh3daiformlauf.lesen('2026.10.18.21.00_vorstufe_form2')
        self.assertEqual(d['lauf']['zustand'], 'läuft')
        self.assertEqual([v['epoche'] for v in d['verlauf']], [1, 20])
        self.assertEqual(d['verlauf'][1]['s'], 300.0)
        self.assertTrue(d['kopfzeile'].startswith('Netz:'))
        self.assertEqual(d['vorgaenger']['lauf']['name'], '2026.10.17.15.43_vorstufe_form78_v3')   # nicht der jüngere Probelauf

    def test_3_vergleich_faerbt_nur_fehlermasse(self):
        t = Mesh3daiformlaufgruppen.vergleich({'zusammen': {'A': {'form_mm': 10.0, 'grundfigur_mm': 30.0, 'figuren': 4}}},
                                              {'zusammen': {'A': {'form_mm': 12.0, 'grundfigur_mm': 25.0, 'figuren': 3}}})
        zeilen = {z[0]['titel']: z for z in t['zeilen'] if isinstance(z, list)}
        self.assertEqual(zeilen['form_mm'][3]['text'], '-2,0')
        self.assertIn('mesh3dai-besser', zeilen['form_mm'][3]['klasse'])
        self.assertNotIn('mesh3dai-', zeilen['grundfigur_mm'][3]['klasse'])
        self.assertEqual((zeilen['figuren'][3]['text'], zeilen['figuren'][3]['klasse']), ('+1', 'num'))

    def test_4_vorstufe_ohne_zusammen_vergleicht_je_figur(self):
        jetzt = {'je_figur': {'Ursula1': {'training': {'mm': 6.7, 'je_gruppe_mm': {'arm': 8.3}}}}}
        vorher = {'je_figur': {'Ursula1': {'training': {'mm': 6.8, 'je_gruppe_mm': {'arm': 8.2}}}}}
        t = Mesh3daiformlaufgruppen.vergleich(jetzt, vorher)
        self.assertEqual(t['zeilen'][0], {'gruppe': 'Ursula1 · Training'})
        arm = next(z for z in t['zeilen'] if isinstance(z, list) and z[0]['titel'] == 'je_gruppe_mm.arm')
        self.assertEqual((arm[0]['text'], arm[3]['text']), ('Arm (mm)', '+0,1'))
        self.assertIn('mesh3dai-schlechter', arm[3]['klasse'])

    def test_5_unterschiede_nennen_was_die_messung_aendert(self):
        u = Mesh3daiformlaufgruppen.unterschiede({'formregler_datei': 'formregler_v6.json', 'epochen': 2}, {'formregler_datei': 'formregler_v3.json', 'epochen': 2})
        self.assertEqual(u, [('Formregler-Datei', 'formregler_v3.json', 'formregler_v6.json')])

    def test_6_kurve_je_messgroesse_eine_linie(self):
        k = Mesh3daiformlaufkurve.zeichnen([{'epoche': 1, 'training_mm': 300.0, 'pruefung_mm': 400.0, 's': 6.0}, {'epoche': 20, 'training_mm': 20.0, 'pruefung_mm': 30.0, 's': 300.0}])
        self.assertEqual(str(k['svg']).count('<polyline'), 2)                       # `s` (Sekunden) ist keine Messgröße
        self.assertEqual([r['gestrichelt'] for r in k['reihen']], [False, True])
        self.assertIsNone(Mesh3daiformlaufkurve.zeichnen([]))

    def test_7_figuren_mit_echter_nachrechnung_und_ganzzahligen_schluesseln(self):
        e = {'je_figur': {'Form028': {'pruefung': {'proben': 12, 'form_mm': 28.4}}, 'Ursula1': {'pruefung': {'proben': 15, 'form_mm': 22.4}}}}
        echt = {'ergebnis': {'Form028': {'gruppe': 'pruefung', 'vorhersage': {'rms_mm': 81.0}, 'hoehe_soll_m': 2.085, 'hoehe_vorhersage_m': 1.9}}}
        t = Mesh3daiformlauffiguren.figuren(e, echt)
        html = ''.join(str(z['html']) for z in t['zeilen'])
        self.assertIn('Prüfform (nie trainiert)', html)
        self.assertIn('Prüfposen', html)
        self.assertIn('data-sort="810"', html)
        self.assertIn('data-sort="2085"', html)
        self.assertIsNone(re.search(r'data-sort="-?\d+\.\d', html))

    def test_8_kopfmessung_mit_vorgaenger(self):
        kopf = {'mittel_pruefung': {'varianten': 11, 'vorhersage': {'kopf_form': {'rms_mm': 6.0}}, 'mittlere_form': {'kopf_form': {'rms_mm': 5.9}}}}
        vorher = {'mittel_pruefung': {'vorhersage': {'kopf_form': {'rms_mm': 7.5}}}}
        t = Mesh3daiformlauffiguren.kopf(kopf, vorher)
        self.assertEqual(t['kopf'][-1], 'Prüfformen: Vorhersage des vorigen Laufs')
        self.assertEqual([c['text'] for c in t['zeilen'][0]], ['Kopf-Form (Lage abgezogen)', '6,0', '5,9', '7,5'])
        self.assertIsNone(Mesh3daiformlauffiguren.kopf(None))


class LaufaktuellTest(SimpleTestCase):
    def test_9_gpu_je_prozess_wie_der_taskmanager(self):
        last = {'pid_12_luid_0x0_0x1_phys_0_eng_0_engtype_3D': 30.0, 'pid_12_luid_0x0_0x1_phys_0_eng_1_engtype_3D': 15.0,
                'pid_12_luid_0x0_0x1_phys_0_eng_2_engtype_Copy': 5.0, 'pid_13_luid_0x0_0x1_phys_0_eng_0_engtype_3D': 0.0}
        aus = Mesh3daigpuprozesse.auswerten(last, {'pid_12_luid_0x0_0x1_phys_0': 2e9})
        self.assertEqual((aus[12]['prozent'], aus[12]['arten'], aus[12]['mb']), (45.0, {'3D': 45.0, 'Copy': 5.0}, 2000.0))
        self.assertNotIn(13, aus)

    def test_10_befehl_und_gpu_des_baums(self):
        b = Mesh3dailaufprozesse._befehl([r'A:\3DTools\python14\Scripts\python.exe', '-u', 'mesh3dai_vorstufe_mia_daten_lauf.py', '--k', '1', 'Form001'])
        self.assertEqual(b, {'skript': 'mesh3dai_vorstufe_mia_daten_lauf.py', 'argumente': ['--k', '1', 'Form001'], 'umgebung': 'python14'})
        g = Mesh3dailaufprozesse._gpu_baum([1, 2, 3], {1: {'arten': {'3D': 30.0}, 'mb': 100.0}, 2: {'arten': {'3D': 40.0, 'Copy': 5.0}, 'mb': 200.0}})
        self.assertEqual((g['gpu_prozent'], g['gpu_mb'], g['gpu_pids']), (70.0, 300, [1, 2]))

    def test_11_baum_und_vorfahren(self):
        kinder = {1: [2, 3], 2: [4]}
        self.assertEqual(sorted(Mesh3dailaufprozesse._baum(1, kinder)), [1, 2, 3, 4])
        self.assertEqual(Mesh3dailaufprozesse._vorfahren(4, {4: 2, 2: 1, 1: 4}), [2, 1, 4])   # Ring: bricht ab statt endlos

    def test_12_datenlauf_zaehlt_nur_genannte_varianten_und_rechnet_das_tempo_seit_dem_start(self):
        varianten = [{'name': 'Form001', 'geplant': 12, 'mia': 10, 'wolken': 0, 'mia_zeiten': [900.0] * 4 + [1100.0] * 6, 'wolken_zeiten': []},
                     {'name': 'Form002', 'geplant': 12, 'mia': 0, 'wolken': 0, 'mia_zeiten': [], 'wolken_zeiten': []}]
        mia, wolken = Mesh3dailaufaktuell._daten({'argumente': ['--k', '1', 'Form001'], 'start': 1000.0}, varianten, 1000.0 + 3600.0)
        self.assertEqual((mia['fertig'], mia['gesamt'], wolken['fertig']), (10, 12, 0))
        self.assertAlmostEqual(mia['rest_s'], 1200.0)        # 6 neue Proben in 1 h → 2 fehlende in 20 min
        self.assertIsNone(wolken['rest_s'])

    def test_13_training_restzeit_und_ladephase(self):
        (f,) = Mesh3dailaufaktuell._training({'epoche': 20, 'epochen': 200, 'dauer_s': 300.0})
        self.assertEqual((f['text'], f['rest_s']), ('Durchgang 20 von 200', 2700.0))
        (f,) = Mesh3dailaufaktuell._training(None)
        self.assertIsNone(f['gesamt'])
        self.assertIn('lädt die Beispielfiguren', f['text'])

# -*- coding: utf-8 -*-
"""Seite je Formvariante /mesh-3D-AI/formvariante/<figur>/ (18.10.2026 abends): `Mesh3daiformvariante` (Lauf, Proben ↔ Zeilen der Vorhersage, Regler), `Mesh3daiformvariantefigur`
(Reglervektor, Klemmen, Abstand, Pakete — ohne Genesis: `punkte` und `ursprung` als Attrappe mit `autospec`), die Links aus Formvarianten- und Figurtabelle. Ohne Datenbank, Läufe in `Pruefablage`.

Sabotage-Gegenprobe (von Hand): in `Mesh3daiformvariante.finden` die Bedingung `pfad.parent == wurzel` streichen → Fall 1 rot; in `zuordnung` den Vergleich mit `zeilen` streichen → Fall 3 rot
(verschobene Zuordnung); die Vorgabe in `lesen` wieder auf `laeufe[0]` → Fall 4 rot (Probelauf); in `Mesh3daiformvariantefigur.regler` die Schwelle streichen → Fall 6 rot; im Paket `p[ursprung]`
durch `p` ersetzen → Fall 8 rot (Länge); in `koerper` die Indexprüfung streichen → Fall 9 rot.
"""

import json
import struct
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase, override_settings

from core.dienste.mesh3daiformlauffiguren import Mesh3daiformlauffiguren
from core.dienste.mesh3daiformvariante import Mesh3daiformvariante
from core.dienste.mesh3daiformvariantefigur import Mesh3daiformvariantefigur as F
from core.dienste.mesh3daiformvariantentabelle import Mesh3daiformvariantentabelle

from ._pruefablage import Pruefablage

FERTIG = '2026.10.17.15.43_vorstufe_form78_v3'
PROBE = '2026.10.18.19.00_vorstufe_form2_probe'
LISTE = [{'name': 'a', 'min': -1.0, 'max': 1.0, 'anzeige': 'A', 'bereich_titel': 'Kopf'}, {'name': 'b', 'min': 0.0, 'max': 1.0}, {'name': 'c', 'min': -1.0, 'max': 1.0}]


class FormvarianteTest(SimpleTestCase):
    @staticmethod
    def _schreiben(datei, inhalt):
        datei.parent.mkdir(parents=True, exist_ok=True)
        datei.write_text(json.dumps(inhalt, ensure_ascii=False), encoding='utf-8')

    @staticmethod
    def _wolke(datei):
        datei.parent.mkdir(parents=True, exist_ok=True)
        np.savez(datei, punkte=np.zeros((4, 3), np.float32), farbe=np.full((4, 3), 0.5, np.float32))

    def _ablage(self, o):
        """Form001 mit drei Trainingsproben; Lauf FERTIG (apose_v4, eine Wolke) und der jüngere Probelauf PROBE (apose_v9, Wolken 0,1,2, k1 von Probe 2 durchgefallen)."""
        wurzel = Path(o) / '3DObjects' / 'mesh3dai'
        figur = wurzel / 'Form001'
        self._schreiben(figur / 'modell.json', {'name': 'Form001', 'grundlage': 'Ursula1', 'geschlecht': 'weiblich', 'gruppe': 'training'})
        self._schreiben(figur / 'proben.json', [{'nr': n, 'name': 'Pose %d' % n, 'gruppe': 'training'} for n in (1, 2, 3)] + [{'nr': 4, 'name': 'Spagat', 'gruppe': 'spagat'}])
        for n in (1, 2, 3):
            self._wolke(figur / 'proben' / ('%04d' % n) / 'apose_v4_0.npz')
            self._wolke(figur / 'proben' / ('%04d' % n) / 'apose_v9_0.npz')
        self._wolke(figur / 'proben' / '0002' / 'apose_v9_1.npz')
        (wurzel / 'Ursula1').mkdir(parents=True)
        zeilen = np.array([[0.2, 0.5, -0.4], [0.4, 0.5, -0.4], [0.6, 0.5, -0.4]], np.float32)
        for name, eingabe in ((FERTIG, {'eingang': 'apose_v4'}), (PROBE, {'eingang': 'apose_v9', 'wolken': '0,1,2', 'ausgelassen': {'Form001/2/k1': 'MIA-Prüfung nicht bestanden'}})):
            lauf = wurzel / '_vorstufe' / 'laeufe' / name
            self._schreiben(lauf / 'lauf_ergebnis.json', dict(eingabe, epochen=2, formkopf=3, je_figur={'Form001': {'training': {'form_mm': 31.1, 'proben': 3}}}))
            self._schreiben(lauf / 'formregler_liste.json', {'regler': LISTE})
            np.savez(lauf / 'formen_vorhersagen.npz', Form001_training_form=zeilen, Form001_soll_form=np.array([0.5, 0.005, -2.0], np.float32))
        return override_settings(OBJECTS_ROOT=Path(o) / '3DObjects', TOOLS_ROOT=Path(o))

    def test_1_finden_nur_direkte_unterordner(self):
        with Pruefablage.ordner('formvariante_') as o, self._ablage(o):
            self.assertIsNotNone(Mesh3daiformvariante.finden('Form001'))
            for name in ('', '..', '_vorstufe', 'a/b', '..\\x', 'Form001/proben', 'Form999'):
                self.assertIsNone(Mesh3daiformvariante.finden(name), name)

    def test_2_wolken_des_laufs(self):
        self.assertEqual(Mesh3daiformvariante.wolken({}), [0])
        self.assertEqual(Mesh3daiformvariante.wolken({'wolken': '0,1,2'}), [0, 1, 2])
        self.assertEqual(Mesh3daiformvariante.wolken({'wolken': '2,0'}), [0, 2])

    def test_3_zuordnung_nur_bei_passender_zeilenzahl(self):
        with Pruefablage.ordner('formvariante_') as o, self._ablage(o):
            ordner = Mesh3daiformvariante.finden('Form001')
            paare = Mesh3daiformvariante.zuordnung('Form001', ordner, 'training', 3, 'apose_v9', [0, 1, 2], {'Form001/2/k1': 'x'})
            self.assertEqual([(e['nr'], da) for e, da in paare], [(1, [0]), (2, [0]), (3, [0])])
            self.assertIsNone(Mesh3daiformvariante.zuordnung('Form001', ordner, 'training', 4, 'apose_v9', [0], {}))
            # Formtraining 1 vermerkt eine durchgefallene Probe ohne Wolke — dann hat der Lauf nur zwei Zeilen
            paare = Mesh3daiformvariante.zuordnung('Form001', ordner, 'training', 2, 'apose_v4', [0], {'Form001/2': 'x'})
            self.assertEqual([e['nr'] for e, _ in paare], [1, 3])

    def test_4_vorgabe_ist_der_fertige_lauf_ohne_probelauf(self):
        with Pruefablage.ordner('formvariante_') as o, self._ablage(o):
            d = Mesh3daiformvariante.lesen('Form001')
            self.assertEqual(d['lauf']['name'], FERTIG)
            self.assertEqual([x['name'] for x in d['laeufe']], [PROBE, FERTIG])
            self.assertEqual([(p['nr'], p['zeile']) for p in d['proben']], [(1, 0), (2, 1), (3, 2)])
            self.assertEqual(d['grundlage'], 'Ursula1')
            self.assertTrue(any(w['schluessel'] == 'form_mm' and w['fehler'] for w in d['werte']))
            self.assertEqual(Mesh3daiformvariante.lesen('Form001', PROBE)['lauf']['wolken'], [0, 1, 2])
            self.assertEqual(Mesh3daiformvariante.lesen('Form001', 'gibtsnicht')['lauf']['name'], FERTIG)
            self.assertEqual(Mesh3daiformvariante.mit_seite(Path(o) / '3DObjects' / 'mesh3dai' / '_vorstufe' / 'laeufe' / FERTIG), {'Form001'})

    def test_5_regler_nach_abweichung_geklemmt(self):
        with Pruefablage.ordner('formvariante_') as o, self._ablage(o):
            r = Mesh3daiformvariante.lesen('Form001')['regler']
        # Soll a 0,5 · b 0,005 (weg) · c −2 → −1 (geklemmt); Vorhersage im Mittel a 0,4 · b 0,5 · c −0,4
        self.assertEqual((r['gesetzt_soll'], r['gesetzt_vorhersage'], r['gesamt']), (2, 3, 3))
        self.assertEqual([(z['name'], z['soll'], z['vorhersage'], z['delta']) for z in r['zeilen']], [('c', -1.0, -0.4, 0.6), ('b', 0.0, 0.5, 0.5), ('a', 0.5, 0.4, -0.1)])
        self.assertEqual((r['zeilen'][2]['anzeige'], r['zeilen'][2]['bereich']), ('A', 'Kopf'))

    def test_6_reglervektor_und_klemmen(self):
        self.assertEqual(F.regler([0.5, 0.005, -2.0], LISTE), {'a': 0.5, 'c': -1.0})
        z = {'X_soll_form': np.array([1.0, 0, 0]), 'X_training_form': np.array([[0.0, 0, 0], [1.0, 0, 0]]), 'X_pruefung_form': np.array([[2.0, 0, 0]])}
        ns = type('Npz', (), {'files': list(z), '__getitem__': lambda self, k: z[k]})()
        proben = [{'nr': 5, 'gruppe': 'pruefung', 'zeile': 0}, {'nr': 6, 'gruppe': 'training', 'zeile': None}]
        self.assertEqual(F.vektor(ns, 'X', 'ziel', proben).tolist(), [1.0, 0, 0])
        self.assertEqual(F.vektor(ns, 'X', 'mittel', proben).tolist(), [1.0, 0, 0])     # Mittel über BEIDE Gruppen: (0 + 1 + 2) / 3
        self.assertEqual(F.vektor(ns, 'X', '5', proben).tolist(), [2.0, 0, 0])
        self.assertIsNone(F.vektor(ns, 'X', '6', proben))
        self.assertIsNone(F.vektor(ns, 'X', '9', proben))

    def test_7_abstand_in_mm(self):
        a = np.zeros((10, 3))
        b = a + [0.003, 0.0, 0.0]
        self.assertEqual(F.abstand(a, b), {'rms_mm': 3.0, 'median_mm': 3.0, 'p95_mm': 3.0})

    def test_8_paket_traegt_die_browserpunkte(self):
        lagen = {'ziel': np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]), 'mittel': np.array([[0.0, 1.002, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])}

        def punkte(lauf, name, was, liste, proben):
            return lagen[was], 7

        with mock.patch.object(F, 'punkte', autospec=True, side_effect=punkte), mock.patch.object(F, '_ursprung', np.array([0, 1, 1, 2])):
            roh = F.paket(Path('.'), 'X', 'mittel', LISTE, [])
            ziel = F.paket(Path('.'), 'X', 'ziel', LISTE, [])
        n = struct.unpack('<I', roh[:4])[0]
        kopf = json.loads(roh[4:4 + n])
        self.assertEqual((kopf['punkte'], kopf['regler_gesetzt'], kopf['hoehe_m'], kopf['hoehe_ziel_m']), (4, 7, 1.002, 1.0))
        self.assertEqual(kopf['abstand']['median_mm'], 0.0)
        lage = np.frombuffer(roh[4 + n:], '<f4').reshape(-1, 3)
        self.assertEqual(lage.shape, (4, 3))
        self.assertAlmostEqual(float(lage[0, 1]), 1.002, places=5)
        self.assertNotIn('abstand', json.loads(ziel[4:4 + struct.unpack('<I', ziel[:4])[0]]))

    def test_9_koerper_aus_dem_anzeigenetz_der_grundlage(self):
        netz = {'etikett': np.array([0, 0, 2], np.uint8), 'dreiecke': np.array([[0, 1, 2], [1, 2, 3], [4, 5, 6]], np.uint32), 'uv': np.zeros((7, 2), np.float32),
                'material': np.array([1, -1, 0], np.int16), 'materialien': [{'name': 'Haar', 'bild': None}, {'name': 'Body', 'bild': 'm1.jpg', 'farbe': [1, 1, 1]}]}
        with mock.patch('core.dienste.mesh3daiformvariantefigur.Mesh3daiflaechennetz.laden', return_value=netz), mock.patch.object(F, '_ursprung', np.arange(4)), \
                mock.patch.object(F, '_koerper', {}):
            roh = F.koerper('Ursula1')
            netz2 = dict(netz, dreiecke=np.array([[0, 1, 5], [1, 2, 3], [4, 5, 6]], np.uint32))
            with mock.patch('core.dienste.mesh3daiformvariantefigur.Mesh3daiflaechennetz.laden', return_value=netz2):
                self.assertIsNone(F.koerper('Damira0'))      # Index 5 liegt hinter den 4 Körperpunkten
        n = struct.unpack('<I', roh[:4])[0]
        kopf = json.loads(roh[4:4 + n])
        self.assertEqual((kopf['punkte'], kopf['dreiecke']), (4, 2))
        self.assertEqual([m['genutzt'] for m in kopf['materialien']], [False, True])
        self.assertEqual(len(roh), 4 + n + 2 * 12 + 4 * 8 + 4)          # Dreiecke, UV, Material (2 × int16, auf 4 aufgefüllt)

    def test_10_formvariante_oeffnet_ihre_seite(self):
        v = {'name': 'Form001', 'grundlage': 'Ursula1', 'lauf': None, 'geschlecht': 'weiblich', 'kind': False, 'gruppe': 'training', 'geplant': 12, 'mia': 12, 'wolken': 12,
             'daten_zeit': None, 'zustand': 'fertig'}
        t = Mesh3daiformvariantentabelle().tabelle([v])
        self.assertIn('mesh3daitabelle', t['klasse'])
        self.assertIn('href="/mesh-3D-AI/formvariante/Form001/"', str(t['zeilen'][0]['html']))

    def test_11_figurtabelle_der_laufseite_verlinkt_nur_figuren_mit_vorhersage(self):
        e = {'je_figur': {'Form001': {'training': {'form_mm': 1.0}}, 'Ursula1': {'training': {'form_mm': 2.0}}}}
        t = Mesh3daiformlauffiguren.figuren(e, None, FERTIG, {'Form001'})
        html = {z['id']: str(z['html']) for z in t['zeilen']}
        self.assertIn('href="/mesh-3D-AI/formvariante/Form001/?lauf=%s"' % FERTIG, html['Form001|training'])
        self.assertNotIn('href=', html['Ursula1|training'])
        self.assertNotIn('href=', str(Mesh3daiformlauffiguren.figuren(e, None)['zeilen'][0]['html']))

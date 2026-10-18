# -*- coding: utf-8 -*-
u"""Gliederung der Genesis-9-Regler nach Körperteil (18.10.2026) — Kunstdaten, keine Daz-Bibliothek.

WARUM (Edgar, 18.10.2026: „mach die Empfehlung … Ich verstehe nicht die ‚versteckten‘ Regler, die haben doch auch eine Wirkung? dann glieder die ein in
die richtigen Kategorien“; Konzept `Docu/konzepte/2026-10-18_genesis9-regler-vereinfachen-konzept.md`). Vorher 52 Bereiche, 599 Regler nach Herkunft,
738 in „Verborgen (Daz)“, Haltung und Form gemischt.

Zusagen:

1. `G9reglerplatz.gemessen`: Kopfanteil ≥ 50 % → Kopf mit dem stärksten Kopfteil als Gruppe (sonst „Ganzer Kopf“); Größenanteil ≥ 80 % → Ganzer Körper ·
   Größe; sonst die stärkste Region ab 40 %; sonst Ganzer Körper · Körperbau.
2. `G9reglerplatz.platz`: Charakter → Charaktere; Daz-Kopfregler bekommt Daz' Teilregion (Nose → Nase); Daz-Pose eines Körperteils → Haltung; ein
   Daz-Formregler zieht nur um, wenn unter 50 % im eigenen Bereich UND mindestens 50 % woanders; ohne Wirkung mit Treiber → „Wirkt nur mit …“ (eine
   Korrektur → „Korrekturen“); ohne Wirkung und ohne Treiber → Daz-Steuerung; die zwei JCM-Schalter → Ganzer Körper · Schalter; ungemessen → Herkunft.
3. `G9reglerzusammenlegung`: Alias — sichtbar vor verborgen, der Faktor kehrt sich um, wenn der andere Hauptregler wird, Ketten ziehen mit; Paar — nur
   Daz, gleicher Bereich und gleiche Gruppe, Form; „A ↔ B“ mit gemeinsamem Anfang einmal.
4. `G9reglergliederung.bereiche`: Reihenfolge (Charaktere vorn, feste Bereiche unverändert, Daz-Steuerung zuletzt), jeder Regler genau einmal
   (Zeilen + Aliasse + Paar-Hälften = Plan), ohne Tabelle bleiben Familienregler in ihrem Herkunftsbereich, kleine „Wirkt nur mit“-Gruppen werden
   eine Sammelgruppe.
5. Abteilung „Genitalien" (`G9genitalregler`, Edgar 18.10.2026: „mach eine extra Abteilung bei Genesis Morphs für die Genitalien"): steht hinter „Hüfte
   und Po", nimmt Daz' `Hip Genital Bulge`, MakeHumans Genitalvolumen und die Scham-Körperform eines Imports auf — auch aus einem festen Bereich
   („Modell-Eigen"), der sie dann nicht mehr führt —, Gruppen in der Folge Daz, MakeHuman, eigene; ohne einen dieser Regler steht sie leer da.

Sabotage-Gegenprobe (nicht gefahren): in `gemessen` `KOPF_AB` auf 0,9 → Fall 1 rot; in `_daz_form` die Bedingung `eigen < EIGEN_UNTER` streichen →
Fall 2 (Umzug) rot; in `_einhaengen` den Faktor nicht umkehren → Fall 3 rot; in `_zusammenstellen` die festen Bereiche weglassen → Fall 4 rot;
in `_zusammenstellen` die Filterung der festen Bereiche streichen → Fall 5 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
from unittest import mock

from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.genitalregler import G9genitalregler  # noqa: E402
from Genesis9.reglergliederung import G9reglergliederung  # noqa: E402
from Genesis9.reglerplatz import G9reglerplatz  # noqa: E402
from Genesis9.reglerzusammenlegung import G9reglerzusammenlegung  # noqa: E402


class _Ablage:
    def __init__(self, **kanaele):
        self.kanaele = {k: dict({'id': k, 'label': k, 'gruppe': '/Base', 'region': '', 'sichtbar': True}, **v) for k, v in kanaele.items()}


def regler(name, **mehr):
    return dict({'name': name, 'anzeige': name, 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0, 'art': 'form'}, **mehr)


def gemessen(mm=5.0, skal=0.0, **anteile):
    return {'mm': mm, 'ende': 1.0, 'skal': skal, 'anteile': anteile}


class GliederungTest(SimpleTestCase):
    def setUp(self):
        patch = mock.patch.object(G9reglerplatz, 'anhangtreiber', return_value=frozenset())
        patch.start()
        self.addCleanup(patch.stop)

    def test_1_gemessener_ort(self):
        p = G9reglerplatz(_Ablage())
        self.assertEqual(p.gemessen(gemessen(nase=0.5, mund=0.2)), ('kopf', 'Nase'))
        self.assertEqual(p.gemessen(gemessen(nase=0.3, mund=0.25, augen=0.2)), ('kopf', 'Ganzer Kopf'), 'kein Kopfteil trägt die Hälfte')
        self.assertEqual(p.gemessen(gemessen(skal=0.85, beine=0.9)), ('koerper', 'Größe'))
        self.assertEqual(p.gemessen(gemessen(hals=0.45, brust=0.3)), ('hals', ''))
        self.assertEqual(p.gemessen(gemessen(hals=0.3, brust=0.3, arme=0.3)), ('koerper', 'Körperbau'))

    def test_2_platz_je_art(self):
        ablage = _Ablage(nase={'region': 'Nose'}, held={'gruppe': '/People/Held'}, heldkopf={'gruppe': '/People/Held', 'label': 'Held Head'},
                         halsweg={'gruppe': '/Neck'}, korr={'gruppe': '/Hidden/Body/BodyHeavy'}, treiber={'label': 'Body Heavy'},
                         leer={'gruppe': '/Hidden/CTRLMDs'}, body_basejointcorrectives={'gruppe': '/General/Misc'})
        p = G9reglerplatz(ablage)
        self.assertEqual(p.platz(regler('held'), 'figur', gemessen())[:2], ('charaktere', 'Charaktere'))
        self.assertEqual(p.platz(regler('heldkopf', anzeige='Held Head'), 'kopf', gemessen())[:2], ('charaktere', 'Nur Kopf'))
        self.assertEqual(p.platz(regler('nase'), 'kopf', gemessen(nase=0.9))[:2], ('kopf', 'Nase'))
        self.assertEqual(p.platz(regler('arm', art='pose'), 'arme', gemessen(arme=1.0))[:2], ('haltung', 'Arme und Schultern'))
        # Umzug nur bei klarer Messung: 30 % Hals, 60 % Rücken → Rücken; 45 % Hals, 40 % Rücken → bleibt.
        self.assertEqual(p.platz(regler('halsweg'), 'hals', gemessen(hals=0.3, ruecken=0.6))[:2], ('ruecken', ''))
        self.assertEqual(p.platz(regler('halsweg'), 'hals', gemessen(hals=0.45, ruecken=0.4))[:2], ('hals', ''))
        bedingt = dict(gemessen(mm=0.0), bedingt={'treiber': ['treiber'], 'mm': 6.3, 'anteile': {'arme': 1.0}, 'skal': 0.0})
        bereich, gruppe, hinweis = p.platz(regler('korr'), 'verborgen_body', bedingt)
        self.assertEqual((bereich, gruppe), ('arme', G9reglerplatz.G_KORREKTUR))
        self.assertIn('Body Heavy', hinweis)
        self.assertEqual(p.platz(regler('frei'), 'verborgen_x', bedingt)[1], G9reglerplatz.G_NUR % 'Body Heavy')
        self.assertEqual(p.platz(regler('leer'), 'verborgen_ctrlmds', gemessen(mm=0.0))[:2], ('daz_steuerung', 'CTRLMDs'))
        self.assertEqual(p.platz(regler('body_basejointcorrectives'), 'koerper', gemessen(mm=0.0))[:2], ('koerper', G9reglerplatz.G_SCHALTER))
        self.assertEqual(p.platz(regler('hb:x'), 'hb_koerper', None)[:2], ('hb_koerper', ''), 'ungemessen: Herkunftsbereich')

    def test_3_zusammenlegen(self):
        familie = G9reglerplatz.familie
        e = {'a': regler('a', herkunft='verborgen_facs', bereich='mimik', gruppe=''),
             'b': regler('b', herkunft='mimik', bereich='mimik', gruppe=''),
             'c': regler('c', herkunft='verborgen_facs', bereich='mimik', gruppe='')}
        # a(w) = b(w·2): b ist sichtbar und wird Hauptregler mit Alias a × 2; dann c(w) = a(w·0,5) → c = b(w·1).
        G9reglerzusammenlegung({'aliase': [['a', 'b', 2.0, 0.1], ['c', 'a', 0.5, 0.1]]}, familie).anwenden(e)
        self.assertEqual(list(e), ['b'])
        self.assertEqual(e['b']['aliase'], [{'name': 'a', 'faktor': 2.0}, {'name': 'c', 'faktor': 1.0}])
        # Umgekehrt: der verborgene steht vorn in der Liste, der sichtbare wird trotzdem Hauptregler (Faktor kehrt sich um).
        e = {'x': regler('x', herkunft='mimik', bereich='mimik', gruppe=''), 'y': regler('y', herkunft='verborgen_x', bereich='mimik', gruppe='')}
        G9reglerzusammenlegung({'aliase': [['x', 'y', 4.0, 0.1]]}, familie).anwenden(e)
        self.assertEqual(e['x']['aliase'], [{'name': 'y', 'faktor': 0.25}])
        e = {'p': regler('200+ Ears Move Backward', bereich='kopf', gruppe='Ohren'),
             'q': regler('200+ Ears Move Forward', bereich='kopf', gruppe='Ohren'),
             'mh:r': regler('mh:r', anzeige='Rasse A', bereich='koerper', gruppe=''), 'mh:s': regler('mh:s', anzeige='Rasse B', bereich='koerper', gruppe='')}
        e['p']['name'], e['q']['name'] = 'p', 'q'
        G9reglerzusammenlegung({'paare': [['p', 'q', -0.99], ['mh:r', 'mh:s', -1.0]]}, familie).anwenden(e)
        self.assertEqual(sorted(e), ['mh:r', 'mh:s', 'q'], 'nur Daz wird ein Paar')
        self.assertEqual((e['q']['paar'], e['q']['anzeige'], e['q']['min'], e['q']['max']), ('p', u'200+ Ears Move Backward ↔ Forward', -1.0, 1.0))

    def test_4_gliederung_reihenfolge_und_summe(self):
        roh = [{'schluessel': 'figur', 'name': 'Figur', 'regler': [regler('held')]},
               {'schluessel': 'alter', 'name': 'Alter', 'regler': [regler('alter:jahre')]},
               {'schluessel': 'kopf', 'name': 'Kopf', 'regler': [regler('nase'), regler('p', anzeige='Nose In'), regler('q', anzeige='Nose Out')]},
               {'schluessel': 'hb_koerper', 'name': 'HB-Morphs Körper', 'regler': [regler('hb:Waist')]},
               {'schluessel': 'verborgen_x', 'name': 'Verborgen', 'regler': [regler('leer'), regler('k1'), regler('k2')]}]
        ablage = _Ablage(nase={'region': 'Nose'}, p={'region': 'Nose'}, q={'region': 'Nose'}, held={'gruppe': '/People/Held'},
                         leer={'gruppe': '/Hidden/CTRLMDs'}, k1={'gruppe': '/Hidden/Tools'}, k2={'gruppe': '/Hidden/Tools'}, t={'label': 'T'})
        nur = dict(gemessen(mm=0.0), bedingt={'treiber': ['t'], 'mm': 1.0, 'anteile': {'nase': 1.0}, 'skal': 0.0})
        orte = {'regler': {'held': gemessen(), 'nase': gemessen(nase=1.0), 'p': gemessen(nase=1.0), 'q': gemessen(nase=1.0),
                           'hb:Waist': gemessen(taille=0.9), 'leer': gemessen(mm=0.0), 'k1': nur, 'k2': nur},
                'aliase': [], 'paare': [['p', 'q', -0.99]]}
        with mock.patch('Genesis9.reglerorte.G9reglerorte.fehlende_melden'):
            aus = G9reglergliederung.bereiche(roh=roh, ablage=ablage, orte=orte)
        self.assertEqual([b['schluessel'] for b in aus], ['charaktere', 'alter', 'kopf', 'taille', 'genitalien', 'daz_steuerung'])
        kopf = next(b for b in aus if b['schluessel'] == 'kopf')['regler']
        self.assertEqual([(r['name'], r['gruppe']) for r in kopf][:2], [('nase', 'Nase'), ('q', 'Nase')])
        self.assertEqual(kopf[-1]['gruppe'], G9reglerplatz.G_NUR_REST, 'zwei Regler mit demselben Treiber sind keine eigene Gruppe')
        zeilen = sum(len(b['regler']) for b in aus)
        haelften = sum(1 for b in aus for r in b['regler'] if r.get('paar'))
        self.assertEqual(zeilen + haelften, sum(len(b['regler']) for b in roh), 'jeder Regler genau einmal')
        # Ohne Tabelle: der Familienregler bleibt im Herkunftsbereich, Daz an seinem Platz.
        aus = G9reglergliederung.bereiche(roh=roh, ablage=ablage, orte={'regler': {}, 'aliase': [], 'paare': []})
        self.assertIn('hb_koerper', [b['schluessel'] for b in aus])
        self.assertEqual(next(b for b in aus if b['schluessel'] == 'hb_koerper')['name'], 'HB-Morphs Körper')

    def test_5_genitalien_eigene_abteilung(self):
        roh = [{'schluessel': 'huefte', 'name': 'Hüfte', 'regler': [regler('body_bs_HipGenitalBulge'), regler('glute')]},
               {'schluessel': 'mh_koerper', 'name': 'MH', 'regler': [regler('mh:pelvis_bulge-decr_incr')]},
               {'schluessel': 'modell_eigen', 'name': 'Modell-Eigen', 'regler': [regler('eigen:cute_girl_mesh_1_scham'), regler('eigen:x_bauch')]}]
        ablage = _Ablage(body_bs_HipGenitalBulge={'region': 'Hip'}, glute={'region': 'Hip'})
        orte = {'regler': {'body_bs_HipGenitalBulge': gemessen(huefte=1.0), 'glute': gemessen(huefte=1.0),
                           'mh:pelvis_bulge-decr_incr': gemessen(huefte=1.0)}, 'aliase': [], 'paare': []}
        with mock.patch('Genesis9.reglerorte.G9reglerorte.fehlende_melden'):
            aus = G9reglergliederung.bereiche(roh=roh, ablage=ablage, orte=orte)
        je = {b['schluessel']: b for b in aus}
        schluessel = [b['schluessel'] for b in aus]
        self.assertEqual(schluessel.index('genitalien'), schluessel.index('huefte') + 1, 'direkt hinter „Hüfte und Po"')
        self.assertEqual(je['genitalien']['name'], 'Genitalien')
        self.assertEqual([(r['name'], r['gruppe']) for r in je['genitalien']['regler']],
                         [('body_bs_HipGenitalBulge', G9genitalregler.G_DAZ), ('mh:pelvis_bulge-decr_incr', G9genitalregler.G_MH),
                          ('eigen:cute_girl_mesh_1_scham', G9genitalregler.G_EIGEN)])
        self.assertEqual([r['name'] for r in je['huefte']['regler']], ['glute'])
        self.assertEqual([r['name'] for r in je['modell_eigen']['regler']], ['eigen:x_bauch'], 'der feste Bereich führt die Scham nicht mehr')
        # Ohne Genitalregler steht die Abteilung trotzdem da — der Browser hängt die Stücke hinein (`genesis9genitalien.js`).
        with mock.patch('Genesis9.reglerorte.G9reglerorte.fehlende_melden'):
            aus = G9reglergliederung.bereiche(roh=[dict(roh[0], regler=[regler('glute')])], ablage=ablage, orte=orte)
        self.assertEqual(next(b for b in aus if b['schluessel'] == 'genitalien')['regler'], [])

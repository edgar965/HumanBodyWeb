# -*- coding: utf-8 -*-
"""Umriss der Fotos: Profile aus Sichtungseinträgen, gesperrte Zeilen, Blickrichtung (19.09.2026).

Edgar (Testfall Ursula, „mach"): die Silhouetten formen das Zielnetz Zeile für
Zeile (`G9umrissformung`, Wahrheitsprobe im LongRunner `test_bildmodell_umriss`).
Hier die Vorbereitung ohne Renderer: `Bildmodellumriss` sucht die Fotos heraus,
baut je Foto das Profil und sperrt Zeilen, in denen ein Arm die Silhouette
macht — von vorn die Zeilen, in denen die Armkette im Rumpfsegment liegt; von
der Seite die Zeilen, in denen Ellbogen oder Handgelenk an der Kante steht.
Die Nase gegen die Schulter sagt, wohin die Person schaut. Sabotage: ein Arm
mitten im Rumpf sperrt Zeilen, ein Arm weit draußen nicht.
"""

from django.test import SimpleTestCase

from core.dienste.bildmodellumriss import Bildmodellumriss

N = 64
BREITE, HOEHE = 400, 1000


def _profil(breite=0.2):
    links = [0.5 - breite * HOEHE / BREITE / 2] * N
    rechts = [0.5 + breite * HOEHE / BREITE / 2] * N
    return {'breiten': [breite] * N, 'links': links, 'rechts': rechts, 'oben': 0, 'unten': HOEHE - 1,
            'mitte': 0.5}


def _rig(punkte):
    rig = [[0.0, 0.0, 0.0] for _ in range(17)]
    for i, (x, y) in punkte.items():
        rig[i] = [x, y, 1.0]
    return {'yolo': {'punkte': rig}}


def _bild(ansicht, rig, **mehr):
    b = {'datei': ansicht + '.jpg', 'kategorie': 'koerper', 'ansicht': ansicht, 'haltung': 'neutral',
         'gewicht': 1.0, 'nutzung': 'form_textur', 'breite': BREITE, 'hoehe': HOEHE,
         'rigs': rig, 'textur': {'profil': _profil()}}
    b.update(mehr)
    return b


class _Job:
    kennung = 'pruef'
    optionen = {}
    ergebnis = {'ziel': {'hoehe_ziel_cm': 170.0}}

    def __init__(self, bilder):
        self.bilder = bilder


class UmrissTest(SimpleTestCase):
    def test_arm_im_rumpfsegment_sperrt_zeilen_von_vorn(self):
        # Arm haengt an der Seite: Schulter (5) aussen, Ellbogen (7) und Handgelenk (9) im Segment.
        haengend = _rig({5: (0.35, 0.2), 6: (0.65, 0.2), 7: (0.45, 0.35), 9: (0.47, 0.5), 11: (0.45, 0.5),
                         12: (0.55, 0.5)})
        gesperrt = Bildmodellumriss(_Job([]), {}).profil_vorn(_bild('vorne', haengend))['gesperrt']
        self.assertTrue(gesperrt, 'der haengende Arm liegt im Rumpfsegment')
        # Schulter (0,2) bis Handgelenk (0,5) plus eine Handlaenge (0,108) — nichts darunter.
        self.assertTrue(all(0.18 * N <= i <= 0.62 * N for i in gesperrt), sorted(gesperrt))
        # Sabotage: Arm weit ausgestreckt — unter der Schulterzeile liegt kein Punkt der Kette im
        # Segment (die Schulter selbst liegt immer drin; ueber der Achsel formt nichts).
        gestreckt = _rig({5: (0.35, 0.2), 6: (0.65, 0.2), 7: (0.1, 0.3), 9: (0.02, 0.4), 11: (0.45, 0.5),
                          12: (0.55, 0.5)})
        frei = Bildmodellumriss(_Job([]), {}).profil_vorn(_bild('vorne', gestreckt))
        self.assertTrue(all(i <= 0.25 * N for i in frei['gesperrt']), sorted(frei['gesperrt']))

    def test_seite_blickrichtung_und_arm_an_der_kante(self):
        u = Bildmodellumriss(_Job([]), {})
        links = u.profil_seite(_bild('seite', _rig({0: (0.3, 0.1), 5: (0.5, 0.2), 6: (0.5, 0.2)})))
        self.assertTrue(links['front_links'])
        rechts = u.profil_seite(_bild('seite', _rig({0: (0.7, 0.1), 5: (0.5, 0.2), 6: (0.5, 0.2)})))
        self.assertFalse(rechts['front_links'])
        # Handgelenk (9) an der Vorderkante (links = 0,25 bei Breite 0,2): gesperrt um seine Zeile.
        kante = u.profil_seite(_bild('seite', _rig({0: (0.3, 0.1), 5: (0.5, 0.2), 9: (0.26, 0.5)})))
        self.assertTrue({31, 32, 33} & kante['gesperrt'], sorted(kante['gesperrt']))
        # Sabotage: Handgelenk mitten im Rumpf — keine Kante, keine Sperre.
        mitte = u.profil_seite(_bild('seite', _rig({0: (0.3, 0.1), 5: (0.5, 0.2), 9: (0.5, 0.5)})))
        self.assertEqual(mitte['gesperrt'], set())

    def test_bilderwahl_und_option(self):
        bilder = [_bild('vorne', _rig({})), _bild('hinten', _rig({})), _bild('seite', _rig({})),
                  _bild('dreiviertel', _rig({})), _bild('vorne', _rig({}), haltung='posiert'),
                  _bild('vorne', _rig({}), nutzung='aus')]
        u = Bildmodellumriss(_Job(bilder), {})
        self.assertEqual([b['ansicht'] for b in u.bilder(('vorne', 'hinten'))], ['vorne', 'hinten'])
        self.assertEqual(len(u.bilder(('seite',))), 1)
        self.assertTrue(Bildmodellumriss.an({}))
        self.assertFalse(Bildmodellumriss.an({'umriss': 'aus'}))
        p, g, bericht = Bildmodellumriss(_Job(bilder), {'umriss': 'aus'}).formen('p', 'g')
        self.assertEqual((p, g, bericht), ('p', 'g', None))
        self.assertIsNone(Bildmodellumriss(_Job([]), {}).formen('p', 'g')[2])

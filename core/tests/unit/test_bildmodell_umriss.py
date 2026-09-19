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

20.09.2026, Damira („woher hast du diese Donauwellen Maße???"): die Armkette
wurde mit festen 12 Punkten je Glied abgetastet — bei 125 Zeilen kreuzt ein
Oberarm 19 Zeilen, jede zweite blieb ungesperrt, und der Umriss formte sie auf
Rumpf PLUS Arm (Taille 32 statt 20 cm, Hüfte mit Händen 44). Jetzt LÜCKENLOS:
jede Zeile von der Schulter bis eine Handlänge unter dem Handgelenk ist gesperrt.

Und die Sperre muss auch ANKOMMEN (20.09.2026, spät, „so eine Donauwellenfigur darf
nicht sein"): `G9umrissprofile._sperre` übersetzte jede gesperrte Fotozeile (64) in EINE
von drei Stufen (192), und `_auf_kaefig` füllte diese Stufe per `np.interp` aus den zwei
freien Nachbarn — Damiras Rumpf wurde auf Rumpf plus Arme geformt (Faktor 1,47) und die
Maßbänder schnürten ihn danach dreimal ein. Jetzt sperrt eine Fotozeile alle Stufen, die
sie überdeckt, die Ausrichtung lässt nan stehen, und ein gesperrter Block bleibt Faktor 1
(`_gefuellt` füllt nur Lücken bis 4 % der Höhe). Sabotage: die alte Einstufen-Sperre.
"""

import numpy as np
from django.test import SimpleTestCase

from core.daten.wrapperpfad import Wrapperpfad
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

    def test_haengende_arme_sperren_lueckenlos(self):
        # Damira 09: 125 Zeilen, Arme haengen an der Seite (Schulter 0,22, Ellbogen 0,37,
        # Handgelenk 0,49), die Silhouette spannt ueber die Arme — jede Zeile der Kette gesperrt.
        n = 125
        breit = {'breiten': [0.25] * n, 'links': [0.17] * n, 'rechts': [0.9] * n, 'oben': 25,
                 'unten': 2560, 'mitte': 0.53}
        rig = _rig({5: (0.72, 0.22), 6: (0.34, 0.22), 7: (0.775, 0.37), 8: (0.276, 0.37),
                    9: (0.83, 0.49), 10: (0.21, 0.49), 11: (0.65, 0.46), 12: (0.4, 0.46)})
        b = _bild('vorne', rig, breite=922, hoehe=2626, textur={'profil': breit})
        gesperrt = Bildmodellumriss(_Job([]), {}).profil_vorn(b)['gesperrt']
        hoch = 2560 - 25 + 1
        von = int((0.22 * 2626 - 25) / hoch * n)
        bis = int(((0.49 + 0.108) * 2626 - 25) / hoch * n)
        # Die Hand haengt in Armrichtung (leicht schraeg), ihr Ende liegt eine Zeile ueber `bis`.
        fehlend = [i for i in range(von + 1, bis - 1) if i not in gesperrt]
        self.assertEqual(fehlend, [], 'Zeilen zwischen Schulter und Hand ohne Sperre')
        self.assertGreaterEqual(len(gesperrt), bis - von - 2)

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


class SperreKommtAnTest(SimpleTestCase):
    def _profile(self):
        with Wrapperpfad():
            from Genesis9.umrissprofile import G9umrissprofile
        return G9umrissprofile(192)

    def test_gesperrter_block_bleibt_nan_und_faktor_eins(self):
        pr = self._profile()
        profil = dict(_profil(0.3), gesperrt=set(range(14, 37)))  # Damira: Rumpf 14..36 von 64
        # Alle drei Stufen je Fotozeile sind gesperrt — keine Lücke dazwischen.
        sperre = pr._sperre(profil)
        self.assertEqual(sperre, set(range(42, 111)), sorted(sperre)[:6])
        foto = pr._foto_zeilen([profil], 'breiten')
        self.assertTrue(np.isnan(foto[42:111]).all())
        # Die Ausrichtung (np.interp über die gültigen Stützen) lässt die Sperre stehen.
        aus = pr._auf_kaefig(foto, 0.0, 1.0)
        self.assertTrue(np.isnan(aus[42:111]).all(), 'die Ausrichtung füllte die Sperre auf')
        self.assertFalse(np.isnan(aus[20:42]).any())
        # Ein gesperrter Block wird nicht aus den Nachbarn gefüllt; eine kurze Lücke (Daumen) schon.
        aktiv = np.ones(192, bool)
        f = np.where(np.isnan(aus), np.nan, 1.3)
        f[150:153] = np.nan
        gefuellt = pr._gefuellt(f, aktiv)
        self.assertTrue(np.isnan(gefuellt[42:111]).all(), 'der Block wurde gefüllt')
        self.assertTrue(np.allclose(gefuellt[150:153], 1.3), 'die kurze Lücke blieb leer')

    def test_sabotage_einstufen_sperre_kommt_nicht_an(self):
        pr = self._profile()
        profil = dict(_profil(0.3), gesperrt=set(range(14, 37)))
        # Die alte Übersetzung: eine Stufe je Fotozeile.
        alt = {int(round((i + 0.5) / 64 * 192 - 0.5)) for i in profil['gesperrt']}
        foto = pr._laufender_median(pr._zeilen(profil, 'breiten'))
        for j in alt:
            foto[j] = np.nan
        aus = pr._auf_kaefig(foto, 0.0, 1.0)
        # Nur ein Drittel der Rumpfstufen ist nan — und eine gefüllte Formung nähme die Nachbarn.
        self.assertLess(np.isnan(aus[42:111]).sum(), 30)

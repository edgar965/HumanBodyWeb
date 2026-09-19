# -*- coding: utf-8 -*-
"""Fotomaße: die Proportionen der Silhouette formen das Zielnetz (19.09.2026).

Edgar (Testfall Ursula): „versuchst du aus dem Genesis9 Modell das Ursula
Modell zu erstellen" — der erste Lauf traf Kopf und Breiten, aber Hüfte
34,6 statt 38,4 cm und jede Tiefe 3–5 cm zu klein: das Ziel war die
schlanke Schätzung, obwohl die Silhouette die Maße hatte.

Kunstdaten: ein Breitenprofil mit 64 Stufen, das eine Figur mit bekannten
Maßen beschreibt (Schulterlinie bei 20 %, Hüftlinie bei 50 % der Höhe),
dazu ein YOLO-Rig und Mundlandmarken. Geprüft wird, dass `G9fotoproportionen`
die eingebauten Maße wiederfindet (Hüfte = breiteste Stelle um die Hüftlinie,
Taille = schmalste dazwischen, Oberschenkel = Beinsegment, Tiefen von der
Seite, Vorsprung an der Vorderkante), dass verschmolzene Beine kein Maß geben,
und dass `Bildmodellzielproportionen` die Fotomaße als Ziel nimmt — Eingaben
darüber, `aus` schaltet sie ab. Sabotage: Beine verschmolzen → Oberschenkel weg.
"""

from django.test import SimpleTestCase
from Genesis9.fotoproportionen import G9fotoproportionen

from core.dienste.bildmodellfotomasse import Bildmodellfotomasse
from core.dienste.bildmodellzielproportionen import Bildmodellzielproportionen

N = 64
BREITE, HOEHE = 400, 1000


def _profil(breite_je_stufe, links_je_stufe=None, mitte_je_stufe=lambda t: 0.5):
    breiten = [breite_je_stufe(i / N) for i in range(N)]
    links = [links_je_stufe(i / N) if links_je_stufe else mitte_je_stufe(i / N) - b * HOEHE / BREITE / 2
             for i, b in zip(range(N), breiten, strict=True)]
    rechts = [lk + b * HOEHE / BREITE for lk, b in zip(links, breiten, strict=True)]
    return {'breiten': breiten, 'links': links, 'rechts': rechts, 'oben': 0, 'unten': HOEHE - 1, 'mitte': 0.5}


def _rig(punkte):
    """17 YOLO-Punkte, alle unsichtbar außer den genannten (x, y als Bildanteile)."""
    rig = [[0.0, 0.0, 0.0] for _ in range(17)]
    for i, (x, y) in punkte.items():
        rig[i] = [x, y, 1.0]
    return {'yolo': {'punkte': rig}}


def _vorn(breite_je_stufe, beine_getrennt=True):
    """Figur von vorn: Rumpf 0,20–0,50, Knie bei 0,72, Knöchel bei 0,95.

    Getrennte Beine: das gespeicherte Segment ist das linke Bein (Mitte x 0,42);
    verschmolzen: ein Segment doppelter Breite um 0,5, beide Knie darin.
    """
    rig = _rig({5: (0.4, 0.20), 6: (0.6, 0.20), 11: (0.45, 0.50), 12: (0.55, 0.50),
                13: (0.42, 0.72), 14: (0.58, 0.72), 15: (0.42, 0.95), 16: (0.58, 0.95)})
    landmarken = [[0.5, 0.12, 1.0]] * 33
    if beine_getrennt:
        profil = _profil(breite_je_stufe, mitte_je_stufe=lambda t: 0.42 if t >= 0.56 else 0.5)
    else:
        profil = _profil(lambda t: breite_je_stufe(t) * (2 if t >= 0.56 else 1))
    return {'ansicht': 'vorne', 'breite': BREITE, 'hoehe': HOEHE, 'rigs': rig, 'landmarken': landmarken,
            'textur': {'profil': profil}}


def _figur(t):
    """Breiten als Anteil der Höhe: Hals 0,06, Rumpf 0,20 mit Taille 0,14 bei 0,40, Hüfte 0,24, Bein 0,10."""
    if t < 0.10:
        return 0.12
    if t < 0.18:
        return 0.06
    if t < 0.32:
        return 0.20
    if t < 0.45:
        return 0.14
    if t < 0.56:
        return 0.24
    return 0.10


class FotoproportionenTest(SimpleTestCase):
    def test_breiten_von_vorn(self):
        m = G9fotoproportionen(_vorn(_figur)).messen()
        self.assertAlmostEqual(m['huefte_breite'], 0.24, places=3)
        self.assertAlmostEqual(m['taille_breite'], 0.14, places=3)
        self.assertAlmostEqual(m['oberschenkel_dicke'], 0.10, places=3)
        self.assertAlmostEqual(m['wade_dicke'], 0.10, places=3)
        self.assertAlmostEqual(m['hals_breite_roh'], 0.06, places=3)
        self.assertNotIn('hals_breite', m)

    def test_sabotage_verschmolzene_beine_geben_kein_gliedmass(self):
        m = G9fotoproportionen(_vorn(_figur, beine_getrennt=False)).messen()
        self.assertNotIn('oberschenkel_dicke', m)
        self.assertNotIn('wade_dicke', m)
        self.assertIn('huefte_breite', m)

    def test_tiefen_von_der_seite_mit_vorsprung(self):
        def tiefe(t):
            return 0.16 if 0.24 < t < 0.30 else 0.12  # Brust ragt 0,04 vor (Band 25 % des Rumpfs)

        def linke_kante(t):  # Vorderkante links (die Nase zeigt nach links), der Rücken bleibt, wo er ist
            return 0.5 + 0.06 * HOEHE / BREITE - tiefe(t) * HOEHE / BREITE

        rig = _rig({0: (0.3, 0.08), 5: (0.5, 0.20), 6: (0.5, 0.20), 11: (0.5, 0.50), 12: (0.5, 0.50)})
        bild = {'ansicht': 'seite', 'breite': BREITE, 'hoehe': HOEHE, 'rigs': rig,
                'textur': {'profil': _profil(tiefe, linke_kante)}}
        m = G9fotoproportionen(bild).messen()
        self.assertAlmostEqual(m['brust_tiefe'], 0.16, places=3)
        self.assertAlmostEqual(m['bauch_tiefe'], 0.12, places=3)
        self.assertAlmostEqual(m['gesaess_tiefe'], 0.12, places=3)
        self.assertAlmostEqual(m['brust_vorsprung'], 0.04, places=3)

    def test_ohne_profil_oder_schraeg_nichts(self):
        self.assertEqual(G9fotoproportionen({'ansicht': 'vorne'}).messen(), {})
        b = _vorn(_figur)
        b['ansicht'] = 'dreiviertel'
        self.assertEqual(G9fotoproportionen(b).messen(), {})


class _Job:
    kennung = 'pruef'

    def __init__(self, bilder, hoehe=170.0, optionen=None):
        self.bilder = bilder
        self.ergebnis = {'ziel': {'hoehe_ziel_cm': hoehe}}
        self.optionen = optionen or {}


class ZielTest(SimpleTestCase):
    def _bild(self):
        b = _vorn(_figur)
        b.update({'kategorie': 'koerper', 'haltung': 'neutral', 'gewicht': 1.0, 'nutzung': 'form_textur'})
        return b

    def test_fotomasse_in_cm_und_als_ziel(self):
        job = _Job([self._bild(), self._bild()])
        m = Bildmodellfotomasse(job, 170.0).messen()
        self.assertEqual(m['anzahl'], 2)
        self.assertAlmostEqual(m['cm']['huefte_breite'], 40.8, places=1)
        self.assertEqual(m['bilder']['huefte_breite'], 2)
        eingabe = {'proportionen': {'huefte_breite': '39'}}
        ziele, quelle = Bildmodellzielproportionen(job, None, eingabe).ziele_m()
        self.assertAlmostEqual(ziele['huefte_breite'], 0.39)  # die Eingabe schlägt das Foto
        self.assertEqual(quelle['huefte_breite'], 'eingabe')
        self.assertAlmostEqual(ziele['taille_breite'], 0.238)
        self.assertEqual(quelle['taille_breite'], 'foto')
        self.assertNotIn('hals_breite_roh', ziele)

    def test_aus_schaltet_die_fotomasse_ab(self):
        job = _Job([self._bild()])
        ziele, _ = Bildmodellzielproportionen(job, None, {'fotomasse': 'aus'}).ziele_m()
        self.assertEqual(ziele, {})
        job = _Job([self._bild()], optionen={'fotomasse': 'aus'})
        ziele, _ = Bildmodellzielproportionen(job, None, {}).ziele_m()
        self.assertEqual(ziele, {})
        # Ohne Zielhöhe keine cm.
        self.assertEqual(Bildmodellfotomasse(_Job([self._bild()], hoehe=None), None).messen()['cm'], {})

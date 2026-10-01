# -*- coding: utf-8 -*-
u"""Prüf-KI der Begutachtung („2D3D Kleider", 01.10.2026): Prompt, Antwort, Fälligkeit, Ende — ohne Ollama, ohne Ablage.

1. Der Prompt nennt das Ziel (genau wie die Fotos, animierbar, Textur von allen Seiten, keine Haut durch die Kleidung),
   die A-Pose, die sechs Bereiche, die Zahlen der Runde, den Zustand, die Funktionsliste des Modells und die Garderobe.
2. Aus der Antwort werden nur Zeilen, die `G9rezept` versteht UND die Regeln halten: keine Haltung, keine Funktion der
   Automatik, Stücke nur aus der Garderobe, Form nur an getragenen Stücken, `morph_wert` nur an vorhandenen Reglern.
3. Fällig alle `pruefki_alle` Runden oder nach `pruefki_stillstand` Runden ohne Besserung; nie zweimal für eine Runde.
4. `ergaenzen` hängt die Zeilen HINTER das Rezept der Automatik; `fertig` zählt nur ab `FERTIG_AB`.

Sabotage: in `_pruefen` die Prüfung `if name in self.VERBOTEN` entfernen → Fall 2 rot (die Haltung käme durch); in
`faellig` `seit < 1` streichen → Fall 3 rot (dieselbe Runde zweimal).
"""
from django.test import SimpleTestCase
from Genesis9.modellmitkleidern import ModellMitKleidern

from core.dienste.begutachtungskritik import Begutachtungskritik
from core.dienste.begutachtungsprompt import Begutachtungsprompt


class BegutachtungskritikTest(SimpleTestCase):

    databases = set()
    OPTIONEN = {'pruefki': 'qwen3.8:27b', 'pruefki_alle': 5, 'pruefki_stillstand': 3}

    @staticmethod
    def _prompt():
        return Begutachtungsprompt([('Oberteile', ['g9_base_shirt', 'angie_top']), ('Hosen', ['angie_jeans'])],
                                   ['kin_hair', 'mavick_hair'])

    @staticmethod
    def _modell():
        m = ModellMitKleidern()
        m.kleid_nur('g9_base_shirt')
        m.haar_nur('kin_hair')
        m.kleidung['g9_base_shirt.eigen.netz_b2s4'] = 0.5
        return m

    def test_1_prompt(self):
        befund = {'teile': {'koerper': {'art': 'koerper', 'netz_mm': -12.0},
                            'g9_base_shirt': {'art': 'kleidung', 'netz_mm': 22.0, 'grund_mm': 10.0,
                                              'haut_min_mm': -1.5, 'haut_innen': 0.04},
                            'kin_hair': {'art': 'haar', 'netz_abs_mm': 9.0}},
                  'koerper_baender': {'rumpf': [0.3, 0.3, 0.3], 'oberschenkel': [0.7, 0.5, 0.4]}}
        text = self._prompt().text(self._modell(), befund, {'abweichung': 1.765, 'iou': 0.62, 'farbe': 0.1}, 7, 8)
        for erwartet in ('GENAU entsprechen', 'keine Haut durch die Kleidung', 'A-Pose', 'Durchschimmern',
                         'Runde 7: Gesamtabweichung 1.765',
                         'Luft zur Haut mindestens -1.5 mm, 4.0 % der Stoffpunkte in der Haut',
                         'rumpf = Stoff, oberschenkel = Haut', 'm.kleid_welle(', 'm.haar_biegen(', 'm.koerper_ort(',
                         'g9_base_shirt.eigen.netz_b2s4 = 0.5', 'Kleidung: g9_base_shirt (Anteil 1.0)',
                         'Oberteile: g9_base_shirt, angie_top', 'Frisuren — Kennungen', '"fertig": true NUR',
                         'höchstens 8 Zeilen'):
            self.assertIn(erwartet, text)

    def test_2_zeilen(self):
        kritik = Begutachtungskritik(self.OPTIONEN, None, self._prompt())
        roh = ["m.kleid_nur('angie_top', 'angie_jeans')",                            # Garderobe: gilt
               "m.kleid_nur('fantasie_kleid')",                                       # nicht in der Garderobe
               'm.haltung(30)',                                                       # verboten: A-Pose
               "m.kleid_drapieren('g9_base_shirt')",                                  # Sache der Automatik
               "m.morph_ort('kleidung', 'g9_base_shirt', 'bauch', {'landmarke': 'bauch', 'radius_cm': 8}, weg_cm=2.0)",
               "m.morph_ort('kleidung', 'angie_jeans', 'knie', {'band': (0.3, 0.5)})",      # nicht getragen
               "m.haar_biegen('kin_hair', 'pony', {'landmarke': 'stirn', 'radius_cm': 6}, richtung='vorn')",
               "m.morph_wert('kleidung', 'g9_base_shirt', 'netz_b2s4', 0.8)",       # den Regler gibt es
               "m.morph_wert('kleidung', 'g9_base_shirt', 'erfunden', 0.8)",        # den nicht
               "print('hallo')",                                                     # kein Rezept
               '# Kommentar', '']
        zeilen, verworfen = kritik.zeilen(roh, self._modell(), self._prompt())
        self.assertEqual(zeilen, [roh[0], roh[4], roh[6], roh[7]])
        self.assertEqual([grund.split(':')[0] for _zeile, grund in verworfen],
                         ['nicht in der Garderobe', 'haltung regelt die Automatik',
                          'kleid_drapieren regelt die Automatik', 'nicht getragen', 'Regler gibt es nicht', 'Zeile 1'])

    def test_3_faellig(self):
        kritik = Begutachtungskritik(self.OPTIONEN, None, self._prompt())
        verlauf = [[r, a, a] for r, a in ((1, 2.0), (2, 1.9), (3, 1.8), (4, 1.85), (5, 1.86), (6, 1.87))]
        self.assertTrue(kritik.faellig({'letzte_runde': 5, 'verlauf': verlauf[:5]}))               # alle 5 Runden
        self.assertFalse(kritik.faellig({'letzte_runde': 5, 'verlauf': verlauf[:5], 'kritik_runde': 5}))
        self.assertFalse(kritik.faellig({'letzte_runde': 4, 'verlauf': verlauf[:4]}))       # erst 1 ohne Besserung
        self.assertTrue(kritik.faellig({'letzte_runde': 6, 'verlauf': verlauf}))            # 3 ohne Besserung
        self.assertFalse(kritik.faellig({'letzte_runde': 6, 'verlauf': verlauf, 'kritik_runde': 5}))  # eben gefragt
        self.assertFalse(Begutachtungskritik({'pruefki': 'aus'}, None).faellig({'letzte_runde': 5, 'verlauf': verlauf}))
        self.assertEqual(Begutachtungskritik.ohne_besserung(verlauf), 3)

    def test_4_ergaenzen(self):
        antwort = {'runde': 5, 'modell': 'qwen3.8:27b', 'aehnlichkeit': 6, 'urteil': 'Der Saum ist zu kurz.',
                   'fertig': False, 'bereiche': [], 'fehlt': [], 'verworfen': [], 'begruendung': '', 'sekunden': 40.0,
                   'zeilen': ["m.kleid_ring('g9_base_shirt', 'saum', 0.05, weite=1.2)"]}

        class Stumm(Begutachtungskritik):
            def fragen(self, modell, z):
                return dict(antwort, runde=int(z.get('letzte_runde') or 0))

        kritik = Stumm(self.OPTIONEN, None, self._prompt())
        z = {'letzte_runde': 5, 'verlauf': [[r, 2.0, 2.0] for r in range(1, 6)]}
        rezept, zusatz, fertig = kritik.ergaenzen('# automatisch\nm.passform(weite_cm=1.0)\n', self._modell(), z)
        self.assertFalse(fertig)
        self.assertEqual(rezept, '# automatisch\nm.passform(weite_cm=1.0)\n'
                                 "# Prüf-KI qwen3.8:27b nach Runde 5: Der Saum ist zu kurz.\n"
                                 "m.kleid_ring('g9_base_shirt', 'saum', 0.05, weite=1.2)\n")
        self.assertEqual(zusatz, 'Prüf-KI qwen3.8:27b: Ähnlichkeit 6/10 — Der Saum ist zu kurz.')
        self.assertEqual((z['kritik_runde'], len(z['kritiken'])), (5, 1))
        # Nicht fällig: nichts passiert.
        self.assertEqual(kritik.ergaenzen('x', self._modell(), {'letzte_runde': 5, 'verlauf': [], 'kritik_runde': 5}),
                         ('x', '', False))
        # Fertig zählt nur ab FERTIG_AB.
        antwort.update(fertig=True, aehnlichkeit=7)
        self.assertFalse(kritik.ergaenzen('', self._modell(), {'letzte_runde': 10, 'verlauf': []})[2])
        antwort.update(aehnlichkeit=8)
        rezept, zusatz, fertig = kritik.ergaenzen('', self._modell(), {'letzte_runde': 15, 'verlauf': []})
        self.assertTrue(fertig)
        self.assertTrue(zusatz.endswith(' · fertig'))

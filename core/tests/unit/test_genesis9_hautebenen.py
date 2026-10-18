# -*- coding: utf-8 -*-
u"""Die Hautebenen (17.10.2026): Gebietskarten, Muskel-/Fettzeichnung, Ablage und die Deckung durch alle Schichten. Kunstdaten, keine Figur, keine Paarung. Geschrieben, nicht gelaufen.

Edgar, 17.10.2026: „Hautebenen: Hautton, Sommersprossen, Altersflecken, graue Haare, Muskel- und Fettzeichnung … wo sind die Regler Haut?"

1. Gebiete (`G9hautebenen.felder`): Körper nimmt MB-Labs Sommersprossenmaske (auf ihren größten Wert normiert, mal 0,9); an einer Nasenlandmarke steht das Gesicht auf 1, 20 cm weiter
   auf 0; kein Gesicht ohne Landmarkentabelle.
2. Altersflecken: Handrücken (Normale vom Körper weg) 1, Handfläche (Normale zum Körper) 0; Unterarm 0,7 des Handwerts; Rumpf unter 1,25 m keine, im Décolleté nach oben gewandt 0,45; Beine nie.
3. Die Zeichnung packt Muskel in R/G und Fett in B/A, flach = 128; ihre Dateien tragen eine eigene Fassung und einen anderen Stamm als die Falten.
4. Jedes Produkt hat seine eigene Ablage (eigene Sperre, eigene Läufe, eigene Fehler: `__init_subclass__`) und führt NUR seine Dateien — die Liste der Zeichnung nennt kein Bild der Falten.
5. Das Feld `hautebenen` geht durch ALLE Schichten — Modell (JS), Figur-JSON (Speichern, Undo), Vorgabe eines gespeicherten Modells, Server-Eintrag (zweimal), Bedienfeld
   (`artefakte-benennen.md`). Sabotage: `hautebenen` aus `toJSON` streichen → Fall 5 rot.
6. Die Adresse der Karten ist im Router eingetragen (`g9_figur_hautebenen`).

Sabotage-Gegenprobe (nicht gefahren): in `felder` den Kopf nicht ausnehmen → Fall 1 rot; `aussen` ohne `seite` → Fall 2 rot; `PRODUKT` in der Unterklasse weglassen → Fall 4 rot.
"""
import json
from pathlib import Path
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse

from core.projekt_temp import ProjektTemp

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.koerperteile import G9koerperteile  # noqa: E402

from core.dienste.g9hautebenen import G9hautebenen  # noqa: E402
from core.dienste.g9hautebenenablage import G9hautebenenablage  # noqa: E402
from core.dienste.g9hautfalten import G9hautfalten  # noqa: E402
from core.dienste.g9hautfaltenablage import G9hautfaltenablage  # noqa: E402
from core.dienste.g9hautzeichnung import G9hautzeichnung  # noqa: E402
from core.dienste.g9hautzeichnungablage import G9hautzeichnungablage  # noqa: E402

N = G9koerperteile.NUMMER


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


def felder(teil, pos, normale=(0.0, 0.0, 1.0), maske=0.0, gesicht=None, geschlecht='female'):
    u"""`(sommer, alter)` für EINEN Texel."""
    g = G9hautebenen(geschlecht)
    wert = np.full((8, 8), maske)
    s, a = g.felder(np.array([pos], dtype=float), np.array([normale], dtype=float), np.array([N[teil]]), np.array([[0.5, 0.5]]), wert, gesicht or {})
    return float(s[0]), float(a[0])


class GebietTest(SimpleTestCase):
    databases = set()

    def test_1_sommersprossen_koerper_nimmt_die_maske_gesicht_die_landmarken(self):
        voll = G9hautebenen.MASKE_MAX['female']
        s, _a = felder('rumpf', (0.0, 1.2, 0.1), maske=voll * 0.5)
        self.assertAlmostEqual(s, 0.45, places=6, msg='halbe Maske mal 0,9')
        s, _a = felder('kopf', (0.0, 1.55, 0.117), gesicht={'nase': np.array([[0.0, 1.55, 0.117]])})
        self.assertAlmostEqual(s, 1.0, places=6, msg='an der Nasenlandmarke voll')
        s, _a = felder('kopf', (0.0, 1.55, 0.317), gesicht={'nase': np.array([[0.0, 1.55, 0.117]])})
        self.assertLess(s, 1e-6, '20 cm weiter kein Gesichtsgebiet')
        s, _a = felder('kopf', (0.0, 1.55, 0.117), maske=voll)
        self.assertEqual(s, 0.0, 'ohne Landmarkentabelle kein Gesicht — und die Körpermaske zählt am Kopf nicht')

    def test_2_altersflecken_hand_unterarm_rumpf_beine(self):
        hand_aussen = felder('l_hand', (0.7, 0.9, 0.0), normale=(1.0, 0.0, 0.0))[1]
        hand_innen = felder('l_hand', (0.7, 0.9, 0.0), normale=(-1.0, 0.0, 0.0))[1]
        arm_aussen = felder('l_unterarm', (0.5, 1.1, 0.0), normale=(1.0, 0.0, 0.0))[1]
        self.assertAlmostEqual(hand_aussen, 1.0, places=6)
        self.assertEqual(hand_innen, 0.0)
        self.assertAlmostEqual(arm_aussen, 0.7, places=6, msg='Unterarm 0,7 des Handwerts')
        rechts_aussen = felder('r_hand', (-0.7, 0.9, 0.0), normale=(-1.0, 0.0, 0.0))[1]
        self.assertAlmostEqual(rechts_aussen, 1.0, places=6, msg='die rechte Hand: außen heißt −x')
        unten = felder('rumpf', (0.0, 1.0, 0.1), normale=(0.0, 1.0, 0.0))[1]
        oben = felder('rumpf', (0.0, 1.4, 0.1), normale=(0.0, 1.0, 0.0))[1]
        self.assertEqual(unten, 0.0, 'unter 1,25 m keine Altersflecken am Rumpf')
        self.assertAlmostEqual(oben, 0.45, places=6, msg='Décolleté, nach oben gewandt')
        self.assertEqual(felder('l_oberschenkel', (0.1, 0.7, 0.0), normale=(0.0, 1.0, 0.0))[1], 0.0, 'Beine nie')


class ZeichnungTest(SimpleTestCase):
    databases = set()

    def test_3_pakete_fassung_und_stamm(self):
        self.assertNotEqual(G9hautzeichnung.stamm('male').name.split('_v')[0], G9hautfalten.stamm('male').name.split('_v')[0])
        self.assertIn('v%d' % G9hautzeichnung.FASSUNG, G9hautzeichnung.bildpfad('male', 1001).name)
        self.assertEqual(G9hautzeichnung.KANAELE, ((2, 'muskel'), (3, 'fett')), 'B = Muskel, A = Fett im Verschiebungsbild')
        self.assertIn('hautebenen_', G9hautebenen.stamm('female').name)

    def test_3b_kachel_packt_muskel_in_rg_und_fett_in_ba(self):
        s = 16
        z = G9hautzeichnung('male')
        traeger = mock.Mock()
        abtastung = mock.Mock()
        abtastung.stellen.return_value = (np.ones((s, s), dtype=bool), None, None)
        rampen = iter([np.arange(s)[None, :] * 0.0004 * np.ones((s, s)), np.arange(s)[:, None] * 0.0004 * np.ones((s, s))])      # Muskel steigt nach rechts, Fett nach unten
        eins = np.full((s, s), 0.001)

        def hoehe_und_mass(_t, _a, _n, _q):
            z.naht = None
            return np.ones((s, s), dtype=bool), next(rampen), eins, eins
        with mock.patch.object(z, 'hoehe_und_mass', side_effect=hoehe_und_mass):
            bild, p99 = z.kachel(traeger, abtastung, 1001, [None, None])
        self.assertEqual(bild.shape, (s, s, 4))
        mitte = bild[s // 2, s // 2].astype(int)
        self.assertLess(mitte[0], 128, 'Muskel steigt nach rechts: Normale x < 128')
        self.assertAlmostEqual(int(mitte[1]), 128, delta=1)
        self.assertGreater(mitte[3], 128, 'Fett steigt nach unten: Normale y > 128')
        self.assertAlmostEqual(int(mitte[2]), 128, delta=1)
        self.assertEqual(set(p99), {'muskel', 'fett'})


class AblageTest(SimpleTestCase):
    databases = set()

    def test_4_jedes_produkt_hat_seine_ablage(self):
        self.assertIs(G9hautzeichnungablage.PRODUKT, G9hautzeichnung)
        self.assertIs(G9hautebenenablage.PRODUKT, G9hautebenen)
        self.assertIs(G9hautfaltenablage.PRODUKT, G9hautfalten)
        for ablage in (G9hautzeichnungablage, G9hautebenenablage):
            self.assertIsNot(ablage._laeuft, G9hautfaltenablage._laeuft)
            self.assertIsNot(ablage._schloss, G9hautfaltenablage._schloss)
            self.assertIsNot(ablage._fehler, G9hautfaltenablage._fehler)
        self.assertIsNot(G9hautzeichnungablage._laeuft, G9hautebenenablage._laeuft)

    def test_4b_die_liste_nennt_nur_die_dateien_des_eigenen_produkts(self):
        with ProjektTemp.wegwerfordner(prefix='g9hautebenen_') as ordner:
            stamm = Path(ordner) / ('hautzeichnung_male_v%d' % G9hautzeichnung.FASSUNG)
            leer = Path(ordner) / 'hautebenen_leer'                       # das Gebiet bekommt einen Stamm ohne Dateien (die echte Ablage kann gebaut sein)
            with mock.patch.object(G9hautzeichnung, 'stamm', classmethod(lambda cls, g: stamm)), \
                    mock.patch.object(G9hautebenen, 'stamm', classmethod(lambda cls, g: leer)):
                self.assertIsNone(G9hautzeichnungablage.liste('male'))
                G9hautzeichnung.listenpfad('male').write_text(json.dumps({'fassung': 1, 'kacheln': {'1001': {}}}), encoding='utf-8')
                self.assertIsNone(G9hautzeichnungablage.liste('male'), 'Bild fehlt: nicht fertig')
                G9hautzeichnung.bildpfad('male', 1001).write_bytes(b'png')
                self.assertEqual(G9hautzeichnungablage.liste('male')['kacheln'], {'1001': {}})
                self.assertIsNone(G9hautebenenablage.liste('male'), 'die Zeichnung ist kein Gebiet')

    def test_6_router(self):
        self.assertEqual(reverse('g9_figur_hautebenen', args=['zeichnung', 'male']), '/api/character/genesis9-figur/hautebenen/zeichnung/male/')
        self.assertEqual(reverse('g9_figur_hautebenen_bild', args=['gebiet', 'female', 1001]), '/api/character/genesis9-figur/hautebenen/gebiet/female/1001.png')


class DeckungTest(SimpleTestCase):
    databases = set()

    def test_5_feld_hautebenen_in_allen_schichten(self):
        modell = quelltext('gemeinsam', 'genesis9modell.js')
        self.assertIn('this.hautebenen = { ...(daten.hautebenen || {}) };', modell)
        self.assertIn('Genesis9hautebenen.anwenden(this)', modell, 'nach jedem Körperbau neu auf die frischen Materialien')
        self.assertIn('async hautebenenSetzen(name, prozent)', modell)
        self.assertIn('eintrag.hautebenen', quelltext('gemeinsam', 'genesis9vorgabe.js'), 'gespeichertes Modell: Vorgabe übernehmen')
        self.assertIn('hautebenen: { ...this.hautebenen },', quelltext('charakter', 'genesis9', 'genesis9figur.js'), 'Undo und Speichern')
        server = (Path(settings.BASE_DIR) / 'core' / 'api' / 'g9figur.py').read_text(encoding='utf-8')
        self.assertEqual(server.count("'hautebenen':"), 2, 'gespeicherte Liste UND Eintrag')
        ui = quelltext('charakter', 'genesis9', 'genesis9hautebenenregler.js')
        self.assertIn('inst.hautebenenSetzen(feld.name, neu)', ui)
        vorlage = (Path(settings.BASE_DIR) / 'templates' / '_genesis9_eigenschaften.html').read_text(encoding='utf-8')
        self.assertIn('id="prop-genesis9-hautebenen"', vorlage)
        self.assertIn('Genesis9hautebenenregler.fuellen(inst)', quelltext('charakter', 'genesis9', 'genesis9eigenschaften.js'))
        self.assertIn('Genesis9hautebenen.haar(inst);', quelltext('gemeinsam', 'genesis9kleidung.js'), 'ein neu gebautes Haarstück wird wieder grau')

    def test_5b_shader_haengt_hautebenen_ein_und_der_schluessel_nennt_sie(self):
        haut = quelltext('gemeinsam', 'genesis9haut.js')
        self.assertIn('Genesis9hautebenenGLSL.einhaengen(shader, ebenen, Boolean(zusatz.schminke))', haut)
        self.assertIn("'e' + (zusatz.hautebenen.zeichnung ? 'z' : '') + (zusatz.hautebenen.mimik ? 'm' : '')", haut,
                      'der Programmschlüssel nennt die Hautebenen samt Zeichnung und Mimik (Three teilt sonst das Programm)')
        ebenen = quelltext('gemeinsam', 'genesis9hautebenenglsl.js')
        self.assertIn('Object.assign(shader.uniforms, ebenen.uniforms);', ebenen)
        self.assertIn("#include <alphamap_fragment>", ebenen)
        glsl = quelltext('gemeinsam', 'genesis9hautglsl.js')
        self.assertIn('static normalen(mitGlitzer, mitDetail, mischung = 0, mitFalten = false, mitZeichnung = false, mitMimik = false)', glsl)

# -*- coding: utf-8 -*-
"""Schleife der Iterationen der „Haar Engine" (30.09.2026) — Wertesatz, Optimierer, Note, Referenzwinkel,
Auswahl, Optionen. Rein rechnend: keine Datenbank, keine Engine, kein Ollama.

`Haarparameter` hat noch keine Einträge (die Engine legt fest, welche Maße das Haar hat) — die Tests hängen
deshalb erfundene ein (`SCHEMA`, nur in diesem Modul). Dateien entstehen nur unter `HumanBodyWeb/_wegwerf/`
(nie System-Temp).
"""

import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.haarparameter import Haarparameter
from core.dienste.iterationsbild import Iterationsbild
from core.dienste.iterationskreislauf import Iterationskreislauf
from core.dienste.iterationsnote import Iterationsnote
from core.dienste.iterationsoptimierer import Iterationsoptimierer
from core.dienste.iterationsoptionen import Iterationsoptionen
from core.dienste.iterationsreferenz import Iterationsreferenz
from core.dienste.iterationsrunde import Iterationsrunde
from core.dienste.iterationswahl import Iterationswahl

MASSE = [
    ('locke.weite', 'Locken: Weite (× Kopf)', 1.2, 1.0, 2.0),
    ('locke.laenge', 'Locken: Länge (× Körperhöhe)', 0.15, 0.05, 0.3),
    ('scheitel.seite', 'Scheitel: zur Seite (× Kopf)', 0.0, -0.4, 0.4),
    ('straehnen.dicke', 'Strähnen: Dicke (× Kopf)', 0.02, 0.005, 0.05),
]
SCHALTER = [('straehnen.an', 'Einzelne Strähnen', 1)]
FARBEN = {'haar': ('Haar', (0.30, 0.22, 0.15))}


class MitSchema(SimpleTestCase):
    """Hängt erfundene Maße, Schalter und Farben in `Haarparameter` ein — statt der echten, die aus
    der Daz-Garderobe kommen (`masse()`/`schalter()` seit dem 30.09.2026: je Frisur ein Teil).
    So hängt dieser Test nicht daran, welche Frisuren auf dem Rechner installiert sind."""

    def setUp(self):
        for name, wert in (('masse', MASSE), ('schalter', SCHALTER)):
            patcher = mock.patch.object(Haarparameter, name,
                                        classmethod(lambda cls, w=wert: w))
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(Haarparameter, 'FARBEN', FARBEN)
        patcher.start()
        self.addCleanup(patcher.stop)


class HaarparameterTest(MitSchema):
    def test_startwerte_liegen_in_ihren_grenzen(self):
        for k, e in Haarparameter.schema().items():
            self.assertLessEqual(e['min'], e['start'], k)
            self.assertLessEqual(e['start'], e['max'], k)

    def test_pruefen_zieht_auf_die_grenzen_und_schaltet_binaer(self):
        werte = Haarparameter.pruefen(
            {'locke.weite': 99, 'straehnen.an': 0.7, 'locke.laenge': 'kaputt', 'x': 1}
        )
        self.assertEqual(werte['locke.weite'], Haarparameter.schema()['locke.weite']['max'])
        self.assertEqual(werte['straehnen.an'], 1)
        self.assertEqual(werte['locke.laenge'], Haarparameter.start()['locke.laenge'])
        self.assertNotIn('x', werte)
        self.assertEqual(set(werte), set(Haarparameter.schema()))

    def test_farben_werden_zu_drei_massen_je_stoff(self):
        schema = Haarparameter.schema()
        self.assertEqual(
            {k for k in schema if k.startswith('farbe.haar.')},
            {'farbe.haar.r', 'farbe.haar.g', 'farbe.haar.b'},
        )
        self.assertEqual(schema['farbe.haar.g']['start'], 0.22)

    def test_unterschiede_nennen_nur_merkliche_aenderungen(self):
        alt = Haarparameter.start()
        neu = dict(alt, **{'locke.laenge': alt['locke.laenge'] + 0.05, 'straehnen.an': 0})
        self.assertEqual(set(Haarparameter.unterschiede(alt, neu)), {'locke.laenge', 'straehnen.an'})
        self.assertEqual(
            Haarparameter.unterschiede(alt, dict(alt, **{'locke.weite': alt['locke.weite'] + 1e-9})), {}
        )

    def test_ohne_einen_einzigen_eintrag_ist_das_schema_leer_und_pruefen_gibt_ein_leeres_woerterbuch(self):
        with (
            mock.patch.object(Haarparameter, 'masse', classmethod(lambda cls: [])),
            mock.patch.object(Haarparameter, 'schalter', classmethod(lambda cls: [])),
            mock.patch.object(Haarparameter, 'FARBEN', {}),
        ):
            self.assertEqual(Haarparameter.schema(), {})
            self.assertEqual(Haarparameter.pruefen({'a': 1}), {})


class IterationsoptimiererTest(MitSchema):
    def test_dieselbe_runde_schlaegt_dieselben_kandidaten_vor(self):
        start = Haarparameter.start()
        a = Iterationsoptimierer('2026.09.30.10.00.00').kandidaten(start, 4, 7)
        b = Iterationsoptimierer('2026.09.30.10.00.00').kandidaten(start, 4, 7)
        self.assertEqual(a, b)
        self.assertNotEqual(a, Iterationsoptimierer('2026.09.30.10.00.00').kandidaten(start, 4, 8))

    def test_kandidaten_sind_gueltig_und_weichen_ab(self):
        start = Haarparameter.start()
        for k in Iterationsoptimierer('x').kandidaten(start, 8, 1):
            self.assertEqual(k, Haarparameter.pruefen(k))
            self.assertTrue(Haarparameter.unterschiede(start, k), 'mindestens ein Wert geändert')

    def test_der_optimierer_schaltet_keine_teile_und_laesst_ausgeschaltete_in_ruhe(self):
        # Erfahrung aus BlenderModel: Er schaltete einen Teil ab und „gewann" 14 % — Teile an/aus ist Sache der Prüf-KI.
        start = dict(Haarparameter.start(), **{'straehnen.an': 0})
        for runde in range(1, 40):
            for k in Iterationsoptimierer('x').kandidaten(start, 4, runde):
                self.assertEqual(k['straehnen.an'], 0)
                self.assertEqual(k['straehnen.dicke'], start['straehnen.dicke'], 'die Strähnen sind aus')
        # Ein Maß eines Teils mit Schalter (`<teil>.an`) ist nur veränderlich, solange der Teil an ist:
        self.assertNotIn('straehnen.dicke', Iterationsoptimierer.veraenderlich(start))
        self.assertIn(
            'straehnen.dicke', Iterationsoptimierer.veraenderlich(dict(start, **{'straehnen.an': 1}))
        )
        self.assertIn('locke.weite', Iterationsoptimierer.veraenderlich(start))

    def test_farben_wuerfelt_der_optimierer_nicht(self):
        start = Haarparameter.start()
        self.assertFalse([k for k in Iterationsoptimierer.veraenderlich(start) if k.startswith('farbe.')])
        for runde in range(1, 20):
            for k in Iterationsoptimierer('x').kandidaten(start, 4, runde):
                self.assertEqual(
                    {f: v for f, v in k.items() if f.startswith('farbe.')},
                    {f: v for f, v in start.items() if f.startswith('farbe.')},
                )

    def test_schritt_waechst_bei_erfolg_und_schrumpft_sonst_in_grenzen(self):
        o = Iterationsoptimierer('x')
        self.assertGreater(o.anpassen(True), Iterationsoptimierer.SCHRITT_START)
        for _ in range(200):
            o.anpassen(False)
        self.assertEqual(o.schritt, Iterationsoptimierer.SCHRITT_MIN)


class IterationsnoteTest(SimpleTestCase):
    @staticmethod
    def bild(maske, farbe=(0.2, 0.3, 0.6)):
        f = np.zeros(maske.shape + (3,), np.float32)
        f[:] = farbe
        return Iterationsbild(f, maske)

    def test_gleiche_bilder_haben_keine_abweichung(self):
        m = np.zeros((Iterationsbild.HOEHE, Iterationsbild.BREITE), bool)
        m[20:180, 40:90] = True
        note = Iterationsnote.vergleichen(self.bild(m), self.bild(m))
        self.assertEqual((note['iou'], note['farbe'], note['abweichung']), (1.0, 0.0, 0.0))

    def test_andere_farbe_und_anderer_umriss_kosten(self):
        a = np.zeros((Iterationsbild.HOEHE, Iterationsbild.BREITE), bool)
        a[20:180, 40:90] = True
        b = np.zeros_like(a)
        b[20:180, 40:120] = True
        gleich = Iterationsnote.vergleichen(self.bild(a), self.bild(a))
        breiter = Iterationsnote.vergleichen(self.bild(a), self.bild(b))
        bunter = Iterationsnote.vergleichen(self.bild(a), self.bild(a, (0.8, 0.7, 0.4)))
        self.assertGreater(breiter['abweichung'], gleich['abweichung'])
        self.assertAlmostEqual(breiter['iou'], 50 / 80, places=3)
        self.assertGreater(bunter['farbe'], 0.2)

    def test_gesamt_gewichtet_nach_den_fotos(self):
        n1, n2 = {'abweichung': 0.2, 'iou': 0.9, 'farbe': 0.1}, {'abweichung': 0.6, 'iou': 0.5, 'farbe': 0.1}
        self.assertEqual(Iterationsnote.gesamt([(3.0, n1), (1.0, n2)])['abweichung'], 0.3)

    def test_eine_figur_wird_auf_die_flaeche_normiert_und_ein_leeres_bild_bleibt_leer(self):
        rgb = np.ones((200, 120, 3), np.float32)
        maske = np.zeros((200, 120), bool)
        maske[20:180, 40:80] = True
        bild = Iterationsbild._normieren(rgb, maske)
        zeilen = np.flatnonzero(bild.maske.any(axis=1))
        # Höhe = Figurhöhe: von 3 % Rand oben bis 3 % Rand unten
        anteil = (zeilen[-1] - zeilen[0] + 1) / Iterationsbild.HOEHE
        self.assertAlmostEqual(anteil, 1 - 2 * Iterationsbild.RAND, delta=0.02)
        leer = Iterationsbild._normieren(rgb, np.zeros((200, 120), bool))
        self.assertFalse(leer.maske.any())
        self.assertEqual(leer.maske.shape, (Iterationsbild.HOEHE, Iterationsbild.BREITE))


class IterationsreferenzTest(SimpleTestCase):
    def test_winkel_von_hand_dann_bogenname_dann_rolle(self):
        self.assertEqual(Iterationsreferenz.winkel_von({'original': 'ansicht_1_2.jpg', 'winkel': 42}), 42.0)
        self.assertEqual(Iterationsreferenz.winkel_von({'original': 'ansicht_1_2.jpg'}), -90.0)
        self.assertEqual(Iterationsreferenz.winkel_von({'datei': 'x.png', 'rolle': 'hinten'}), 180.0)
        self.assertIsNone(Iterationsreferenz.winkel_von({'datei': 'x.png', 'rolle': 'auto'}))


class IterationswahlTest(SimpleTestCase):
    def regeln(self, toleranz=2):
        return Iterationswahl(
            {'toleranz': toleranz, 'pruefki': 'qwen3.8:27b', 'pruefki_alle': 5, 'pruefki_stillstand': 3}
        )

    @staticmethod
    def erg(name, abweichung, werte=None):
        return {'name': name, 'note': {'abweichung': abweichung}, 'werte': werte or {}}

    def test_besserer_optimierer_wird_uebernommen(self):
        wahl, art = self.regeln().auswaehlen([self.erg('k0', 0.5), self.erg('k1', 0.4)], 0.45)
        self.assertEqual((wahl['name'], art), ('k1', 'optimierer'))

    def test_nichts_besseres_heisst_nichts_uebernehmen(self):
        self.assertEqual(self.regeln().auswaehlen([self.erg('k0', 0.5)], 0.45), (None, None))

    def test_pruefki_darf_innerhalb_der_toleranz_schlechter_sein(self):
        regeln = self.regeln(toleranz=2)
        wahl, art = regeln.auswaehlen([self.erg('k0', 0.5), self.erg('ki', 0.458)], 0.45)
        self.assertEqual((wahl['name'], art), ('ki', 'ki'))
        self.assertEqual(regeln.auswaehlen([self.erg('k0', 0.5), self.erg('ki', 0.47)], 0.45), (None, None))

    def test_die_toleranz_misst_sich_am_besten_modell_aller_runden(self):
        regeln = self.regeln(toleranz=2)
        # Arbeitsstand 0,50, das Beste aller Runden 0,40: 0,45 wäre gegen den Arbeitsstand erlaubt, gegen das Beste nicht.
        self.assertEqual(
            regeln.auswaehlen([self.erg('k0', 0.6), self.erg('ki', 0.45)], 0.50, 0.40), (None, None)
        )

    def test_pruefki_faellig_alle_n_runden_und_nach_stillstand(self):
        regeln = self.regeln()
        self.assertEqual([regeln.kritik_faellig(i, 0, 9) for i in range(6)], [False] * 4 + [True, False])
        self.assertTrue(regeln.kritik_faellig(1, 3, 3))
        regeln.o['pruefki'] = Iterationsoptionen.AUS
        self.assertFalse(regeln.kritik_faellig(4, 9, 9))

    def test_mischen_setzt_die_aenderungen_der_anderen_gewinner_auf_den_neuen_stand(self):
        with (
            mock.patch.object(Haarparameter, 'masse', classmethod(lambda cls: MASSE)),
            mock.patch.object(Haarparameter, 'schalter', classmethod(lambda cls: [])),
            mock.patch.object(Haarparameter, 'FARBEN', {}),
        ):
            alt = Haarparameter.start()
            a = self.erg('k0', 0.40, dict(alt, **{'locke.weite': 1.5}))
            b = self.erg('k1', 0.42, dict(alt, **{'locke.laenge': 0.2}))
            mix = Iterationswahl.mischen(alt, a, [a, b, self.erg('k2', 0.6, alt)], 0.5)
            self.assertEqual((mix['locke.weite'], mix['locke.laenge']), (1.5, 0.2))
            self.assertIsNone(
                Iterationswahl.mischen(alt, a, [a, self.erg('k2', 0.6, alt)], 0.5), 'kein weiterer Gewinner'
            )

    def test_die_notiz_nennt_zahlen_und_art(self):
        regeln = self.regeln()
        note = {'abweichung': 0.5}
        text = regeln.notiz('optimierer', note, self.erg('k1', 0.4), None)
        self.assertIn('0.5000 → 0.4000', text)
        self.assertIn('-20.0 %', text)
        self.assertIn('übernommen', regeln.notiz('ki', note, self.erg('ki', 0.4), {'begruendung': 'Länge'}))
        self.assertIn(
            'verworfen (Toleranz 2 %)', regeln.notiz('ki_verworfen', note, self.erg('ki', 0.9), None)
        )


class IterationsoptionenTest(SimpleTestCase):
    def test_pruefki_bleibt_ein_gespeichertes_modell_auch_ohne_ollama(self):
        self.assertEqual(
            Iterationsoptionen.pruefen({'pruefki': 'gemma4:26b-a4b-it-qat'})['pruefki'],
            'gemma4:26b-a4b-it-qat',
        )
        self.assertEqual(
            Iterationsoptionen.pruefen({'pruefki': 'rm -rf /'})['pruefki'], Iterationsoptionen.VORGABE_KI
        )
        self.assertEqual(
            Iterationsoptionen.pruefen({'runden': 0})['runden'], 20, 'außerhalb der Grenzen → Vorgabe'
        )

    def test_ohne_ollama_bleibt_die_vorgabe_waehlbar(self):
        with mock.patch('core.dienste.iterationsoptionen.Ollamamodelle.mit_bildern', return_value=[]):
            feld = next(f for f in Iterationsoptionen.katalog()['optionen'] if f['schluessel'] == 'pruefki')
        self.assertEqual([w['wert'] for w in feld['werte']], ['aus', Iterationsoptionen.VORGABE_KI])

    def test_es_gibt_keine_optionen_die_zum_bau_in_blender_gehoerten(self):
        schluessel = {e['schluessel'] for e in Iterationsoptionen.KATALOG}
        self.assertFalse(schluessel & {'textur', 'huelle', 'sichtmodell'})
        self.assertEqual(Iterationsoptionen.vorgaben()['parallel'], 1)


class IterationskreislaufTest(SimpleTestCase):
    def test_die_naechste_runde_zaehlt_auch_die_geloeschten_mit(self):
        # Sonst bekäme eine neue Runde Nummer und Dateinamen einer gelöschten, und die Kurve hätte zwei Punkte für dieselbe.
        k = Iterationskreislauf.__new__(Iterationskreislauf)
        k.job = SimpleNamespace(
            ergebnis={
                'iterationen': [{'runde': 1}, {'runde': 4}],
                'kreislauf': {'verlauf': [[1, 0.5, 0.5], [7, 0.4, 0.4]]},
            }
        )
        self.assertEqual(k._letzte_runde(), 7)
        k.job = SimpleNamespace(ergebnis={})
        self.assertEqual(k._letzte_runde(), 0)


class IterationsrundeTest(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(settings.BASE_DIR) / '_wegwerf' / 'test_iterationsrunde'
        self.ordner.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, self.ordner, True)

    def test_render_wird_auf_die_figur_zugeschnitten(self):
        quelle = self.ordner / 'render.png'
        bild = Image.new('RGBA', (256, 384), (0, 0, 0, 0))
        bild.paste((200, 100, 50, 255), (100, 50, 150, 250))  # Figur: 50 × 200 px
        bild.save(quelle)
        Iterationsrunde.zuschneiden(quelle, self.ordner / 'aus.png')
        with Image.open(self.ordner / 'aus.png') as aus:
            rand = round(200 * Iterationsrunde.RAND)
            self.assertEqual(aus.size, (50 + 2 * rand, 200 + 2 * rand))

    def test_leerer_render_bleibt_unveraendert(self):
        quelle = self.ordner / 'leer.png'
        Image.new('RGBA', (256, 384), (0, 0, 0, 0)).save(quelle)
        Iterationsrunde.zuschneiden(quelle, self.ordner / 'aus.png')
        with Image.open(self.ordner / 'aus.png') as aus:
            self.assertEqual(aus.size, (256, 384))

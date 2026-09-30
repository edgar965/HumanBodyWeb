# -*- coding: utf-8 -*-
"""Bereich „Haar Engine" (30.09.2026) — Optionen, Lauf, Ablage und die Engine-Schnittstelle. Rein rechnend:
keine Datenbank, keine Dateien, keine Grafikkarte. Die Endpunkte samt gemeinsamer Register:
`test_haarengine_endpunkte.py`, die Schleife der Iterationen: `test_iterationen.py`.
"""

import inspect
import re
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from core.daten.haarengineablage import Haarengineablage
from core.dienste.genesishaarengine import Genesishaarengine
from core.dienste.haarenginelauf import Haarenginelauf
from core.dienste.haarengineoptionen import Haarengineoptionen
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.ollamamodelle import Ollamamodelle


class HaarengineoptionenTest(SimpleTestCase):
    def setUp(self):
        # Die Testfiguren stehen in der Daz-Bibliothek, die Prüf-KIs in Ollama — hier geht es
        # nur um die Kataloge.
        for ziel, name, wert in (
            (Meshfiguroptionen, '_referenzen', [('', '—')]),
            (Ollamamodelle, 'mit_bildern', [('qwen3.8:27b', 'qwen3.8:27b (Q4_K_M)')]),
        ):
            patcher = mock.patch.object(ziel, name, return_value=wert)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_katalog_hat_drei_gruppen_und_die_rollen(self):
        katalog = Haarengineoptionen.katalog()
        self.assertEqual(set(katalog), {'figur', 'iterationen', 'film', 'rollen'})
        figur = [f['schluessel'] for f in katalog['figur']['optionen']]
        self.assertEqual(sorted(figur), ['basis', 'modell'])
        iterationen = {f['schluessel']: f for f in katalog['iterationen']['optionen']}
        self.assertIn('qwen3.8:27b', [w['wert'] for w in iterationen['pruefki']['werte']])
        self.assertIn('aus', [w['wert'] for w in iterationen['pruefki']['werte']])
        self.assertIn('vorne', [r['wert'] for r in katalog['rollen']])

    def test_die_gruppe_film_kennt_keine_blender_einstellung(self):
        felder = [f['schluessel'] for f in Haarengineoptionen.katalog()['film']['optionen']]
        self.assertEqual(sorted(felder), ['bilder', 'breite', 'bvh', 'hoehe'])

    def test_das_modell_wird_nicht_ungefragt_in_die_bibliothek_geschrieben(self):
        katalog = Haarengineoptionen.katalog()
        modell = next(f for f in katalog['figur']['optionen'] if f['schluessel'] == 'modell')
        self.assertEqual(modell['vorgabe'], 'aus')
        self.assertEqual(Haarengineoptionen.pruefen({})['figur']['modell'], 'aus')
        self.assertEqual(Haarengineoptionen.pruefen({'figur': {'modell': 'an'}})['figur']['modell'], 'an')

    def test_fremde_gruppen_und_kaputte_werte_fallen_weg(self):
        optionen = Haarengineoptionen.pruefen(
            {'netz': {'formmodell': 'trellis2'}, 'figur': 'kein dict', 'x': 1}
        )
        self.assertEqual(set(optionen), {'figur', 'iterationen', 'film'})
        self.assertEqual(optionen['figur']['basis'], 'feminine')
        self.assertEqual(Haarengineoptionen.pruefen(None), Haarengineoptionen.pruefen({}))

    def test_mischen_aendert_nur_die_geschickte_gruppe(self):
        alt = Haarengineoptionen.pruefen({'iterationen': {'runden': 55}, 'figur': {'basis': 'masculine'}})
        neu = Haarengineoptionen.mischen(alt, {'iterationen': {'pruefki': 'aus'}})
        self.assertEqual((neu['iterationen']['runden'], neu['iterationen']['pruefki']), (55, 'aus'))
        self.assertEqual(neu['figur']['basis'], 'masculine')


class HaarenginelaufTest(SimpleTestCase):
    def test_jeder_schritt_hat_sein_band_und_die_baender_schliessen_lueckenlos_an(self):
        self.assertEqual(set(Haarenginelauf.BAENDER), set(Haarenginelauf.SCHRITTE))
        ende = 0
        for name in Haarenginelauf.SCHRITTE:
            von, bis = Haarenginelauf.BAENDER[name]
            self.assertEqual(von, ende, 'Lücke oder Überlappung vor „%s"' % name)
            self.assertGreater(bis, von, name)
            ende = bis
        self.assertEqual(ende, 100)

    def test_jeder_schritt_steht_in_der_schrittfolge(self):
        # Die Folge baut Lambdas mit späten Importen der schweren Schrittklassen — hier nur der Quelltext.
        quelle = inspect.getsource(Haarenginelauf.schrittfolge)
        for name in Haarenginelauf.SCHRITTE:
            self.assertIn("'%s':" % name, quelle, 'Schritt „%s" fehlt in schrittfolge()' % name)

    def test_die_grundfigur_kommt_zuerst_und_es_gibt_kein_netz_aus_fotos(self):
        self.assertEqual(Haarenginelauf.SCHRITTE[0], 'grundfigur')
        self.assertNotIn('netz', Haarenginelauf.SCHRITTE)
        quelle = inspect.getsource(Haarenginelauf.schrittfolge).lower()
        for verboten in ('_run_mesh', 'trellis', 'hunyuan', 'blender'):
            self.assertNotIn(verboten, quelle, verboten)

    def test_weiter_iterieren_rechnet_nur_den_schritt_der_iterationen(self):
        # Der Reiter „Iterationen" schickt ab = bis = „iterationen" (`haarengineiterationen.js`).
        self.assertIn('iterationen', Haarenginelauf.SCHRITTE)


class HaarengineablageTest(SimpleTestCase):
    def test_lesbar_sind_fotos_vorlage_ergebnis_und_runden_nicht_die_arbeit(self):
        ablage = Haarengineablage('2026.09.30.00.00.00')
        for ordner in ('eingang', 'vorlage', 'ergebnis', 'iterationen'):
            self.assertTrue(str(ablage.datei(ordner, 'x.png')).endswith('x.png'), ordner)
        for ordner, name in (
            ('arbeit', 'auftrag.json'),
            ('vorbereitet', 'x.png'),
            ('netz', 'x.png'),
            ('vorlage', '../a'),
            ('ergebnis', '..'),
            ('eingang', 'a/b.png'),
        ):
            with self.assertRaises(ValueError, msg='%s/%s' % (ordner, name)):
                ablage.datei(ordner, name)

    def test_der_ordner_heisst_wie_der_bereich(self):
        ablage = Haarengineablage('2026.09.30.00.00.00')
        self.assertEqual(ablage.ordner().parent.name, 'haarengineauftraege')


class GenesishaarengineTest(SimpleTestCase):
    """Die Engine seit dem 30.09.2026: `rendern` ist gebaut, `film` nicht. Mit Attrappen statt Bau und
    Renderer — die echten brauchen die Daz-Bibliothek und einen GPU-Kontext."""

    def engine(self):
        return Genesishaarengine(
            SimpleNamespace(job=SimpleNamespace(kennung='2026.09.30.00.00.00',
                                                ergebnis={'regler': {'stellung': {}}})),
            parallel=2,
        )

    def _attrappen(self):
        """(Bau-Klasse, Render-Klasse) — gepatcht in den Modulen, aus denen `rendern` sie holt."""
        bau = mock.patch('core.dienste.genesishaarbau.Genesishaarbau')
        render = mock.patch('core.dienste.genesishaarrender.Genesishaarrender')
        formung = mock.patch('Genesis9.formung.G9formung')
        for p in (bau, render, formung):
            self.addCleanup(p.stop)
        b, r = bau.start(), render.start()
        formung.start()
        b.return_value.punkte.return_value = ('kin_hair', object())
        b.return_value.farbe.return_value = '#332019'
        return b, r

    def test_rendern_liefert_je_kandidat_ein_bild_je_winkel(self):
        bau, _render = self._attrappen()
        bericht = self.engine().rendern(
            Path('koerper.glb'), Path('aus'), [('k0', {}), ('k1', {})], [0.0, -35.0])
        self.assertEqual(sorted(bericht['kandidaten']), ['k0', 'k1'])
        self.assertEqual(sorted(bericht['kandidaten']['k0']['bilder']), ['-35', '0'])
        self.assertEqual(bericht['kandidaten']['k0']['bilder']['0'], 'ansicht_+000.png')
        self.assertEqual(bericht['kandidaten']['k0']['teile'], {'kin_hair': 1})
        self.assertIsInstance(bericht['sekunden'], float)
        self.assertEqual(bau.return_value.punkte.call_count, 2)

    def test_bau_und_renderer_leben_ueber_den_ganzen_lauf(self):
        """Gemessen am 30.09.2026: je Aufruf neu angelegt kostete jede Runde 20,7 s (der Deltavorrat
        entsteht neu), am Engine-Objekt gehalten nur noch 1,7 s. Ein Rückfall wäre nicht zu sehen —
        nur zu spüren."""
        bau, render = self._attrappen()
        engine = self.engine()
        engine.rendern(Path('koerper.glb'), Path('aus'), [('k0', {})], [0.0])
        engine.rendern(Path('koerper.glb'), Path('aus'), [('k1', {})], [0.0])
        self.assertEqual(bau.call_count, 1, 'der Deltavorrat wird EINMAL gefüllt')
        self.assertEqual(render.call_count, 1, 'der GPU-Kontext entsteht EINMAL')

    def test_schliessen_gibt_den_renderer_frei_und_wirft_nie(self):
        _bau, render = self._attrappen()
        engine = self.engine()
        engine.schliessen()                       # nichts gebaut — wirft nicht
        engine.rendern(Path('koerper.glb'), Path('aus'), [('k0', {})], [0.0])
        engine.schliessen()
        render.return_value.schliessen.assert_called_once()
        engine.schliessen()                       # zweimal schließen wirft auch nicht

    def test_der_film_ist_noch_nicht_gebaut_und_sagt_es(self):
        with self.assertRaises(Genesishaarengine.NichtAngebunden) as gefangen:
            self.engine().film('figur.glb', 'bewegung.json', 'aus', 10, 64, 64)
        self.assertIn('Film', str(gefangen.exception))

    def test_die_meldung_ist_kein_runtimeerror(self):
        # Die Schleife fängt `RuntimeError` an mehreren Stellen ab, um weiterzurechnen (ein
        # gescheitertes Modell einer Runde, ein gescheiterter Arbeiter) — das hier soll den
        # Lauf beenden.
        self.assertFalse(issubclass(Genesishaarengine.NichtAngebunden, RuntimeError))


class KeinBlenderImBereichTest(SimpleTestCase):
    """„Alle Blender-Aufrufe werden durch Genesis Haar Engine ersetzt" (Edgar, 30.09.2026): Im Bereich ruft
    nichts Blender."""

    MUSTER = re.compile(r'BLENDER_EXE|\bimport bpy\b|blender\.exe|effekte/blender|--factory-startup')

    def test_kein_code_des_bereichs_startet_blender(self):
        dienste = Path(settings.BASE_DIR) / 'core' / 'dienste'
        dateien = [
            *dienste.glob('haarengine*.py'),
            *dienste.glob('iterations*.py'),
            dienste / 'genesishaarengine.py',
            dienste / 'haarparameter.py',
            *(Path(settings.BASE_DIR) / 'core' / 'api').glob('haarengine*.py'),
        ]
        self.assertGreater(len(dateien), 20, 'die Dateien des Bereichs wurden gefunden')
        for datei in dateien:
            treffer = self.MUSTER.search(datei.read_text(encoding='utf-8'))
            self.assertIsNone(treffer, '%s ruft Blender: %s' % (datei.name, treffer and treffer.group(0)))

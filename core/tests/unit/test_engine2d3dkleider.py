# -*- coding: utf-8 -*-
"""Bereich „2D3D Kleider" (30.09.2026) — Optionen, Lauf, Ablage und die Engine-Schnittstelle. Rein rechnend:
keine Datenbank, keine Dateien, keine Grafikkarte. Die Endpunkte samt gemeinsamer Register:
`test_engine2d3dkleider_endpunkte.py`, die Schleife der Iterationen: `test_iterationen.py`.
"""

import inspect
import re
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from core.dienste.genesisengine2d3dkleider import Genesisengine2d3dkleider
from core.dienste.meshfiguroptionen import Meshfiguroptionen
from core.dienste.ollamamodelle import Ollamamodelle


class Engine2d3dKleideroptionenTest(SimpleTestCase):
    RENDER = ('rendermimik', 'renderhaut', 'renderlicht', 'renderqualitaet', 'renderphysik')

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

    def test_katalog_hat_sieben_gruppen_und_die_rollen(self):
        katalog = Engine2d3dKleideroptionen.katalog()
        # Seit dem 30.09.2026 abends fünf Gruppen: Netz (TRELLIS) und Körper kamen mit „2D3D Kleider" dazu; seit dem
        # 02.10.2026 die sechste, `mesh` (die Regler von TRELLIS.2, `test_engine2d3dkleider_meshoptionen.py`); seit dem
        # 03.10.2026 die siebte, `vorbereitung` (Körper senkrecht stellen, `test_engine2d3dkleider_vorbereitung.py`).
        # Seit dem 04.10.2026 die achte, `segmentierung` (Sapiens, optional, `test_engine2d3dkleider_segmentierung.py`).
        # Dazu fünf Gruppen der Rendereinstellungen (`rendermimik`, `renderhaut`, `renderlicht`, `renderqualitaet`, `renderphysik`; Mitsuba-Render der Runden).
        self.assertEqual(set(katalog), {'figur', 'vorbereitung', 'netz', 'mesh', 'segmentierung', 'koerper', 'iterationen', 'film', 'rollen', *self.RENDER})
        figur = [f['schluessel'] for f in katalog['figur']['optionen']]
        self.assertLessEqual({'basis', 'modell'}, set(figur))            # die Gruppe hat inzwischen mehr Felder (Frisur, Textur, Kleidung, Runden …)
        iterationen = {f['schluessel']: f for f in katalog['iterationen']['optionen']}
        self.assertIn('qwen3.8:27b', [w['wert'] for w in iterationen['pruefki']['werte']])
        self.assertIn('aus', [w['wert'] for w in iterationen['pruefki']['werte']])
        self.assertIn('vorne', [r['wert'] for r in katalog['rollen']])

    def test_die_gruppe_film_kennt_keine_blender_einstellung(self):
        felder = [f['schluessel'] for f in Engine2d3dKleideroptionen.katalog()['film']['optionen']]
        self.assertEqual(sorted(felder), ['bilder', 'breite', 'bvh', 'hoehe', 'ton'])           # `ton`: die Tonspur des Films (Studioton)

    def test_das_modell_wird_nicht_ungefragt_in_die_bibliothek_geschrieben(self):
        katalog = Engine2d3dKleideroptionen.katalog()
        modell = next(f for f in katalog['figur']['optionen'] if f['schluessel'] == 'modell')
        self.assertEqual(modell['vorgabe'], 'aus')
        self.assertEqual(Engine2d3dKleideroptionen.pruefen({})['figur']['modell'], 'aus')
        self.assertEqual(Engine2d3dKleideroptionen.pruefen({'figur': {'modell': 'an'}})['figur']['modell'], 'an')

    def test_fremde_gruppen_und_kaputte_werte_fallen_weg(self):
        optionen = Engine2d3dKleideroptionen.pruefen(
            {'netz': {'formmodell': 'trellis2'}, 'figur': 'kein dict', 'x': 1}
        )
        self.assertEqual(set(optionen), {'figur', 'vorbereitung', 'netz', 'mesh', 'segmentierung', 'koerper', 'iterationen', 'film', *self.RENDER})
        self.assertEqual(optionen['netz']['formmodell'], 'trellis2')
        self.assertEqual(optionen['figur']['basis'], 'feminine')
        self.assertEqual(Engine2d3dKleideroptionen.pruefen(None), Engine2d3dKleideroptionen.pruefen({}))

    def test_mischen_aendert_nur_die_geschickte_gruppe(self):
        alt = Engine2d3dKleideroptionen.pruefen({'iterationen': {'runden': 55}, 'figur': {'basis': 'masculine'}})
        neu = Engine2d3dKleideroptionen.mischen(alt, {'iterationen': {'pruefki': 'aus'}})
        self.assertEqual((neu['iterationen']['runden'], neu['iterationen']['pruefki']), (55, 'aus'))
        self.assertEqual(neu['figur']['basis'], 'masculine')


class Engine2d3dKleiderlaufTest(SimpleTestCase):
    def test_jeder_schritt_hat_sein_band_und_die_baender_schliessen_lueckenlos_an(self):
        self.assertEqual(set(Engine2d3dKleiderlauf.BAENDER), set(Engine2d3dKleiderlauf.SCHRITTE))
        ende = 0
        for name in Engine2d3dKleiderlauf.SCHRITTE:
            von, bis = Engine2d3dKleiderlauf.BAENDER[name]
            self.assertEqual(von, ende, 'Lücke oder Überlappung vor „%s"' % name)
            self.assertGreater(bis, von, name)
            ende = bis
        self.assertEqual(ende, 100)

    def test_jeder_schritt_steht_in_der_schrittfolge(self):
        # Die Folge baut Lambdas mit späten Importen der schweren Schrittklassen — hier nur der Quelltext.
        quelle = inspect.getsource(Engine2d3dKleiderlauf.schrittfolge)
        for name in Engine2d3dKleiderlauf.SCHRITTE:
            self.assertIn("'%s':" % name, quelle, 'Schritt „%s" fehlt in schrittfolge()' % name)

    def test_die_grundfigur_kommt_zuerst_und_es_gibt_kein_netz_aus_fotos(self):
        # Seit dem 30.09.2026 abends beginnt der Lauf mit dem Netz aus den Fotos (TRELLIS) und dem Körper dazu;
        # die Grundfigur mit Rig folgt darauf (Engine2d3dKleidernetz, Engine2d3dKleiderkoerper).
        # Seit dem 03.10.2026 steht die Vorbereitung der Fotos (Freistellen, Ausrichten, Zuschnitt) als eigener Schritt davor.
        # Seit dem 04.10.2026 steht die optionale Segmentierung (Sapiens) zwischen Netz und Körper.
        self.assertEqual(Engine2d3dKleiderlauf.SCHRITTE[:5], ('vorbereitung', 'netz', 'segmentierung', 'koerper', 'grundfigur'))
        quelle = inspect.getsource(Engine2d3dKleiderlauf.schrittfolge).lower()
        self.assertNotIn('_run_mesh', quelle, 'das Netz rechnet der Runner (Engine2d3dKleidernetz), nicht die Schrittfolge')

    def test_weiter_iterieren_rechnet_nur_den_schritt_der_iterationen(self):
        # Der Reiter „Iterationen" schickt ab = bis = „iterationen" (`engine2d3dkleideriterationen.js`).
        self.assertIn('iterationen', Engine2d3dKleiderlauf.SCHRITTE)


class Engine2d3dKleiderablageTest(SimpleTestCase):
    def test_lesbar_sind_fotos_vorlage_ergebnis_und_runden_nicht_die_arbeit(self):
        ablage = Engine2d3dKleiderablage('2026.09.30.00.00.00')
        for ordner in ('eingang', 'vorlage', 'ergebnis', 'iterationen', 'netz', 'vorbereitet'):
            self.assertTrue(str(ablage.datei(ordner, 'x.png')).endswith('x.png'), ordner)
        for ordner, name in (
            ('arbeit', 'auftrag.json'),
            ('vorlage', '../a'),
            ('ergebnis', '..'),
            ('eingang', 'a/b.png'),
        ):
            with self.assertRaises(ValueError, msg='%s/%s' % (ordner, name)):
                ablage.datei(ordner, name)

    def test_der_ordner_heisst_wie_der_bereich(self):
        ablage = Engine2d3dKleiderablage('2026.09.30.00.00.00')
        self.assertEqual(ablage.ordner().parent.name, 'engine2d3dkleiderauftraege')


class Genesisengine2d3dkleiderTest(SimpleTestCase):
    """Die Engine seit dem 30.09.2026: `rendern` und (seit dem Abend) `film` sind gebaut. Mit Attrappen statt Bau und
    Renderer — die echten brauchen die Daz-Bibliothek und einen GPU-Kontext."""

    def engine(self):
        return Genesisengine2d3dkleider(
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

    def test_der_film_baut_das_modell_der_iterationen_und_tanzt(self):
        """Seit dem 30.09.2026 abends (`Kleidertanz`): der Film häutet Körper, Kleider und Haar des Modells aus
        `kreislauf.modell` über die Bewegung — gebaut aus der Stellung des Auftrags, nicht aus der GLB."""
        bau = mock.patch('core.dienste.kleidermodellbau.Kleidermodellbau')
        tanz = mock.patch('core.dienste.kleidertanz.Kleidertanz')
        for p in (bau, tanz):
            self.addCleanup(p.stop)
        bau_k, tanz_k = bau.start(), tanz.start()
        bau_k.return_value.teile.return_value = ['koerper', 'shirt']
        bau_k.return_value.stellung = {'FBMHeavy': 0.5}            # der Tanz bekommt die Stellung des Baus (samt Reglern des Modells), nicht die des Auftrags
        tanz_k.return_value.film.return_value = {'video': 'film.mp4', 'bilder': 10}
        job = SimpleNamespace(kennung='2026.09.30.00.00.00', stellung=lambda: {'FBMHeavy': 0.5},
                              ergebnis={'kreislauf': {'modell': {'haar': {'sorte.kin_hair': 1.0}}}}, optionen=None)
        bericht = Genesisengine2d3dkleider(SimpleNamespace(job=job, ablage='ablage-attrappe')).film('figur.glb', 'bewegung.json', 'aus', 10, 64, 64)
        self.assertEqual(bericht['bilder'], 10)
        # Der Bau bekommt die Ablage des Auftrags (Klemme und Haarumbau, Option iterationen.haarumbau, Vorgabe Herrenhaar) und die Regler des Modells.
        bau_k.assert_called_once_with({'FBMHeavy': 0.5}, koerper=mock.ANY, ablage='ablage-attrappe', haarumbau='herren')
        modell = bau_k.return_value.teile.call_args[0][0]
        self.assertEqual(modell.haar, {'sorte.kin_hair': 1.0})
        tanz_k.assert_called_once_with({'FBMHeavy': 0.5}, ['koerper', 'shirt'])
        tanz_k.return_value.film.assert_called_once()

    def test_die_meldung_ist_kein_runtimeerror(self):
        # Die Schleife fängt `RuntimeError` an mehreren Stellen ab, um weiterzurechnen (ein
        # gescheitertes Modell einer Runde, ein gescheiterter Arbeiter) — das hier soll den
        # Lauf beenden.
        self.assertFalse(issubclass(Genesisengine2d3dkleider.NichtAngebunden, RuntimeError))


class BlenderNurUeberEinenArbeiterTest(SimpleTestCase):
    """Blender-Aufrufe sind im Bereich erlaubt (Edgar, 30.09.2026, nachts: „blender aufrufe sind möglich") — bis
    dahin hielt `KeinBlenderImBereichTest` den Bereich Blender-frei. Was bleibt: Blender wird nicht in Diensten
    und Ansichten verstreut gestartet, sondern über EINE Arbeiterklasse (wie `Kostuemblender`/`Kostuemarbeiter`
    in BlenderModel). Solange es keine gibt, darf kein Modul des Bereichs `blender.exe` oder `BLENDER_EXE` direkt
    anfassen; sobald eine da ist, steht sie in `ARBEITER` und darf es allein."""

    MUSTER = re.compile(r'BLENDER_EXE|blender\.exe|--factory-startup')
    ARBEITER = ('engine2d3dkleiderblender.py',)

    def test_blender_startet_nur_der_arbeiter_des_bereichs(self):
        dienste = Path(settings.BASE_DIR) / 'core' / 'dienste'
        dateien = [
            *dienste.glob('engine2d3dkleider*.py'),
            *dienste.glob('iterations*.py'),
            dienste / 'genesisengine2d3dkleider.py',
            dienste / 'haarparameter.py',
            *(Path(settings.BASE_DIR) / 'core' / 'api').glob('engine2d3dkleider*.py'),
        ]
        self.assertGreater(len(dateien), 20, 'die Dateien des Bereichs wurden gefunden')
        for datei in dateien:
            if datei.name in self.ARBEITER:
                continue
            treffer = self.MUSTER.search(datei.read_text(encoding='utf-8'))
            self.assertIsNone(treffer, '%s startet Blender selbst statt über den Arbeiter: %s'
                              % (datei.name, treffer and treffer.group(0)))

# -*- coding: utf-8 -*-
"""Exportleiste mit dem eigenen Modell des Bereichs (`Exportleistequelle.EIGENES_MODELL`, 31.10.2026: 2D3D Kleider auf die Exportleiste umgestellt).

1. Render: Die Leiste rendert das Modell des Bereichs unverändert — kein Neubau aus einer Seiten-GLB (`Exportleisterendermodell` hätte Stoff `kleidung__gc_` und Strähnen `haar__`
   in starre `kleidung__eigen_…` umbenannt), keine Kopie (Mimik und Gelenkkorrektur lesen die Stellung dann aus der Datenbank wie bisher).
2. „Neu rendern": abgelegte Läufe mit ihren Einstellungen (und ihrer BVH), der erste startet, der Rest wartet in der Warteschlange.
3. Die GLB einer Seite heißt `seite_<Fingerabdruck>.glb`; ihr Aufräumen lässt `modell_animiert.*` im selben `ergebnis/` stehen (bei 2D3D Kleider ist das der Ordner des Auftrags).
4. Export: Modell und Bewegung vom Bereich, ohne Hautmaske. Regler: ohne eigene Datei die Werte des Bereichs.
5. `Engine2d3dKleiderexportquelle`: Render-Ordner = der von `Engine2d3dKleiderrender` (alte Läufe, Rezept und Videos bleiben), Vorgaben aus den Optionen „Film" und `render…`.

Kunstdateien unter `ProjektTemp/pruefungen` (`Pruefablage`); kein Prozess wird gestartet (`Auftragsarbeiter._popen` ist eine Attrappe), keine Datenbank.
Sabotage-Gegenprobe (31.10.2026): in `Exportleisterender._glb` den Zweig `EIGENES_MODELL` entfernt → `test_render_nimmt_das_modell_des_bereichs` rot; in `_modell` wieder `glob('modell_*')`
→ `test_aufraeumen_laesst_die_dateien_des_auftrags_stehen` rot.
"""

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from core.dienste.auftragsarbeiter import Auftragsarbeiter
from core.dienste.engine2d3dkleiderexportquelle import Engine2d3dKleiderexportquelle
from core.dienste.engine2d3dkleiderfilmoptionen import Engine2d3dKleiderfilmoptionen
from core.dienste.engine2d3dkleiderrender import Engine2d3dKleiderrender
from core.dienste.engine2d3dkleiderrenderneu import Engine2d3dKleiderrenderneu
from core.dienste.exportleiste import Exportleiste
from core.dienste.exportleistequelle import Exportleistequelle
from core.dienste.exportleisterender import Exportleisterender
from core.dienste.studioton import Studioton

from ._pruefablage import Pruefablage


class _Quelle(Exportleistequelle):
    BEREICH = 'kunst'
    EIGENES_MODELL = True

    def __init__(self, ordner):
        super().__init__('kunst1')
        self.ordner = ordner

    def name(self):
        return 'Kunst'

    def exportordner(self):
        return self.ordner / 'export'

    def arbeitsordner(self):
        return self.ordner / 'auftrag'

    def modell(self):
        return self.ordner / 'auftrag' / 'ergebnis' / 'standmodell.glb'

    def regler_vorgabe(self):
        return {'renderlicht': {'licht.modus': 'sonne'}}


class _Hochgeladen:
    def __init__(self, roh):
        self.roh = roh

    def chunks(self):
        yield self.roh


class ExportleisteEigenesModellTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='exportleiste_eigen_', dir=Pruefablage.wurzel()))
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)
        self.quelle = _Quelle(self.ordner)
        (self.ordner / 'auftrag' / 'ergebnis').mkdir(parents=True)
        self.quelle.modell().write_bytes(b'glTF' + b'\0' * 16)
        self.bvh = self.ordner / 'tanz.bvh'
        self.bvh.write_text('HIERARCHY\nMOTION\nFrames: 90\nFrame Time: 0.0333333\n', encoding='utf-8')
        prozess = mock.patch.object(Auftragsarbeiter, '_popen', staticmethod(lambda befehl, protokoll: SimpleNamespace(pid=4711)))
        prozess.start()
        self.addCleanup(prozess.stop)
        self.render = Exportleisterender(Exportleiste(self.quelle))

    def _angaben(self, **mehr):
        return dict({'sekunden': 1.0, 'kamera': 'zoom_ein', 'groesse': '480x600', 'spp': 16, 'bvh': str(self.bvh), 'ordner': str(self.ordner / 'export')}, **mehr)

    def _auftrag(self):
        return json.loads(self.render._datei('auftrag.json').read_text(encoding='utf-8'))

    def test_render_nimmt_das_modell_des_bereichs(self):
        self.render.starten(None, self._angaben(datei='Kunst Video'))
        auftrag = self._auftrag()
        self.assertEqual(Path(auftrag['glb']), self.quelle.modell())
        self.assertEqual(auftrag['datei'], 'Kunst Video')                 # Ziel des Videos aus dem Render-Block (Edgar 31.10.2026: „wo wird die gerenderte Datei gespeichert?“)
        self.assertEqual(list(self.quelle.modell().parent.glob('seite_*')), [])            # keine Kopie
        self.assertEqual(self.render.figur(Path(auftrag['glb']), {}), self.quelle.modell())   # kein Neubau

    def test_neu_rendern_startet_den_ersten_und_reiht_den_rest_ein(self):
        laeufe = [{'nr': 1, 'sekunden': 0.5, 'kamera': 'gesicht', 'groesse': '480x600', 'spp': 16, 'ton': False},
                  {'nr': 2, 'sekunden': 2.0, 'kamera': 'brust', 'groesse': '960x1200', 'spp': 96, 'ton': False, 'bvh': str(self.bvh), 'anmerkung': 'zwei'}]
        self.render._datei('laeufe.json').write_text(json.dumps(laeufe), encoding='utf-8')
        bericht = self.render.neu(None, {'alle': True, 'bvh': str(self.bvh), 'ordner': str(self.ordner / 'export')})
        erster, rest = self._auftrag(), Engine2d3dKleiderrenderneu(self.render).lesen()
        self.assertEqual((erster['neu_nr'], erster['kamera'], erster['sekunden']), (1, 'gesicht', 0.5))
        self.assertEqual([(a['neu_nr'], a['kamera'], a['breite'], a['anmerkung']) for a in rest], [(2, 'brust', 960, 'zwei')])
        self.assertTrue(all(Path(a['glb']) == self.quelle.modell() for a in [erster] + rest))
        self.assertEqual(bericht['wartend'], 1)
        self.render._datei('render.pid').unlink()                       # die Attrappe hat keinen Prozess — sonst hieße es „läuft schon"
        with self.assertRaisesRegex(ValueError, '#7'):
            self.render.neu(None, {'nummern': [7]})

    def test_aufraeumen_laesst_die_dateien_des_auftrags_stehen(self):
        ergebnis = self.render.ablage.ergebnis()
        for name in ('modell.glb', 'modell_animiert.glb', 'modell_animiert.blend'):
            (ergebnis / name).write_bytes(b'x')
        alt = self.render._modell(_Hochgeladen(b'glTF' + b'a' * 8), {})
        neu = self.render._modell(_Hochgeladen(b'glTF' + b'b' * 8), {})
        self.assertTrue(neu.name.startswith('seite_') and neu.is_file())
        self.assertFalse(alt.exists())
        self.assertEqual(sorted(p.name for p in ergebnis.glob('modell*')), ['modell.glb', 'modell_animiert.blend', 'modell_animiert.glb'])

    def test_export_nimmt_modell_und_bewegung_des_bereichs_ohne_hautmaske(self):
        gelesen = []

        class _Glb:
            def __init__(self, pfad):
                gelesen.append(Path(pfad))

            def schreiben(self, ziel):
                Path(ziel).write_bytes(b'glTF')

        with mock.patch('Genesis9.glbanimation.G9glbanimation', _Glb), \
                mock.patch('core.dienste.exportleiste.Exportleistehautmaske.glb', side_effect=AssertionError('Hautmaske beim eigenen Modell')):
            aus = Exportleiste(self.quelle).exportieren(None, {'format': 'glb', 'ordner': str(self.ordner / 'export'), 'name': 'Kunst'})
        self.assertEqual(gelesen, [self.quelle.modell()])
        self.assertIsNone(aus['hautverdeckung'])
        self.assertEqual([d['name'] for d in aus['dateien']], ['Kunst.glb', 'Kunst_export.json'])

    def test_freie_aufloesung_und_physik_aus(self):
        """MP4-Export und Rendern (31.10.2026): Breite × Höhe frei (gerade, 64–4096), `groesse` alter Läufe gilt weiter; ohne Physik Stoff gehäutet, Strähnen, Bart, Uhr aus, Wind 0."""
        self.render.starten(None, self._angaben(breite=1919, hoehe=1080, physik=False))
        auftrag = self._auftrag()
        self.assertEqual((auftrag['breite'], auftrag['hoehe'], auftrag['physik']), (1918, 1080, False))
        self.assertEqual(Exportleisterender._groesse({'groesse': '1280x720'}), (1280, 720))
        with self.assertRaises(ValueError):
            Exportleisterender._groesse({'breite': 8000, 'hoehe': 1080})
        aus = Exportleisterender.ohne_physik(Exportleiste(self.quelle).optionen())
        self.assertEqual((aus['renderqualitaet']['stoff.modus'], aus['renderphysik']['haar.an'], aus['renderphysik']['wind.staerke']), ('haut', False, 0.0))
        self.assertNotEqual(Exportleiste(self.quelle).optionen()['renderqualitaet']['stoff.modus'], None)        # die Leiste selbst bleibt unverändert

    def test_regler_ohne_eigene_datei_vom_bereich(self):
        leiste = Exportleiste(self.quelle)
        self.assertEqual(leiste.optionen()['renderlicht']['licht.modus'], 'sonne')
        leiste.optionen_speichern({'renderlicht': {'licht.modus': 'studio'}})
        self.assertEqual(leiste.optionen()['renderlicht']['licht.modus'], 'studio')


class Engine2d3dKleiderexportquelleTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='exportleiste_2d3d_', dir=Pruefablage.wurzel()))
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)
        # Ablage in die Prüfablage; Tanz und Studioton ohne Bibliothek und Einstellungen (beide lesen sonst die Pfadwurzeln aus der Datenbank)
        for ziel, attrappe in ((Engine2d3dKleiderablage, ('wurzel', classmethod(lambda cls: self.ordner))),
                               (Engine2d3dKleiderfilmoptionen, ('tanz', classmethod(lambda cls: r'A:\tanz.bvh'))),
                               (Studioton, ('pfad', staticmethod(lambda: '')))):
            umlenken = mock.patch.object(ziel, *attrappe)
            umlenken.start()
            self.addCleanup(umlenken.stop)
        self.job = SimpleNamespace(id='kunst-id', kennung='kunst2d3d', name='Kunst', optionen={'film': {'ton': r'A:\ton.mp3'}, 'renderlicht': {}},
                                   ergebnis={'film': {'bvh': r'A:\alt.bvh'}})
        self.quelle = Engine2d3dKleiderexportquelle(self.job.id, self.job)

    def test_render_ordner_ist_der_des_auftrags(self):
        leiste = Exportleisterender(Exportleiste(self.quelle))
        self.assertEqual(leiste._datei('laeufe.json'), Engine2d3dKleiderrender(self.job)._datei('laeufe.json'))
        self.assertEqual(leiste.ablage.ergebnis(), Engine2d3dKleiderablage(self.job.kennung).ergebnis())
        self.assertTrue(self.quelle.EIGENES_MODELL)

    def test_vorgaben_aus_den_optionen(self):
        self.assertEqual(self.quelle.ton_vorgabe(), r'A:\ton.mp3')
        self.assertEqual(self.quelle.bvh_vorgabe(), r'A:\tanz.bvh')     # Option „Film" (Vorgabe: der Tanz) vor dem letzten Film
        self.assertEqual(sorted(self.quelle.regler_vorgabe()), ['renderhaut', 'renderlicht', 'rendermimik', 'renderphysik', 'renderqualitaet'])

# -*- coding: utf-8 -*-
u"""Kein relativer Import verlässt den Statikstamm.

DER BEFUND (Edgar, 11.09.2026: „GVHMR pipeline starten funktioniert nicht")
=========================================================================
`static/js/auftraege/pipelinevorgaben.js` importierte
`'../../../static/viewer/gemeinsam/protokoll.js'`. Auf der PLATTE stimmt das:
zwei Ebenen hoch ist `static/`, die dritte ist der Projektordner, und darunter
liegt `static/viewer/…`. Deshalb blieb `esmodulimporte` (djangoBase) grün —
es löst relative Importe im Dateisystem auf.

Im BROWSER heißt die Datei seit b2839ae (06.09.2026)
`/statik/v-<fassung>/js/auftraege/pipelinevorgaben.js`. Drei Ebenen hoch ist
`/statik/`, und `/statik/static/viewer/…` gibt es nicht: 404, das Modul lädt
nicht, und mit ihm fällt `pipelinewahl.js` — der Klick auf „Pipeline
starten" tat nichts, kein Alert, kein Eintrag im Serverlog. Fünf Tage lang.

DIE REGEL
=========
Ein relativer Import darf höchstens so viele `../` haben, wie die Datei Ordner
unter `static/` liegt. `js/auftraege/x.js` liegt zwei Ordner tief: `../..`
ist der Statikstamm, `../../..` liegt darüber — und darüber gibt es in der
Fassungsadresse nichts, was der Platte entspricht.
"""
import re
from pathlib import Path

from django.test import SimpleTestCase

STATIK = Path(__file__).resolve().parents[3] / 'static'
AUSGENOMMEN = ('node_modules', 'theatre')   # gebaute Bündel, keine Quellen
IMPORT = re.compile(r"""(?:^|\n)\s*(?:import|export)\b[^'"\n]*?\bfrom\s*['"]([^'"]+)['"]"""
                    r"""|import\(\s*['"]([^'"]+)['"]""")


class Statikimporte:

    @staticmethod
    def dateien():
        for pfad in STATIK.rglob('*.js'):
            if any(teil in AUSGENOMMEN for teil in pfad.relative_to(STATIK).parts):
                continue
            yield pfad

    @staticmethod
    def ziele(quelltext):
        for treffer in IMPORT.finditer(quelltext):
            yield treffer.group(1) or treffer.group(2)

    @staticmethod
    def zu_hoch(pfad, ziel):
        u"""True, wenn `ziel` (relativ zu `pfad`) über `static/` hinausführt."""
        if not ziel.startswith(('./', '../')):
            return False
        tiefe = len(pfad.relative_to(STATIK).parts) - 1
        hoch = 0
        for teil in ziel.split('/'):
            if teil == '..':
                hoch += 1
            elif teil not in ('.', ''):
                break
        return hoch > tiefe

    @classmethod
    def befunde(cls):
        aus = []
        for pfad in cls.dateien():
            for ziel in cls.ziele(pfad.read_text(encoding='utf-8', errors='replace')):
                if cls.zu_hoch(pfad, ziel):
                    aus.append((str(pfad.relative_to(STATIK)), ziel))
        return aus


class KeinImportVerlaesstDenStatikstamm(SimpleTestCase):

    databases = []

    def test_alle_relativen_importe_bleiben_unter_static(self):
        befunde = Statikimporte.befunde()
        self.assertEqual(befunde, [], 'Importe über den Statikstamm hinaus '
                         '(im Browser /statik/v-…/ — dort gibt es darüber nichts):\n'
                         + '\n'.join('  %s  ->  %s' % b for b in befunde))

    def test_es_werden_ueberhaupt_dateien_geprueft(self):
        self.assertGreater(len(list(Statikimporte.dateien())), 200)

    def test_der_fall_von_damals_wird_gemeldet(self):
        pfad = STATIK / 'js' / 'auftraege' / 'pipelinevorgaben.js'
        self.assertTrue(Statikimporte.zu_hoch(
            pfad, '../../../static/viewer/gemeinsam/protokoll.js'))
        self.assertFalse(Statikimporte.zu_hoch(pfad, '../../viewer/gemeinsam/protokoll.js'))
        self.assertFalse(Statikimporte.zu_hoch(pfad, './pipelinefelder.js'))
        self.assertFalse(Statikimporte.zu_hoch(pfad, '/static/djangobase/js/htmltext.js'))

    def test_der_import_ist_auch_wirklich_umgestellt(self):
        text = (STATIK / 'js' / 'auftraege' / 'pipelinevorgaben.js').read_text(encoding='utf-8')
        self.assertIn("from '../../viewer/gemeinsam/protokoll.js'", text)
        self.assertNotIn("../../../static/", text)

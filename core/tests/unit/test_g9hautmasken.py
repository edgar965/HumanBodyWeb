# -*- coding: utf-8 -*-
u"""Die Haut-Maske im dauerhaften Vorrat (`G9hautmasken`) und die Fassung ihres Codes (`Jsquellen`, 19.10.2026).

1. `G9hautmasken`: Fassung und Schlüssel aus der Anfrage werden geprüft (kein Pfad außerhalb der Ablage); nur gzip wird angenommen; abgelegt → gefunden,
   unter einer anderen Fassung nicht; ein zweites Ablegen ändert nichts.
2. Ausdünnen: über der Grenze fällt die am längsten nicht gelesene Maske zuerst, ein leerer Ordner einer alten Fassung mit.
3. `Jsquellen.fassung`: der Baum eines Moduls über relative Importe (statisch, `export … from`, `import()`); eine Änderung an einem importierten Modul ändert die
   Fassung, eine an einem fremden nicht; ein Modul außerhalb der Statik zählt nicht.

Sabotage (von Hand, nicht als Lauf): `FASSUNG`-Muster auf `.*` → Fall 1 rot (`../x`); in `huelle` die gefundenen Importe nicht weiterverfolgen → Fall 3 rot.
Geschrieben, nicht gelaufen.
"""
import gzip
import os
import time
import unittest
from pathlib import Path
from unittest import mock

from core.dienste.g9hautmasken import G9hautmasken
from core.dienste.jsquellen import Jsquellen

from ._pruefablage import Pruefablage


class G9hautmaskenTest(unittest.TestCase):

    FASSUNG = '0123456789abcdef'
    INHALT = gzip.compress(b'HBF1' + b'\0' * 60)

    def test_1_ablegen_und_holen(self):
        with Pruefablage.ordner('hautmasken_') as wurzel, mock.patch.object(G9hautmasken, 'wurzel', return_value=Path(wurzel)):
            self.assertIsNone(G9hautmasken.datei('../x', 'abcdefgh'))
            self.assertIsNone(G9hautmasken.datei(self.FASSUNG, '../../abcdefgh'))
            self.assertFalse(G9hautmasken.ablegen(self.FASSUNG, 'abcdefgh', b'HBF1 nicht gepackt'))
            self.assertIsNone(G9hautmasken.holen(self.FASSUNG, 'abcdefgh'))
            self.assertTrue(G9hautmasken.ablegen(self.FASSUNG, 'abcdefgh', self.INHALT))
            self.assertEqual(G9hautmasken.holen(self.FASSUNG, 'abcdefgh').read_bytes(), self.INHALT)
            self.assertIsNone(G9hautmasken.holen('fedcba9876543210', 'abcdefgh'))
            self.assertTrue(G9hautmasken.ablegen(self.FASSUNG, 'abcdefgh', gzip.compress(b'anders')))
            self.assertEqual(G9hautmasken.holen(self.FASSUNG, 'abcdefgh').read_bytes(), self.INHALT)

    def test_2_ausduennen(self):
        with Pruefablage.ordner('hautmasken_') as wurzel, mock.patch.object(G9hautmasken, 'wurzel', return_value=Path(wurzel)), \
                mock.patch.object(G9hautmasken, 'PLATTE_MB', 100 / 1024 / 1024):
            alt = Path(wurzel) / 'fedcba9876543210'
            alt.mkdir()
            (alt / 'aaaaaaaa.bin').write_bytes(b'x' * 60)
            os.utime(alt / 'aaaaaaaa.bin', (time.time() - 3600, time.time() - 3600))
            neu = Path(wurzel) / self.FASSUNG
            neu.mkdir()
            (neu / 'bbbbbbbb.bin').write_bytes(b'y' * 60)
            G9hautmasken.ausduennen(mindestens_s=0)
            self.assertFalse(alt.exists())
            self.assertTrue((neu / 'bbbbbbbb.bin').is_file())


class JsquellenTest(unittest.TestCase):

    def test_3_baum_und_fassung(self):
        with Pruefablage.ordner('jsquellen_') as wurzel:
            statik = Path(wurzel) / 'static'
            (statik / 'a').mkdir(parents=True)
            (statik / 'a' / 'start.js').write_text("import { B } from './b.js';\nexport { C } from '../c.js';\nconst d = () => import('./d.js');\n", encoding='utf-8')
            (statik / 'a' / 'b.js').write_text("import {\n  E,\n} from './e.js';\n", encoding='utf-8')
            for name in ('c.js', 'a/d.js', 'a/e.js', 'a/fremd.js'):
                (statik / name).write_text('// %s\n' % name, encoding='utf-8')
            (Path(wurzel) / 'draussen.js').write_text('//\n', encoding='utf-8')
            (statik / 'a' / 'e.js').write_text("import { X } from '../../draussen.js';\n", encoding='utf-8')
            with mock.patch.object(Jsquellen, 'statik', return_value=statik), mock.patch.object(Jsquellen, 'FRISCHE_S', 0):
                Jsquellen.vergessen()
                namen = sorted(p.relative_to(statik.resolve()).as_posix() for p in Jsquellen.huelle('a/start.js'))
                self.assertEqual(namen, ['a/b.js', 'a/d.js', 'a/e.js', 'a/start.js', 'c.js'])
                eins = Jsquellen.fassung('a/start.js')
                self.assertEqual(len(eins), Jsquellen.LAENGE)
                (statik / 'a' / 'fremd.js').write_text('// geändert\n', encoding='utf-8')
                self.assertEqual(Jsquellen.fassung('a/start.js'), eins)
                (statik / 'a' / 'd.js').write_text('// geändert\n', encoding='utf-8')
                os.utime(statik / 'a' / 'd.js', (time.time() + 5, time.time() + 5))
                self.assertNotEqual(Jsquellen.fassung('a/start.js'), eins)
                self.assertEqual(Jsquellen.fassung('a/fehlt.js'), '')
                Jsquellen.vergessen()

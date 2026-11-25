"""Code-Stempel der Teile-Ablage (`G9teileablage._bau_module`, 17.11.2026): nur der Code des Teilebaus zählt, nicht jede Datei in `Genesis9/`. Kunstordner unter `ProjektTemp/`,
wird gelöscht. Nur auf Ansage laufen lassen (`testsuite-nur-auf-ansage`).

  test_1 Wurzel mit allen Importen (auch in Funktionen), darunter nur die auf Modulebene: `a` (Funktion in der Wurzel), `b` (Modulebene), `c` (Modulebene in `a`) zählen,
         `d` (in einer Funktion von `a`) und `material` (nirgends) nicht; ein Ring `c` ↔ `b` endet
  test_2 echter Ordner: der Teilebau (folger, strang, stueckknoepfe) zählt, Material/Glanz/Bump nicht
  test_3 mitgeschrieben (`_bauen_mit_spur`): ein im Bau gelaufenes Modul außerhalb des Abschlusses zählt
Sabotage: `oben` = `alle` → test_1 rot (`d` zählt mit); `alle.findall(wurzel)` weg → test_1 rot (`a` fehlt).
"""
import os
import shutil
import sys
import unittest
from pathlib import Path

for _pfad in (r'A:\3DTools',):
    if _pfad not in sys.path:
        sys.path.append(_pfad)


class TeileablageStempelTest(unittest.TestCase):
    databases = []

    def test_1_kunstordner(self):
        from Genesis9.teileablage import G9teileablage
        ordner = Path(r'A:\3DTools\ProjektTemp') / ('_test_teileablage_%d' % os.getpid())
        try:
            ordner.mkdir(parents=True)
            dateien = {'garderobeteile': 'from .b import B\n\ndef bauen():\n    from .a import A\n',
                       'a': 'from .c import C\n\ndef f():\n    from .d import D\n',
                       'b': 'from Genesis9.c import C\n', 'c': 'from .b import B\n', 'd': '', 'material': ''}
            for name, text in dateien.items():
                (ordner / ('%s.py' % name)).write_text(text, encoding='utf-8')
            self.assertEqual(G9teileablage._bau_module(ordner), ['a', 'b', 'c', 'garderobeteile'])
        finally:
            shutil.rmtree(ordner, ignore_errors=True)

    def test_3_spur(self):
        """`_bauen_mit_spur`: ein Modul, dessen Code im Bau läuft (`kanalnamen`, nicht im statischen Abschluss), steht in der Liste; ohne Aufruf nicht. Sabotage:
        in `G9codespur._beginn` `menge.add(datei)` weg → `kanalnamen` fehlt."""
        from Genesis9.teileablage import G9teileablage
        self.assertNotIn('kanalnamen', G9teileablage._bau_module())

        def bauen():
            from Genesis9.kanalnamen import G9kanalnamen
            G9kanalnamen({'a': {'name': 'A', 'sichtbar': True}, 'b': {'name': 'B', 'alias': True}})    # wie `G9morphablage.kanaele`: Kennung → Kanal
            return []
        teile, module = G9teileablage._bauen_mit_spur(bauen)
        self.assertEqual(teile, [])
        self.assertIn('kanalnamen', module)
        self.assertNotIn('kanalnamen', G9teileablage._bauen_mit_spur(lambda: [])[1])

    def test_2_genesis9(self):
        from Genesis9.teileablage import G9teileablage
        m = set(G9teileablage._bau_module())
        self.assertTrue({'garderobeteile', 'folger', 'strang', 'stueckknoepfe', 'teileablage'} <= m, sorted(m))
        self.assertFalse({x for x in m if x.startswith('material') or x in ('materialglanz', 'bumpnormalen', 'browserbilder')}, sorted(m))


if __name__ == '__main__':
    unittest.main()

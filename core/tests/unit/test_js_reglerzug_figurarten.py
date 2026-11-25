# -*- coding: utf-8 -*-
"""Reglerzug an HumanBody, UMA Python und SMPL-X (25.11.2026, Edgar: „alle regler unter 0,2 s“) — die Zusagen am Quelltext (die Module hängen an `three`, der Node-Harness löst das nicht auf).

1. `umformen` (UMA Python, SMPL-X): geteilte Puffer verlassen die alte Geometrie, BEVOR sie frei wird; das neue Netz trägt das stehende Material, Materialien werden nicht entsorgt —
   sonst lüde jeder Zug die Texturen neu (gemessen 1,4–1,8 s Stillstand).
2. Ein Zug zur Zeit, der letzte Wert gewinnt (`Smplformzug`, `Figurneuladen`), die Sanduhr läuft, bis der letzte Wert zu sehen ist.
3. Die stehenden Gewichte gelten nur bei denselben Knochen in derselben Reihe; sonst kein `umformen`.
4. Trägt eine SMPL-X-Figur Stücke, baut sie neu wie bisher.

Sabotage-Gegenprobe (nicht gefahren): `deleteAttribute` nach `dispose` setzen → Fall 1 rot; `'nochmal'` streichen → Fall 2 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static' / 'viewer').joinpath(*teile).read_text(encoding='utf-8')


class ReglerzugFigurartenTest(SimpleTestCase):
    databases = set()

    def test_1_umformen_teilt_statt_zu_entsorgen(self):
        for datei in ('umapythonnetz.js', 'smplnetz.js'):
            text = quelltext('gemeinsam', datei)
            rumpf = re.search(r'static umformen\(.*?\n    \}\n', text, re.S)
            self.assertIsNotNone(rumpf, datei)
            rumpf = rumpf.group(0)
            self.assertLess(rumpf.index('von.deleteAttribute(name)'), rumpf.index('von.dispose()'), datei)
            self.assertLess(rumpf.index('von.setIndex(null)'), rumpf.index('von.dispose()'), datei)
            self.assertIn('new THREE.SkinnedMesh(geo, alt.material)', rumpf, datei)
            self.assertNotIn('Netzentsorgung', rumpf, datei)
            self.assertNotIn('material.dispose', rumpf, datei)
        # Der Stoffschwung stellt `count` einer laufenden Gruppe auf 0 — die unveränderten Gruppen stehen daneben.
        self.assertIn('geo.userData.gruppen = geo.groups.map(g => ({ ...g }));', quelltext('gemeinsam', 'umapythonnetz.js'))

    def test_2_der_letzte_wert_gewinnt(self):
        zug = quelltext('gemeinsam', 'smplformzug.js')
        self.assertRegex(zug, r"if \(Smplformzug\._laeuft\.has\(inst\)\) \{\s*Smplformzug\._laeuft\.set\(inst, 'nochmal'\);\s*return false;")
        self.assertIn("} while (Smplformzug._laeuft.get(inst) === 'nochmal');", zug)
        neu = quelltext('charakter', 'figurneuladen.js')
        self.assertIn('if (Figurneuladen._laeuft) return;', neu)
        self.assertIn('for (let figur = Figurneuladen._figur; figur; figur = Figurneuladen._figur) {', neu)
        self.assertLess(neu.index("Sanduhr.an('Figur wird neu gerechnet …')"), neu.index('setTimeout(() => Figurneuladen._laufen(nachher), 0)'))
        self.assertIn('Figurneuladen.planen(inst, updateEquippedList);', quelltext('charakter', 'properties.js'))

    def test_3_nur_bei_denselben_knochen(self):
        for datei, aufruf in (('umapythonmodell.js', 'if (!this._formPasst(daten)) return this._holen();'),
                              ('smplformzug.js', "throw new Error('Das Skelett der Form passt nicht zur Figur');")):
            text = quelltext('gemeinsam', datei)
            self.assertIn(aufruf, text, datei)
            self.assertLess(text.index(aufruf), text.index('.umformen(inst.group' if datei == 'smplformzug.js' else 'Umapythonnetz.umformen('), datei)

    def test_4_mit_stuecken_neu_bauen(self):
        self.assertIn('!Object.keys(inst.clothMeshes || {}).length', quelltext('gemeinsam', 'smplformzug.js'))
        self.assertIn('if (!Smplformzug.moeglich(inst)) return Smplformregler._neuBauen(', quelltext('charakter', 'smpl', 'smplformregler.js'))

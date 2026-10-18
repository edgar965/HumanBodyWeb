# -*- coding: utf-8 -*-
u"""Bausteine der gemessenen Reglerzuordnung (18.10.2026) — Kunstdaten, keine Daz-Bibliothek, kein Formungslauf.

WARUM: Wohin ein HB-/MH-/SM-/UM-Regler oder ein verborgener Daz-Kanal im Bedienfeld gehört, misst `manage.py genesis9_reglerorte` (Konzept
`Docu/konzepte/2026-10-18_genesis9-regler-vereinfachen-konzept.md`). Die erste Inventur meldete per Kosinus 83 Doppelte — die Stichprobe widerlegte das
(MB Allyne/Olesia: cos 0,993, bis 19,6 mm auseinander). Hier stehen die Regeln, die das verhindern.

Zusagen:

1. `G9reglerregionen.bauen`: je Punkt die Daz-Region mit dem größten Gewicht (jeder Regler verteilt 1 über seine Punkte); `/Neck` ist der Hals;
   Charaktere (`/People`) und Posen zählen nicht; unbewegte Punkte nehmen die Region des nächsten bewegten. `anteile` summiert auf 1.
2. `Reglerortedoppelte.bauen`: Alias nur bei Lage in Millimetern (max|x − c·y| < 0,5 mm) UND gleicher Wirkung an den Stützstellen (x(w) ≈ y(w ×
   faktor)); der Faktor rechnet die Anschläge um; „ähnlich“ (gleiche Richtung, mm auseinander) und ein Kandidat, der nur am Anschlag passt (wächst
   quadratisch), werden NICHT zusammengelegt; Gegenstücke (cos ≤ −0,98, Stärke 0,8 … 1,25) sind Paare.
3. `genesis9seiten.js`: Left↔Right, `_l`↔`_r`, MakeHumans `l-`↔`r-`; ohne Kopplung kein Partner.

Sabotage-Gegenprobe (nicht gefahren): in `bauen` die Normierung je Regler streichen → Fall 1 (breiter Regler überstimmt die Nase) rot; in
`Reglerortedoppelte` `GLEICH_MM` auf 50 → Fall 2 (ähnlich wird Alias) rot; Muster `Left` streichen → Fall 3 rot. Geschrieben, nicht gelaufen.
"""
import numpy as np
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul
from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.morphablage import G9morphablage  # noqa: E402
from Genesis9.reglerregionen import G9reglerregionen  # noqa: E402

from core.dienste.reglerortedoppelte import Reglerortedoppelte  # noqa: E402


def ablage(kanaele, deltas):
    u"""`deltas`: {kennung: [(punkt, (dx, dy, dz)), …]} → eine echte `G9morphablage` mit Kunstdaten."""
    punkt, delta, ab, bis = [], [], {}, {}
    for k in kanaele:
        ab[k] = len(punkt)
        for p, d in deltas.get(k, ()):
            punkt.append(p)
            delta.append(d)
        bis[k] = len(punkt)
    voll = {k: dict({'id': k, 'label': k, 'gruppe': '/Base', 'region': '', 'sichtbar': True, 'alias': '', 'hd': ''}, **v) for k, v in kanaele.items()}
    return G9morphablage(voll, np.asarray(punkt, dtype=np.int32), np.asarray(delta, dtype=np.float32).reshape(-1, 3), ab, bis)


class _Messung:
    u"""Stützstellen: `nichtlinear` liefert bei 50 % ein anderes Feld."""
    def __init__(self, felder, nichtlinear=()):
        self.felder, self.nichtlinear = felder, set(nichtlinear)

    def messen(self, stellung):
        (name, wert), = stellung.items()
        feld = self.felder[name] * wert
        if name in self.nichtlinear:
            feld = feld * wert
        return {'feld': feld.astype(np.float32)}


class ReglerorteTest(SimpleTestCase):
    def test_1_regionenkarte(self):
        a = ablage({'nase': {'region': 'Nose'}, 'breit': {'region': 'Face'}, 'hals': {'gruppe': '/Neck/Base', 'region': 'Head'},
                    'held': {'gruppe': '/People/Held', 'region': 'Head'}, 'pose': {'gruppe': '/Pose Controls/Head', 'region': 'Mouth'}},
                   {'nase': [(0, (0.0, 0.0, 0.01))], 'breit': [(p, (0.0, 0.0, 0.01)) for p in range(4)],
                    'hals': [(3, (0.01, 0.0, 0.0))], 'held': [(p, (0.0, 0.0, 1.0)) for p in range(6)], 'pose': [(1, (0.0, 0.0, 1.0))]})
        basis = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [3.1, 0, 0], [10, 0, 0]], dtype=np.float64)
        region = G9reglerregionen.bauen(a, basis)
        orte = [G9reglerregionen.ORTE[i] for i in region]
        # Punkt 0: Nase (1 auf einem Punkt) schlägt „breit“ (¼); 1, 2: nur „breit“ (die Pose zählt nicht); 3: Hals 1 > ¼; 4: nächster ist 3; 5: nächster ist 4/3.
        self.assertEqual(orte, ['nase', 'gesicht', 'gesicht', 'hals', 'hals', 'hals'])
        anteile = G9reglerregionen.anteile(np.array([1.0, 1.0, 0.0, 2.0, 0.0, 0.0]), region)
        self.assertAlmostEqual(sum(anteile.values()), 1.0)
        self.assertAlmostEqual(anteile['hals'], 0.5)

    def test_2_doppelte_streng(self):
        rng = np.random.default_rng(1)
        y = rng.normal(0.0, 0.004, (200, 3))
        aehnlich = y + rng.normal(0.0, 0.0006, (200, 3))        # gleiche Richtung (cos ≈ 0,989), aber Millimeter daneben
        felder = {'x': 0.5 * y, 'y': y, 'z': aehnlich, 'n': 2.0 * y, 'g': -y * 1.1}
        k = [{'name': n, 'ende': 1.0, 'mm': 5.0, 'feld': f.astype(np.float32)} for n, f in felder.items()]
        k[0]['ende'] = 2.0                                       # x am Anschlag 2: x(2) = 0,5·y(1) → x(w) = y(w·0,25)
        aliase, paare, linear = Reglerortedoppelte(_Messung({n: f / e for n, f, e in ((d['name'], d['feld'], d['ende']) for d in k)},
                                                           nichtlinear={'n'})).bauen(k)
        namen = {(a, b) for a, b, *_ in aliase}
        self.assertIn(('x', 'y'), namen)
        faktor = next(f for a, b, f, _ in aliase if (a, b) == ('x', 'y'))
        self.assertAlmostEqual(faktor, 0.25, places=3)
        self.assertFalse(any('z' in (a, b) for a, b in namen), 'ähnlich ist kein Alias')
        self.assertFalse(any('n' in (a, b) for a, b in namen), 'nichtlinear ist kein Alias')
        self.assertTrue(any('n' in paar.split('|') for paar in linear), 'der nichtlineare Kandidat ist an den Stützstellen geprüft')
        self.assertTrue(any({a, b} == {'y', 'g'} for a, b, _ in paare), 'gegenläufig gleich stark ist ein Paar')

    def test_3_seiten_koppeln(self):
        ausgabe = Jsmodul('charakter', 'genesis9', 'genesis9seiten.js').laufen("""
const { Genesis9seiten } = await import(MODUL);
pruefe('Left', Genesis9seiten.gegenname('facs_ctrl_EyeLookDownLeft'), 'facs_ctrl_EyeLookDownRight');
pruefe('Right', Genesis9seiten.gegenname('facs_ctrl_EyeLookDownRight'), 'facs_ctrl_EyeLookDownLeft');
pruefe('_l', Genesis9seiten.gegenname('body_cbs_forearm_y75n_l'), 'body_cbs_forearm_y75n_r');
pruefe('mh l-', Genesis9seiten.gegenname('mh:eyes_l-eye-height1-decr|incr'), 'mh:eyes_r-eye-height1-decr|incr');
pruefe('ohne Seite', Genesis9seiten.gegenname('Nose Width'), null);
Genesis9seiten.kennen({bereiche: [{regler: [{name: 'aLeft'}, {name: 'aRight'}]}]});
Genesis9seiten._an = false;
pruefe('aus', Genesis9seiten.partner({name: 'aLeft'}), null);
Genesis9seiten._an = true;
pruefe('an', Genesis9seiten.partner({name: 'aLeft'}).name, 'aRight');
pruefe('fehlt im Plan', Genesis9seiten.partner({name: 'bLeft'}), null);
Genesis9seiten.kennen({bereiche: [{regler: [{name: 'cLeft-0xa37fe31'}, {name: 'cRight-0xa37fe21'}]}]});
pruefe('andere Daz-Kennung', Genesis9seiten.partner({name: 'cLeft-0xa37fe31'}).name, 'cRight-0xa37fe21');
console.log(JSON.stringify({ok: true}));
""")
        self.assertTrue(ausgabe.get('ok'), ausgabe)

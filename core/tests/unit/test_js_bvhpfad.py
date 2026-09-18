# -*- coding: utf-8 -*-
"""`Bvhpfad`: der Ordner aus dem BVH-Pfad — Windows- und POSIX-Trenner.

WARUM (Edgar, 13.09.2026: „so dass ich das Verzeichnis kopieren kann"): Der
Ordner wird im Browser aus `job.bvh_file` geschnitten; ein Pfad ohne
Trenner bleibt, wie er ist, ein Trenner am Ende kommt nicht mit.

Sabotage-Gegenprobe: `schnitt > 0` → `schnitt >= 0` macht Fall 3 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'bvhpfad.js')

SKRIPT = """
const { Bvhpfad: B } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (ist !== soll) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt '
                        + JSON.stringify(soll));
    }
};
pruefe('windows',
       B.ordner('A:\\\\3DTools\\\\media\\\\output\\\\abc\\\\smplx_005 Dance.bvh'),
       'A:\\\\3DTools\\\\media\\\\output\\\\abc');
pruefe('posix', B.ordner('/srv/out/abc/lauf.bvh'), '/srv/out/abc');
pruefe('ohne trenner', B.ordner('lauf.bvh'), 'lauf.bvh');
pruefe('wurzel', B.ordner('/lauf.bvh'), '/lauf.bvh');
pruefe('leer', B.ordner(''), '');
pruefe('null', B.ordner(null), '');
console.log(JSON.stringify({ ok: true }));
"""


class BvhpfadTest(SimpleTestCase):
    def test_ordner_aus_pfad(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

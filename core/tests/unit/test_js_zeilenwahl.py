# -*- coding: utf-8 -*-
u"""Zeilenwahl: Kästchen je Zeile, Bereich mit Shift, Kopfkästchen.

Edgar (12.09.2026): „Checkbox auswählen, Multi-Select mit Shift und
Batch-Delete" für die Auftragstabelle.

Die Bereichsrechnung und der Stand des Kopfkästchens sind reine Funktionen
und laufen hier in Node ohne DOM: Der Bereich geht von der zuletzt
angeklickten bis zur jetzt angeklickten Zeile, in beide Richtungen, beide
einschließlich — und ist LEER, wenn eine der beiden nicht mehr in der Liste
steht (die Zeile wurde gelöscht). Das Kopfkästchen ist voll, wenn alle
gewählt sind, teils bei einigen, sonst leer — und bei null Zeilen nie voll.

Dazu die Verdrahtung: Die Zeilen tragen `data-id` (Zeilenform von
`djangobase/_tabelle.html`), und kein Modul sucht mehr nach `row-<id>` oder
`jobTableBody` — das alte Drahtformat der handgeschriebenen Tabelle.

Sabotage-Gegenprobe: `Math.max(a, b) + 1` → `Math.max(a, b)` lässt „vorwärts"
rot werden; `gesamt > 0 &&` entfernt lässt „null Zeilen" rot werden.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

AUFTRAEGE = Path(settings.BASE_DIR) / 'static' / 'js' / 'auftraege'

MODUL = Jsmodul('..', 'js', 'auftraege', 'zeilenwahl.js')

SKRIPT = """
const { Zeilenwahl } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const z = ['a', 'b', 'c', 'd', 'e', 'f'];
// Bereich: beide Richtungen, einschließlich, ein Element, gelöschte Zeile
pruefe('vorwärts', Zeilenwahl.bereich(z, 'b', 'e'), ['b', 'c', 'd', 'e']);
pruefe('rückwärts', Zeilenwahl.bereich(z, 'e', 'b'), ['b', 'c', 'd', 'e']);
pruefe('Ränder', Zeilenwahl.bereich(z, 'a', 'f'), z);
pruefe('dasselbe', Zeilenwahl.bereich(z, 'c', 'c'), ['c']);
pruefe('gelöscht', Zeilenwahl.bereich(z, 'x', 'c'), []);
pruefe('leer', Zeilenwahl.bereich([], 'a', 'b'), []);
// Kopfkästchen: leer / teils / voll / null Zeilen
pruefe('keines', Zeilenwahl.kopfstand(0, 6), { checked: false, indeterminate: false });
pruefe('teils', Zeilenwahl.kopfstand(2, 6), { checked: false, indeterminate: true });
pruefe('alle', Zeilenwahl.kopfstand(6, 6), { checked: true, indeterminate: false });
pruefe('null Zeilen', Zeilenwahl.kopfstand(0, 0), { checked: false, indeterminate: false });
// Drahtformat
pruefe('Kästchen', Zeilenwahl.KASTEN, 'input.job-check');
pruefe('Kopf', Zeilenwahl.ALLE, 'select-all');
console.log(JSON.stringify({ok: true}));
"""


class ZeilenwahlTest(SimpleTestCase):

    databases = set()

    def test_bereich_und_kopfkaestchen(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class DrahtformatTest(SimpleTestCase):
    u"""Die Zeilen heißen `data-id`, nicht mehr `row-<id>`."""

    databases = set()

    MODULE = ('auftragsliste.js', 'auftragslauf.js', 'auftragszeile.js',
              'detailzeilen.js', 'zeilenwahl.js')

    def test_kein_modul_sucht_das_alte_markup(self):
        for name in self.MODULE:
            with self.subTest(modul=name):
                quelle = (AUFTRAEGE / name).read_text(encoding='utf-8')
                # Kommentare dürfen die Geschichte erzählen; Code nicht.
                code = '\n'.join(z for z in quelle.splitlines()
                                 if not z.strip().startswith(('*', '//', '/*')))
                self.assertNotIn("'row-'", code)
                self.assertNotIn('id^="row-"', code)
                self.assertNotIn('jobTableBody', code)
                self.assertNotIn("getElementById('jobTable')", code)

    def test_die_zeile_wird_ueber_data_id_gefunden(self):
        quelle = (AUFTRAEGE / 'auftragszeile.js').read_text(encoding='utf-8')
        self.assertIn('tr[data-id="${this.id}"]', quelle)
        lauf = (AUFTRAEGE / 'auftragslauf.js').read_text(encoding='utf-8')
        self.assertIn('zeile.dataset.id = neueId', lauf)
        self.assertIn('class="job-check" value="${neueId}"', lauf)

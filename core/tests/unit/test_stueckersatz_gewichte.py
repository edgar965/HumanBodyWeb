# -*- coding: utf-8 -*-
"""Eigene Hautgewichte eines Stücks (Edgar, 09.10.2026: „Gespreizte Beine: Das Stück ist starr").

Befund (Chrome, Scham-Stück von „cute girl"): Die Gewichte, die `G9eigenstueck.schreiben` in die `.dsf` schreibt, kamen im Browser nie
an — `G9garderobe.teile` übergab jedem Kleidungsstück `koerperhaut=True`, und `G9folger` ersetzt dann die Gewichte der Datei durch die der
drei nächsten Körperpunkte der Grundfigur. Vor und nach dem Neuschreiben stand im Browser derselbe Anteil (`pelvis` 98,1 %). Seither:

1. `eigene_gewichte: true` neben der `.dsf` wird gelesen — nur bei echtem `true`; ohne Datei, bei Text „true", bei kaputter Datei: nicht.
2. `G9garderobe.teile` fragt Stücke mit dem Zeichen mit `koerperhaut=False` an, alle anderen mit `True`; ein Prop (Lage) nie.

Sabotage-Gegenprobe: in `eigene_gewichte` `is True` durch `bool(...)` ersetzen → Fall 1 rot („true" als Text); in `teile` den Zusatz
`and not …` streichen → Fall 2 rot; `lage is None` streichen → Fall 3 rot.

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.garderobe import G9garderobe
from Genesis9.stueckersatz import G9stueckersatz

from core.tests.unit._pruefablage import Pruefablage


class EigeneGewichteTest(SimpleTestCase):
    databases = set()

    def test_1_nur_ein_echtes_true_zaehlt(self):
        with Pruefablage.ordner('eigengewichte_') as ordner:
            duf = Path(ordner) / 'stueck.duf'
            self.assertFalse(G9stueckersatz.eigene_gewichte(duf), 'ohne Datei')
            G9stueckersatz.schreiben(duf, [], eigene_gewichte=True)
            self.assertTrue(G9stueckersatz.eigene_gewichte(duf))
            G9stueckersatz.schreiben(duf, [])
            self.assertFalse(G9stueckersatz.eigene_gewichte(duf), 'ohne das Zeichen')
            G9stueckersatz.pfad(duf).write_text('{"eigene_gewichte": "true"}', encoding='utf-8')
            self.assertFalse(G9stueckersatz.eigene_gewichte(duf), 'Text ist kein true')
            G9stueckersatz.pfad(duf).write_text('{kaputt', encoding='utf-8')
            self.assertFalse(G9stueckersatz.eigene_gewichte(duf), 'kaputte Datei')

    def _teile(self, eigene, lage=None):
        """Ruft `G9garderobe.teile` mit Attrappen auf und gibt zurück, welches `koerperhaut` an `G9folger.holen` ging."""
        folger = mock.MagicMock()
        with mock.patch.object(G9garderobe, 'eintrag', return_value={'zeigbar': True, 'name': 'x'}), \
                mock.patch.object(G9garderobe, 'datei', return_value=Path('x.duf')), \
                mock.patch.object(G9garderobe, '_knoten', return_value=[('p', {'id': 'g'}, 'k')]), \
                mock.patch('Genesis9.garderobe.G9dson.lesen', return_value=object()), \
                mock.patch('Genesis9.requisit.G9requisit.aus_knoten', return_value=lage), \
                mock.patch('Genesis9.requisit.G9requisit.definition_fuer', return_value=None), \
                mock.patch('Genesis9.garderobe.G9garderobekategorien.kategorie', return_value='Hose'), \
                mock.patch('Genesis9.garderobe.G9knotensicht.sichtbar', return_value=True), \
                mock.patch('Genesis9.stoff.G9stoff.entscheiden'), \
                mock.patch('Genesis9.garderobe.G9folger.holen', return_value=folger) as holen, \
                mock.patch.object(G9stueckersatz, 'eigene_gewichte_fuer', return_value=eigene):
            G9garderobe.teile('x')
        return holen.call_args.kwargs['koerperhaut']

    def test_2_ein_stueck_mit_eigenen_gewichten_bekommt_keine_koerperhaut(self):
        self.assertFalse(self._teile(eigene=True))
        self.assertTrue(self._teile(eigene=False), 'jedes andere Kleidungsstück behält die Gewichte der Körperhaut')

    def test_3_ein_prop_bekommt_nie_koerperhaut(self):
        self.assertFalse(self._teile(eigene=False, lage=object()))

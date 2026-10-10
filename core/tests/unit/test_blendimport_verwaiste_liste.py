# -*- coding: utf-8 -*-
"""Die Liste der verwaisten Importe liest weder Garderobe noch Datenbank (Edgar, 10.10.2026: „warum dauert das Aufbauen des Dialogs so lange?").

`GET /api/character/blendimport/verwaist/` (`Blendimportloeschen.verwaiste`) baute für JEDEN der Importe den vollen Plan: Garderobenliste, alle
anderen Stände je Stück, Auftrag aus der Datenbank. Gemessen 10.10.2026 (`ProjektTemp/_wegwerf/dialog_verwaist_profil.py`): warm 1,1–1,7 s, kalt
20 s (Neuaufbau der Garderobenliste, wenn ein Import ein Stück geschrieben hatte), im `client.log` bis 41 s — und der Figurwahl-Dialog wartete darauf.
Die Liste und die Rückfrage „Alle verwaisten löschen" brauchen nur Kennung, Name, Größe und Grund.

1. `verwaiste` liefert nur die verwaisten Importe, ohne `stuecke`, `auftrag` oder die Garderobe anzufassen.
2. Der volle Plan (`plan`, für die Rückfrage vor dem Löschen) hat sie weiter: `auftrag`, `stuecke`, `behalten`.

Sabotage-Gegenprobe: in `verwaiste` statt `kurzplan` wieder `plan` rufen → `test_1` rot (die Attrappen für `stuecke` und `auftrag` werfen); in `plan` das
`plan.update(…)` streichen → `test_2` rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

from unittest import mock

from django.test import SimpleTestCase

from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportloeschen import Blendimportloeschen

WAISE = '2026.10.01.00.00.01'
MIT_MODELL = '2026.10.01.00.00.02'

STAENDE = {
    WAISE: {'status': 'gescheitert', 'fehler': 'Boom', 'quelle': {'name': 'Rosemary'}},
    MIT_MODELL: {'status': 'fertig', 'quelle': {'name': 'Rainy'}},
}
MODELLE = [{'name': 'Rainy', 'import': MIT_MODELL, 'kleidung': set()}]


def _stand(self):
    return STAENDE[self.kennung]


class VerwaisteListeTest(SimpleTestCase):
    databases = set()

    def _patchen(self, **zusatz):
        """Die Dinge, die die Liste NICHT anfassen darf, werfen; alles andere ist festgelegt."""
        return [
            mock.patch.object(Blendimportablage, 'alle', return_value=[WAISE, MIT_MODELL]),
            mock.patch.object(Blendimportloeschen, 'modelle_lesen', return_value=MODELLE),
            mock.patch.object(Blendimportloeschen, 'stand', _stand),
            mock.patch.object(Blendimportloeschen, 'laeuft', return_value=False),
            mock.patch.object(Blendimportloeschen, 'megabyte', return_value=12.5),
            mock.patch.object(Blendimportloeschen, 'stuecke', **zusatz.get('stuecke', {'side_effect': AssertionError('Garderobe gelesen')})),
            mock.patch.object(Blendimportloeschen, 'auftrag', **zusatz.get('auftrag', {'side_effect': AssertionError('Datenbank gelesen')})),
        ]

    def _mit(self, patches, tun):
        for p in patches:
            p.start()
        try:
            return tun()
        finally:
            for p in reversed(patches):
                p.stop()

    def test_1_die_liste_der_verwaisten_liest_keine_garderobe_und_keine_datenbank(self):
        liste = self._mit(self._patchen(), Blendimportloeschen.verwaiste)
        self.assertEqual([p['kennung'] for p in liste], [WAISE], 'nur der Import ohne Modell ist verwaist')
        plan = liste[0]
        self.assertEqual((plan['name'], plan['mb'], plan['verwaist']), ('Rosemary', 12.5, 'Gescheitert: Boom'))
        for feld in ('stuecke', 'auftrag', 'behalten'):
            self.assertNotIn(feld, plan, 'der Kurzplan trägt %s nicht — das braucht die Rückfrage, nicht die Liste' % feld)

    def test_2_der_volle_plan_hat_weiter_stuecke_auftrag_und_behalten(self):
        patches = self._patchen(stuecke={'return_value': []}, auftrag={'return_value': None})
        plan = self._mit(patches, lambda: Blendimportloeschen(WAISE).plan(MODELLE))
        for feld in ('stuecke', 'auftrag', 'behalten', 'modelle', 'mb', 'verwaist', 'laeuft'):
            self.assertIn(feld, plan)
        self.assertEqual((plan['stuecke'], plan['behalten'], plan['auftrag']), ([], [], None))

# -*- coding: utf-8 -*-
"""Der Hautabstand von Schuhen auf einer HumanBody-Figur (`G9kleidhumanbody.hautabstand`, 05.10.2026).

Edgar (05.10.2026): „Angie_Sneakers passt nicht auf Modell F2_ShirtLeggins, große Zehe geht durch den Schuh". Gemessen an F2_ShirtLeggins (Strahl +z von 960 Hautpunkten der
Zehenfront bis zur ersten Schuhfläche): mit 6 mm ragten 17 Hautpunkte heraus, mit 8, 10 und 12 mm keiner. Zusagen:

1. Ein Stück der Kategorie „Schuhe" bekommt `HAUTABSTAND_SCHUH`, jedes andere `HAUTABSTAND` (die 6 mm der Kleidung bleiben).
2. Die Kategorie ist die WIRKSAME (Edgars Einteilung vor der Vorgabe aus Daz' Metadaten): ein verschobener Schuh zählt nicht mehr, ein verschobenes Stück als Schuh schon.
3. Ist die Einteilung nicht lesbar, gilt der Abstand der Kleidung — kein Fehler.
"""
from unittest import mock

from django.test import SimpleTestCase

from core.api.g9kleidhumanbody import G9kleidhumanbody

KATEGORIE = 'Genesis9.garderobekategorien.G9garderobekategorien.kategorie'


class DerHautabstandVonSchuhen(SimpleTestCase):
    def test_1_schuhe_bekommen_den_groesseren_abstand(self):
        with mock.patch(KATEGORIE, return_value=u'Schuhe'):
            self.assertEqual(G9kleidhumanbody.hautabstand({'id': 'angie_sneakers'}), G9kleidhumanbody.HAUTABSTAND_SCHUH)
        with mock.patch(KATEGORIE, return_value=u'Oberteile'):
            self.assertEqual(G9kleidhumanbody.hautabstand({'id': 'g9_base_shirt'}), G9kleidhumanbody.HAUTABSTAND)
        self.assertGreater(G9kleidhumanbody.HAUTABSTAND_SCHUH, G9kleidhumanbody.HAUTABSTAND)

    def test_2_die_wirksame_kategorie_zaehlt(self):
        eintrag = {'id': 'angie_sneakers', 'art': 'kleidung', 'datei': 'Angie/Angie Sneakers.duf', 'wurzel': 'People/Genesis 9/Clothing'}
        with mock.patch('Genesis9.garderobekategorien.G9garderobekategorien.laden', return_value={'kategorien': [], 'zuordnung': {'angie_sneakers': u'Zubehör'}}), \
                mock.patch('Genesis9.garderobekategorien.G9garderobekategorien.vorgabe', return_value=u'Schuhe'):
            self.assertEqual(G9kleidhumanbody.hautabstand(eintrag), G9kleidhumanbody.HAUTABSTAND)

    def test_3_eine_unlesbare_einteilung_gibt_den_abstand_der_kleidung(self):
        with mock.patch(KATEGORIE, side_effect=OSError('weg')):
            self.assertEqual(G9kleidhumanbody.hautabstand({'id': 'x'}), G9kleidhumanbody.HAUTABSTAND)

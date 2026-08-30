# -*- coding: utf-8 -*-
"""Importe INNERHALB von Funktionen zeigen auf etwas, das es gibt.

ANLASS (18.08.2026): `core/api/dateien.py` holte `retarget_bvh_data` aus
`core.character_api` — die Datei war beim Umbau am 15.08.2026 in `core/api/`
aufgegangen. Der Endpunkt `/api/bvh/<auftrag>/?mode=retarget` lief damit in
einen `ModuleNotFoundError`, und zwar erst BEIM AUFRUF:

* Der Serverstart merkt nichts — die Zeile wird nicht ausgefuehrt.
* Das Werkzeug `tote-importe` merkt nichts — es sieht nur den Modulkopf.
* Ein Seitenaufruf-Test merkt nichts — die Seite lädt ja.

Genau die Fehlerklasse aus `.claude/rules/es-module-stumme-fehler.md`, nur auf
der Python-Seite. Dieser Test liest jede Projektdatei mit `ast`, sammelt die
Importe unterhalb einer Funktion und prueft, ob das Ziel auffindbar ist —
ausgefuehrt wird dabei nichts.

DER TEST WAR ZU GROSSZUEGIG (27.08.2026)
========================================
Er prüfte nur, ob das MODUL auffindbar ist — nicht, ob der importierte NAME
darin steht. Beim Umbau desselben Tages wurde `_copy_bvh_to_results` aus
`core/api/bibliothek.py` entfernt, obwohl `pipelines/auftragslauf.py` sie an
VIER Stellen ruft, jedesmal mit einem Import in der Funktion. Modul da, Name
weg: `manage.py check` blieb still, alle 625 Tests blieben grün, und aufgefallen
wäre es erst beim nächsten Pipeline-Lauf. Seitdem prüft `name_vorhanden`
zusätzlich den Syntaxbaum des Zielmoduls.

Warum lokale Importe ueberhaupt vorkommen: Sie brechen Ringe (`cv2`, schwere
ML-Pakete) oder halten den Start schnell. Sie sind also nicht zu verbieten,
sondern zu pruefen.
"""

import ast

from django.test import SimpleTestCase

from ._importsuche import WURZEL, Lokalerimport, Modulsuche


class LokaleImporteTest(SimpleTestCase):

    def test_jeder_import_in_einer_funktion_findet_sein_modul(self):
        suche = Modulsuche(WURZEL / 'core')
        tot = []
        for eintrag in suche.importe():
            if eintrag.pruefbar and not eintrag.loesbar:
                tot.append(str(eintrag))
        self.assertEqual(tot, [], 'Import in einer Funktion zeigt ins Leere: '
                         + ', '.join(tot))
        self.assertEqual(suche.nicht_lesbar, [],
                         'Diese Dateien parsen nicht und wurden deshalb NICHT '
                         'geprueft: %s' % suche.nicht_lesbar)

    def test_jeder_geholte_name_steht_auch_im_zielmodul(self):
        """Modul da, Name weg — der Fall vom 27.08.2026."""
        fehlend = []
        for eintrag in Modulsuche(WURZEL / 'core').importe():
            if eintrag.pruefbar and eintrag.loesbar \
                    and not eintrag.name_vorhanden:
                fehlend.append(str(eintrag))
        self.assertEqual(fehlend, [],
                         'Der Name steht nicht (mehr) im Zielmodul: '
                         + ', '.join(fehlend))

    def test_der_test_findet_einen_kaputten_import(self):
        """Gegenprobe: Ein erfundener Modulname MUSS auffallen."""
        knoten = ast.parse('from ..gibtesnicht import x').body[0]
        eintrag = Lokalerimport(WURZEL / 'core' / 'api' / 'x.py', knoten,
                                'core.gibtesnicht')
        self.assertTrue(eintrag.pruefbar)
        self.assertFalse(eintrag.loesbar)

    def test_der_test_findet_einen_fehlenden_namen(self):
        """Gegenprobe zum zweiten Fall: Modul da, Name erfunden."""
        knoten = ast.parse('from ..models import GibtEsNicht').body[0]
        eintrag = Lokalerimport(WURZEL / 'core' / 'api' / 'x.py', knoten,
                                'core.models', 'GibtEsNicht')
        self.assertTrue(eintrag.loesbar, 'core.models muss auffindbar sein')
        self.assertFalse(eintrag.name_vorhanden)
        # Und die Gegenrichtung: ein Name, den es wirklich gibt.
        echt = Lokalerimport(WURZEL / 'core' / 'api' / 'x.py', knoten,
                             'core.models', 'BVHJob')
        self.assertTrue(echt.name_vorhanden)

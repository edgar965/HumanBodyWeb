# -*- coding: utf-8 -*-
"""Wächter: die Scham-Messung wird IMMER aufgerufen (11.10.2026).

Edgar: „Ich hatte schon extra beauftragt, dass die Messung bei jedem Import ausgeführt wird. Und auch bei jedem Mesh-to-3D Auftrag. Ist das sichergestellt, dass das nun gemacht wird oder muss ich
nochmal zehnmal das beauftragen?" Diese Prüfung hält die Aufrufer fest — nimmt jemand einen Aufruf heraus, wird sie rot:

    Mesh to 3D (jeder Auftrag)     `Meshfigurvorschau.ausfuehren` → `Meshfigurschammessung.sicher`; `Meshfigurlauf` führt den Schritt „vorschau" immer aus, ebenso `Engine2d3dKleiderkoerperlauf`
    Blender-Import, Schritt figur  `Blendimportlauf._figur` legt `ergebnis.figur.schammessung` ab (aus dem Auftrag von Mesh to 3D), auch wenn es kein Scham-Stück gibt
    Scham-Stück                    `Blendimportstuecke.scham_stueck` → `Schammessungablage.messen`; `Blendimporthaut.backen` → `Schammessungablage.nachtragen` (Farbe am Ring)
    Daz-Geograft                   `Dazgeograft.bauen` → `self.messen`

Die Prüfung liest nur Quelltext (`inspect.getsource`), startet nichts. Sabotage-Gegenprobe: eine der Zeilen in der jeweiligen Methode streichen → der zugehörige Fall wird rot.
"""
import inspect

from django.test import SimpleTestCase


class SchammessungAufruferTest(SimpleTestCase):
    def _quelle(self, klasse, name):
        return inspect.getsource(getattr(klasse, name))

    def test_1_mesh_to_3d_misst_bei_jedem_auftrag_im_schritt_vorschau(self):
        from core.dienste.meshfigurvorschau import Meshfigurvorschau

        quelle = self._quelle(Meshfigurvorschau, 'ausfuehren')
        # Seit 12.10.2026 läuft die Messung in einem Faden neben Haar- und Kleidungsobjekt (`pool.submit(Meshfigurschammessung.sicher, self.lauf)`).
        self.assertIn('Meshfigurschammessung.sicher, self.lauf', quelle)
        self.assertIn("self.job.ergebnis['schammessung']", quelle)
        # kein Schalter davor: der `with`-Block mit den Fäden steht auf der Ebene des Methodenrumpfs, nicht unter einer Bedingung
        zeilen = quelle.splitlines()
        aufruf = next(z for z in zeilen if 'Meshfigurschammessung.sicher' in z)
        block = next(z for z in zeilen if 'ThreadPoolExecutor(' in z)
        self.assertEqual(len(block) - len(block.lstrip()), 8, 'der Block steht nicht auf der Ebene des Methodenrumpfs, sondern unter einer Bedingung')
        self.assertEqual(len(aufruf) - len(aufruf.lstrip()), 12, 'der Aufruf steht nicht unmittelbar im Block')

    def test_2_der_schritt_vorschau_laeuft_in_jedem_lauf(self):
        from core.dienste.engine2d3dkleiderkoerperlauf import Engine2d3dKleiderkoerperlauf
        from core.dienste.meshfigurlauf import Meshfigurlauf

        self.assertIn('vorschau', Meshfigurlauf.SCHRITTE)
        # Seit 12.10.2026 bekommt jede Fabrik den Lauf (ein Nebenlauf rechnet mit einer Kopie): `lambda lauf: …`.
        self.assertIn("'vorschau': lambda lauf: Meshfigurvorschau(lauf).ausfuehren()", self._quelle(Meshfigurlauf, 'ausfuehren'))
        self.assertIn('Meshfigurvorschau(self).ausfuehren()', inspect.getsource(Engine2d3dKleiderkoerperlauf))

    def test_3_der_blender_import_traegt_die_messung_des_schritts_figur(self):
        from core.dienste.blendimportlauf import Blendimportlauf

        self.assertIn('figur', Blendimportlauf.SCHRITTE)
        self.assertIn("'schammessung': (job.ergebnis or {}).get('schammessung')", self._quelle(Blendimportlauf, '_figur'))

    def test_4_das_scham_stueck_wird_gemessen_und_die_farbe_am_ring_nachgetragen(self):
        from core.dienste.blendimporthaut import Blendimporthaut
        from core.dienste.blendimportstuecke import Blendimportstuecke

        self.assertIn('Schammessungablage.messen(', self._quelle(Blendimportstuecke, 'scham_stueck'))
        self.assertIn('Schammessungablage.nachtragen(', self._quelle(Blendimporthaut, 'backen'))

    def test_5_das_daz_geograft_misst_bei_jedem_bau(self):
        from core.dienste.dazgeograft import Dazgeograft

        quelle = self._quelle(Dazgeograft, 'bauen')
        self.assertIn('self.messen(figur, punkte, dreiecke, uv_ecken, loch)', quelle)
        self.assertIn('Schammessung.sicher(', self._quelle(Dazgeograft, 'messen'))

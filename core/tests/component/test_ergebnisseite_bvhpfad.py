# -*- coding: utf-8 -*-
"""Ergebnisseiten: der BVH-Pfad steht ganz oben — Ordner, Datei, Bibliothekskopie.

WARUM (Edgar, 12./13.09.2026: „schreibe … wo sich das BVH befindet … direkt
ganz oben" — „auf allen ergebnis seiten … sollte immer der Pfad der BVH
kommen, so dass ich das Verzeichnis kopieren kann"): Beide Ergebnisseiten
(`/process/<id>/result/` und `/process/result/`) binden `_bvh_pfad.html`
ein — vor allem anderen Inhalt, mit Kopierknöpfen je Zeile und der Kopie
aus `A_Results`, wenn sie liegt.
"""

from pathlib import Path

from django.test import Client, TestCase, override_settings

from core.models import BVHJob
from core.tests.unit._pruefablage import Pruefablage

DATEI = '<code id="bvhDatei">A:\\irgendwo\\ausgabe\\smplx_probe.bvh</code>'


class ErgebnisseiteBvhpfad(TestCase):
    def setUp(self):
        self.job = BVHJob.objects.create(
            name="probe.mp4",
            pipeline="smplx",
            status="complete",
            bvh_file=r"A:\irgendwo\ausgabe\smplx_probe.bvh",
        )
        self.client = Client()

    def _seite(self, adresse):
        antwort = self.client.get(adresse)
        self.assertEqual(antwort.status_code, 200)
        return antwort.content.decode("utf-8")

    def test_auftragsseite_zeigt_ordner_datei_und_knoepfe_vor_dem_inhalt(self):
        text = self._seite("/process/%s/result/" % self.job.kennung)
        self.assertIn('id="bvhPfad" data-pfad="A:\\irgendwo\\ausgabe\\smplx_probe.bvh"', text)
        self.assertIn('<code id="bvhOrdner"></code>', text)
        self.assertIn(DATEI, text)
        self.assertEqual(text.count('class="bvh-kopieren"'), 2)
        self.assertNotIn('id="bvhKopie"', text)
        self.assertLess(text.index('id="bvhPfad"'), text.index('class="result-header"'))
        self.assertIn("viewer/gemeinsam/bvhpfad.js", text)

    def test_bibliothekskopie_wird_genannt_wenn_sie_liegt(self):
        ablage = Pruefablage.ordner("ablage_")
        ordner = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        (ordner / "probe_smplx.bvh").write_text("HIERARCHY\n", encoding="utf-8")
        with override_settings(BVH_RESULTS_DIR=str(ordner)):
            text = self._seite("/process/%s/result/" % self.job.kennung)
        self.assertIn('<code id="bvhKopie">%s</code>' % (ordner / "probe_smplx.bvh"), text)
        self.assertEqual(text.count('class="bvh-kopieren"'), 3)

    def test_auswahlseite_zeigt_den_pfad_ebenso(self):
        text = self._seite("/process/result/?job=%s" % self.job.id)
        self.assertIn(DATEI, text)
        self.assertIn('data-kopie="ordner"', text)

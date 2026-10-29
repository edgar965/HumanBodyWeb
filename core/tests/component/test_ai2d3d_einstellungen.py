# -*- coding: utf-8 -*-
"""Einstellungen → 2d-3d-AI (24.10.2026): die Seite, das Speichern über `/api/ui-prefs/` und der Weg bis zum Rechenlauf (`Fotogelenke`).

WARUM: Edgar, 24.10.2026: „Mach auch du eine Seite Einstellungen - 2d-3d-KI wo du sowas einstellen kannst, damit man das später beides ausprobieren kann?“. Ein Wert, der auf der Seite
steht, aber beim Lauf nicht ankommt, sähe aus wie gewählt und rechnete doch mit der Vorgabe — darum geht der Test durch alle Schichten: Seite lesen, speichern, Seite wieder lesen, Lauf.
"""
import json
import sys

from django.conf import settings
from django.test import TestCase

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.fotogelenke import Fotogelenke  # noqa: E402
from KoerperKI_Fotos.gesichtserkenner import Gesichtserkenner  # noqa: E402

from core.dienste.ai2d3dgesichtswahl import Ai2d3dgesichtswahl  # noqa: E402
from core.dienste.ai2d3dmeshwahl import Ai2d3dmeshwahl  # noqa: E402
from core.dienste.ai2d3dposewahl import Ai2d3dposewahl  # noqa: E402


class DieEinstellungsseite(TestCase):
    ADRESSE = '/settings/2d-3d-ai/'

    def _speichern(self, wert):
        antwort = self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dposewahl.SCHLUESSEL: wert}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)

    def _seite(self):
        antwort = self.client.get(self.ADRESSE)
        self.assertEqual(antwort.status_code, 200)
        return antwort.content.decode('utf-8')

    def test_beide_quellen_und_die_vorgabe_gewaehlt(self):
        html = self._seite()
        self.assertIn('id="ai2d3d-settings-form"', html)
        self.assertIn('name="%s"' % Ai2d3dposewahl.SCHLUESSEL, html)
        self.assertIn('<option value="vitpose" selected>', html)
        self.assertIn('<option value="sam3dbody">', html)
        for _w, text in Ai2d3dposewahl.WERTE:
            self.assertIn(text, html)

    def test_gespeicherte_quelle_gilt_fuer_seite_und_lauf(self):
        self._speichern('sam3dbody')
        html = self._seite()
        self.assertIn('<option value="sam3dbody" selected>', html)
        self.assertIn('<option value="vitpose">', html)
        self.assertEqual(Ai2d3dposewahl.gewaehlt(), 'sam3dbody')
        self.assertEqual(Fotogelenke().quelle, 'sam3dbody')

    def test_unbekannter_wert_faellt_auf_die_vorgabe(self):
        self._speichern('sapiens')
        self.assertIn('<option value="vitpose" selected>', self._seite())
        self.assertEqual(Fotogelenke().quelle, 'vitpose')

    def test_im_menue_der_einstellungen(self):
        self.assertIn('href="%s"' % self.ADRESSE, self._seite())

    # 27.10.2026, Edgar: „in den Einstellungen umschaltbar zwischen Insight und MediaPipe. MediaPipe soll weiter lauffähig bleiben“ — durch alle Schichten bis zum Erkenner des Laufs

    def test_erkenner_der_gesichtspunkte_vorgabe_insightface(self):
        html = self._seite()
        self.assertIn('name="%s"' % Ai2d3dgesichtswahl.SCHLUESSEL, html)
        self.assertIn('<option value="insightface" selected>', html)
        self.assertIn('<option value="mediapipe">', html)
        self.assertEqual(Gesichtserkenner.gewaehlt(), 'insightface')

    def test_gespeicherter_erkenner_gilt_fuer_seite_und_lauf(self):
        antwort = self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dgesichtswahl.SCHLUESSEL: 'mediapipe'}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        self.assertIn('<option value="mediapipe" selected>', self._seite())
        self.assertEqual(Gesichtserkenner.gewaehlt(), 'mediapipe')
        ge = Gesichtserkenner(geraet='cpu')
        self.assertEqual((ge.art, ge.n, ge.schema.FAECHER), ('mediapipe', 478, (0,)))

    def test_unbekannter_erkenner_faellt_auf_insightface(self):
        self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dgesichtswahl.SCHLUESSEL: 'dlib'}), content_type='application/json')
        ge = Gesichtserkenner(geraet='cpu')
        self.assertEqual((ge.art, ge.n, ge.schema.FAECHER), ('insightface', 106, (0, 1, 3)))

    # 28.10.2026, Edgar: „portiere beide Methoden, mach in den Einstellungen - 2d-3d-AI die Option welche Portierung wir dafür nehmen, per default die beste“ — bis zum Lauf

    def test_portierung_der_einpassung_vorgabe_gewaehlt(self):
        from Genesis9.meshgenesis import G9meshgenesis
        html = self._seite()
        self.assertIn('name="%s"' % Ai2d3dmeshwahl.SCHLUESSEL, html)
        self.assertIn('<option value="%s" selected>' % Ai2d3dmeshwahl.VORGABE, html)
        for w, text in Ai2d3dmeshwahl.WERTE:
            self.assertIn(text, html)
            self.assertIn(w, G9meshgenesis.VERFAHREN)
        self.assertEqual(G9meshgenesis.gewaehlt(), Ai2d3dmeshwahl.VORGABE)
        self.assertEqual(G9meshgenesis.VORGABE, Ai2d3dmeshwahl.VORGABE)

    def test_gespeicherte_portierung_gilt_fuer_seite_und_lauf(self):
        from Genesis9.meshgenesis import G9meshgenesis
        andere = next(w for w, _t in Ai2d3dmeshwahl.WERTE if w != Ai2d3dmeshwahl.VORGABE)
        antwort = self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dmeshwahl.SCHLUESSEL: andere}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        self.assertIn('<option value="%s" selected>' % andere, self._seite())
        self.assertEqual(G9meshgenesis.gewaehlt(), andere)

    def test_unbekannte_portierung_faellt_auf_die_vorgabe(self):
        from Genesis9.meshgenesis import G9meshgenesis
        self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dmeshwahl.SCHLUESSEL: 'smplify'}), content_type='application/json')
        self.assertIn('<option value="%s" selected>' % Ai2d3dmeshwahl.VORGABE, self._seite())
        self.assertEqual(G9meshgenesis.gewaehlt(), Ai2d3dmeshwahl.VORGABE)

    # 28.10.2026 abends, Edgar: „mach deinen Vorschlag“ — der Versatz nach der Einpassung (längs der Normale statt frei je Punkt), bis zum Lauf

    def test_versatz_vorgabe_laengs_der_normale(self):
        from core.dienste.ai2d3dmeshversatz import Ai2d3dmeshversatz
        from Genesis9.meshgenesis import G9meshgenesis
        html = self._seite()
        self.assertIn('name="%s"' % Ai2d3dmeshversatz.SCHLUESSEL, html)
        self.assertIn('<option value="normale" selected>', html)
        for w, text in Ai2d3dmeshversatz.WERTE:
            self.assertIn(text, html)
            self.assertIn(w, G9meshgenesis.VERSATZ)
        self.assertEqual(G9meshgenesis.versatz_gewaehlt(), 'normale')
        self.assertEqual(G9meshgenesis.VERSATZ_VORGABE, Ai2d3dmeshversatz.VORGABE)

    def test_gespeicherter_versatz_gilt_fuer_seite_und_lauf(self):
        from core.dienste.ai2d3dmeshversatz import Ai2d3dmeshversatz
        from Genesis9.meshgenesis import G9meshgenesis
        antwort = self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dmeshversatz.SCHLUESSEL: 'frei'}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        self.assertIn('<option value="frei" selected>', self._seite())
        self.assertEqual(G9meshgenesis.versatz_gewaehlt(), 'frei')

    # 28.10.2026 abends, Edgar: „in den Einstellungen - 2d-3d-ai einstellbar, KopfKI oder iterative MeshKi“

    def test_ki_der_form_vorgabe_kopfki(self):
        from core.dienste.ai2d3dformki import Ai2d3dformki
        html = self._seite()
        self.assertIn('name="%s"' % Ai2d3dformki.SCHLUESSEL, html)
        self.assertIn('<option value="kopfki" selected>', html)
        self.assertIn('<option value="iterativ">', html)
        self.assertEqual(Ai2d3dformki.gewaehlt(), 'kopfki')

    def test_gespeicherte_ki_der_form_gilt(self):
        from core.dienste.ai2d3dformki import Ai2d3dformki
        antwort = self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dformki.SCHLUESSEL: 'iterativ'}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        self.assertIn('<option value="iterativ" selected>', self._seite())
        self.assertEqual(Ai2d3dformki.gewaehlt(), 'iterativ')

    def test_unbekannte_ki_der_form_faellt_auf_kopfki(self):
        from core.dienste.ai2d3dformki import Ai2d3dformki
        self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dformki.SCHLUESSEL: 'smplx'}), content_type='application/json')
        self.assertEqual(Ai2d3dformki.gewaehlt(), 'kopfki')

    def test_unbekannter_versatz_faellt_auf_die_vorgabe(self):
        from core.dienste.ai2d3dmeshversatz import Ai2d3dmeshversatz
        from Genesis9.meshgenesis import G9meshgenesis
        self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dmeshversatz.SCHLUESSEL: 'smpld'}), content_type='application/json')
        self.assertIn('<option value="normale" selected>', self._seite())
        self.assertEqual(G9meshgenesis.versatz_gewaehlt(), 'normale')

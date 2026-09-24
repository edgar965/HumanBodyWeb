# -*- coding: utf-8 -*-
"""Das gebündelte Seitenskript (Szene, BVH Studio): Adresse, Schalter, Ausfallsicherheit.

WARUM (Edgar, 10.09.2026: „laden dauert doch noch immer länger als 10 s!!"):
Die Szene-Seite lud 229 einzelne JS-Module. Jede Anfrage kostet diesen
Server 10–12 ms, und er beantwortet sie nacheinander. Im echten Vordergrund
gemessen (Playwright, Occlusion-Tracking abgeschaltet):

    JS-Anfragen        229  ->  18
    JS-Ladezeit    3.300–5.996 ms  ->    518–1.143 ms
    Figur sichtbar 5.956–8.025 ms  ->  2.170–2.909 ms
    alles fertig  10.807–15.374 ms ->  4.826–6.011 ms

Was hier festgehalten wird:

1. Die Adresse trägt die FASSUNG. Das ist der ganze Schutz gegen einen
   veralteten Stand: Ändert sich eine Datei, ändert sich die Fassung und
   damit die Adresse.
2. Das Bündel liegt NICHT unter `static/`. Läge es dort, änderte sein Bau
   die Fassung und löste den nächsten Bau aus — genau das ist beim ersten
   Versuch passiert (zwei Bündel für eine Änderung).
3. Der Schalter unter Einstellungen → Szene schaltet es ab; ohne
   Einstellung ist es AN.
4. Fehlt esbuild oder scheitert der Lauf, liefert die Seite die
   Einzelmodule. Ein Bündelfehler darf die Seite nie kosten.
5. Die Auslieferung baut NICHT nach: Wer eine alte Adresse anfragt,
   bekommt 404 und lädt neu — sonst bekäme er Code, der nicht zu seiner
   Seite gehört.

ZWEITE SEITE (22.09.2026): BVH Studio lud seine ~290 Module ebenso einzeln —
derselbe Mechanismus jetzt je Seite (`Modulbuendel.EINSTIEGE`), ein
gemeinsamer Ablageordner. Punkt 6 hier: der Bau der einen Seite darf das
Bündel der ANDEREN nicht mitlöschen.
"""

import os
from unittest import mock

from django.test import SimpleTestCase

from ...dienste.modulbuendel import Modulbuendel
from ...templatetags import szenenskript


class ModulbuendelTest(SimpleTestCase):
    def test_die_adresse_traegt_die_fassung(self):
        self.assertEqual(Modulbuendel.adresse('scene', '1789043967'), '/buendel/1789043967/scene.js')

    def test_studio_ist_eine_eigene_seite(self):
        """Zweite Seite, eigener Einstiegspunkt und eigene Adresse."""
        self.assertEqual(Modulbuendel.adresse('studio', '1789043967'), '/buendel/1789043967/studio.js')
        self.assertEqual(Modulbuendel.EINSTIEGE['studio'], 'viewer/studio/index.js')

    def test_zwei_fassungen_sind_zwei_dateien(self):
        """Der Name haengt an der Fassung — sonst gibt es stille Altstaende."""
        self.assertNotEqual(Modulbuendel.dateiname('scene', '111'), Modulbuendel.dateiname('scene', '222'))

    def test_zwei_seiten_sind_zwei_dateien(self):
        """Derselbe Aufbau-Fehler, andersherum: Szene und Studio teilen sich
        den Ablageordner — ihre Dateinamen duerfen nicht kollidieren."""
        self.assertNotEqual(Modulbuendel.dateiname('scene', '111'), Modulbuendel.dateiname('studio', '111'))

    def test_das_buendel_liegt_nicht_in_der_statik(self):
        """Sonst dreht sein Bau die Fassung weiter und loest den naechsten aus."""
        ablage = os.path.abspath(Modulbuendel.ablage())
        statik = os.path.abspath(Modulbuendel.wurzel())
        self.assertFalse(ablage.startswith(statik + os.sep), '%s liegt unter %s' % (ablage, statik))

    def test_ohne_esbuild_bleibt_es_bei_den_einzelmodulen(self):
        with (
            mock.patch.object(Modulbuendel, 'esbuild', return_value=None),
            mock.patch.object(
                Modulbuendel, 'pfad', return_value=os.path.join(Modulbuendel.ablage(), '_gibtsnicht.js')
            ),
        ):
            self.assertIsNone(Modulbuendel.bereit('scene', '999999'))

    def test_der_bau_der_einen_seite_loescht_nicht_die_andere(self):
        """Sabotage-Gegenprobe zum gemeinsamen Ablageordner (22.09.2026-Fund):
        ohne den Praefix-Filter in `_aufraeumen` haette der Studio-Bau das
        Szene-Buendel mitgeraeumt."""
        ordner = Modulbuendel.ablage()
        os.makedirs(ordner, exist_ok=True)
        szene_datei = os.path.join(ordner, 'scene_alt.js')
        with open(szene_datei, 'w', encoding='utf-8') as f:
            f.write('// szene')
        try:
            Modulbuendel._aufraeumen('studio', ordner, 'studio_neu.js')
            self.assertTrue(os.path.isfile(szene_datei), 'Szene-Buendel wurde beim Studio-Aufraeumen gelöscht')
        finally:
            if os.path.isfile(szene_datei):
                os.remove(szene_datei)

    def test_ein_gescheiterter_lauf_kostet_die_seite_nicht(self):
        """Die Marke faellt auf den Einstiegspunkt zurueck, statt zu werfen.

        `_gewuenscht` wird mitgesetzt: Es liest die Einstellung aus der
        Datenbank, und ein Test darf sie nicht anfassen
        (`~/.claude/rules/tests-und-produktivdaten.md`). Ohne das lief der
        Fall nur deshalb durch, weil derselbe Auffangblock auch den
        verbotenen Zugriff schluckte — der Test haette dann etwas anderes
        geprueft, als sein Name sagt.
        """
        with (
            mock.patch.object(szenenskript, '_gewuenscht', return_value=True),
            mock.patch.object(Modulbuendel, 'bereit', side_effect=RuntimeError('Absicht')),
        ):
            adresse = szenenskript.szenenskript()
        self.assertIn(szenenskript.EINZELN, adresse)

    def test_ohne_einstellung_ist_es_eingeschaltet(self):
        """Wer nichts einstellt, bekommt die schnelle Seite."""
        with (
            mock.patch.object(szenenskript, '_gewuenscht', return_value=True),
            mock.patch.object(Modulbuendel, 'bereit', return_value='/buendel/42/scene.js'),
        ):
            self.assertEqual(szenenskript.szenenskript(), '/buendel/42/scene.js')

    def test_studio_nutzt_denselben_schalter(self):
        with (
            mock.patch.object(szenenskript, '_gewuenscht', return_value=True),
            mock.patch.object(Modulbuendel, 'bereit', return_value='/buendel/42/studio.js') as bereit,
        ):
            self.assertEqual(szenenskript.studioskript(), '/buendel/42/studio.js')
        bereit.assert_called_once_with('studio', mock.ANY)

    def test_ausgeschaltet_kommen_die_einzelmodule(self):
        """Gegenprobe zum Schalter — sonst wuerde er nie geprueft."""
        with mock.patch.object(szenenskript, '_gewuenscht', return_value=False):
            adresse = szenenskript.szenenskript()
        self.assertIn(szenenskript.EINZELN, adresse)
        with mock.patch.object(szenenskript, '_gewuenscht', return_value=False):
            adresse = szenenskript.studioskript()
        self.assertIn(szenenskript.EINZELN_STUDIO, adresse)

    def test_eine_fassung_mit_pfadanteilen_wird_abgewiesen(self):
        """Die Fassung kommt aus dem Pfad; „..“ darin fuehrte aus der Ablage."""
        from django.http import Http404

        from ...api.buendel import buendel_datei

        for boese in ('..', '../..', 'a/b', 'abc'):
            with self.assertRaises(Http404, msg=boese):
                buendel_datei(None, boese, 'scene')

    def test_eine_unbekannte_seite_wird_abgewiesen(self):
        from django.http import Http404

        from ...api.buendel import buendel_datei

        with self.assertRaises(Http404):
            buendel_datei(None, '123', 'unbekannt')

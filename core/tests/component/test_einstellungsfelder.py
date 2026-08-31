# -*- coding: utf-8 -*-
u"""Kommt jede registrierte Einstellung so auf ihrer Seite an, wie sie im
Register steht?

WARUM (30.08.2026)
==================
Titel, Erklärung und Grenzen standen an drei Stellen — englischer
`help_text` am Model, deutscher Text als Include-Parameter, Grenzen ein
drittes Mal als `min`/`max` in der Vorlage. Seit dem Umbau ist
`core/daten/einstellungsfelder.py` die eine Quelle.

DIESER TEST IST DIE KLAMMER: Er liest das Register und prüft auf der
echten Seite nach. Ohne ihn merkt niemand, wenn eine Grenze nur noch im
Register steht und die Seite sie nicht mehr ausliefert — die Seite sieht
dann vollständig aus und nimmt jeden Wert an.

DER FALL, DER IHN AUSGELÖST HAT: `{% if min %}` liess `min="0"` weg,
weil 0 falsy ist. `gvhmr_focal_length_mm` hatte danach keine untere
Grenze mehr und nahm negative Brennweiten. Gefunden hat es der
Feld-für-Feld-Vergleich gegen den Stand vorher, nicht der Blick auf die
Seite. Deshalb prüft der Test unten ausdrücklich auch die 0.
"""
import re

from django.test import TestCase

from core.daten.einstellungsfelder import Einstellungsfelder

#: Auf welcher Seite steht welches Feld. Ein Feld darf auf mehreren stehen —
#: `mp_min_*` steht auf der 2D- und der 3D-Seite und ist DIESELBE Spalte.
SEITEN = {
    '/settings/model/': ('progress_update_interval', 'show_rig_config',
                         'show_rig_animations'),
    '/settings/scene/': ('show_rig_scene',),
    '/settings/smpl/': ('smpl_default_wireframe',),
    '/settings/video-to-bvh-2d/': ('mp_min_detection_confidence',
                                   'mp_min_tracking_confidence'),
    '/settings/video-to-bvh-3d/': (
        'v4_hcd_iterations', 'v4_hcd_epochs', 'v4_hcd_learning_rate',
        'v4_smoothing_cutoff', 'v4_smoothing_sampling',
        'mp_min_detection_confidence', 'mp_min_tracking_confidence',
        'gvhmr_static_cam', 'gvhmr_focal_length_mm',
        'wham_estimate_local_only', 'wham_run_smplify',
        'prompthmr_static_camera'),
}


class EinstellungsfelderTest(TestCase):
    u"""Register und ausgelieferte Seite müssen dasselbe sagen."""

    def _felder(self, weg):
        u"""{name: {attribut: wert}} der Eingabefelder einer Seite."""
        antwort = self.client.get(weg)
        self.assertEqual(antwort.status_code, 200, weg)
        html = antwort.content.decode('utf-8')
        raus = {}
        for treffer in re.finditer(r'<input\b([^>]*)>', html):
            angaben = dict(re.findall(r'([\w-]+)="([^"]*)"', treffer.group(1)))
            if 'name' in angaben:
                raus[angaben['name']] = angaben
        return raus

    def test_jedes_feld_traegt_die_grenzen_aus_dem_register(self):
        gepruefte = set()
        for weg, kennungen in SEITEN.items():
            felder = self._felder(weg)
            for kennung in kennungen:
                self.assertIn(kennung, felder,
                              u'%s liefert %s nicht aus' % (weg, kennung))
                soll = Einstellungsfelder.feld(kennung)
                ist = felder[kennung]
                if ist.get('type') == 'checkbox':
                    continue
                for name in ('min', 'max'):
                    erwartet = getattr(soll, name)
                    if erwartet is None:
                        self.assertNotIn(name, ist,
                                         u'%s: %s ist im Register leer'
                                         % (kennung, name))
                    else:
                        self.assertEqual(ist.get(name), str(erwartet),
                                         u'%s auf %s: %s' % (kennung, weg, name))
                self.assertEqual(ist.get('step'), str(soll.schritt or 1),
                                 u'%s auf %s: schritt' % (kennung, weg))
                gepruefte.add(kennung)
        self.assertTrue(gepruefte, u'kein einziges Zahlenfeld geprüft')

    def test_die_grenze_null_faellt_nicht_weg(self):
        u"""`min="0"` ist gültig — `{% if min %}` liesse es weg (0 ist falsy)."""
        self.assertEqual(
            Einstellungsfelder.feld('gvhmr_focal_length_mm').min, 0,
            u'Vorbedingung: dieses Feld hat die untere Grenze 0')
        felder = self._felder('/settings/video-to-bvh-3d/')
        self.assertEqual(felder['gvhmr_focal_length_mm'].get('min'), '0')

    def test_jedes_registrierte_feld_gehoert_zum_model(self):
        u"""Ein Register-Name ohne Model-Feld wirft erst beim Seitenaufruf."""
        from core.models import AppSettings
        namen = {f.name for f in AppSettings._meta.get_fields()}
        for kennung in Einstellungsfelder.REGISTER:
            self.assertIn(kennung, namen,
                          u'%s steht im Register, aber nicht im Model' % kennung)

    def test_jedes_animationsfeld_hat_eine_eigene_kennung(self):
        u"""Zwei Auswahlfelder auf einer Seite brauchen zwei `id`.

        DER FALL (31.08.2026): Beim Umstellen der fünf
        `_einstellungen_animation.html`-Einbindungen auf die Marke
        `{% animation %}` hat mein Ersetzungsmuster (Wortzeichen und Punkt)
        den Bindestrich verschluckt — aus `anim-sel-config` wurde `anim`.
        Danach trugen BEIDE
        Felder auf `/settings/model/` dieselbe `id`, und
        `animationsauswahl.js` (`getElementById`) hätte immer das erste
        erwischt: Wer die Animation der Animationsseite setzt, ändert die der
        Konfigurationsseite. Die Seite sah dabei vollständig aus.
        """
        import re
        for weg, erwartet in (('/settings/model/', 2), ('/settings/scene/', 1),
                              ('/settings/theatre/', 1),
                              ('/settings/result/', 1)):
            antwort = self.client.get(weg)
            self.assertEqual(antwort.status_code, 200, weg)
            kennungen = re.findall(
                r'class="anim-auswahl" id="([\w-]+)"',
                antwort.content.decode('utf-8'))
            self.assertEqual(len(kennungen), erwartet, weg)
            self.assertEqual(len(set(kennungen)), len(kennungen),
                             u'%s: doppelte Kennung %s' % (weg, kennungen))
            for kennung in kennungen:
                self.assertNotEqual(kennung, 'anim',
                                    u'%s: die Kennung ist abgeschnitten' % weg)

    def test_erklaerung_und_hilfetext_sind_dieselbe_quelle(self):
        u"""Der `help_text` am Model kommt aus dem Register — nicht daneben."""
        from core.models import AppSettings
        for kennung, feld in Einstellungsfelder.REGISTER.items():
            modelfeld = AppSettings._meta.get_field(kennung)
            self.assertEqual(modelfeld.help_text, feld.hilfetext,
                             u'%s: help_text weicht vom Register ab' % kennung)

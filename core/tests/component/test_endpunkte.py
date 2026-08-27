# -*- coding: utf-8 -*-
"""Endpunkt-Proben — abgeleitet von `djangobase.endpunkttests.EndpunktProbe`.

WARUM DIESE DATEI (17.08.2026)
------------------------------
Das Werkzeug `testdeckung` hielt die URL-Tabelle gegen alle Testtexte und meldete
**87 Endpunkte, die in keinem einzigen Test vorkamen**. Zwei echte Fehler hingen
daran, und beide fand erst ein Aufruf:

* `/process/<uuid>/delete/` löschte Auftrag UND Dateien auf ein **GET** hin.
  In der Liste stand ein `<a href>` mit `onclick="return confirm(…)"` — das
  schützt genau einen Fall: den menschlichen Klick.
* `/library/scan/` las auf GET 7.067 BVH-Köpfe und schrieb die Bibliothek neu.

ABGELEITET, NICHT NACHGEBAUT (Ansage 17.08.2026: „Halte dich an die djangoBase
test implementierung und baue nichts neues, leite nur ab")
-----------------------------------------------------------------------------
Die erste Fassung hatte eine eigene Tabelle mit eigenen Prüfungen. Jetzt kommt
alles aus `EndpunktProbe`:

    Route auflösbar und zeigt auf die genannte View
    LESEN-Endpunkte werden angefahren -> kein 5xx
    WIRKUNG-Endpunkte werden NICHT ausgelöst, nur geprüft
    der Verzicht steht im Protokoll (sonst sieht die Deckung vollständig aus)

ZWEI ABWEICHUNGEN, BEIDE BEGRÜNDET
----------------------------------
1. **`test_kein_endpunkt_ist_ohne_anmeldung_erreichbar` ist hier gegenstandslos.**
   HumanBodyWeb hat keine Anmeldung (`DJANGOBASE["zugriff"] = "none"`, siehe
   `ui/settings/djangobase_conf.py`); ALLE Seiten sind offen. Die Basisprüfung
   würde jeden Leseendpunkt als Loch melden. Sie wird deshalb überschrieben und
   begründet — nicht stillschweigend übergangen.
2. **Der Methodenschutz wird zusätzlich geprüft.** `EndpunktProbe` löst wirkende
   Endpunkte gar nicht aus; dass ein GET darauf mit 405 abgewiesen WIRD, ist hier
   aber die eigentliche Absicherung (siehe die zwei Fehler oben). Ein GET ist
   dafür ungefährlich: Es wird ja gerade abgewiesen.

Die Verteilung ist gemessen (`Docu/umbau/endpunkt_tabelle.py`), nicht geraten:
119 Routen, davon 43 mit Methodenschutz (die eigene Test-API
`/api/tests/run/` ist am 17.08.2026 entfallen — die Fälle sind jetzt
reguläre Django-Tests).
"""

import logging

from djangobase.endpunkttests import EndpunktProbe, LESEN, WIRKUNG
from django.test import Client, override_settings

logger = logging.getLogger('core')


@override_settings(ALLOWED_HOSTS=['*'])
class EndpunkteTest(EndpunktProbe):
    """Alle 119 API-Routen — lesende angefahren, wirkende nur geprüft."""

    #: So viele Routen weisen ein GET ab. Die Zahl steht hier ausgeschrieben:
    #: Sinkt sie, hat jemand einen Methodenschutz verloren — und das ist der
    #: Fehler, der `delete_job` und `scan_bvh_files` gekostet hat.
    NUR_POST_ANZAHL = 43

    ENDPUNKTE = [
        (LESEN, 'animationen_der_kategorie', '/api/animationen/probe/'),
        (LESEN, 'bvh_gesicht', '/api/bvh-face/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'bvh', '/api/bvh/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'test_character_mesh', '/api/character-test/mesh/'),
        (LESEN, 'test_character_morphs', '/api/character-test/morphs/'),
        (LESEN, 'test_reload', '/api/character-test/reload/'),
        (LESEN, 'test_character_rigify_skeleton', '/api/character-test/rigify-skeleton/'),
        (LESEN, 'test_character_skin_weights', '/api/character-test/skin-weights/'),
        (LESEN, 'test_character_source', '/api/character-test/source/'),
        (WIRKUNG, 'test_switch_character', '/api/character-test/switch/'),
        (LESEN, 'test_version_info', '/api/character-test/version/'),
        (WIRKUNG, 'analysieren', '/api/character/analyze-photo/'),
        (LESEN, 'backendzustand', '/api/character/analyze-photo/status/'),
        (WIRKUNG, 'animation_save', '/api/character/animation/save/'),
        (LESEN, 'character_animations', '/api/character/animations/'),
        (LESEN, 'character_asset_glb', '/api/character/asset/probe/'),
        (WIRKUNG, 'bvh_verwalten', '/api/character/bvh-manage/'),
        (LESEN, 'character_bvh_file_cat', '/api/character/bvh/probe/probe/'),
        (LESEN, 'character_bvh_file', '/api/character/bvh/probe/'),
        (LESEN, 'kleider', '/api/character/charmorph-assets/'),
        (LESEN, 'frisuren', '/api/character/charmorph-hairstyles/'),
        (LESEN, 'koerpertypen', '/api/character/charmorph-presets/'),
        (LESEN, 'character_cloth', '/api/character/cloth/'),
        (LESEN, 'cloth_preset_list', '/api/character/cloth/presets/'),
        (LESEN, 'cloth_preset_detail', '/api/character/cloth/presets/probe/probe/'),
        (WIRKUNG, 'cloth_preset_save', '/api/character/cloth/presets/save/'),
        (LESEN, 'character_cloth_regions', '/api/character/cloth/regions/'),
        (WIRKUNG, 'herunterladen', '/api/character/garment/download/'),
        (WIRKUNG, 'ausgabeordner', '/api/character/garment/export/'),
        (LESEN, 'garment_fit', '/api/character/garment/fit/'),
        (LESEN, 'bestand', '/api/character/garment/library/'),
        (LESEN, 'neu_einlesen', '/api/character/garment/library/rescan/'),
        (WIRKUNG, 'verwalten', '/api/character/garment/manage/'),
        (LESEN, 'textur', '/api/character/garment/texture/probe/probe/'),
        (LESEN, 'vorschaubild', '/api/character/garment/thumb/probe/'),
        (LESEN, 'frisur_glb', '/api/character/hairstyle/probe/'),
        (LESEN, 'frisuren', '/api/character/hairstyles/'),
        (LESEN, 'character_mesh', '/api/character/mesh/'),
        (LESEN, 'mh_proxy_fit', '/api/character/mh-proxy-fit/'),
        (WIRKUNG, 'mh_push_outside', '/api/character/mh-push-outside/'),
        (LESEN, 'dateiliste', '/api/character/model-files/'),
        (LESEN, 'modell', '/api/character/model/probe/'),
        (WIRKUNG, 'modell_sichern', '/api/character/model/save/'),
        (LESEN, 'modellliste', '/api/character/models/'),
        (LESEN, 'character_morphs', '/api/character/morphs/'),
        (WIRKUNG, 'pattern_generate', '/api/character/pattern/generate/'),
        (LESEN, 'pattern_region_generate', '/api/character/pattern/region/generate/'),
        (WIRKUNG, 'pattern_save', '/api/character/pattern/save/'),
        (LESEN, 'pattern_specification', '/api/character/pattern/specification/'),
        (LESEN, 'daten', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'loeschen', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/delete/'),
        (LESEN, 'erneut_analysieren', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/reprocess/'),
        (WIRKUNG, 'photo_save_alignment', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/save-alignment/'),
        (WIRKUNG, 'photo_save_projection', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/save-projection/'),
        (WIRKUNG, 'bild_sichern', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/screenshot/'),
        (LESEN, 'photo_silhouette_data', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/silhouette/'),
        (WIRKUNG, 'mehrere_loeschen', '/api/character/photo-jobs/bulk-delete/'),
        (WIRKUNG, 'pose_manage', '/api/character/pose-manage/'),
        (LESEN, 'pose_load', '/api/character/pose/probe/'),
        (LESEN, 'list_poses', '/api/character/poses/'),
        (WIRKUNG, 'retarget_bvh_text', '/api/character/retarget-bvh-text/'),
        (LESEN, 'bibliotheks_bvh', '/api/character/retarget-bvh/probe/probe/'),
        (LESEN, 'zuordnungstabellen', '/api/character/retarget-config/'),
        (LESEN, 'auftrag_zusammenfuehren', '/api/character/retarget-job-merge/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'auftrags_bvh', '/api/character/retarget-job/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'zusammenfuehren', '/api/character/retarget-merge/'),
        (LESEN, 'character_rig', '/api/character/rig/'),
        (LESEN, 'character_rigify_skeleton', '/api/character/rigify-skeleton/'),
        (WIRKUNG, 'save_bvh_text', '/api/character/save-bvh-text/'),
        (LESEN, 'szene', '/api/character/scene/probe/'),
        (WIRKUNG, 'szene_sichern', '/api/character/scene/save/'),
        (LESEN, 'szenenliste', '/api/character/scenes/'),
        (LESEN, 'character_skin_weights', '/api/character/skin-weights/'),
        (WIRKUNG, 'smplx_mesh', '/api/character/smplx-mesh/'),
        (LESEN, 'smplx_texture', '/api/character/smplx-texture/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'tpose_vertices', '/api/character/tpose-vertices/'),
        (WIRKUNG, 'vertex_edit_push_outside', '/api/character/vertex-edit/push-outside/'),
        (WIRKUNG, 'vertex_edit_smooth', '/api/character/vertex-edit/smooth/'),
        (LESEN, 'character_wardrobe', '/api/character/wardrobe/'),
        (WIRKUNG, 'export_cloth', '/api/cloth/export/'),
        (LESEN, 'erkennungsdaten', '/api/detection/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'loeschen', '/api/job/00000000-0000-0000-0000-000000000001/delete/'),
        (WIRKUNG, 'starten', '/api/job/00000000-0000-0000-0000-000000000001/start/'),
        (LESEN, 'zustand', '/api/job/00000000-0000-0000-0000-000000000001/status/'),
        (WIRKUNG, 'anhalten', '/api/job/00000000-0000-0000-0000-000000000001/stop/'),
        (WIRKUNG, 'aus_datei', '/api/job/create-from-file/'),
        (WIRKUNG, 'mehrere_loeschen', '/api/jobs/bulk-delete/'),
        (LESEN, 'punkte_2d', '/api/keypoints/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'browsermeldung', '/api/log/'),
        (LESEN, 'ueberlagerungsvideo', '/api/overlay-video/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'umsetzen', '/api/retarget/'),
        (WIRKUNG, 'save_bvh_effects', '/api/retarget/save-bvh-effects/'),
        (WIRKUNG, 'smooth_bvh', '/api/retarget/smooth-bvh/'),
        (LESEN, 'skelettvideo', '/api/rig-video/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'vorgaben', '/api/settings/humanbody/'),
        (LESEN, 'einstellungen', '/api/settings/smpl/'),
        (WIRKUNG, 'einstellungen_sichern', '/api/settings/smpl/save/'),
        (LESEN, 'theatre_einstellungen', '/api/settings/theatre/'),
        (LESEN, 'koerpernetz', '/api/smpl/body/'),
        (LESEN, 'kleid_anpassen', '/api/smpl/garment/fit/'),
        (LESEN, 'kleiderbestand', '/api/smpl/garment/library/'),
        (LESEN, 'kleidernetz', '/api/smpl/garment/mesh/'),
        (LESEN, 'vorschaubild', '/api/smpl/garment/thumb/probe/'),
        (WIRKUNG, 'ton_hochladen', '/api/studio/audio-upload/'),
        (LESEN, 'bodentexturen', '/api/studio/floor-textures/'),
        (LESEN, 'projektliste', '/api/studio/project-list/'),
        (LESEN, 'projekt_laden', '/api/studio/project-load/'),
        (WIRKUNG, 'projekt_sichern', '/api/studio/project-save/'),
        (WIRKUNG, 'objekt_hochladen', '/api/studio/scene-object-upload/'),
        (LESEN, 'lichtvorgabe', '/api/studio/theatre-preset/probe/'),
        (LESEN, 'lichtvorgaben', '/api/studio/theatre-presets/'),
        (WIRKUNG, 'theatre_convert_video', '/api/theatre/convert-video/'),
        (WIRKUNG, 'theatre_encode_frames', '/api/theatre/encode-frames/'),
        (WIRKUNG, 'theatre_render_video', '/api/theatre/render-video/'),
        (LESEN, 'vorschaubild', '/api/thumbnail/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'vorgabe_sichern', '/api/ui-pref/'),
        (LESEN, 'ui_prefs_api', '/api/ui-prefs/'),
        (LESEN, 'video', '/api/video/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'video3d_sichern', '/api/video3d/00000000-0000-0000-0000-000000000001/'),
    ]

    def setUp(self):
        # Ohne Anmeldung: Das Projekt hat keine (siehe Modul-Docstring). Die
        # Basisklasse legt in `setUpTestData` einen Prüfer an und meldet ihn in
        # `test_lesende_endpunkte_…` an — das schadet hier nicht.
        super().setUp()

    def test_kein_endpunkt_ist_ohne_anmeldung_erreichbar(self):
        """Gegenstandslos in diesem Projekt — mit Beleg statt stillem Übergehen.

        HumanBodyWeb läuft ohne Anmeldung (`zugriff: none`). Die Prüfung der
        Basisklasse würde deshalb JEDEN lesenden Endpunkt melden. Statt sie zu
        löschen, hält dieser Test die Bedingung fest: Sobald das Projekt eine
        Anmeldung bekommt, wird er rot und die Basisprüfung muss greifen.
        """
        from djangobase.conf import conf
        self.assertEqual(conf()['zugriff'], 'none',
                         'Das Projekt hat jetzt eine Anmeldung — die Prüfung '
                         'der Basisklasse muss wieder greifen (Aufruf von '
                         'super() hier einsetzen).')

    def test_der_methodenschutz_bleibt(self):
        """Jede wirkende Route weist ein GET ab (405) — und es sind noch so viele.

        Ein GET ist hier ungefährlich: Genau das wird abgewiesen. Wird aus einem
        405 ein 200 oder 302, hat jemand `@require_POST` entfernt.
        """
        offen = []
        for art, ziel, muster in self.ENDPUNKTE:
            if art != WIRKUNG:
                continue
            antwort = Client().get(self._konkret(muster))
            if antwort.status_code != 405:
                offen.append('%s (%s): HTTP %s statt 405'
                             % (ziel, muster, antwort.status_code))
        self.assertEqual(offen, [], 'Methodenschutz verloren: %s' % offen)
        self.assertEqual(
            sum(1 for art, _z, _p in self.ENDPUNKTE if art == WIRKUNG),
            self.NUR_POST_ANZAHL,
            'Zahl der GET-abweisenden Routen hat sich geändert')

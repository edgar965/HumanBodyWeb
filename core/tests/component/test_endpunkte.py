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
        (LESEN, 'serve_bvh_face', '/api/bvh-face/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'serve_bvh_file', '/api/bvh/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'test_character_mesh', '/api/character-test/mesh/'),
        (LESEN, 'test_character_morphs', '/api/character-test/morphs/'),
        (LESEN, 'test_reload', '/api/character-test/reload/'),
        (LESEN, 'test_character_rigify_skeleton', '/api/character-test/rigify-skeleton/'),
        (LESEN, 'test_character_skin_weights', '/api/character-test/skin-weights/'),
        (LESEN, 'test_character_source', '/api/character-test/source/'),
        (WIRKUNG, 'test_switch_character', '/api/character-test/switch/'),
        (LESEN, 'test_version_info', '/api/character-test/version/'),
        (WIRKUNG, 'analyze_photo', '/api/character/analyze-photo/'),
        (LESEN, 'analyze_photo_status', '/api/character/analyze-photo/status/'),
        (WIRKUNG, 'animation_save', '/api/character/animation/save/'),
        (LESEN, 'character_animations', '/api/character/animations/'),
        (LESEN, 'character_asset_glb', '/api/character/asset/probe/'),
        (WIRKUNG, 'bvh_manage', '/api/character/bvh-manage/'),
        (LESEN, 'character_bvh_file_cat', '/api/character/bvh/probe/probe/'),
        (LESEN, 'character_bvh_file', '/api/character/bvh/probe/'),
        (LESEN, 'charmorph_assets', '/api/character/charmorph-assets/'),
        (LESEN, 'charmorph_hairstyles', '/api/character/charmorph-hairstyles/'),
        (LESEN, 'charmorph_presets', '/api/character/charmorph-presets/'),
        (LESEN, 'character_cloth', '/api/character/cloth/'),
        (LESEN, 'cloth_preset_list', '/api/character/cloth/presets/'),
        (LESEN, 'cloth_preset_detail', '/api/character/cloth/presets/probe/probe/'),
        (WIRKUNG, 'cloth_preset_save', '/api/character/cloth/presets/save/'),
        (LESEN, 'character_cloth_regions', '/api/character/cloth/regions/'),
        (WIRKUNG, 'garment_download', '/api/character/garment/download/'),
        (WIRKUNG, 'garment_export', '/api/character/garment/export/'),
        (LESEN, 'garment_fit', '/api/character/garment/fit/'),
        (LESEN, 'garment_library', '/api/character/garment/library/'),
        (LESEN, 'garment_library_rescan', '/api/character/garment/library/rescan/'),
        (WIRKUNG, 'garment_manage', '/api/character/garment/manage/'),
        (LESEN, 'garment_texture', '/api/character/garment/texture/probe/probe/'),
        (LESEN, 'garment_thumbnail', '/api/character/garment/thumb/probe/'),
        (LESEN, 'character_hairstyle_glb', '/api/character/hairstyle/probe/'),
        (LESEN, 'character_hairstyles', '/api/character/hairstyles/'),
        (LESEN, 'character_mesh', '/api/character/mesh/'),
        (LESEN, 'mh_proxy_fit', '/api/character/mh-proxy-fit/'),
        (WIRKUNG, 'mh_push_outside', '/api/character/mh-push-outside/'),
        (LESEN, 'model_files', '/api/character/model-files/'),
        (LESEN, 'character_model_detail', '/api/character/model/probe/'),
        (WIRKUNG, 'character_model_save', '/api/character/model/save/'),
        (LESEN, 'character_models', '/api/character/models/'),
        (LESEN, 'character_morphs', '/api/character/morphs/'),
        (WIRKUNG, 'pattern_generate', '/api/character/pattern/generate/'),
        (LESEN, 'pattern_region_generate', '/api/character/pattern/region/generate/'),
        (WIRKUNG, 'pattern_save', '/api/character/pattern/save/'),
        (LESEN, 'pattern_specification', '/api/character/pattern/specification/'),
        (LESEN, 'photo_analysis_job_data', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'photo_analysis_delete', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/delete/'),
        (LESEN, 'photo_analysis_reprocess', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/reprocess/'),
        (WIRKUNG, 'photo_save_alignment', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/save-alignment/'),
        (WIRKUNG, 'photo_save_projection', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/save-projection/'),
        (WIRKUNG, 'photo_analysis_save_screenshot', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/screenshot/'),
        (LESEN, 'photo_silhouette_data', '/api/character/photo-job/00000000-0000-0000-0000-000000000001/silhouette/'),
        (WIRKUNG, 'photo_analysis_bulk_delete', '/api/character/photo-jobs/bulk-delete/'),
        (WIRKUNG, 'pose_manage', '/api/character/pose-manage/'),
        (LESEN, 'pose_load', '/api/character/pose/probe/'),
        (LESEN, 'list_poses', '/api/character/poses/'),
        (WIRKUNG, 'retarget_bvh_text', '/api/character/retarget-bvh-text/'),
        (LESEN, 'retarget_bvh', '/api/character/retarget-bvh/probe/probe/'),
        (LESEN, 'retarget_config', '/api/character/retarget-config/'),
        (LESEN, 'retarget_job_merge', '/api/character/retarget-job-merge/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'retarget_job_bvh', '/api/character/retarget-job/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'retarget_merge', '/api/character/retarget-merge/'),
        (LESEN, 'character_rig', '/api/character/rig/'),
        (LESEN, 'character_rigify_skeleton', '/api/character/rigify-skeleton/'),
        (WIRKUNG, 'save_bvh_text', '/api/character/save-bvh-text/'),
        (LESEN, 'scene_detail', '/api/character/scene/probe/'),
        (WIRKUNG, 'scene_save', '/api/character/scene/save/'),
        (LESEN, 'scene_list', '/api/character/scenes/'),
        (LESEN, 'character_skin_weights', '/api/character/skin-weights/'),
        (WIRKUNG, 'smplx_mesh', '/api/character/smplx-mesh/'),
        (LESEN, 'smplx_texture', '/api/character/smplx-texture/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'tpose_vertices', '/api/character/tpose-vertices/'),
        (WIRKUNG, 'vertex_edit_push_outside', '/api/character/vertex-edit/push-outside/'),
        (WIRKUNG, 'vertex_edit_smooth', '/api/character/vertex-edit/smooth/'),
        (LESEN, 'character_wardrobe', '/api/character/wardrobe/'),
        (WIRKUNG, 'export_cloth', '/api/cloth/export/'),
        (LESEN, 'serve_detection_data', '/api/detection/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'delete_job_api', '/api/job/00000000-0000-0000-0000-000000000001/delete/'),
        (WIRKUNG, 'api_start_processing', '/api/job/00000000-0000-0000-0000-000000000001/start/'),
        (LESEN, 'job_status_api', '/api/job/00000000-0000-0000-0000-000000000001/status/'),
        (WIRKUNG, 'api_stop_processing', '/api/job/00000000-0000-0000-0000-000000000001/stop/'),
        (WIRKUNG, 'create_job_from_file', '/api/job/create-from-file/'),
        (WIRKUNG, 'bulk_delete_jobs', '/api/jobs/bulk-delete/'),
        (LESEN, 'serve_keypoints_2d', '/api/keypoints/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'client_log', '/api/log/'),
        (LESEN, 'save_overlay_video', '/api/overlay-video/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'retarget', '/api/retarget/'),
        (WIRKUNG, 'save_bvh_effects', '/api/retarget/save-bvh-effects/'),
        (WIRKUNG, 'smooth_bvh', '/api/retarget/smooth-bvh/'),
        (LESEN, 'save_rig_video', '/api/rig-video/00000000-0000-0000-0000-000000000001/'),
        (LESEN, 'humanbody_settings_api', '/api/settings/humanbody/'),
        (LESEN, 'smpl_settings_api', '/api/settings/smpl/'),
        (WIRKUNG, 'smpl_settings_save', '/api/settings/smpl/save/'),
        (LESEN, 'theatre_settings_api', '/api/settings/theatre/'),
        (LESEN, 'smpl_body_mesh', '/api/smpl/body/'),
        (LESEN, 'smpl_garment_fit', '/api/smpl/garment/fit/'),
        (LESEN, 'smpl_garment_library', '/api/smpl/garment/library/'),
        (LESEN, 'smpl_garment_mesh', '/api/smpl/garment/mesh/'),
        (LESEN, 'smpl_garment_thumbnail', '/api/smpl/garment/thumb/probe/'),
        (WIRKUNG, 'studio_audio_upload', '/api/studio/audio-upload/'),
        (LESEN, 'studio_floor_textures', '/api/studio/floor-textures/'),
        (LESEN, 'studio_project_list', '/api/studio/project-list/'),
        (LESEN, 'studio_project_load', '/api/studio/project-load/'),
        (WIRKUNG, 'studio_project_save', '/api/studio/project-save/'),
        (WIRKUNG, 'studio_scene_object_upload', '/api/studio/scene-object-upload/'),
        (LESEN, 'studio_theatre_preset_detail', '/api/studio/theatre-preset/probe/'),
        (LESEN, 'studio_theatre_presets', '/api/studio/theatre-presets/'),
        (WIRKUNG, 'theatre_convert_video', '/api/theatre/convert-video/'),
        (WIRKUNG, 'theatre_encode_frames', '/api/theatre/encode-frames/'),
        (WIRKUNG, 'theatre_render_video', '/api/theatre/render-video/'),
        (LESEN, 'video_thumbnail', '/api/thumbnail/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'ui_pref_save', '/api/ui-pref/'),
        (LESEN, 'ui_prefs_api', '/api/ui-prefs/'),
        (LESEN, 'serve_video_file', '/api/video/00000000-0000-0000-0000-000000000001/'),
        (WIRKUNG, 'save_video3d', '/api/video3d/00000000-0000-0000-0000-000000000001/'),
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

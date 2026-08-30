from django.urls import path
from .api import einstellungen, seiten
# Die drei Seiten MIT Logik stehen als je eine Klasse in eigenen Modulen —
# `seiten.py` fuehrt nur noch die reinen Vorlagen (Umbau 17.08.2026).
from .api import (seite_bvhstudio_einstellungen, seite_fotoauftraege,
                  seite_theatre_einstellungen)
from .cloth_export_api import Stoffexport
from .api.testfigur import Testendpunkte, Testverwaltung
from .api.dateien import Auftragsdateien
from .api.auftraege import Auftragsendpunkte
from .api.seiten_web import Webseiten
from .api.retarget import Retargetendpunkte
from .api.smpl import Smplendpunkte
from .api.studio import Studioendpunkte
from .api.studio_projekt import Studioprojekte
from .api.system import Systemendpunkte
from .api.bibliothek import Bibliotheksendpunkte
from .api.bvhtext import Bvhtext
from .api.ui_vorgaben import Uivorgaben
from .api.auftrag_upload import Uploadseiten
from .api.studio_video import Theatrevideo
from .urls_charakter import CHARAKTER

urlpatterns = [
    path('', Webseiten.start, name='dashboard'),
    # Die Auslastungs-Leiste (GPU/VRAM/Temp/CPU/RAM/Netz) hat hier KEINEN Endpunkt
    # mehr: sie kommt seit 12.08.2026 aus djangoBase und antwortet unter
    # /hilfe/api/system-stats/ (ui/urls.py bindet djangobase.urls dort ein).
    path('process/', Uploadseiten.zweid, name='upload'),
    path('process/VideoToBVH/', Uploadseiten.dreid, name='upload_v4'),
    path('process/list/', Webseiten.fertigliste, name='processed'),
    path('process/result/', Webseiten.ergebnisauswahl, name='standalone_result'),
    path('process/<uuid:job_id>/', Webseiten.auftragsseite, name='job_status'),
    path('process/<uuid:job_id>/start/', Auftragsendpunkte.starten_formular,
         name='start_processing'),
    path('process/<uuid:job_id>/stop/', Auftragsendpunkte.anhalten_formular,
         name='stop_processing'),
    path('process/<uuid:job_id>/result/', Webseiten.ergebnisseite, name='job_result'),
    path('process/<uuid:job_id>/delete/', Auftragsendpunkte.loeschen_formular,
         name='delete_job'),
    path('api/bvh/<uuid:job_id>/', Auftragsdateien.bvh, name='serve_bvh'),
    path('api/bvh-face/<uuid:job_id>/', Auftragsdateien.bvh_gesicht,
         name='serve_bvh_face'),
    path('api/video/<uuid:job_id>/', Auftragsdateien.video, name='serve_video'),
    path('api/thumbnail/<uuid:job_id>/', Auftragsdateien.vorschaubild,
         name='video_thumbnail'),
    path('api/detection/<uuid:job_id>/', Auftragsdateien.erkennungsdaten,
         name='serve_detection'),
    path('api/keypoints/<uuid:job_id>/', Auftragsdateien.punkte_2d,
         name='serve_keypoints'),
    path('api/rig-video/<uuid:job_id>/', Auftragsdateien.skelettvideo,
         name='save_rig_video'),
    path('api/overlay-video/<uuid:job_id>/', Auftragsdateien.ueberlagerungsvideo,
         name='save_overlay_video'),
    path('api/video3d/<uuid:job_id>/', Auftragsdateien.video3d_sichern,
         name='save_video3d'),
    path('test/mocapnet/', Webseiten.werkzeugstatus, name='test_mocapnet'),
    path('library/', Webseiten.bvhbibliothek, name='library'),
    path('library/scan/', Bibliotheksendpunkte.einlesen, name='scan_bvh'),
    path('library/<int:pk>/delete/', Bibliotheksendpunkte.loeschen, name='delete_bvh'),
    path('library/<int:pk>/blender/', Bibliotheksendpunkte.in_blender_oeffnen,
         name='open_in_blender'),
    path('webcam/', Webseiten.webcam, name='webcam'),
    path('settings/', Webseiten.einstellungen, name='settings'),
    path('settings/model/', einstellungen.app_settings_model, name='settings_model'),
    path('settings/result/', einstellungen.app_settings_result, name='settings_result'),
    path('settings/scene/', einstellungen.app_settings_scene, name='settings_scene'),
    path('settings/video-to-bvh/', Webseiten.einstellungen_videobvh,
         name='settings_videobvh'),
    path('settings/video-to-bvh-2d/', einstellungen.app_settings_videobvh_2d,
         name='settings_videobvh_2d'),
    path('settings/video-to-bvh-3d/', einstellungen.app_settings_videobvh_3d,
         name='settings_videobvh_3d'),
    path('settings/smpl/', einstellungen.app_settings_smpl, name='settings_smpl'),
    path('settings/theatre/', seite_theatre_einstellungen.theatre_settings_page,
         name='settings_theatre'),
    path('settings/bvh-studio/', seite_bvhstudio_einstellungen.bvh_studio_settings_page,
         name='settings_bvh_studio'),
    path('api/job/<uuid:job_id>/start/', Auftragsendpunkte.starten,
         name='api_start_processing'),
    path('api/job/<uuid:job_id>/stop/', Auftragsendpunkte.anhalten,
         name='api_stop_processing'),
    path('api/job/<uuid:job_id>/status/', Auftragsendpunkte.zustand,
         name='job_status_api'),
    path('api/job/<uuid:job_id>/delete/', Auftragsendpunkte.loeschen,
         name='delete_job_api'),
    path('api/jobs/bulk-delete/', Auftragsendpunkte.mehrere_loeschen,
         name='bulk_delete_jobs'),
    path('api/job/create-from-file/', Auftragsendpunkte.aus_datei,
         name='create_job_from_file'),

    # HumanBody
    path('humanbody/photo-to-3d/', seiten.photo_to_3d_page, name='photo_to_3d'),
    path('humanbody/photo-to-3d/jobs/', seite_fotoauftraege.photo_analysis_jobs_page,
         name='photo_analysis_jobs'),
    path('humanbody/config/', seiten.character_viewer, name='humanbody_config'),
    path('humanbody/scene/', seiten.scene_config, name='humanbody_scene'),
    path('humanbody/scene-model/', seiten.scene_model, name='humanbody_scene_model'),
    path('humanbody/theatre/', seiten.theatre_page, name='theatre'),
    path('humanbody/bvh-studio/', seiten.bvh_studio_page, name='bvh_studio'),
    path('humanbody/theatre-studio/', seiten.theatre_studio_page,
         name='theatre_studio'),
    path('humanbody/theatre/help/', seiten.theatre_help_page, name='theatre_help'),
    path('humanbody/rigging/help/', seiten.rigging_help_page, name='rigging_help'),
    path('api/ui-pref/', Systemendpunkte.vorgabe_sichern, name='ui_pref_save'),
    path('humanbody/animations/', seiten.animations_page, name='humanbody_animations'),
    path('humanbody/test-animation/', seiten.test_animation_page,
         name='test_animation'),
    path('humanbody/test-character/', seiten.test_character_page,
         name='test_character'),
    path('api/retarget/', Retargetendpunkte.umsetzen, name='retarget'),
    path('api/log/', Systemendpunkte.browsermeldung, name='client_log'),
    path('api/retarget/smooth-bvh/', Bvhtext.glaetten, name='smooth_bvh'),
    path('api/retarget/save-bvh-effects/', Bvhtext.effekte_sichern,
         name='save_bvh_effects'),
    path('api/cloth/export/', Stoffexport.ausfuehren, name='cloth_export'),
    path('api/studio/audio-upload/', Studioendpunkte.ton_hochladen,
         name='studio_audio_upload'),
    path('api/studio/project-save/', Studioprojekte.projekt_sichern,
         name='studio_project_save'),
    path('api/studio/project-load/', Studioprojekte.projekt_laden,
         name='studio_project_load'),
    path('api/studio/project-list/', Studioprojekte.projektliste,
         name='studio_project_list'),
    path('api/studio/theatre-presets/', Studioendpunkte.lichtvorgaben,
         name='studio_theatre_presets'),
    path('api/studio/theatre-preset/<str:name>/', Studioendpunkte.lichtvorgabe,
         name='studio_theatre_preset_detail'),
    path('api/studio/scene-object-upload/', Studioendpunkte.objekt_hochladen,
         name='studio_scene_object_upload'),
    path('api/studio/floor-textures/', Studioendpunkte.bodentexturen,
         name='studio_floor_textures'),
    path('api/settings/humanbody/', Systemendpunkte.vorgaben,
         name='humanbody_settings_api'),
    path('api/settings/theatre/', Studioendpunkte.theatre_einstellungen,
         name='theatre_settings_api'),
    path('api/theatre/convert-video/', Theatrevideo.umwandeln,
         name='theatre_convert_video'),
    path('api/theatre/render-video/', Theatrevideo.aufnehmen,
         name='theatre_render_video'),
    path('api/theatre/encode-frames/', Theatrevideo.bilder_kodieren,
         name='theatre_encode_frames'),
    path('api/settings/smpl/', Smplendpunkte.einstellungen, name='smpl_settings_api'),
    path('api/settings/smpl/save/', Smplendpunkte.einstellungen_sichern,
         name='smpl_settings_save'),
    path('api/ui-prefs/', Uivorgaben.vorlieben, name='ui_prefs_api'),
    path('api/animationen/<str:kategorie>/', Uivorgaben.animationen,
         name='animationen_der_kategorie'),
    # CharMorph
    # Cloth
    # Vertex Editor
    # Pattern Editor
    # Hair
    # Garment Fitter
    # SMPL Garments
    path('humanbody/test-smpl/', seiten.smpl_test_page, name='test_smpl'),
    # Hilfe (Logs/Versionen/Tests/Werkzeuge) aus djangoBase:
    # /hilfe/ -> djangobase.urls (ui/urls.py)

    # Test Character API (isolated version from TestCharakter/)
    path('api/character-test/mesh/', Testendpunkte.netz, name='test_character_mesh'),
    path('api/character-test/morphs/', Testendpunkte.regler,
         name='test_character_morphs'),
    path('api/character-test/skin-weights/', Testendpunkte.hautgewichte,
         name='test_character_skin_weights'),
    path('api/character-test/rigify-skeleton/', Testendpunkte.def_skelett,
         name='test_character_rigify_skeleton'),
    path('api/character-test/version/', Testverwaltung.fassung,
         name='test_version_info'),
    path('api/character-test/source/', Testverwaltung.quelltext,
         name='test_character_source'),
    path('api/character-test/reload/', Testverwaltung.neu_laden, name='test_reload'),
    path('api/character-test/switch/', Testverwaltung.figur_wechseln,
         name='test_switch_character'),
]

# Die Charakter- und SMPL-Routen stehen in `urls_charakter.py` —
# 74 Eintraege, die zusammengehoeren (30.08.2026).
urlpatterns += CHARAKTER

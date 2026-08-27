from django.urls import path
from .api import einstellungen, seiten
# Die drei Seiten MIT Logik stehen als je eine Klasse in eigenen Modulen —
# `seiten.py` fuehrt nur noch die reinen Vorlagen (Umbau 17.08.2026).
from .api import (seite_bvhstudio_einstellungen, seite_fotoauftraege,
                  seite_theatre_einstellungen)
from .api.charmorph_bestand import CharmorphBestand
from .cloth_export_api import Stoffexport
from .api.testfigur import Testendpunkte, Testverwaltung
from .api.dateien import Auftragsdateien
from .api.auftraege import Auftragsendpunkte
from .api.seiten_web import Webseiten
from .api.fotoauftraege import Fotoauftraege
from .api.kleidungsbibliothek import Kleiderendpunkte
from .api.retarget import Retargetendpunkte
from .api.smpl import Smplendpunkte
from .api.modelldateien import Modelldateien
from .api.studio import Studioendpunkte
from .api.studio_projekt import Studioprojekte
from .api.system import Systemendpunkte
from .api.bibliothek import Bibliotheksendpunkte
from .api.kleidungsvorlagen import Kleidungsvorlagen
from .api.bvhtext import Bvhtext
from .api.bvhdateien import Bvhauslieferung
from .api.fotoabgleich import Fotoabgleich
from .api.mhproxy import Mhproxy
from .api.netzbearbeitung import Netzbearbeitung
from .api.schnittmuster import Schnittmuster
from .api.schnittmuster_ablage import Schnittmusterablage
from .api.ui_vorgaben import Uivorgaben
from .api.smplx_ausgabe import SmplxAusgabe
from .api.posen import Posen
from .api.skelettdaten import Skelettdaten
from .api.netz import Netzendpunkte
from .api.kleidung import Kleidung
from .api.auftrag_upload import Uploadseiten
from .api.studio_video import Theatrevideo

urlpatterns = [
    path('', Webseiten.start, name='dashboard'),
    # Die Auslastungs-Leiste (GPU/VRAM/Temp/CPU/RAM/Netz) hat hier KEINEN Endpunkt
    # mehr: sie kommt seit 12.08.2026 aus djangoBase und antwortet unter
    # /help/api/system-stats/ (ui/urls.py bindet djangobase.urls auf help/ ein).
    path('process/', Uploadseiten.zweid, name='upload'),
    path('process/VideoToBVH/', Uploadseiten.dreid, name='upload_v4'),
    path('process/list/', Webseiten.fertigliste, name='processed'),
    path('process/result/', Webseiten.ergebnisauswahl, name='standalone_result'),
    path('process/<uuid:job_id>/', Webseiten.auftragsseite, name='job_status'),
    path('process/<uuid:job_id>/start/', Auftragsendpunkte.starten_formular, name='start_processing'),
    path('process/<uuid:job_id>/stop/', Auftragsendpunkte.anhalten_formular, name='stop_processing'),
    path('process/<uuid:job_id>/result/', Webseiten.ergebnisseite, name='job_result'),
    path('process/<uuid:job_id>/delete/', Auftragsendpunkte.loeschen_formular, name='delete_job'),
    path('api/bvh/<uuid:job_id>/', Auftragsdateien.bvh, name='serve_bvh'),
    path('api/bvh-face/<uuid:job_id>/', Auftragsdateien.bvh_gesicht, name='serve_bvh_face'),
    path('api/video/<uuid:job_id>/', Auftragsdateien.video, name='serve_video'),
    path('api/thumbnail/<uuid:job_id>/', Auftragsdateien.vorschaubild, name='video_thumbnail'),
    path('api/detection/<uuid:job_id>/', Auftragsdateien.erkennungsdaten, name='serve_detection'),
    path('api/keypoints/<uuid:job_id>/', Auftragsdateien.punkte_2d, name='serve_keypoints'),
    path('api/rig-video/<uuid:job_id>/', Auftragsdateien.skelettvideo, name='save_rig_video'),
    path('api/overlay-video/<uuid:job_id>/', Auftragsdateien.ueberlagerungsvideo, name='save_overlay_video'),
    path('api/video3d/<uuid:job_id>/', Auftragsdateien.video3d_sichern, name='save_video3d'),
    path('test/mocapnet/', Webseiten.werkzeugstatus, name='test_mocapnet'),
    path('library/', Webseiten.bvhbibliothek, name='library'),
    path('library/scan/', Bibliotheksendpunkte.einlesen, name='scan_bvh'),
    path('library/<int:pk>/delete/', Bibliotheksendpunkte.loeschen, name='delete_bvh'),
    path('library/<int:pk>/blender/', Bibliotheksendpunkte.in_blender_oeffnen, name='open_in_blender'),
    path('webcam/', Webseiten.webcam, name='webcam'),
    path('settings/', Webseiten.einstellungen, name='settings'),
    path('settings/model/', einstellungen.app_settings_model, name='settings_model'),
    path('settings/result/', einstellungen.app_settings_result, name='settings_result'),
    path('settings/scene/', einstellungen.app_settings_scene, name='settings_scene'),
    path('settings/video-to-bvh/', Webseiten.einstellungen_videobvh, name='settings_videobvh'),
    path('settings/video-to-bvh-2d/', einstellungen.app_settings_videobvh_2d, name='settings_videobvh_2d'),
    path('settings/video-to-bvh-3d/', einstellungen.app_settings_videobvh_3d, name='settings_videobvh_3d'),
    path('settings/smpl/', einstellungen.app_settings_smpl, name='settings_smpl'),
    path('settings/theatre/', seite_theatre_einstellungen.theatre_settings_page, name='settings_theatre'),
    path('settings/bvh-studio/', seite_bvhstudio_einstellungen.bvh_studio_settings_page, name='settings_bvh_studio'),
    path('api/job/<uuid:job_id>/start/', Auftragsendpunkte.starten, name='api_start_processing'),
    path('api/job/<uuid:job_id>/stop/', Auftragsendpunkte.anhalten, name='api_stop_processing'),
    path('api/job/<uuid:job_id>/status/', Auftragsendpunkte.zustand, name='job_status_api'),
    path('api/job/<uuid:job_id>/delete/', Auftragsendpunkte.loeschen, name='delete_job_api'),
    path('api/jobs/bulk-delete/', Auftragsendpunkte.mehrere_loeschen, name='bulk_delete_jobs'),
    path('api/job/create-from-file/', Auftragsendpunkte.aus_datei, name='create_job_from_file'),

    # HumanBody
    path('humanbody/photo-to-3d/', seiten.photo_to_3d_page, name='photo_to_3d'),
    path('humanbody/photo-to-3d/jobs/', seite_fotoauftraege.photo_analysis_jobs_page, name='photo_analysis_jobs'),
    path('api/character/analyze-photo/', Fotoauftraege.analysieren, name='analyze_photo'),
    path('api/character/analyze-photo/status/', Fotoauftraege.backendzustand, name='analyze_photo_status'),
    path('api/character/photo-job/<uuid:job_id>/', Fotoauftraege.daten, name='photo_analysis_job_data'),
    path('api/character/photo-job/<uuid:job_id>/screenshot/', Fotoauftraege.bild_sichern, name='photo_analysis_save_screenshot'),
    path('api/character/photo-job/<uuid:job_id>/reprocess/', Fotoauftraege.erneut_analysieren, name='photo_analysis_reprocess'),
    path('api/character/photo-job/<uuid:job_id>/delete/', Fotoauftraege.loeschen, name='photo_analysis_delete'),
    path('api/character/photo-jobs/bulk-delete/', Fotoauftraege.mehrere_loeschen, name='photo_analysis_bulk_delete'),
    path('api/character/photo-job/<uuid:job_id>/silhouette/', Fotoabgleich.silhouette, name='photo_silhouette_data'),
    path('api/character/photo-job/<uuid:job_id>/save-alignment/', Fotoabgleich.ausrichtung_sichern, name='photo_save_alignment'),
    path('api/character/photo-job/<uuid:job_id>/save-projection/', Fotoabgleich.projektion_sichern, name='photo_save_projection'),
    path('api/character/smplx-mesh/', SmplxAusgabe.netz, name='smplx_mesh'),
    path('api/character/smplx-texture/<uuid:job_id>/', SmplxAusgabe.textur, name='smplx_texture'),
    path('humanbody/config/', seiten.character_viewer, name='humanbody_config'),
    path('humanbody/scene/', seiten.scene_config, name='humanbody_scene'),
    path('humanbody/scene-model/', seiten.scene_model, name='humanbody_scene_model'),
    path('humanbody/theatre/', seiten.theatre_page, name='theatre'),
    path('humanbody/bvh-studio/', seiten.bvh_studio_page, name='bvh_studio'),
    path('humanbody/theatre-studio/', seiten.theatre_studio_page, name='theatre_studio'),
    path('humanbody/theatre/help/', seiten.theatre_help_page, name='theatre_help'),
    path('humanbody/rigging/help/', seiten.rigging_help_page, name='rigging_help'),
    path('api/ui-pref/', Systemendpunkte.vorgabe_sichern, name='ui_pref_save'),
    path('api/character/mh-proxy-fit/', Mhproxy.anpassen, name='mh_proxy_fit'),
    path('api/character/tpose-vertices/', Mhproxy.tpose_punkte, name='tpose_vertices'),
    path('api/character/poses/', Posen.liste, name='list_poses'),
    path('api/character/pose/<path:pose_id>/', Posen.pose, name='pose_load'),
    path('api/character/pose-manage/', Posen.verwalten, name='pose_manage'),
    path('api/character/mh-push-outside/', Mhproxy.herausschieben, name='mh_push_outside'),
    path('humanbody/animations/', seiten.animations_page, name='humanbody_animations'),
    path('humanbody/test-animation/', seiten.test_animation_page, name='test_animation'),
    path('humanbody/test-character/', seiten.test_character_page, name='test_character'),
    path('api/character/mesh/', Netzendpunkte.netz, name='character_mesh'),
    path('api/character/morphs/', Netzendpunkte.regler, name='character_morphs'),
    path('api/character/rig/', Skelettdaten.rig, name='character_rig'),
    path('api/character/rigify-skeleton/', Skelettdaten.def_skelett, name='character_rigify_skeleton'),
    path('api/character/skin-weights/', Skelettdaten.hautgewichte, name='character_skin_weights'),
    path('api/character/retarget-config/', Retargetendpunkte.zuordnungstabellen, name='retarget_config'),
    path('api/retarget/', Retargetendpunkte.umsetzen, name='retarget'),
    path('api/character/retarget-bvh/<str:category>/<str:name>/', Retargetendpunkte.bibliotheks_bvh, name='retarget_bvh'),  # legacy
    path('api/character/retarget-merge/', Retargetendpunkte.zusammenfuehren, name='retarget_merge'),
    path('api/character/retarget-job/<uuid:job_id>/', Retargetendpunkte.auftrags_bvh, name='retarget_job_bvh'),  # legacy
    path('api/character/retarget-job-merge/<uuid:job_id>/', Retargetendpunkte.auftrag_zusammenfuehren, name='retarget_job_merge'),
    path('api/character/retarget-bvh-text/', Bvhtext.umsetzen, name='retarget_bvh_text'),
    path('api/log/', Systemendpunkte.browsermeldung, name='client_log'),
    path('api/retarget/smooth-bvh/', Bvhtext.glaetten, name='smooth_bvh'),
    path('api/retarget/save-bvh-effects/', Bvhtext.effekte_sichern, name='save_bvh_effects'),
    path('api/character/save-bvh-text/', Bvhtext.sichern, name='save_bvh_text'),
    path('api/character/bvh-manage/', Retargetendpunkte.bvh_verwalten, name='bvh_manage'),
    path('api/cloth/export/', Stoffexport.ausfuehren, name='cloth_export'),
    path('api/studio/audio-upload/', Studioendpunkte.ton_hochladen, name='studio_audio_upload'),
    path('api/studio/project-save/', Studioprojekte.projekt_sichern, name='studio_project_save'),
    path('api/studio/project-load/', Studioprojekte.projekt_laden, name='studio_project_load'),
    path('api/studio/project-list/', Studioprojekte.projektliste, name='studio_project_list'),
    path('api/studio/theatre-presets/', Studioendpunkte.lichtvorgaben, name='studio_theatre_presets'),
    path('api/studio/theatre-preset/<str:name>/', Studioendpunkte.lichtvorgabe, name='studio_theatre_preset_detail'),
    path('api/studio/scene-object-upload/', Studioendpunkte.objekt_hochladen, name='studio_scene_object_upload'),
    path('api/studio/floor-textures/', Studioendpunkte.bodentexturen, name='studio_floor_textures'),
    path('api/character/wardrobe/', Kleidung.garderobe, name='character_wardrobe'),
    path('api/character/animations/', Bvhauslieferung.animationen, name='character_animations'),
    path('api/character/model-files/', Modelldateien.dateiliste, name='model_files'),
    path('api/character/scenes/', Studioprojekte.szenenliste, name='scene_list'),
    path('api/character/scene/save/', Studioprojekte.szene_sichern, name='scene_save'),
    path('api/character/scene/<str:name>/', Studioprojekte.szene, name='scene_detail'),
    path('api/character/models/', Modelldateien.modellliste, name='character_models'),
    path('api/character/model/save/', Modelldateien.modell_sichern, name='character_model_save'),
    path('api/character/model/<str:name>/', Modelldateien.modell, name='character_model_detail'),
    path('api/settings/humanbody/', Systemendpunkte.vorgaben, name='humanbody_settings_api'),
    path('api/settings/theatre/', Studioendpunkte.theatre_einstellungen, name='theatre_settings_api'),
    path('api/theatre/convert-video/', Theatrevideo.umwandeln, name='theatre_convert_video'),
    path('api/theatre/render-video/', Theatrevideo.aufnehmen, name='theatre_render_video'),
    path('api/theatre/encode-frames/', Theatrevideo.bilder_kodieren, name='theatre_encode_frames'),
    path('api/settings/smpl/', Smplendpunkte.einstellungen, name='smpl_settings_api'),
    path('api/settings/smpl/save/', Smplendpunkte.einstellungen_sichern, name='smpl_settings_save'),
    path('api/ui-prefs/', Uivorgaben.vorlieben, name='ui_prefs_api'),
    path('api/animationen/<str:kategorie>/', Uivorgaben.animationen,
         name='animationen_der_kategorie'),
    path('api/character/asset/<str:name>/', Netzendpunkte.garderobendatei, name='character_asset_glb'),
    path('api/character/bvh/<str:category>/<str:name>/', Bvhauslieferung.datei_der_kategorie, name='character_bvh_file_cat'),
    path('api/character/bvh/<str:name>/', Bvhauslieferung.datei, name='character_bvh_file'),
    path('api/character/animation/save/', Bvhauslieferung.sichern, name='animation_save'),

    # CharMorph
    path('api/character/charmorph-presets/', CharmorphBestand.koerpertypen, name='charmorph_presets'),
    path('api/character/charmorph-assets/', CharmorphBestand.kleider, name='charmorph_assets'),
    path('api/character/charmorph-hairstyles/', CharmorphBestand.frisuren, name='charmorph_hairstyles'),

    # Cloth
    path('api/character/cloth/', Kleidung.stoff, name='character_cloth'),
    path('api/character/cloth/regions/', Kleidungsvorlagen.bereiche, name='character_cloth_regions'),
    path('api/character/cloth/presets/', Kleidungsvorlagen.liste, name='cloth_preset_list'),
    path('api/character/cloth/presets/save/', Kleidungsvorlagen.sichern, name='cloth_preset_save'),
    path('api/character/cloth/presets/<str:category>/<str:name>/', Kleidungsvorlagen.vorlage, name='cloth_preset_detail'),

    # Vertex Editor
    path('api/character/vertex-edit/smooth/', Netzbearbeitung.glaetten, name='vertex_edit_smooth'),
    path('api/character/vertex-edit/push-outside/', Netzbearbeitung.herausschieben, name='vertex_edit_push_outside'),

    # Pattern Editor
    path('api/character/pattern/generate/', Schnittmuster.aus_schnitt, name='pattern_generate'),
    path('api/character/pattern/save/', Schnittmusterablage.sichern, name='pattern_save'),
    path('api/character/pattern/specification/', Schnittmusterablage.beschreibung, name='pattern_specification'),
    path('api/character/pattern/region/generate/', Schnittmuster.aus_bereich, name='pattern_region_generate'),

    # Hair
    path('api/character/hairstyles/', Modelldateien.frisuren, name='character_hairstyles'),
    path('api/character/hairstyle/<str:name>/', Modelldateien.frisur_glb, name='character_hairstyle_glb'),

    # Garment Fitter
    path('api/character/garment/library/', Kleiderendpunkte.bestand, name='garment_library'),
    path('api/character/garment/library/rescan/', Kleiderendpunkte.neu_einlesen, name='garment_library_rescan'),
    path('api/character/garment/manage/', Kleiderendpunkte.verwalten, name='garment_manage'),
    path('api/character/garment/fit/', Kleidung.anpassen, name='garment_fit'),
    path('api/character/garment/export/', Kleiderendpunkte.ausgabeordner, name='garment_export'),
    path('api/character/garment/download/available/', Kleiderendpunkte.angebot, name='garment_download_available'),
    path('api/character/garment/download/', Kleiderendpunkte.herunterladen, name='garment_download'),
    path('api/character/garment/thumb/<path:garment_path>/', Kleiderendpunkte.vorschaubild, name='garment_thumbnail'),
    path('api/character/garment/texture/<path:garment_id>/<str:filename>/', Kleiderendpunkte.textur, name='garment_texture'),

    # SMPL Garments
    path('humanbody/test-smpl/', seiten.smpl_test_page, name='test_smpl'),
    path('api/smpl/body/', Smplendpunkte.koerpernetz, name='smpl_body_mesh'),
    path('api/smpl/garment/library/', Smplendpunkte.kleiderbestand, name='smpl_garment_library'),
    path('api/smpl/garment/mesh/', Smplendpunkte.kleidernetz, name='smpl_garment_mesh'),
    path('api/smpl/garment/fit/', Smplendpunkte.kleid_anpassen, name='smpl_garment_fit'),
    path('api/smpl/garment/thumb/<path:garment_path>/', Smplendpunkte.vorschaubild, name='smpl_garment_thumbnail'),

    # Help (Logs/Versionen/Tests) jetzt aus djangoBase: /help/ -> djangobase.urls

    # Test Character API (isolated version from TestCharakter/)
    path('api/character-test/mesh/', Testendpunkte.netz, name='test_character_mesh'),
    path('api/character-test/morphs/', Testendpunkte.regler, name='test_character_morphs'),
    path('api/character-test/skin-weights/', Testendpunkte.hautgewichte, name='test_character_skin_weights'),
    path('api/character-test/rigify-skeleton/', Testendpunkte.def_skelett, name='test_character_rigify_skeleton'),
    path('api/character-test/version/', Testverwaltung.fassung, name='test_version_info'),
    path('api/character-test/source/', Testverwaltung.quelltext, name='test_character_source'),
    path('api/character-test/reload/', Testverwaltung.neu_laden, name='test_reload'),
    path('api/character-test/switch/', Testverwaltung.figur_wechseln, name='test_switch_character'),
]

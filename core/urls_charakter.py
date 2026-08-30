# -*- coding: utf-8 -*-
u"""Die Routen der Charakter- und SMPL-Endpunkte.

Aus `core/urls.py` herausgeloest (30.08.2026, Befund `dateigroesse`):
Die Tabelle war auf 327 Zeilen und 160 Routen gewachsen. 74 davon
beginnen mit `api/character/` oder `api/smpl/` und gehoeren zusammen —
Netz, Morphs, Rig, Kleidung, Posen, Muster.

`urls.py` haengt sie mit `urlpatterns += CHARAKTER` an; die
Reihenfolge bleibt damit dieselbe wie vorher.
"""
from django.urls import path

from .api.charmorph_bestand import CharmorphBestand
from .api.fotoauftraege import Fotoauftraege
from .api.kleidungsbibliothek import Kleiderendpunkte
from .api.retarget import Retargetendpunkte
from .api.smpl import Smplendpunkte
from .api.modelldateien import Modelldateien
from .api.studio_projekt import Studioprojekte
from .api.kleidungsvorlagen import Kleidungsvorlagen
from .api.bvhtext import Bvhtext
from .api.bvhdateien import Bvhauslieferung
from .api.fotoabgleich import Fotoabgleich
from .api.mhproxy import Mhproxy
from .api.netzbearbeitung import Netzbearbeitung
from .api.schnittmuster import Schnittmuster
from .api.schnittmuster_ablage import Schnittmusterablage
from .api.smplx_ausgabe import SmplxAusgabe
from .api.posen import Posen
from .api.skelettdaten import Skelettdaten
from .api.netz import Netzendpunkte
from .api.kleidung import Kleidung

CHARAKTER = [
    path('api/character/analyze-photo/', Fotoauftraege.analysieren,
         name='analyze_photo'),
    path('api/character/analyze-photo/status/', Fotoauftraege.backendzustand,
         name='analyze_photo_status'),
    path('api/character/photo-job/<uuid:job_id>/', Fotoauftraege.daten,
         name='photo_analysis_job_data'),
    path('api/character/photo-job/<uuid:job_id>/screenshot/',
         Fotoauftraege.bild_sichern, name='photo_analysis_save_screenshot'),
    path('api/character/photo-job/<uuid:job_id>/reprocess/',
         Fotoauftraege.erneut_analysieren, name='photo_analysis_reprocess'),
    path('api/character/photo-job/<uuid:job_id>/delete/', Fotoauftraege.loeschen,
         name='photo_analysis_delete'),
    path('api/character/photo-jobs/bulk-delete/', Fotoauftraege.mehrere_loeschen,
         name='photo_analysis_bulk_delete'),
    path('api/character/photo-job/<uuid:job_id>/silhouette/', Fotoabgleich.silhouette,
         name='photo_silhouette_data'),
    path('api/character/photo-job/<uuid:job_id>/save-alignment/',
         Fotoabgleich.ausrichtung_sichern, name='photo_save_alignment'),
    path('api/character/photo-job/<uuid:job_id>/save-projection/',
         Fotoabgleich.projektion_sichern, name='photo_save_projection'),
    path('api/character/smplx-mesh/', SmplxAusgabe.netz, name='smplx_mesh'),
    path('api/character/smplx-texture/<uuid:job_id>/', SmplxAusgabe.textur,
         name='smplx_texture'),
    path('api/character/mh-proxy-fit/', Mhproxy.anpassen, name='mh_proxy_fit'),
    path('api/character/tpose-vertices/', Mhproxy.tpose_punkte, name='tpose_vertices'),
    path('api/character/poses/', Posen.liste, name='list_poses'),
    path('api/character/pose/<path:pose_id>/', Posen.pose, name='pose_load'),
    path('api/character/pose-manage/', Posen.verwalten, name='pose_manage'),
    path('api/character/mh-push-outside/', Mhproxy.herausschieben,
         name='mh_push_outside'),
    path('api/character/mesh/', Netzendpunkte.netz, name='character_mesh'),
    path('api/character/morphs/', Netzendpunkte.regler, name='character_morphs'),
    path('api/character/rig/', Skelettdaten.rig, name='character_rig'),
    path('api/character/rigify-skeleton/', Skelettdaten.def_skelett,
         name='character_rigify_skeleton'),
    path('api/character/skin-weights/', Skelettdaten.hautgewichte,
         name='character_skin_weights'),
    path('api/character/retarget-config/', Retargetendpunkte.zuordnungstabellen,
         name='retarget_config'),
    path('api/character/retarget-bvh/<str:category>/<str:name>/',
         Retargetendpunkte.bibliotheks_bvh, name='retarget_bvh'),  # legacy
    path('api/character/retarget-merge/', Retargetendpunkte.zusammenfuehren,
         name='retarget_merge'),
    path('api/character/retarget-job/<uuid:job_id>/', Retargetendpunkte.auftrags_bvh,
         name='retarget_job_bvh'),  # legacy
    path('api/character/retarget-job-merge/<uuid:job_id>/',
         Retargetendpunkte.auftrag_zusammenfuehren, name='retarget_job_merge'),
    path('api/character/retarget-bvh-text/', Bvhtext.umsetzen,
         name='retarget_bvh_text'),
    path('api/character/save-bvh-text/', Bvhtext.sichern, name='save_bvh_text'),
    path('api/character/bvh-manage/', Retargetendpunkte.bvh_verwalten,
         name='bvh_manage'),
    path('api/character/wardrobe/', Kleidung.garderobe, name='character_wardrobe'),
    path('api/character/animations/', Bvhauslieferung.animationen,
         name='character_animations'),
    path('api/character/model-files/', Modelldateien.dateiliste, name='model_files'),
    path('api/character/scenes/', Studioprojekte.szenenliste, name='scene_list'),
    path('api/character/scene/save/', Studioprojekte.szene_sichern, name='scene_save'),
    path('api/character/scene/<str:name>/', Studioprojekte.szene, name='scene_detail'),
    path('api/character/models/', Modelldateien.modellliste, name='character_models'),
    path('api/character/model/save/', Modelldateien.modell_sichern,
         name='character_model_save'),
    path('api/character/model/<str:name>/', Modelldateien.modell,
         name='character_model_detail'),
    path('api/character/asset/<str:name>/', Netzendpunkte.garderobendatei,
         name='character_asset_glb'),
    path('api/character/bvh/<str:category>/<str:name>/',
         Bvhauslieferung.datei_der_kategorie, name='character_bvh_file_cat'),
    path('api/character/bvh/<str:name>/', Bvhauslieferung.datei,
         name='character_bvh_file'),
    path('api/character/animation/save/', Bvhauslieferung.sichern,
         name='animation_save'),

    path('api/character/charmorph-presets/', CharmorphBestand.koerpertypen,
         name='charmorph_presets'),
    path('api/character/charmorph-assets/', CharmorphBestand.kleider,
         name='charmorph_assets'),
    path('api/character/charmorph-hairstyles/', CharmorphBestand.frisuren,
         name='charmorph_hairstyles'),

    path('api/character/cloth/', Kleidung.stoff, name='character_cloth'),
    path('api/character/cloth/regions/', Kleidungsvorlagen.bereiche,
         name='character_cloth_regions'),
    path('api/character/cloth/presets/', Kleidungsvorlagen.liste,
         name='cloth_preset_list'),
    path('api/character/cloth/presets/save/', Kleidungsvorlagen.sichern,
         name='cloth_preset_save'),
    path('api/character/cloth/presets/<str:category>/<str:name>/',
         Kleidungsvorlagen.vorlage, name='cloth_preset_detail'),

    path('api/character/vertex-edit/smooth/', Netzbearbeitung.glaetten,
         name='vertex_edit_smooth'),
    path('api/character/vertex-edit/push-outside/', Netzbearbeitung.herausschieben,
         name='vertex_edit_push_outside'),

    path('api/character/pattern/generate/', Schnittmuster.aus_schnittmuster,
         name='pattern_generate'),
    path('api/character/pattern/save/', Schnittmusterablage.sichern,
         name='pattern_save'),
    path('api/character/pattern/specification/', Schnittmusterablage.beschreibung,
         name='pattern_specification'),
    path('api/character/pattern/region/generate/', Schnittmuster.aus_bereich,
         name='pattern_region_generate'),

    path('api/character/hairstyles/', Modelldateien.frisuren,
         name='character_hairstyles'),
    path('api/character/hairstyle/<str:name>/', Modelldateien.frisur_glb,
         name='character_hairstyle_glb'),

    path('api/character/garment/library/', Kleiderendpunkte.bestand,
         name='garment_library'),
    path('api/character/garment/library/rescan/', Kleiderendpunkte.neu_einlesen,
         name='garment_library_rescan'),
    path('api/character/garment/manage/', Kleiderendpunkte.verwalten,
         name='garment_manage'),
    path('api/character/garment/fit/', Kleidung.anpassen, name='garment_fit'),
    path('api/character/garment/export/', Kleiderendpunkte.ausgabeordner,
         name='garment_export'),
    path('api/character/garment/download/available/', Kleiderendpunkte.angebot,
         name='garment_download_available'),
    path('api/character/garment/download/', Kleiderendpunkte.herunterladen,
         name='garment_download'),
    path('api/character/garment/thumb/<path:garment_path>/',
         Kleiderendpunkte.vorschaubild, name='garment_thumbnail'),
    path('api/character/garment/texture/<path:garment_id>/<str:filename>/',
         Kleiderendpunkte.textur, name='garment_texture'),

    path('api/smpl/body/', Smplendpunkte.koerpernetz, name='smpl_body_mesh'),
    path('api/smpl/garment/library/', Smplendpunkte.kleiderbestand,
         name='smpl_garment_library'),
    path('api/smpl/garment/mesh/', Smplendpunkte.kleidernetz, name='smpl_garment_mesh'),
    path('api/smpl/garment/fit/', Smplendpunkte.kleid_anpassen,
         name='smpl_garment_fit'),
    path('api/smpl/garment/thumb/<path:garment_path>/', Smplendpunkte.vorschaubild,
         name='smpl_garment_thumbnail'),

]

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
from .api.figur_export import Figurexport
from .api.modellexport import Modellexportanfrage
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
from .api.hauttexturen import Hauttexturen
from .api.brauen import Brauenendpunkte
from .api.eigenstueck import Eigenstueckapi
from .api.gcgenesis import Gcgenesisapi
from .api.g9figur import G9figur
from .api.g9garderobe import G9garderobeapi
from .api.g9garderobekategorien import G9garderobekategorienapi
from .api.g9hautmischung import G9hautmischungapi
from .api.g9texturbuendel import G9texturbuendelapi
from .api.g9vorschau import G9vorschau
from .api.g9stoff import G9stoffapi
from .api.g9frisurapi import G9frisurapi
from .api.g9felder import G9felderapi
from .api.mhfigur import Mhfigur
from .api.mhproxy import Mhproxy
from .api.netzbearbeitung import Netzbearbeitung
from .api.schnittmuster import Schnittmuster
from .api.schnittmuster_ablage import Schnittmusterablage
from .api.smplx_ausgabe import SmplxAusgabe
from .api.posen import Posen
from .api.skelettdaten import Skelettdaten
from .api.smplfigur import Smplfigur
from .api.smplform import Smplformung
from .api.umafigur import Umafigur
from .api.umakleidung import Umakleidung
from .api.gemeinsameregler import Gemeinsameregler
from .api.katalogverwaltung import Katalogverwaltung
from .api.netz import Netzendpunkte
from .api.kleidung import Kleidung

CHARAKTER = [
    # Fertige Figur als GLB (Datei -> Exportieren), Abnehmer: Roomguest.
    path('api/character/figur-glb/', Figurexport.liste, name='figur_glb_liste'),
    path('api/character/figur-glb/<str:name>/', Figurexport.datei, name='figur_glb'),
    path('api/character/modellexport/vorgabe/', Modellexportanfrage.vorgabe,
         name='modellexport_vorgabe'),
    path('api/character/modellexport/', Modellexportanfrage.ablegen, name='modellexport_ablegen'),
    path('api/character/figur-glb/<str:name>/ablegen/', Figurexport.ablegen,
         name='figur_glb_ablegen'),
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
    # MB-Lab-Hauttexturen fuer die Figur, nur lesend (13.09.2026).
    path('api/character/textur/<str:name>/', Hauttexturen.datei, name='character_textur'),
    # Displacement-Textur aus Alter/Tonus/Masse (MB-Lab Displace, 17.09.2026).
    path('api/character/textur/verschiebung/<str:geschlecht>/',
         Hauttexturen.verschiebung, name='character_textur_verschiebung'),
    # Die gezeichnete Augenbraue (`Brauendecal`, 16.09.2026).
    path('api/character/brauen/fenster/', Brauenendpunkte.fenster,
         name='brauen_fenster'),
    path('api/character/brauen/bild/', Brauenendpunkte.bild, name='brauen_bild'),
    path('api/character/morphs/', Netzendpunkte.regler, name='character_morphs'),
    # Die gemeinsame Reglertabelle: ein Name, zwei Uebersetzungen (06.09.2026).
    path('api/character/regler/gemeinsam/', Gemeinsameregler.tabelle,
         name='regler_gemeinsam'),
    path('api/character/rig/', Skelettdaten.rig, name='character_rig'),
    path('api/character/rigify-skeleton/', Skelettdaten.def_skelett,
         name='character_rigify_skeleton'),
    path('api/character/skin-weights/', Skelettdaten.hautgewichte,
         name='character_skin_weights'),
    # UMA-Skelett aus dem Figurkatalog, fuer die Vergleichsseite (05.09.2026).
    path('api/character/uma-skeleton/', Skelettdaten.umaskelett,
         name='character_uma_skeleton'),
    # Genesis-9-Skelett der Grundstellung, fuer die Vergleichsseite (19.09.2026).
    path('api/character/genesis9-skeleton/', Skelettdaten.genesis9skelett,
         name='character_genesis9_skeleton'),
    # UMA-Figur aus dem Figurkatalog fuer die Szene-Seite: Dateien, Zettel,
    # Form-Regler (05.09.2026, core/api/umafigur.py).
    # Bauen auf Zuruf (06.09.2026) — vor `uma-figur/<str:name>/`, sonst hieße
    # die Figur „bauen".
    path('api/character/uma-rassen/', Umafigur.rassen, name='uma_rassen'),
    path('api/character/uma-garderobe/', Umakleidung.angebot, name='uma_garderobe'),
    path('api/character/uma-rassen/ermitteln/', Umafigur.rassen_ermitteln,
         name='uma_rassen_ermitteln'),
    path('api/character/uma-figur/bauen/', Umafigur.bauen, name='uma_figur_bauen'),
    path('api/character/uma-figur/bauen/<str:name>/stand/', Umafigur.bau_stand,
         name='uma_figur_bau_stand'),
    path('api/character/uma-figur/bauer/', Umafigur.bauer_stand,
         name='uma_bauer_stand'),
    path('api/character/uma-figur/bauer/vorwaermen/', Umafigur.vorwaermen,
         name='uma_bauer_vorwaermen'),
    # SMPL-Referenzkoerper von GarmentCode (06.09.2026, core/api/smplfigur.py).
    path('api/character/smpl-figur/', Smplfigur.liste, name='smpl_figur_liste'),
    path('api/character/smpl-figur/formen/', Smplformung.formen,
         name='smpl_figur_formen'),
    # Benannte Massregler (Armlänge, Brustgröße, …) mit gemessener Wirkung
    # je Geschlecht (25.09.2026, SMPL/xmassregler.py).
    path('api/character/smpl-figur/massregler/<str:geschlecht>/', Smplformung.massregler,
         name='smpl_figur_massregler'),
    path('api/character/smpl-figur/<str:name>/netz/', Smplfigur.netz,
         name='smpl_figur_netz'),
    # Hautfoto-Textur je Geschlecht (25.09.2026, „SMPL-X-Texturen") —
    # ueberschneidet sich nicht mit `<str:name>/netz/`: das zweite
    # Wegstueck ist dort immer das feste Wort „netz".
    path('api/character/smpl-figur/textur/<str:geschlecht>/', Smplfigur.textur,
         name='smpl_figur_textur'),
    # Detailmaske (Lippen, Nägel, Augen) der SMPL-X-Haut (25.09.2026, SMPL/xdetails.py).
    path('api/character/smpl-figur/details/<str:geschlecht>/maske/', Smplfigur.details_maske,
         name='smpl_figur_details_maske'),
    # BEDLAM-Hauttexturen (26.09.2026, core/dienste/smplxbedlamdienst.py).
    path('api/character/smpl-figur/bedlam/<str:geschlecht>/', Smplfigur.bedlam_liste,
         name='smpl_figur_bedlam_liste'),
    path('api/character/smpl-figur/bedlam/<str:geschlecht>/<str:schluessel>/',
         Smplfigur.bedlam_textur, name='smpl_figur_bedlam_textur'),
    # MakeHuman-Basiskoerper (06.09.2026, core/api/mhfigur.py). Die Garderobe
    # steht VOR `<str:name>/netz/`, sonst hiesse das Modell „garderobe".
    path('api/character/mh-figur/', Mhfigur.liste, name='mh_figur_liste'),
    path('api/character/mh-figur/regler/', Mhfigur.regler,
         name='mh_figur_regler'),
    path('api/character/mh-figur/garderobe/', Mhfigur.garderobe,
         name='mh_figur_garderobe'),
    path('api/character/mh-figur/garderobe/<str:kategorie>/<str:stueck>/netz/',
         Mhfigur.kleidnetz, name='mh_figur_kleidnetz'),
    path('api/character/mh-figur/garderobe/<str:kategorie>/<str:stueck>/'
         'textur/<str:datei>/', Mhfigur.textur, name='mh_figur_textur'),
    path('api/character/mh-figur/<str:name>/netz/', Mhfigur.netz,
         name='mh_figur_netz'),
    # Genesis 9 (Daz, 17.09.2026, core/api/g9figur.py) — dieselbe Ordnung:
    # Regler, Garderobe und Texturen VOR `<str:name>/netz/`.
    path('api/character/genesis9-figur/', G9figur.liste, name='g9_figur_liste'),
    path('api/character/genesis9-figur/regler/', G9figur.regler,
         name='g9_figur_regler'),
    path('api/character/genesis9-figur/posen/', G9garderobeapi.posen,
         name='g9_figur_posen'),
    path('api/character/genesis9-figur/garderobe/', G9garderobeapi.garderobe,
         name='g9_figur_garderobe'),
    # Eigenes Stück aus einem OBJ (Hilfe → Kleidung → Vergleich, 25.09.2026).
    path('api/character/eigenstueck/bauen/', Eigenstueckapi.bauen, name='eigenstueck_bauen'),
    path('api/character/eigenstueck/<str:kennung>/<str:datei>/', Eigenstueckapi.bild,
         name='eigenstueck_bild'),
    path('api/garmentcode/genesis/speichern/', Gcgenesisapi.speichern, name='gcgenesis_speichern'),
    path('api/garmentcode/genesis/<str:stueck>/', Gcgenesisapi.herkunft, name='gcgenesis_herkunft'),
    path('api/character/genesis9-figur/garderobe/kategorien/',
         G9garderobekategorienapi.kategorien, name='g9_figur_garderobe_kategorien'),
    path('api/character/genesis9-figur/garderobe/<str:kennung>/netz/',
         G9garderobeapi.kleidnetz, name='g9_figur_kleidnetz'),
    path('api/character/genesis9-figur/garderobe/<str:kennung>/vorschau/',
         G9vorschau.stueck, name='g9_figur_vorschau'),
    path('api/character/genesis9-figur/garderobe/<str:kennung>/stoff/<int:nummer>/',
         G9stoffapi.bauplan, name='g9_figur_stoffbauplan'),
    # Texturmischung (21.09.2026, core/api/g9hautmischung.py): Bilder eines Hautsatzes.
    path('api/character/genesis9-figur/haut/<str:preset>/bilder/',
         G9hautmischungapi.bilder, name='g9_figur_hautbilder'),
    # HumanBody-Frisur (GLB) auf dem Genesis-Kopf (19.09.2026, core/api/g9frisurapi.py).
    path('api/character/genesis9-figur/frisur/<str:name>/',
         G9frisurapi.netz, name='g9_figur_frisur'),
    # Alle Bilder eines Netzes in EINER Antwort (23.09.2026,
    # core/api/g9texturbuendel.py) — steht VOR `textur/<path:pfad>`, sonst
    # liefe die Adresse in den Einzelbild-Weg.
    path('api/character/genesis9-figur/texturbuendel/', G9texturbuendelapi.buendel,
         name='g9_figur_texturbuendel'),
    path('api/character/genesis9-figur/textur/<path:pfad>', G9garderobeapi.textur,
         name='g9_figur_textur'),
    # Reglerfelder je Stufe (18.09.2026, core/api/g9felder.py): JCMs, Visemes.
    path('api/character/genesis9-figur/felder/gelenke/', G9felderapi.gelenke,
         name='g9_figur_felder_gelenke'),
    path('api/character/genesis9-figur/felder/visemes/', G9felderapi.visemes,
         name='g9_figur_felder_visemes'),
    path('api/character/genesis9-figur/felder/mimik/', G9felderapi.mimik,
         name='g9_figur_felder_mimik'),
    path('api/character/genesis9-figur/garderobe/<str:kennung>/felder/<str:gruppe>/',
         G9felderapi.stueck, name='g9_felder_stueck'),
    path('api/character/genesis9-figur/<str:name>/netz/', G9figur.netz,
         name='g9_figur_netz'),
    path('api/character/uma-figur/', Umafigur.liste, name='uma_figur_liste'),
    path('api/character/uma-figur/<str:name>/', Umafigur.datei, name='uma_figur'),
    path('api/character/uma-figur/<str:name>/zettel/', Umafigur.zettel,
         name='uma_figur_zettel'),
    path('api/character/uma-regler/', Umafigur.regler, name='uma_regler'),
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
    # Umbenennen und Loeschen aus dem Dialog heraus (06.09.2026).
    path('api/character/katalog/uma/umbenennen/', Katalogverwaltung.uma_umbenennen,
         name='katalog_uma_umbenennen'),
    path('api/character/katalog/uma/loeschen/', Katalogverwaltung.uma_loeschen,
         name='katalog_uma_loeschen'),
    path('api/character/katalog/modell/umbenennen/',
         Katalogverwaltung.modell_umbenennen, name='katalog_modell_umbenennen'),
    path('api/character/katalog/modell/loeschen/', Katalogverwaltung.modell_loeschen,
         name='katalog_modell_loeschen'),
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

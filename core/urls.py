from django.urls import path
from . import views
from . import character_api

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('process/', views.upload_video, name='upload'),
    path('process/v4/', views.upload_video_v4, name='upload_v4'),
    path('process/list/', views.processed_list, name='processed'),
    path('process/<uuid:job_id>/', views.job_status, name='job_status'),
    path('process/<uuid:job_id>/start/', views.start_processing, name='start_processing'),
    path('process/<uuid:job_id>/stop/', views.stop_processing, name='stop_processing'),
    path('process/<uuid:job_id>/result/', views.job_result, name='job_result'),
    path('process/<uuid:job_id>/delete/', views.delete_job, name='delete_job'),
    path('api/bvh/<uuid:job_id>/', views.serve_bvh_file, name='serve_bvh'),
    path('api/thumbnail/<uuid:job_id>/', views.video_thumbnail, name='video_thumbnail'),
    path('api/detection/<uuid:job_id>/', views.serve_detection_data, name='serve_detection'),
    path('api/keypoints/<uuid:job_id>/', views.serve_keypoints_2d, name='serve_keypoints'),
    path('api/rig-video/<uuid:job_id>/', views.save_rig_video, name='save_rig_video'),
    path('api/overlay-video/<uuid:job_id>/', views.save_overlay_video, name='save_overlay_video'),
    path('library/', views.bvh_library, name='library'),
    path('library/scan/', views.scan_bvh_files, name='scan_bvh'),
    path('library/<int:pk>/delete/', views.delete_bvh, name='delete_bvh'),
    path('library/<int:pk>/blender/', views.open_in_blender, name='open_in_blender'),
    path('webcam/', views.webcam, name='webcam'),
    path('settings/', views.app_settings, name='settings'),
    path('settings/model/', views.app_settings_model, name='settings_model'),
    path('settings/video-to-bvh/', views.app_settings_videobvh, name='settings_videobvh'),
    path('api/job/<uuid:job_id>/status/', views.job_status_api, name='job_status_api'),
    path('api/job/<uuid:job_id>/delete/', views.delete_job_api, name='delete_job_api'),
    path('api/jobs/bulk-delete/', views.bulk_delete_jobs, name='bulk_delete_jobs'),

    # HumanBody
    path('humanbody/config/', character_api.character_viewer, name='humanbody_config'),
    path('humanbody/scene/', character_api.scene_config, name='humanbody_scene'),
    path('humanbody/animations/', character_api.animations_page, name='humanbody_animations'),
    path('humanbody/test/', character_api.skeleton_test_page, name='humanbody_test'),
    path('api/character/mesh/', character_api.character_mesh, name='character_mesh'),
    path('api/character/morphs/', character_api.character_morphs, name='character_morphs'),
    path('api/character/rig/', character_api.character_rig, name='character_rig'),
    path('api/character/def-skeleton/', character_api.character_def_skeleton, name='character_def_skeleton'),
    path('api/character/skin-weights/', character_api.character_skin_weights, name='character_skin_weights'),
    path('api/character/wardrobe/', character_api.character_wardrobe, name='character_wardrobe'),
    path('api/character/animations/', character_api.character_animations, name='character_animations'),
    path('api/character/models/', character_api.character_models, name='character_models'),
    path('api/character/model/save/', character_api.character_model_save, name='character_model_save'),
    path('api/character/model/<str:name>/', character_api.character_model_detail, name='character_model_detail'),
    path('api/settings/humanbody/', character_api.humanbody_settings_api, name='humanbody_settings_api'),
    path('api/character/asset/<str:name>/', character_api.character_asset_glb, name='character_asset_glb'),
    path('api/character/bvh/<str:category>/<str:name>/', character_api.character_bvh_file_cat, name='character_bvh_file_cat'),
    path('api/character/bvh/<str:name>/', character_api.character_bvh_file, name='character_bvh_file'),

    # Cloth
    path('api/character/cloth/', character_api.character_cloth, name='character_cloth'),
    path('api/character/cloth/regions/', character_api.character_cloth_regions, name='character_cloth_regions'),
    path('api/character/cloth/presets/', character_api.cloth_preset_list, name='cloth_preset_list'),
    path('api/character/cloth/presets/save/', character_api.cloth_preset_save, name='cloth_preset_save'),
    path('api/character/cloth/presets/<str:category>/<str:name>/', character_api.cloth_preset_detail, name='cloth_preset_detail'),

    # Hair
    path('api/character/hairstyles/', character_api.character_hairstyles, name='character_hairstyles'),
    path('api/character/hairstyle/<str:name>/', character_api.character_hairstyle_glb, name='character_hairstyle_glb'),
]

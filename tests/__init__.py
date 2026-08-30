# BVH Studio Tests Package
from .base import TestCase, TestCategory
from .theatre_tests import TheatreTests
from .floor_tests import FloorTests
from .scene_object_tests import SceneObjectTests
from .bundle_upload_tests import BundleUploadTests
from .bundle_mtl_tests import BundleMtlTests
from .projekt_licht_tests import ProjektLichtTests
from .projekt_szene_tests import ProjektSzeneTests
from .ui_prefs_tests import UiPrefsTests
from .client_log_tests import ClientLogTests
from .retarget_tests import RetargetTests
from .character_api_tests import CharacterApiTests
from .cloth_export_tests import ClothExportTests
from .cloth_szene_tests import ClothSzeneTests
from .cloth_engine_tests import ClothEngineTests
from .cloth_backe_tests import ClothBackeTests
from .kamera_keyframe_tests import KameraKeyframeTests
from .kamera_slerp_tests import KameraSlerpTests

ALL_CATEGORIES = [
    TheatreTests,
    FloorTests,
    SceneObjectTests,
    BundleUploadTests,
    BundleMtlTests,
    ProjektLichtTests,
    ProjektSzeneTests,
    RetargetTests,
    CharacterApiTests,
    ClothExportTests,
    ClothSzeneTests,
    ClothEngineTests,
    ClothBackeTests,
    KameraKeyframeTests,
    KameraSlerpTests,
    UiPrefsTests,
    ClientLogTests,
]

__all__ = ['TestCase', 'TestCategory', 'ALL_CATEGORIES']

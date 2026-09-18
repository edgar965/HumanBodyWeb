# BVH Studio Tests Package
from .base import TestCase, TestCategory
from .bundle_mtl_tests import BundleMtlTests
from .bundle_upload_tests import BundleUploadTests
from .character_api_tests import CharacterApiTests
from .client_log_tests import ClientLogTests
from .cloth_backe_tests import ClothBackeTests
from .cloth_engine_tests import ClothEngineTests
from .cloth_export_tests import ClothExportTests
from .cloth_licht_tests import ClothLichtTests
from .cloth_szene_tests import ClothSzeneTests
from .floor_tests import FloorTests
from .kamera_keyframe_tests import KameraKeyframeTests
from .kamera_slerp_tests import KameraSlerpTests
from .projekt_licht_tests import ProjektLichtTests
from .projekt_szene_tests import ProjektSzeneTests
from .retarget_tests import RetargetTests
from .scene_object_tests import SceneObjectTests
from .theatre_tests import TheatreTests
from .ui_prefs_tests import UiPrefsTests

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
    ClothLichtTests,
    ClothBackeTests,
    KameraKeyframeTests,
    KameraSlerpTests,
    UiPrefsTests,
    ClientLogTests,
]

__all__ = ['TestCase', 'TestCategory', 'ALL_CATEGORIES']

# BVH Studio Tests Package
from .base import TestCase, TestCategory
from .theatre_tests import TheatreTests
from .floor_tests import FloorTests
from .scene_object_tests import SceneObjectTests
from .scene_object_bundle_tests import SceneObjectBundleTests
from .project_tests import ProjectTests
from .ui_prefs_tests import UiPrefsTests
from .client_log_tests import ClientLogTests
from .retarget_tests import RetargetTests
from .character_api_tests import CharacterApiTests
from .cloth_export_tests import ClothExportTests
from .camera_track_tests import CameraTrackTests

ALL_CATEGORIES = [
    TheatreTests,
    FloorTests,
    SceneObjectTests,
    SceneObjectBundleTests,
    ProjectTests,
    RetargetTests,
    CharacterApiTests,
    ClothExportTests,
    CameraTrackTests,
    UiPrefsTests,
    ClientLogTests,
]

__all__ = ['TestCase', 'TestCategory', 'ALL_CATEGORIES']

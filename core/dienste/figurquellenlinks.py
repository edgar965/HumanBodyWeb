# -*- coding: utf-8 -*-
"""Figurquellenlinks — die Adressen zu jeder Zeile der Figur-Rangliste.

Aus `figurquellen.py` herausgehalten, damit keine der beiden Dateien über
die Grenze wächst (Regel: 200–300 Zeilen). Schlüssel ist der Bilderordner
unter `3DObjects/humanModels/`, derselbe wie in `Figurquellen.rangliste()`
und `Figurkoepfe.rangliste()` — oder, wo sich zwei Zeilen einen Ordner
teilen, deren `linkschluessel`.
Alle Adressen wurden am 17.09.2026 gelesen; Triplegangers sperrt
automatische Abrufe (403) und wurde im Browser gelesen.
"""

__all__ = ['Figurquellenlinks']


class Figurquellenlinks:
    """`(Beschriftung, Adresse)` je Bilderordner."""

    _3DSS = 'https://www.3dscanstore.com/'

    LINKS = {
        '19_TexturingXYZ_VFace_Kopf': [
            ('VFace-Sammlung', 'https://texturing.xyz/collections/vface'),
            ('Beispiel Tsoy #58', 'https://texturing.xyz/products/vface-tsoy-58'),
            ('Was im Paket ist', 'https://texturing.xyz/pages/vface-docs-whats-in-the-pack'),
        ],
        '15_3DScanStore_AnimationReady_Scans': [
            (
                'Animation Ready Body Scans (66 Personen)',
                _3DSS + 'retopologised-body-models/animation-ready-body-scans',
            ),
            (
                'Female 01',
                _3DSS + 'retopologised-body-models/'
                'animation-ready-body-scans/animation-ready-body-scan-female-01',
            ),
            ('Lizenz', _3DSS + 'terms-and-conditions-licensing'),
        ],
        '01_3DScanStore_Morphable_Frau_Mann': [
            (
                'Morphable Frau + Mann',
                _3DSS + 'base-mesh-3d-models-and-textures/morphable-male-female-base-mesh',
            ),
            ('Morphable Frau', _3DSS + 'base-mesh-3d-models-and-textures/morphable-female-base-mesh'),
        ],
        '02_3DScanStore_Ultimate_Textured': [
            ('Ultimate Textured Frau', _3DSS + 'base-mesh-3d-models-and-textures/female-base-mesh-textured'),
            ('Bundle Frau + Mann', _3DSS + 'base-mesh-3d-models-and-textures/textured-male-female-base-mesh'),
            ('kostenloser Scan (Tutorial)', _3DSS + 'download-free-3d-bodyscan-for-tutorial'),
            ('Multi-Expression-Basemesh (Blog)', _3DSS + 'blog/multi-expression-basemesh'),
        ],
        # Ein Bilderordner, zwei Zeilen (Kopf/Körper): Schlüssel `linkschluessel`.
        'eisko_louise': [
            ('Louise', 'https://www.eisko.com/louise/virtual-model'),
        ],
        'eisko_freakyhoody': [
            ('FreakyHoody', 'https://eisko.com/freakyhoody/'),
        ],
        '3dss_kopf_frei': [
            ('Multi-Expression-Basemesh (Blog)', _3DSS + 'blog/multi-expression-basemesh'),
        ],
        'ten24_kopf': [
            (
                'CG Channel (2023): freier Kopfscan',
                'https://www.cgchannel.com/'
                '2023/09/download-ten24s-free-hi-res-3d-scan-of-a-female-human-head/',
            ),
            ('Download bei 3D Scan Store', _3DSS + 'blog/Free-3D-Head-Model'),
        ],
        '16_Triplegangers': [
            ('Ganzkörper-Scans', 'https://triplegangers.com/browse/scans/full-body'),
            ('Beispiel Sadie Lehman', 'https://triplegangers.com/browse/scans/full-body/sadie-lehman-body'),
            ('Gratis-Samples', 'https://triplegangers.com/blog/technology/free-scan-samples'),
            ('Lizenz', 'https://triplegangers.com/terms-and-conditions-of-supply'),
            (
                '80.lv über Triplegangers',
                'https://80.lv/articles/create-realistic-3d-digital-humans-with-this-enormous-database',
            ),
        ],
        '04_Ten24_SampleScan': [
            ('Sample Scan', 'https://ten24.info/sample-scan/'),
            (
                'CG Channel (2016)',
                'https://www.cgchannel.com/2016/03/download-ten24s-free-full-body-scan-of-an-adult-male/',
            ),
        ],
        '17_Ten24_Shop': [
            ('Shop', 'https://ten24.info/shop/'),
            ('Ganzkörper-Scans im Shop', 'https://ten24.info/new-full-colour-full-body-scans-on-the-store/'),
        ],
        '06_Blender_HumanBaseMeshes_CC0': [
            ('Blender Demo-Dateien', 'https://www.blender.org/download/demo-files/#assets'),
            (
                'Spiegel (ZIP)',
                'https://mirror.blender.org/demo/asset-bundles/'
                'human-base-meshes/human-base-meshes-bundle-v1.4.1.zip',
            ),
            (
                'CG Channel (2023)',
                'https://www.cgchannel.com/2023/06/download-blender-studios-free-human-base-meshes/',
            ),
        ],
        '11_Daz_Genesis9': [
            ('EULA', 'https://www.daz3d.com/eula'),
            ('Genesis 9 (Blog)', 'https://www.daz3d.com/blog/a-first-look-at-whats-coming-in-genesis-9'),
        ],
        '18_CharacterCreator5_HD': [
            ('HD Character Base', 'https://www.reallusion.com/character-creator/hd-character-base.html'),
            (
                'CG Channel (2025)',
                'https://www.cgchannel.com/2025/08/reallusion-releases-character-creator-5/',
            ),
            (
                'Preis',
                'https://www.reallusion.com/plan-and-pricing/individual/perpetual/character-creator-5-3101',
            ),
        ],
        '05_MetaHuman': [
            ('MetaHuman', 'https://www.metahuman.com/'),
            ('Lizenz', 'https://www.metahuman.com/license'),
            (
                'CG Channel: außerhalb Unreal',
                'https://www.cgchannel.com/2025/06/'
                'you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/',
            ),
            ('Export: MetaHumanMeshTools', 'https://github.com/Ignifex/MetaHumanMeshTools'),
            (
                '80.lv: MetaHuman 5.6',
                'https://80.lv/articles/explore-new-metahuman-features-in-unreal-engine-5-6',
            ),
        ],
        '08_RenderPeople_frei': [
            ('Free 3D People', 'https://renderpeople.com/free-3d-people/'),
        ],
        '10_HumanGenerator_Blender': [
            ('Human Generator', 'https://humgen3d.com/'),
            ('Preise', 'https://humgen3d.com/pricing'),
            ('Lizenz', 'https://help.humgen3d.com/license'),
        ],
        '07_Blender_Einar_CC-BY': [
            ('Einar', 'https://studio.blender.org/characters/einar/'),
            ('Blender Studio Figuren', 'https://studio.blender.org/characters/'),
        ],
        'anny': [
            ('Anny', 'https://github.com/naver/anny'),
        ],
        'mpfb2': [
            ('MPFB2', 'https://github.com/makehumancommunity/mpfb2'),
            ('MakeHuman', 'https://github.com/makehumancommunity/makehuman'),
        ],
        # Die eigenen Figurarten: Quelle des Netzes bzw. des Ports.
        'humanbody': [
            ('MB-Lab (Ursprung des Netzes)', 'https://github.com/animate1978/MB-Lab'),
        ],
        'uma': [
            ('UMA 2', 'https://github.com/umasteeringgroup/UMA'),
        ],
        'smpl': [
            ('SMPL-X', 'https://smpl-x.is.tue.mpg.de/'),
            ('SMPL', 'https://smpl.is.tue.mpg.de/'),
        ],
        '12_Reallusion_CC_Base': [
            ('CC-Basis', 'https://www.reallusion.com/character-creator/free-3d-character-base.html'),
        ],
        '13_Forschung_THuman_2K2K': [
            ('THuman2.0', 'https://github.com/ytrock/THuman2.0-Dataset'),
            ('2K2K', 'https://github.com/SangHunHan92/2K2K'),
        ],
    }

    #: Was geprüft wurde und keine Netze liefert.
    AUSGESCHIEDEN = [
        (
            'Anatomy 360',
            'https://anatomy360.info/product/female-01-pose-pack/',
            'Pose-Scans nur im eigenen Viewer, kein Netz',
        ),
    ]

    @classmethod
    def fuer(cls, ordner):
        return cls.LINKS.get(ordner, [])

    @classmethod
    def alle(cls):
        return [adresse for links in cls.LINKS.values() for _n, adresse in links]

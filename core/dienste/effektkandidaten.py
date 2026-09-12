# -*- coding: utf-8 -*-
u"""Effektkandidaten — offener Code fuer Mimik, Haare, Kleidung und Wind.

Die Kandidatentabelle der Seite „Hilfe — Animationseffekte" und ihre
Quellen. Aus `Animationseffekte` herausgehalten, damit keine der beiden
Dateien ueber die Grenze waechst (Regel: 200–300 Zeilen).

Lizenz und Stand stammen aus den Adressen in `quellen()` (Web, 12.09.2026).
„Läuft hier" ist ehrlich: Gelaufen sind auf dieser Maschine nur MPFB und
Blender Cloth — in der Effekte-Pipeline (Process Videos → Effekte); alles
andere ist nachgelesen. Die Stoff-Kandidaten fuer das Theatre stehen NICHT
hier — sie sind unter Hilfe → Kleidung → Kleiderphysik gemessen und
entschieden.
"""

__all__ = ['Effektkandidaten']


class Effektkandidaten:
    u"""Die Kandidatentabelle und ihre Quellen."""

    @staticmethod
    def kandidaten():
        u"""Eine Zeile je Kandidat; `schicht` ordnet ihn der Tabelle oben zu."""
        return [
            {'name': 'MediaPipe Face Landmarker',
             'schicht': 'Mimik',
             'lizenz': 'Apache-2.0 (Code und Gewichte)',
             'laeuft': 'installiert (python14, `mediapipe`); Modell liegt in '
                       'MocapNET v4',
             'liefert': '478 Punkte, 52 Verformungswerte (ARKit-Namen) und '
                        'die Kopfpose je Bild, aus Video oder Webcam',
             'urteil': 'erster Kandidat — schon im Haus'},
            {'name': 'NVIDIA Audio2Face-3D',
             'schicht': 'Mimik',
             'lizenz': 'SDK MIT; Modelle NVIDIA Open Model License '
                       '(Hugging Face, Klick-Lizenz)',
             'laeuft': 'nicht geprüft',
             'liefert': 'Lippen und Ausdruck als Verformungswerte aus der '
                        'Tonspur; C++/CUDA-SDK, Plugins für Maya und Unreal',
             'urteil': 'für Szenen ohne Gesicht im Bild'},
            {'name': 'OpenSeeFace',
             'schicht': 'Mimik',
             'lizenz': 'BSD-2-Clause',
             'laeuft': 'nicht geprüft',
             'liefert': 'Landmarken und Kopfpose in Echtzeit auf der CPU '
                        '(VTuber-Szene); keine ARKit-Werte',
             'urteil': 'nur, wenn MediaPipe ausfällt'},
            {'name': 'FLAME + DECA / EMOCA / SMIRK',
             'schicht': 'Mimik',
             'lizenz': 'MPI, nur nicht-kommerziell',
             'laeuft': 'nicht geprüft',
             'liefert': 'Gesicht als 3D-Modell mit Ausdrucksparametern aus '
                        'einem Bild — dieselbe Familie wie SMPL-X',
             'urteil': 'nicht: Lizenz, und die Werte reichen'},
            {'name': 'Blender Hair Dynamics (Geometry Nodes, XPBD)',
             'schicht': 'Haare',
             'lizenz': 'GPL (als Werkzeug; Ergebnisse frei)',
             'laeuft': 'Blender 5.0 installiert; die Haardynamik kam mit '
                       '5.2 LTS',
             'liefert': 'Strähnen als biegsame Stäbe mit Kollidern und '
                        'Kraftfeldern (Wind, Turbulenz); Ablage als Cache',
             'urteil': 'der einzige fertige offene Strähnenlöser — '
                       'Kandidat für die Haar-Kette'},
            {'name': 'MPFB 2 (MakeHuman für Blender)',
             'schicht': 'Figur',
             'lizenz': 'GPLv3 (Code), Assets CC0',
             'laeuft': 'ja — 2.0.14 als Blender-Erweiterung, siehe '
                       'Effekte-Pipeline (Bestand)',
             'liefert': 'Figur mit Rigs (`cmu_mb` für den BVH Retargeter), zieht '
                        'MakeHuman-Kleider (.mhclo) aus der Kleiderbibliothek an; '
                        'Ausdrucksziele vorhanden',
             'urteil': 'die Figur der Effekte-Pipeline; Testfigur für Mimik'},
            {'name': 'Blender Cloth + Windfeld',
             'schicht': 'Kleidung, Wind (Video)',
             'lizenz': 'GPL (als Werkzeug; Ergebnisse frei)',
             'laeuft': 'ja — siehe Effekte-Pipeline (Bestand)',
             'liefert': 'Stoff mit Körper- und Selbstkollision, Wind mit '
                        'Turbulenz, Ablage je Bild; gerendert mit Workbench',
             'urteil': 'für das Offline-Video; im Theatre bleibt Newton'},
            {'name': 'BVH Retargeter (Blender-Erweiterung, Thomas Larsson)',
             'schicht': 'Körper',
             'lizenz': 'GPL',
             'laeuft': 'ja — 5.0.0, siehe Effekte-Pipeline (Bestand)',
             'liefert': 'BVH auf bekannte Rigs (SMPL-Namen → CMU MB), T-Pose '
                        'und Skalierung automatisch',
             'urteil': 'der Retarget-Schritt der Effekte-Pipeline'},
            {'name': 'Gaussian Haircut / Im2Haircut',
             'schicht': 'Haare',
             'lizenz': 'CC BY-NC-SA 4.0',
             'laeuft': 'nicht geprüft',
             'liefert': 'Strähnen-Frisur aus Video (Gaussian Haircut) oder '
                        'einem Bild (Im2Haircut, ICCV 2025)',
             'urteil': 'Forschung; Frisur kommt hier aus dem Bestand'},
            {'name': 'Newton SolverStyle3D',
             'schicht': 'Kleidung, Wind',
             'lizenz': 'Apache-2.0',
             'laeuft': 'ja — siehe Effekte-Pipeline (Bestand) und Kleiderphysik',
             'liefert': 'Stoff auf dem bewegten Körper (Kollider je Teilschritt), '
                        'Selbstkollision, Wind als Kraft je Punkt (`particle_f`)',
             'urteil': 'Motor der Wahl für Stoff — ohne Blender'},
            {'name': 'MetaHuman / Unreal Engine 5',
             'schicht': 'Mimik, Haare, Kleidung',
             'lizenz': 'Epic-EULA — kostenlos, nicht offen',
             'laeuft': 'nicht geprüft',
             'liefert': 'Gesichts-Capture per iPhone, Chaos Cloth, Groom',
             'urteil': 'nicht: lässt sich nicht in die Kette einbauen'},
        ]

    @staticmethod
    def quellen():
        return [
            ('MediaPipe Face Landmarker (Anleitung, Apache-2.0)',
             'https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker'),
            ('MediaPipe Blendshape V2 — Modellblatt (52 Werte)',
             'https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Blendshape%20V2.pdf'),
            ('NVIDIA Audio2Face-3D (Sammelrepo, Lizenzen)',
             'https://github.com/NVIDIA/Audio2Face-3D'),
            ('NVIDIA Audio2Face-3D SDK (MIT)',
             'https://github.com/NVIDIA/Audio2Face-3D-SDK'),
            ('OpenSeeFace (BSD-2-Clause)',
             'https://github.com/emilianavt/OpenSeeFace'),
            ('FLAME (MPI-Lizenz)', 'https://flame.is.tue.mpg.de/'),
            ('Blender 5.2 LTS Handbuch — Hair Dynamics',
             'https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/simulation/hair_dynamics.html'),
            ('Blender Developers Blog — Geometry Nodes Physics (Juli 2026)',
             'https://code.blender.org/2026/07/geometry-nodes-physics/'),
            ('MPFB 2 (GPLv3, Assets CC0)',
             'https://github.com/makehumancommunity/mpfb2'),
            ('MPFB als Blender-Erweiterung',
             'https://extensions.blender.org/add-ons/mpfb/'),
            ('BVH Retargeter (ehemals MakeWalk, GPL)',
             'https://github.com/Diffeomorphic/retarget-bvh'),
            ('Gaussian Haircut (CC BY-NC-SA 4.0)',
             'https://github.com/eth-ait/GaussianHaircut'),
            ('Im2Haircut (ICCV 2025)',
             'https://github.com/Vanessik/Im2Haircut'),
        ]

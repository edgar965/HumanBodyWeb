# -*- coding: utf-8 -*-
"""BVH aus Video — SMPL-X (eigene Pipeline) direkt starten, ohne die Web-Seite.

Ruft denselben Weg wie „Process Videos" -> SMPL-X (eigen) in der Web-Oberfläche:
`lift_3d.py --pipeline smplx`, mit denselben Standardquellen wie dort
(core/pipelines/smplbefehl.Smplbefehl.SMPLX_QUELLEN, Stand 29.09.2026):
Körper GEM-SMPL, Hände GEM-X, Gesicht SMPLest-X, Handgelenk aus der Hand.
Details und Hintergrund: Hilfe -> BVH aus Video.

VORAUSSETZUNGEN (nur auf dem eigenen Rechner lauffähig, kein portables Skript):
  - venv `python10` unter A:\\3DTools\\python10 (Python 3.10, CUDA-Torch)
  - Repo `VideoToBVH` unter A:\\3DTools\\VideoToBVH mit den eingelagerten
    Gewichten für GEM-SMPL/GEM-X und SMPLest-X (und GVHMR/DuoMo, falls als
    Körperquelle gewählt) — siehe requirements-ml.txt und die READMEs der
    jeweiligen Quelle.

AUFRUF:
    python bvh_aus_video_starten.py <video.mp4> [<ziel.bvh>]
        [--body gem|gvhmr|duomo] [--hands gemx|smplestx]
        [--face smplestx|keins] [--wrist hand|koerper]
        [--device cuda|cpu] [--kein_boden] [--kein_video]

Ohne <ziel.bvh> entsteht die BVH neben dem Video, unter gleichem Namen.
Ergebnis: <ziel>.bvh (54 Gelenke), <ziel>_ausdruck.json (Kiefer/Mimik) und,
ohne --kein_video, <ziel>_smplx.mp4 (das SMPL-X-Netz über dem Originalvideo).
"""
import argparse
import pathlib
import subprocess

PYTHON10 = r'A:\3DTools\python10\Scripts\python.exe'
LIFT_3D = r'A:\3DTools\VideoToBVH\wrappers\lift_3d.py'


def hauptprogramm():
    p = argparse.ArgumentParser(description='BVH aus Video ueber die SMPL-X-Pipeline starten.')
    p.add_argument('video', help='Eingabevideo (mp4)')
    p.add_argument('ziel', nargs='?', default=None, help='Ziel-BVH (Vorgabe: neben dem Video)')
    p.add_argument('--body', default='gem', choices=['gem', 'gvhmr', 'duomo'], help='Koerperquelle')
    p.add_argument('--hands', default='gemx', choices=['gemx', 'smplestx'], help='Handquelle')
    p.add_argument('--face', default='smplestx', choices=['smplestx', 'keins'], help='Gesichtsquelle')
    p.add_argument('--wrist', default='hand', choices=['hand', 'koerper'], help='Handgelenk aus Hand- oder Koerperquelle')
    p.add_argument('--device', default='cuda', choices=['cuda', 'cpu'])
    p.add_argument('--kein_boden', action='store_true', help='ohne Bodenkontakt-Korrektur der Wurzel')
    p.add_argument('--kein_video', action='store_true', help='ohne das Netz-Video ueber dem Original')
    a = p.parse_args()

    video = pathlib.Path(a.video)
    ziel = pathlib.Path(a.ziel) if a.ziel else video.with_suffix('.bvh')

    befehl = [
        PYTHON10, LIFT_3D, '--pipeline', 'smplx',
        '--video', str(video), '--output', str(ziel), '--device', a.device,
        '--body_source', a.body, '--hands_source', a.hands,
        '--face_source', a.face, '--wrist_source', a.wrist,
    ]
    if a.kein_boden:
        befehl.append('--no_ground')
    if a.kein_video:
        befehl.append('--no_video')

    print('Starte:', ' '.join(befehl))
    subprocess.run(befehl, check=True)


if __name__ == '__main__':
    hauptprogramm()

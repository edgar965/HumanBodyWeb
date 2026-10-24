# -*- coding: utf-8 -*-
"""Mesh3daikifassungen — EINE Stelle, die festlegt, welches Netz der KI ein Rechenlauf von Mesh3D-AI nimmt (23.10.2026).

Edgar: „Was fehlt dir noch, um diese Trainingsjobs perfekt per Knopfklick zu erzeugen??? ohne Wegwerf-Skripte!!“ — bis heute wählte jedes Skript der Ketten sein Netz selbst (`ls … | tail -1`,
„jüngster Lauf“, `gewaehlt.json`), ein Neulauf konnte darum ein anderes Ergebnis geben. Der Rechenlauf (`Mesh3dairechenlauf`) liest die Fassungen nur hier und reicht sie den Schritten
ausdrücklich weiter. Die Datei `3DObjects/mesh3dai/ki_fassungen.json` wird beim ersten Lesen mit den Netzen geschrieben, die die Testseiten am 23.10.2026 zeigen (Edgar: `test.json` → `lauf`,
`form.apose_lauf`); wer ein Netz tauscht, ändert die Datei — jeder Lauf schreibt die Fassungen, mit denen er rechnete, in seinen Stand.
"""
import json
from pathlib import Path

from django.conf import settings

from core.atomic_write import AtomarSchreiber

__all__ = ['Mesh3daikifassungen']


class Mesh3daikifassungen:
    #: Stand 23.10.2026 (Testjob `edgar`): Haltung = gemeinsames Netz auf Posen (`mesh3dai_test_form.py --vorhersagen`), Form = Formkopf auf der A-Pose-Wolke, Vorstufe = Netz des Wegs MIA,
    #: Kostüm-Weg A in Stufe 1 (Rückhäutung). Seit 23.10.2026 nachts (Edgar: „KI-Fassungen: Für Zerlegung und Haut legt die Datei noch nichts fest“ → „mach alles“) auch Zerlegung und Stufe 2 —
    #: die gewählten Läufe dieses Tages (`_zerlegung/gewaehlt.json`, `_stufe2/gewaehlt.json`, „EINE KI für alle Modelle“). Stufe 2 schreibt die Haut (`Stufe2hauteinsatz`) und nimmt den
    #: Schichtlauf, mit dem sie trainiert ist (`netz.pt` → `schichtlauf`); die Kleider der Testseite kommen weiter aus dem Kostüm-Weg (Sapiens2 + SAM 3).
    VORGABE = {
        'vorstufe_mia': '2026.10.18.16.22_vorstufe_apose9_mia_ab_alle4',
        'haltung': '2026.10.17.14.18_form_pose80_v3',
        'formkopf': '2026.10.19.18.04_vorstufe_form2_grenze_paare_compile',
        'zerlegung': '2026.10.20.17.18_zerlegung_b3d_job_tripo6_stelle_eineki',
        'stufe2': '2026.10.23.01.48_alle_p2000000_n64_t1024_s3',
        # Soll-Fassung, mit der dieser Lauf trainiert ist (`netz.pt` → `soll_fassung`): der Code steht seit 22.10.2026 auf 10, der Einsatz verweigert einen Lauf anderer Fassung;
        # `--fassung 8` stellt Bau und Soll auf dessen Stand (`Stufe2.alter_bau`) — gemessen 23.10.2026 nachts am Knopf-Lauf edgar_knopf
        'stufe2_fassung': 8,
        'kostuem_stufe': 1,
        # 24.10.2026: Start des Schritts „kopf“ (`Kopfangleich`) — das einzige trainierte Kopfnetz (21.10.2026, gewürfelte Köpfe); allein schlechter als der Formkopf an Tripo-Jobs mit Wahrheit
        'kopfnetz': '2026.10.21.17.51_kopf1',
    }
    TEXTE = {
        'vorstufe_mia': 'Rig und A-Pose: Netz der Vorstufe (Weg MIA)',
        'haltung': 'Haltung: gemeinsames Netz auf Posen',
        'formkopf': 'Form: Formkopf auf der A-Pose-Wolke',
        'zerlegung': 'Zerlegung: welcher Punkt des Netzes Haut, Haar oder welches Kleidungsstück ist',
        'stufe2': 'Haut: Stufe 2 der KI (Farbe je Texel der fünf Hautkacheln)',
        'stufe2_fassung': 'Haut: Soll-Fassung des Stufe-2-Laufs (Bau und Soll, mit denen er trainiert ist)',
        'kostuem_stufe': 'Kleider und Haar aus dem Mesh: Stufe (1 = an der Stelle des Eingangs, Rückhäutung)',
        'kopfnetz': 'Kopf: Kopfnetz als Start der Angleichung an das Mesh',
    }

    @staticmethod
    def datei():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / 'ki_fassungen.json'

    @classmethod
    def lesen(cls):
        datei = cls.datei()
        try:
            gelesen = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            gelesen = None
        if not isinstance(gelesen, dict):
            gelesen = {}
        if any(k not in gelesen for k in cls.VORGABE):
            # ein neuer Eintrag kommt mit der Vorgabe in die Datei; was dort schon steht, bleibt (wer ein Netz tauschte, behält seinen Tausch)
            gelesen = dict(cls.VORGABE, **gelesen)
            AtomarSchreiber.json_schreiben(datei, gelesen)
        return dict(cls.VORGABE, **{k: v for k, v in gelesen.items() if k in cls.VORGABE})

    @staticmethod
    def vorstufe_pfad(name):
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_vorstufe' / 'laeufe' / name

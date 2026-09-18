# -*- coding: utf-8 -*-
"""`manage.py mimik_vorbereiten` — die Mimik-Posenbibliothek aus MB-Lab bauen.

Liest die MB-Lab-Ausdrücke (`tools/MB-Lab/data`), rechnet jede Einheit über
die Hautgewichte in Drehungen der 49 DEF-Gesichtsknochen um
(`humanbody_core.mimik`) und schreibt

    static/mimik/basis.json     Einheit → Knochendrehungen (+1 / −1)
    static/mimik/posen.json     78 Posen mit Namen, Gruppe und Gewichten
    static/mimik/smplx_basis.json  Einheit → Netzverschiebung des SMPL-X-Kopfes
                                (16.09.2026, `core/dienste/mimiksmplx.py`)
    static/mimik/vorschau/      Kopfbilder je Pose (mit --vorschau)

Die Dateien sind versioniert; der Lauf ist nur nach einem Wechsel der
MB-Lab-Daten oder des Skeletts nötig. Schreibt nichts nach `HumanBody/data/`.
"""

import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from humanbody_core.mimik.knochendeltas import Knochendeltas
from humanbody_core.mimik.mblab_ausdruecke import MblabAusdruecke
from humanbody_core.mimik.posenbibliothek import Posenbibliothek


class Command(BaseCommand):
    help = "Mimik-Posen aus den MB-Lab-Ausdrücken für das DEF-Skelett bauen"

    def add_arguments(self, parser):
        parser.add_argument("--vorschau", action="store_true", help="Kopfbilder je Pose rendern (pyrender)")

    def handle(self, *args, **optionen):
        mblab = settings.TOOLS_ROOT / "tools" / "MB-Lab" / "data"
        daten = settings.HUMANBODY_ROOT / "data" / "humanBody"
        if not mblab.is_dir():
            raise CommandError("MB-Lab-Daten fehlen: %s" % mblab)
        ziel = settings.BASE_DIR / "static" / "mimik"
        ziel.mkdir(parents=True, exist_ok=True)

        start = time.perf_counter()
        ausdruecke = MblabAusdruecke(str(mblab))
        deltas = Knochendeltas(
            str(daten / "def_skeleton.json"),
            str(daten / "skin_weights_base.json"),
            str(daten / "vertices_tpose.npy"),
        )
        bibliothek = Posenbibliothek(ausdruecke, deltas)
        bibliothek.schreiben(str(ziel / "basis.json"), str(ziel / "posen.json"))
        posen = bibliothek.posen()
        basis = bibliothek.basis()
        knochen = {k for e in basis.values() for r in e.values() for k in r}
        self.stdout.write(
            "%d Einheiten, %d Posen, %d Gesichtsknochen bewegt, %.1f s"
            % (len(basis), len(posen), len(knochen), time.perf_counter() - start)
        )
        from core.dienste.mimiksmplx import Mimiksmplx

        if Mimiksmplx.vorhanden():
            start = time.perf_counter()
            bericht = Mimiksmplx.schreiben(ausdruecke.einheiten(), daten, ziel)
            self.stdout.write(
                "SMPL-X: %d Einheiten, bis %d Punkte je Feld, Landmarken %.2f mm, "
                "Zuordnung Median %.1f / p90 %.1f mm, %d Punkte ohne Quelle, %.1f s"
                % (
                    bericht["einheiten"],
                    bericht["punkte"],
                    bericht["landmarken_rest_mm"],
                    bericht["abstand_median_mm"],
                    bericht["abstand_p90_mm"],
                    bericht["ohne_quelle"],
                    time.perf_counter() - start,
                )
            )
        else:
            self.stdout.write("SMPL-X-Modell fehlt — smplx_basis.json nicht gebaut")
        if optionen.get("vorschau"):
            from core.dienste.mimikvorschau import Mimikvorschau

            anzahl = Mimikvorschau(ausdruecke, daten, ziel / "vorschau").alle(posen)
            self.stdout.write("%d Vorschaubilder" % anzahl)

# -*- coding: utf-8 -*-
"""Blendimportfigur — der Körper einer .blend wird über „Mesh to 3D" zur Genesis-9-Figur.

Konzept (Hilfe → Architektur → Genesis, 08.10.2026): Regler-Fit, Gesichtskette und Eigenmorph von „Mesh to 3D" sind
gebaut und gemessen; der Import gibt ihnen statt eines Scans den NACKTEN Körper (`Blendimportkoerper`). Dafür passen die
Optionen: keine Frisur und keine Haarkarten (das Haar wird ein eigenes Stück), Kleidung „wie Haut" (es gibt keine im
Netz), Kopfhaut „Haut lassen" (eigenes Haar), kein Modell `<Name> Mesh` — das Modell schreibt der Import selbst
(`Blendimportmodell`), mit Kleidern, Haar und der gebackenen Haut.

Der Auftrag ist ein gewöhnlicher `Meshfigurauftrag`: Er steht in der Liste von „Mesh to 3D", seine Seite zeigt Erkennung,
Runden und Vergleich. Gerechnet wird er im Prozess des Imports (`Meshfigurlauf.ausfuehren`), nicht in einem zweiten.
"""

import logging

from django.utils import timezone

logger = logging.getLogger('core')

__all__ = ['Blendimportfigur']


class Blendimportfigur:
    OPTIONEN = {
        'frisur': 'aus',
        'haarkarten': 'aus',
        'kleidung': 'wie_haut',
        'kopfhaut': 'haut',
        'textur': 'mesh',
        'modell': 'aus',
        'einheit': 'meter',
        'gesicht': 'an',
        'eigenmorph': 'an',
    }

    #: Weg „netz“ (`Blendimportweg`, 11.10.2026): das Netz ist verschmolzen und trägt Kleidung und Haar selbst — es gelten die Vorgaben des Reiters „Mesh to 3D“ (Stoff zieht schwach, Frisur und Haarkarten aus dem
    #: Netz, Kopfhaut, Textur aus dem Netz), nur Einheit (Meter: `Blendimportnetz` hat das Netz auf Menschenhöhe gebracht), Gesicht, Eigenmorph und das Speichern des Modells `<Name> Mesh` stehen fest.
    #: `kleidungsluft_mm` 4 (13.10.2026): die Haut der Figur darf nicht durch den Stoff des Netzes ragen. Spiralballerina (Strumpfhose, Mieder): 6 % der Kleidungspunkte lagen im Körper der Figur (15 % an den Knien, 13 % an der
    #: Brust, 5,5 % tiefer als 5 mm) — „Hautflecken auf dem Kleid"; der Rest-Schritt schob die Punkte bis auf die Fläche, nicht darunter. Der Katalog von „Mesh to 3D" bleibt bei 0 (Ten24, 07.10.2026: 4 mm nahmen
    #: Punkte außerhalb der Kleiderfläche von 359 auf 25 und machten die Figur unter dem Pullover ~2 mm schmaler); der Weg „netz" hat immer bekleidete Netze und setzt 4 mm (eine Einstellung dafür im Import gibt es noch nicht).
    OPTIONEN_NETZ = {
        'einheit': 'meter',
        'gesicht': 'an',
        'eigenmorph': 'an',
        'modell': 'an',
        'kleidungsluft_mm': 4,
    }

    def __init__(self, ablage, name, basis, netz=False, kleidung_zug=None, animationspruefung=None):
        self.ablage = ablage
        self.name = name
        self.basis = basis
        self.netz = netz
        #: Einstellung `animationspruefung` des Imports (`an`/`aus`, fehlt bei Aufträgen von vor dem 13.10.2026: an) — wird die Option `animationspruefung` von „Mesh to 3D“ (`Meshfigurtanzpruefung`).
        self.animationspruefung = animationspruefung
        #: Einstellung `kleidung_zug` des Imports (nur Weg „netz“): `weich` (Vorgabe von „Mesh to 3D“) oder `ignorieren`.
        self.kleidung_zug = kleidung_zug

    def optionen(self):
        """Die geprüften Optionen von „Mesh to 3D“ für diesen Import. Beim Weg „netz“ wählt die Einstellung `kleidung_zug` des Imports, wie der Stoff die Figur zieht
        (`weich`, `nah`, `ignorieren`); ein Wert, den der Katalog von „Mesh to 3D“ nicht kennt, fällt in `pruefen` auf dessen Vorgabe."""
        from .meshfiguroptionen import Meshfiguroptionen

        roh = dict(self.OPTIONEN_NETZ if self.netz else self.OPTIONEN, basis=self.basis)
        if self.netz and self.kleidung_zug:
            roh['kleidung'] = self.kleidung_zug
        if self.animationspruefung:
            roh['animationspruefung'] = self.animationspruefung
        return Meshfiguroptionen.pruefen(roh)

    def anlegen(self, glb):
        from ..daten.auftragskennung import Auftragskennung
        from ..daten.meshfigurablage import Meshfigurablage
        from ..models import Meshfigurauftrag
        from .meshfigureingang import Meshfigureingang

        kennung = Auftragskennung.frei(timezone.now(), lambda k: Meshfigurauftrag.objects.filter(kennung=k).exists())
        ablage = Meshfigurablage(kennung)
        eingang = Meshfigureingang(ablage).anlegen([], str(glb), None)
        job = Meshfigurauftrag.objects.create(kennung=kennung, name=self.name, eingang=eingang, optionen=self.optionen())
        logger.info('Blender-Import %s: Auftrag „Mesh to 3D" %s angelegt', self.ablage.kennung, kennung)
        return job

    @staticmethod
    def rechnen(job, zusatz=None, sapiens=None):
        """Den Auftrag in DIESEM Prozess rechnen; danach muss er „fertig“ sein, sonst ein Fehler mit seinem Grund.
        `zusatz`: weitere Felder für `auftrag.json` des Runners (`Meshfigurlauf.zusatz`) — die Pose des Schritts „pose“ (`landmarken_hand`, `Blendimportpose.zusatz`).
        `sapiens`: die Einstellungen der Segmentierung des Wegs „netz“ (`Blendimportsegmentierung.fuer_figur`) — dann nehmen Kleidungsmaske, Haarmaske und Hautton die Etiketten von Sapiens."""
        from ..models import Meshfigurauftrag
        from .meshfigurlauf import Meshfigurlauf

        job.status = 'laeuft'
        job.started_at = timezone.now()
        job.save(update_fields=['status', 'started_at', 'updated_at'])
        lauf = Meshfigurlauf(job.id)
        # Das Körper-Tor (`Meshfigurrumpfpruefung`, 01.10.2026) fängt Scans mit Stoff ab, deren Rumpf nicht stimmt. Hier ist
        # der Körper nackt und sauber: im ersten Lauf (2026.10.08.11.28.34) Rumpftiefe 95,5–101 % des Netzes, Abstand
        # Figur↔Netz 2,67 mm RMS, aber 11 Brust-/Schulterregler am Anschlag (Soll ≤ 8) — die Brust ist größer, als die Regler
        # hergeben. „melden": der Lauf geht weiter, der Befund steht in `ergebnis.koerper.tor` (wie bei „2D3D Kleider").
        lauf.tor = 'melden'
        lauf.zusatz.update(zusatz or {})
        if sapiens:
            # Dieselben Attribute setzt „2D3D Kleider“ aus der Option `segmentierung` (`Engine2d3dKleiderkoerperlauf`); „Mesh to 3D“ hat sie sonst nicht (`Meshfigurkleidung._sapiens`, `Sapienshaar.quelle`).
            lauf.sapiens_maske = sapiens.get('verwenden') == 'an'
            lauf.sapiens_einstellungen = dict(sapiens)
            lauf.sapiens_haar = sapiens.get('haar') or 'farbe'
        lauf.ausfuehren()
        job = Meshfigurauftrag.objects.get(pk=job.pk)
        if job.status != 'fertig':
            raise RuntimeError('Mesh to 3D %s: %s (%s)' % (job.kennung, job.status, job.error_message or 'ohne Grund'))
        return job

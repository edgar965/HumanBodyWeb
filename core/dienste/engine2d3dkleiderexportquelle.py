# -*- coding: utf-8 -*-
"""Engine2d3dKleiderexportquelle — die Exportleiste auf der Auftragsseite „2D3D Kleider" (31.10.2026, `Exportleistequelle`).

Edgar: „mach beides" (auf den Vorschlag, 2D3D Kleider auf die Exportleiste umzustellen). Die rechte Spalte der Seite war das Vorbild der Leiste (Export 03.10.2026, Render
04.10.2026); jetzt trägt sie die Leiste selbst. Anders als Mesh3D-AI und 2d-3d-AI baut der SERVER das Modell (`EIGENES_MODELL`): das Stand-Modell der Bühne
(`Engine2d3dKleideranimexport.quelle`: Körper mit gebackenen Kacheln, Augen, Mund, Wimpern, Brauen, Kleider und Haar am Rig, sonst die GLB der besten Runde). Nur so behält der
Render die Stoffsimulation der Kleider (`kleidung__gc_…`) und die Haarsträhnen (`haar__…`) — `Exportleisterendermodell` würde jedes Stück der Browser-GLB in `kleidung__eigen_…`
umbenennen und starr häuten. Die Bewegung ist die des Auftrags (`Engine2d3dKleideranimexport.bewegung`: `film_bewegung.json`, bei einer anderen BVH neu gerechnet und so abgelegt,
dass die Abspielleiste der Bühne sie ebenfalls spielt); Mimik und Gelenkkorrektur lesen die Stellung aus der Datenbank, weil das Modell in `<Auftrag>/ergebnis/` liegt.

Arbeitsordner = der Ordner des Auftrags: `arbeit/render/` (Rezept, Läufe, Programme, Warteschlange) und `ergebnis/` (Videos `render_lauf_NNN.mp4`) sind dieselben wie vor der
Umstellung — die bisherigen Render-Läufe, ein eigenes Rezept (Randy) und die Videos bleiben sichtbar. Die Regler übernimmt die Leiste beim ersten Öffnen aus den Optionen des
Auftrags (`regler_vorgabe`, Gruppen `render…`); danach gehören sie ihr (`arbeit/regler_werte.json`). Exportordner wie bisher `output/Export/Engine2d3dKleider/<Name>_<Anlagezeit>/`.
"""

from django.core.exceptions import ValidationError

from .exportleistequelle import Exportleistequelle

__all__ = ['Engine2d3dKleiderexportquelle']


class Engine2d3dKleiderexportquelle(Exportleistequelle):
    BEREICH = 'engine2d3dkleider'
    EIGENES_MODELL = True

    def __init__(self, kennung, job):
        super().__init__(kennung)
        self.job = job

    @classmethod
    def finden(cls, kennung):
        from ..models import Engine2d3dKleiderauftrag
        try:
            job = Engine2d3dKleiderauftrag.objects.filter(pk=kennung).first()
        except (ValidationError, ValueError):                 # keine UUID in der Adresse
            return None
        return cls(job.id, job) if job else None

    def name(self):
        return (self.job.name or 'modell').strip() or 'modell'

    def exportordner(self):
        from .engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
        return Engine2d3dKleiderspeichern.zielordner_fuer(self.job)

    def arbeitsordner(self):
        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        return Engine2d3dKleiderablage(self.job.kennung).ordner()

    def _film(self):
        from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
        return Engine2d3dKleideroptionen.film(self.job.optionen)

    def bvh_vorgabe(self):
        """Die BVH der Option „Film" (Vorgabe: der Tanz), sonst die des letzten Films — wie das Feld „BVH-Animation" bis zur Umstellung."""
        return str(self._film().get('bvh') or ((self.job.ergebnis or {}).get('film') or {}).get('bvh') or '')

    def ton_vorgabe(self):
        return str(self._film().get('ton') or '') or super().ton_vorgabe()

    def regler_vorgabe(self):
        from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
        werte = Engine2d3dKleideroptionen.pruefen(self.job.optionen)
        return {g: werte.get(g) or {} for g in Engine2d3dKleideroptionen.RENDERGRUPPEN}

    def sperre(self):
        from .engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
        self.job.refresh_from_db()                                  # `laeuft` ist eine Eigenschaft aus Status und Prozess, kein Feld
        if self.job.laeuft and Engine2d3dKleiderarbeiter.lebt(self.job):
            return 'Der Auftrag rechnet gerade — exportieren und rendern, wenn er fertig ist'
        return None

    def modell(self):
        from .engine2d3dkleideranimexport import Engine2d3dKleideranimexport
        pfad, _runde, _art = Engine2d3dKleideranimexport(self.job).quelle()
        if pfad is None:
            raise ValueError('Es gibt noch kein Modell — erst die Iterationen rechnen')
        return pfad

    def bewegung(self, bvh, stellung):
        from .engine2d3dkleideranimexport import Engine2d3dKleideranimexport
        return Engine2d3dKleideranimexport(self.job).bewegung(str(bvh))[0]

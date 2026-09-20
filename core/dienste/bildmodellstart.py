# -*- coding: utf-8 -*-
"""Bildmodellstart — ein Lauf aus dem Anfrage-Rumpf des Start-Endpunkts.

Herausgelöst aus `Bildmodellendpunkte.starten` (die Datei stand bei 300 Zeilen,
20.09.2026). Der Knopf „Bild neu" je Tabellenzeile läuft NICHT hierüber — er
rechnet kein Modell, nur die Bilder (`Bildmodellzeilenbild`).

Rumpf: `optionen` (sonst die des Auftrags), `fest` (festgehaltene Regler),
`ab` (Startschritt), `bis` (nur bis zu diesem Schritt), `schritte` (genau diese).
"""

from .bildmodellarbeiter import Bildmodellarbeiter
from .bildmodelloptionen import Bildmodelloptionen

__all__ = ['Bildmodellstart']


class Bildmodellstart:
    @classmethod
    def optionen(cls, job, rumpf):
        """Die Optionen des Laufs: geprüft, mit dem, was bleibt, und `fest`."""
        optionen = Bildmodelloptionen.pruefen(rumpf.get('optionen') or job.optionen)
        for feld in Bildmodelloptionen.BLEIBEN:
            # Ohne eigene Angabe bleiben Proportionen (Popup), Testfall, gezogene Linien und
            # Bildtypen-Vorgaben erhalten — `pruefen` kennt sie nicht.
            if feld not in (rumpf.get('optionen') or {}):
                optionen[feld] = (job.optionen or {}).get(feld) or {}
        if isinstance(rumpf.get('fest'), dict):
            optionen['fest'] = rumpf['fest']
        return optionen

    @classmethod
    def schritte(cls, rumpf):
        """`(ab, bis, schritte)` aus dem Rumpf — nur Schritte, die es gibt."""
        reihe = Bildmodelloptionen.REIHENFOLGE
        ab = rumpf.get('ab') or 'sichtung'
        if ab not in reihe:
            ab = 'sichtung'
        # `bis`: nur bis zu diesem Schritt (die Sichtung neuer Dateien, 19.09.2026).
        bis = rumpf.get('bis') if rumpf.get('bis') in reihe else None
        # `schritte`: genau diese Schritte — „Textur anpassen" = [sichtung,] textur (19.09.2026).
        schritte = [s for s in (rumpf.get('schritte') or []) if s in reihe]
        if schritte:
            ab, bis = schritte[0], schritte[-1]
        return ab, bis, schritte

    @classmethod
    def starten(cls, job, rumpf):
        """Optionen und Schritte setzen, den Arbeiter starten — die Antwort des Endpunkts."""
        optionen = cls.optionen(job, rumpf)
        ab, bis, schritte = cls.schritte(rumpf)
        optionen['ab'] = ab  # für `Bildmodelllauf.relativ`: Balken ab dem Startschritt
        job.optionen = optionen
        job.progress = 0
        job.schritt = ab
        job.save(update_fields=['optionen', 'progress', 'schritt', 'updated_at'])
        pid = Bildmodellarbeiter.starten(job, ab, bis, schritte or None)
        return {'ok': True, 'pid': pid, 'ab': ab, 'bis': bis, 'schritte': schritte}

# -*- coding: utf-8 -*-
"""Bildmodellstart — ein Lauf aus dem Anfrage-Rumpf des Start-Endpunkts.

Herausgelöst aus `Bildmodellendpunkte.starten` (die Datei stand bei 300 Zeilen),
als der Knopf „Bild neu" je Tabellenzeile dazukam (Edgar, 20.09.2026: „mach in
jeder Zeile einen Button mit dem ich das errechnete Bild für DIESE Zeile neu
berechnen kann, das muss schnell gehen"): der Rumpf nennt dann `schritte`
(Anpassung, Restmorph, Vorschau, Speichern — ohne die Textur, die Minuten
braucht) und `ansicht` — `optionen['nur_ansicht']` lässt Vorschau und
Proportionenbilder nur diese Ansicht rendern, die anderen bleiben stehen.

Rumpf: `optionen` (sonst die des Auftrags), `fest` (festgehaltene Regler),
`ab` (Startschritt), `bis` (nur bis zu diesem Schritt), `schritte` (genau
diese), `ansicht` (`vorn`, `seite`, `hinten`, `kopf`).
"""

from .bildmodellarbeiter import Bildmodellarbeiter
from .bildmodelloptionen import Bildmodelloptionen
from .bildmodellproportionen import Bildmodellproportionen

__all__ = ['Bildmodellstart']


class Bildmodellstart:
    #: Was der Knopf „Bild neu" je Zeile rechnet — ohne Textur.
    SCHRITTE_BILD = ('anpassung', 'rest', 'vorschau', 'speichern')

    @classmethod
    def optionen(cls, job, rumpf):
        """Die Optionen des Laufs: geprüft, mit dem, was bleibt, `fest` und `nur_ansicht`."""
        optionen = Bildmodelloptionen.pruefen(rumpf.get('optionen') or job.optionen)
        for feld in Bildmodelloptionen.BLEIBEN:
            # Ohne eigene Angabe bleiben Proportionen (Popup), Testfall, gezogene Linien und
            # Bildtypen-Vorgaben erhalten — `pruefen` kennt sie nicht.
            if feld not in (rumpf.get('optionen') or {}):
                optionen[feld] = (job.optionen or {}).get(feld) or {}
        if isinstance(rumpf.get('fest'), dict):
            optionen['fest'] = rumpf['fest']
        ansicht = rumpf.get('ansicht')
        if ansicht in Bildmodellproportionen.ANSICHTEN:
            optionen['nur_ansicht'] = ansicht
        else:
            optionen.pop('nur_ansicht', None)
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
        return {'ok': True, 'pid': pid, 'ab': ab, 'bis': bis, 'schritte': schritte,
                'ansicht': optionen.get('nur_ansicht')}

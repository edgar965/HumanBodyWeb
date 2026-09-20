# -*- coding: utf-8 -*-
"""Bildmodellstart — ein Lauf aus dem Anfrage-Rumpf des Start-Endpunkts.

Herausgelöst aus `Bildmodellendpunkte.starten` (die Datei stand bei 300 Zeilen,
20.09.2026). Der Knopf „Bild neu" je Tabellenzeile läuft NICHT hierüber — er
rechnet kein Modell, nur die Bilder (`Bildmodellzeilenbild`).

Rumpf: `optionen` (sonst die des Auftrags), `fest` (festgehaltene Regler),
`ab` (Startschritt), `bis` (nur bis zu diesem Schritt), `schritte` (genau diese),
`bild` (Einzelschritt `gvhmr` — stellt Körperschätzer und Weg auf GVHMR, danach
rechnet der Lauf das Modell, `Bildmodelllauf.NACH_GVHMR`).
"""

import logging

from .bildmodellarbeiter import Bildmodellarbeiter
from .bildmodelloptionen import Bildmodelloptionen

logger = logging.getLogger('core')

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
        # Einzelschritt `gvhmr` (Knopf „SMPL (GVHMR)" je Kachel, 20.09.2026): das Bild — oder eine
        # Liste (Edgar: „baue für jedes Bild das GVHMR") — und ob neu gerechnet wird; `pruefen`
        # kennt beides nicht, ein späterer Start räumt es weg.
        bild = rumpf.get('bild')
        if isinstance(bild, list):
            optionen['gvhmr_bild'] = [str(b)[:200] for b in bild if isinstance(b, str) and b][:500]
            optionen['gvhmr_neu'] = bool(rumpf.get('neu'))
        elif bild:
            optionen['gvhmr_bild'] = str(bild)[:200]
            optionen['gvhmr_neu'] = bool(rumpf.get('neu'))
        if bild:
            geaendert = cls.gvhmr_als_schaetzer(optionen)
            if geaendert:
                logger.info('Bildmodell %s: GVHMR-Lauf stellt Optionen um: %s',
                            getattr(job, 'kennung', '?'), geaendert)
        return optionen

    #: Der Weg zum Zielnetz, der die Betas des Schätzers wirklich nimmt: SMPL-X aus den Betas,
    #: auf den Genesis-Käfig gepaart. `silhouette` sieht nur die Umrisse — die Vorher/Nachher-
    #: Bilder blieben dann die alten, egal wie gut das SMPL-X aus GVHMR ist.
    WEG_SCHAETZER = 'schaetzer'

    @classmethod
    def gvhmr_als_schaetzer(cls, optionen):
        """Der GVHMR-Lauf rechnet danach das Modell (`Bildmodelllauf.NACH_GVHMR`) — dafür
        werden Körperschätzer und Weg zum Zielnetz auf GVHMR gestellt (Edgar, 20.09.2026:
        „ich verstehe nicht, [warum] die kranken Bilder … kommen, wenn das SMPL-Bild besser
        ausschaut … Berechne auch die immer neu, mit dem GVHMR-Lauf"). Bleibt am Auftrag,
        sichtbar im Optionenformular; wer wieder Silhouetten will, stellt es dort zurück."""
        geaendert = {}
        # Und nichts formt das GVHMR-Ziel hinterher um: Umriss der Fotos, Fotomaße und die
        # Popup-Eingaben aus (Damira, 20.09.: die Popup-Linien zwischen den anliegenden Armen
        # machten aus Brustbreite 30,2 → 21,0 cm, Oberarm 8,2 → 4,8 — der „Alien" blieb trotz GVHMR).
        for feld, wert in (('koerper', 'gvhmr'), ('weg', cls.WEG_SCHAETZER),
                           ('umriss', 'aus'), ('fotomasse', 'aus'), ('popup', 'aus')):
            if optionen.get(feld) != wert:
                geaendert[feld] = (optionen.get(feld), wert)
                optionen[feld] = wert
        return geaendert

    @classmethod
    def schritte(cls, rumpf):
        """`(ab, bis, schritte)` aus dem Rumpf — nur Schritte, die es gibt."""
        reihe = Bildmodelloptionen.REIHENFOLGE
        ab = rumpf.get('ab') or 'sichtung'
        if ab not in reihe:
            ab = 'sichtung'
        # `bis`: nur bis zu diesem Schritt (die Sichtung neuer Dateien, 19.09.2026).
        bis = rumpf.get('bis') if rumpf.get('bis') in reihe else None
        # `schritte`: genau diese Schritte — „Textur anpassen" = [sichtung,] textur (19.09.2026);
        # Einzelschritte (`EINZELN`) nur hier, nie über `ab`.
        bekannt = reihe + list(Bildmodelloptionen.EINZELN)
        schritte = [s for s in (rumpf.get('schritte') or []) if s in bekannt]
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

# -*- coding: utf-8 -*-
"""Bildmodelldateien — ein Bild ersetzen oder löschen, mit allem, was daran hängt.

Edgar (19.09.2026): „Mach in jeder Zeile einen Button zum Bild hochladen,
mit dem ich ein anderes Bild hochladen kann, und eines zum Bild löschen."

Ein Original (`original/<name>`) kann mehrere Ausschnitte haben (Collage,
Gruppenbild) — jeder ist ein Eintrag in `job.bilder` mit `quelle` = Name
des Originals, `datei` = Ausschnitt in `zuschnitt/`, und die Schätzer legen
je Ausschnitt `<stamm>_posed.npy`, `<stamm>_flame.npy` in `schaetzung/` ab.

    original_ersetzen(name, upload)   neue Datei unter demselben Namen;
                                      alle Einträge dieser Quelle und ihre
                                      Dateien weg — die Sichtung (Umfang
                                      „nur neue Dateien") holt den Befund nach
    original_entfernen(name)          Original samt Einträgen und Dateien
    bild_entfernen(datei)             ein Ausschnitt; das Original geht mit,
                                      wenn kein anderer Eintrag es braucht

Gelöscht wird nur innerhalb des Auftragsordners (`Bildmodellablage.datei`
prüft den Pfad). Das Ergebnis des Auftrags bleibt stehen — es gilt bis
zum nächsten Lauf.
"""

import logging
import os

logger = logging.getLogger('core')

__all__ = ['Bildmodelldateien']


class Bildmodelldateien:
    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    # ------------------------------------------------------------ Lesen

    def eintraege_zu(self, quelle):
        return [b for b in self.job.bilder if (b.get('quelle') or b.get('datei')) == quelle]

    def ohne_befund(self):
        """Originale (Bilder und Videos), zu denen kein Eintrag gehört — noch nicht gesichtet."""
        quellen = {b.get('quelle') or b.get('datei') for b in self.job.bilder}
        return [p.name for p in self.ablage.originale() + self.ablage.videos() if p.name not in quellen]

    # ---------------------------------------------------------- Löschen

    def _weg(self, unterordner, name):
        if not name:
            return
        try:
            pfad = self.ablage.datei(unterordner, name)
        except ValueError:
            return
        if pfad.is_file():
            pfad.unlink()

    def _eintrag_dateien_weg(self, eintrag):
        """Ausschnitt und Schätzernetze eines Eintrags."""
        datei = eintrag.get('datei') or ''
        if eintrag.get('video'):
            # Das Standbild des Videos liegt im Zuschnittordner; die GVHMR-Rechnung bleibt.
            self._weg(self.ablage.ZUSCHNITT, datei)
            return
        self._weg(self.ablage.ZUSCHNITT, datei)
        stamm = os.path.splitext(datei)[0]
        for feld in ('schaetzung', 'gesichtsschaetzung'):
            s = eintrag.get(feld) or {}
            for k in ('posed_vertices_path', 'flame_vertices_path'):
                if s.get(k):
                    self._weg(self.ablage.SCHAETZUNG, os.path.basename(s[k]))
        for anhang in ('_posed.npy', '_flame.npy'):
            self._weg(self.ablage.SCHAETZUNG, stamm + anhang)

    def _eintraege_weg(self, eintraege):
        weg = {id(e) for e in eintraege}
        for e in eintraege:
            self._eintrag_dateien_weg(e)
        self.job.bilder = [b for b in self.job.bilder if id(b) not in weg]

    def original_entfernen(self, name):
        """Original samt Einträgen und Dateien; Anzahl entfernter Einträge."""
        eintraege = self.eintraege_zu(name)
        self._eintraege_weg(eintraege)
        self._weg(self.ablage.ORIGINAL, name)
        self.job.save(update_fields=['bilder', 'updated_at'])
        logger.info('Bildmodell %s: Original %s entfernt (%d Einträge)', self.job.kennung, name,
                    len(eintraege))
        return len(eintraege)

    def bild_entfernen(self, datei):
        """Einen Ausschnitt entfernen; True, wenn das Original mitging."""
        eintrag = self.job.bild(datei)
        if eintrag is None:
            return False
        quelle = eintrag.get('quelle') or datei
        self._eintraege_weg([eintrag])
        original_weg = not self.eintraege_zu(quelle)
        if original_weg:
            self._weg(self.ablage.ORIGINAL, quelle)
        self.job.save(update_fields=['bilder', 'updated_at'])
        logger.info('Bildmodell %s: Bild %s entfernt (Original %s)', self.job.kennung, datei,
                    'weg' if original_weg else 'bleibt')
        return original_weg

    # --------------------------------------------------------- Ersetzen

    def original_ersetzen(self, name, hochgeladen):
        """Die Datei `name` durch den Upload ersetzen (Name bleibt, Endung vom Upload);
        Einträge und Dateien der alten gehen; liefert den neuen Namen."""
        self._eintraege_weg(self.eintraege_zu(name))
        self._weg(self.ablage.ORIGINAL, name)
        stamm = os.path.splitext(name)[0]
        endung = os.path.splitext(self.ablage.sauber(getattr(hochgeladen, 'name', name)))[1] or '.jpg'
        neu = stamm + endung
        self.ablage.anlegen()
        ziel = self.ablage.datei(self.ablage.ORIGINAL, neu)
        with open(ziel, 'wb') as f:
            for stueck in hochgeladen.chunks():
                f.write(stueck)
        self.job.save(update_fields=['bilder', 'updated_at'])
        logger.info('Bildmodell %s: Original %s ersetzt durch %s', self.job.kennung, name, neu)
        return neu

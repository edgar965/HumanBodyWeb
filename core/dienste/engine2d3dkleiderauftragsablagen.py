# -*- coding: utf-8 -*-
"""Engine2d3dKleiderauftragsablagen — die Ablagen eines Auftrags „2D3D Kleider" AUSSERHALB seines Ordners, die sein Kürzel im Namen tragen (06.10.2026).

Der Auftragsordner (`3DObjects/engine2d3dkleiderauftraege/<Kennung>/`) ist nur ein Teil seines Zustands. Alles, was die Runden aus SEINEN Fotos oder SEINEM Körper rechnen, liegt neben der Bibliothek und trägt das Kürzel der Kennung
(`Rezeptumgebung.kuerzel`: '2026.10.06.14.20.55' → 'j20261006142055'), damit zwei Aufträge mit demselben Stück einander nicht überschreiben (`artefakte-benennen.md`):
  `kleidtexturen/`   Foto-Atlanten je Materialgruppe (`<Stück>__<Gruppe>__foto_<Kürzel>_f1.png`) und ihr Verzeichnis (`<Stück>__foto_<Kürzel>_f1.json`), Decals
  `kleidmorphe/`     Hülle, Drapieren, Zellenmorphe (`<Stück>__huelle_<Kürzel>_f1.npz`, `…__drapiert_<Kürzel>_f1.*`, `…__netz_b<i>s<j>_<Kürzel>_f1.npz`)
  `eigenmorphe/`     Körper-Ortsmorphe (`ort_rumpftiefe_<Kürzel>.npz`, `ort_gesichtsprofil_<Kürzel>.*`)
Die Auftragskopie (`Engine2d3dKleiderauftragskopie`) nahm bis dahin nur den Ordner mit: Die Kopie hatte die Runden, aber das Hemd war im Standmodell grau, weil die Atlanten mit dem Kürzel der QUELLE
und nicht dem der Kopie benannt waren (Kopie `2026.10.06.14.20.55` von „Edgar - Sapiens 4": sieben Atlas-Dateien von Hand nachgelegt, die Körper-Ortsmorphe gar nicht).

Hier: jede Datei der drei Ordner, deren Name das Kürzel der Quelle als eigenes Wort trägt, wird unter dem Kürzel des Ziels NEU ANGELEGT (nichts überschrieben — gibt es den Namen schon, bleibt er und wird gezählt; die Dateien der
Quelle bleiben). Die JSON-Dateien dort bekommen das neue Kürzel auch im Text. `ersetzen` setzt das Kürzel (und die Kennung mit Punkten) in einem Text um — die Kopie benutzt es für die JSON-Felder der Zeile, damit `werte`, Rezepte und
Regler des Ziels auf SEINE Dateien zeigen.
Nicht kopiert: die Fotostücke der Bibliothek (`eigen_foto_<letzte acht Ziffern>_…`, `3DObjects/models/Genesis9/bibliothek`) — sie tragen die letzten acht Ziffern statt des Kürzels, die Kopie nennt sie weiter beim Namen der Quelle; und der Inhalt
der `.npz`-Dateien wird nicht umgeschrieben (ob in ihnen der Name steht, ist nicht geprüft).
"""

import logging
import re
import shutil

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderauftragsablagen']


class Engine2d3dKleiderauftragsablagen:
    def __init__(self, quelle_kennung, ziel_kennung):
        from Genesis9.rezeptumgebung import Rezeptumgebung
        self.quelle_kennung, self.ziel_kennung = str(quelle_kennung), str(ziel_kennung)
        self.alt = Rezeptumgebung.kuerzel(quelle_kennung)
        self.neu = Rezeptumgebung.kuerzel(ziel_kennung)
        #: Das Kürzel als eigenes Wort: davor und danach kein Buchstabe und keine Ziffer (der Unterstrich trennt).
        self._wort = re.compile(r'(?<![0-9a-z])%s(?![0-9a-z])' % re.escape(self.alt)) if self.alt else None
        self.angelegt = []
        self.schon_da = []

    @staticmethod
    def ordner():
        """Die Ordner neben der Bibliothek, in denen Dateien mit dem Kürzel liegen."""
        from Genesis9.eigenmorphe import G9eigenmorphe
        from Genesis9.kleidmorphe import G9kleidmorphe
        from Genesis9.kleidtexturen import G9kleidtexturen
        return [G9kleidtexturen.ordner(), G9kleidmorphe.ordner(), G9eigenmorphe.ordner()]

    # ------------------------------------------------------------------ Text

    def enthaelt(self, text):
        """Kommt die Kennung oder das Kürzel der Quelle im Text vor?"""
        return self.quelle_kennung in text or bool(self._wort and self._wort.search(text))

    def ersetzen(self, text):
        """Kennung (mit Punkten) und Kürzel der Quelle durch die des Ziels ersetzen."""
        text = text.replace(self.quelle_kennung, self.ziel_kennung)
        return self._wort.sub(self.neu, text) if self._wort and self.neu else text

    # ----------------------------------------------------------------- Dateien

    def dateien(self):
        """`[(Quelle, Ziel)]` — jede Datei der Ordner mit dem Kürzel der Quelle als Wort im Namen, mit dem Kürzel des Ziels benannt."""
        if self._wort is None or not self.neu or self.alt == self.neu:
            return []
        liste = []
        for ordner in self.ordner():
            if not ordner.is_dir():
                continue
            for pfad in sorted(ordner.glob('*%s*' % self.alt)):
                if pfad.is_file() and self._wort.search(pfad.name):
                    liste.append((pfad, ordner / self._wort.sub(self.neu, pfad.name)))
        return liste

    def kopieren(self):
        """Die Dateien unter dem Kürzel des Ziels anlegen → Zahl der neu angelegten. Scheitert eine, werden die in diesem Aufruf angelegten wieder entfernt (`zuruecknehmen`)."""
        try:
            for quelle, ziel in self.dateien():
                if ziel.exists():
                    self.schon_da.append(ziel.name)
                    continue
                if quelle.suffix.lower() == '.json':
                    AtomarSchreiber.text_schreiben(ziel, self.ersetzen(quelle.read_text(encoding='utf-8')))
                else:
                    shutil.copy2(quelle, ziel)
                self.angelegt.append(ziel)
        except BaseException:
            self.zuruecknehmen()
            raise
        if self.schon_da:
            logger.warning('2D3D Kleider %s → %s: %d Ablagen gab es schon und blieben unberührt (z. B. %s)', self.quelle_kennung, self.ziel_kennung,
                           len(self.schon_da), self.schon_da[0])
        return len(self.angelegt)

    def zuruecknehmen(self):
        """Nur, was DIESER Aufruf angelegt hat, wieder entfernen."""
        for datei in self.angelegt:
            datei.unlink(missing_ok=True)
        self.angelegt = []

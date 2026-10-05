# -*- coding: utf-8 -*-
"""Engine2d3dKleiderauftragskopie — der Stand eines gerechneten Auftrags „2D3D Kleider" in einen anderen, noch leeren Auftrag kopieren (05.10.2026).

Edgar: „Du solltest eine Kopie des gerechneten Auftrages machen" — der Auftrag „Edgar - Sapiens 2" hatte nur die Fotos, kein Netz, keine Figur; „Edgar - Sapiens 1" ist bis „Kleiderstücke" gerechnet.

Was kopiert wird
    Dateien   der ganze Auftragsordner, mit `copy2` (Änderungszeit bleibt: `ergebnis.fotostuecke.stand` und der Zettel des Tiefennetzes prüfen Größe und Änderungszeit der Dateien),
              OHNE `tmp/` (Zwischenstände eines Laufs), `*.teil` (halb geschriebene Dateien), `auftrag.log`/`auftrag.pid` und `arbeit/render/` (die Renderläufe des Quellauftrags: eigene Zettel mit
              Pfaden, neu zu rechnen — der Zielauftrag fängt dort leer an)
    Zeile     `status`, `schritt`, `progress`, `progress_detail`, `optionen`, `bilder`, `eingang`, `ergebnis`, `started_at`, `finished_at` — die Kennung des Quellauftrags wird in den JSON-Feldern
              und in den kleinen JSON-Dateien durch die des Ziels ersetzt (sie steht in absoluten Pfaden). Name, Kennung, ID bleiben die des Ziels.
Was NICHT kopiert wird: `pid` (leer), `error_message` (leer), `modell` (der Name eines gespeicherten Modells gehört der Quelle), die Handwertung `qualitaet_*` (jeder Rang gilt je Liste nur einmal).
`ergebnis['kopie']` hält fest, woher der Stand kommt.

Zwei Umfänge (`mit_allem`):
    schlank   wie oben beschrieben — der Stand der Figur und der Runden, ohne Renderläufe und Protokoll (die Kopie „Edgar - Sapiens 2" aus „Edgar - Sapiens 1")
    alles     (Edgar, 05.10.2026: „Einmal MIT allen Daten, Modellen, usw. und Ausgaben") — der GANZE Auftragsordner: auch `arbeit/render/` (Renderläufe, Film), `tmp/` und `auftrag.log`;
              nur `auftrag.pid` und halb geschriebene `*.teil` bleiben zurück. NICHT dabei: Dateien außerhalb des Auftragsordners — die gespeicherten Modelle der Bibliothek und die Ablage
              unter `output/Export/Engine2d3dKleider/` (`Engine2d3dKleiderspeichern`) gehören dem Quellauftrag; ihre Adressen enthalten seine ID.
Die ohne Daten (nur Fotos und Einstellungen) macht `Auftragsduplikat` („Job duplizieren").

Nur in einen LEEREN Zielauftrag (Status „angelegt", kein Ergebnis) und nur aus einem Auftrag, der nicht rechnet — es wird nichts überschrieben, was jemand gerechnet hat.
`als_neuer_auftrag` legt den Zielauftrag selbst an (Name + „ (Kopie)", neue Kennung) und räumt Zeile und Ordner auf, wenn das Kopieren scheitert.
Binäre Dateien (npz, glb) werden nicht umgeschrieben; ob in ihnen Pfade stehen, ist nicht geprüft (die Prüfung der Änderungszeit läuft über die Zeile, nicht über den Inhalt).
"""

import json
import logging
import os
import shutil
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from ..daten.auftragskennung import Auftragskennung
from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..models import Engine2d3dKleiderauftrag
from .auftragsduplikat import Auftragsduplikat
from .engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter

__all__ = ['Engine2d3dKleiderauftragskopie']

logger = logging.getLogger('core')


class Engine2d3dKleiderauftragskopie:
    #: Was nie mitgeht: die PID eines Laufs und halb geschriebene Dateien.
    NIE_NAMEN = frozenset({'auftrag.pid'})
    NIE_ENDUNGEN = ('.teil',)
    #: Was nur die schlanke Kopie auslässt (`mit_allem=False`).
    AUSLASSEN_NAMEN = frozenset({'tmp', 'auftrag.log'})
    AUSLASSEN_ORDNER = (('arbeit', 'render'),)
    #: Die Spalten, die der Stand mitnimmt; die JSON-Spalten bekommen die Kennung des Ziels.
    FELDER = ('status', 'schritt', 'progress', 'progress_detail', 'optionen', 'bilder', 'eingang', 'ergebnis', 'started_at', 'finished_at')
    JSON_FELDER = ('optionen', 'bilder', 'eingang', 'ergebnis')
    #: Kleine JSON-Dateien, in denen die Kennung des Quellauftrags in Pfaden steht (arbeit/auftrag.json, segmentierung/auftrag.json …).
    TEXT_HOECHSTENS = 4 * 1024 * 1024

    def __init__(self, quelle, ziel, mit_allem=False):
        self.quelle = quelle
        self.ziel = ziel
        self.mit_allem = mit_allem
        self.von = Engine2d3dKleiderablage(quelle.kennung).ordner()
        self.nach = Engine2d3dKleiderablage(ziel.kennung).ordner()

    @classmethod
    def als_neuer_auftrag(cls, quelle, mit_allem=True):
        """Ein NEUER Auftrag (Name + „ (Kopie)", eigene Kennung und Ordner) mit dem Stand von `quelle` → der neue Auftrag. Scheitert etwas, bleiben weder Zeile noch Ordner zurück."""
        cls.quelle_pruefen(quelle)
        kennung = Auftragskennung.frei(timezone.now(), lambda k: Engine2d3dKleiderauftrag.objects.filter(kennung=k).exists())
        ablage = Engine2d3dKleiderablage(kennung)
        ablage.anlegen()
        ziel = Engine2d3dKleiderauftrag.objects.create(kennung=kennung, name=(quelle.name + Auftragsduplikat.ZUSATZ)[:Auftragsduplikat.NAMENSLAENGE])
        try:
            ergebnis = cls(quelle, ziel, mit_allem).kopieren()
        except BaseException:
            ziel.delete()
            ablage.loeschen()
            raise
        logger.info('Kopie 2D3D Kleider: %s (%s) → %s (%s), %s, %d Dateien, %.1f MB', quelle.name, quelle.kennung, ziel.name, kennung, 'alles' if mit_allem else 'schlank', ergebnis['dateien'], ergebnis['mb'])
        ziel.refresh_from_db()
        return ziel

    @classmethod
    def von_kennungen(cls, quelle, ziel):
        """Die Aufträge zu zwei Kennungen (die Adresse der Seite) — ValueError, wenn einer fehlt."""
        gefunden = {}
        for rolle, kennung in (('Quelle', quelle), ('Ziel', ziel)):
            job = Engine2d3dKleiderauftrag.objects.filter(kennung=kennung).first()
            if job is None:
                raise ValueError('%s: kein Auftrag „2D3D Kleider“ mit der Kennung %s' % (rolle, kennung))
            gefunden[rolle] = job
        return cls(gefunden['Quelle'], gefunden['Ziel'])

    # ------------------------------------------------------------------ Prüfen

    @classmethod
    def quelle_pruefen(cls, quelle):
        """ValueError, wenn aus diesem Auftrag nicht kopiert werden darf (er rechnet, oder es gibt nichts)."""
        if quelle.laeuft or Engine2d3dKleiderarbeiter.lebt(quelle):
            raise ValueError('„%s“ rechnet gerade — erst abwarten oder anhalten' % quelle.name)
        if quelle.status == 'angelegt' or not (quelle.ergebnis or {}):
            raise ValueError('„%s“ hat nichts gerechnet, es gibt nichts zu kopieren (dafür gibt es „Job duplizieren“)' % quelle.name)
        if not Engine2d3dKleiderablage(quelle.kennung).ordner().is_dir():
            raise ValueError('Der Ordner von „%s“ fehlt' % quelle.name)

    def pruefen(self):
        """ValueError mit dem Grund, wenn die Kopie nicht gemacht werden darf."""
        if self.quelle.pk == self.ziel.pk:
            raise ValueError('Quelle und Ziel sind derselbe Auftrag')
        self.quelle_pruefen(self.quelle)
        if self.ziel.status != 'angelegt' or (self.ziel.ergebnis or {}):
            raise ValueError('Der Zielauftrag ist nicht leer (Status %s) — es wird nichts überschrieben' % self.ziel.status)
        if self.ziel.laeuft or Engine2d3dKleiderarbeiter.lebt(self.ziel):
            raise ValueError('Der Zielauftrag rechnet gerade')

    # ------------------------------------------------------------------ Dateien

    def _ausgelassen(self, relativ):
        teile = relativ.parts
        if any(t in self.NIE_NAMEN for t in teile) or relativ.name.endswith(self.NIE_ENDUNGEN):
            return True
        if self.mit_allem:
            return False
        if any(t in self.AUSLASSEN_NAMEN for t in teile):
            return True
        return any(teile[:len(ordner)] == ordner for ordner in self.AUSLASSEN_ORDNER)

    def dateien(self):
        """`[(Quelle, Ziel, relativ)]` aller Dateien, die mitgehen."""
        liste = []
        for pfad in sorted(self.von.rglob('*')):
            if pfad.is_file():
                relativ = pfad.relative_to(self.von)
                if not self._ausgelassen(relativ):
                    liste.append((pfad, self.nach / relativ, relativ))
        return liste

    def _text_umschreiben(self, pfad):
        """Die Kennung des Quellauftrags in einer kleinen JSON-Datei ersetzen (Änderungszeit bleibt)."""
        if pfad.suffix.lower() != '.json' or pfad.stat().st_size > self.TEXT_HOECHSTENS:
            return False
        try:
            text = pfad.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return False
        if self.quelle.kennung not in text:
            return False
        stand = pfad.stat()
        pfad.write_text(text.replace(self.quelle.kennung, self.ziel.kennung), encoding='utf-8')
        os.utime(pfad, ns=(stand.st_atime_ns, stand.st_mtime_ns))
        return True

    def _kopieren_dateien(self):
        angelegt, umgeschrieben, groesse = [], 0, 0
        try:
            for quelle, ziel, _ in self.dateien():
                ziel.parent.mkdir(parents=True, exist_ok=True)
                neu = not ziel.exists()
                shutil.copy2(quelle, ziel)
                if neu:
                    angelegt.append(ziel)
                groesse += ziel.stat().st_size
                umgeschrieben += self._text_umschreiben(ziel)
        except BaseException:
            for datei in angelegt:          # nur, was diese Kopie neu angelegt hat; was vorher da war (die Fotos), bleibt
                datei.unlink(missing_ok=True)
            raise
        return len(angelegt), umgeschrieben, groesse

    # ------------------------------------------------------------------ Zeile

    def _wert(self, feld):
        wert = getattr(self.quelle, feld)
        if feld in self.JSON_FELDER:
            text = json.dumps(wert, ensure_ascii=False).replace(self.quelle.kennung, self.ziel.kennung)
            return json.loads(text)
        return wert

    def _zeile(self):
        felder = {feld: self._wert(feld) for feld in self.FELDER}
        felder['ergebnis'] = dict(felder['ergebnis'], kopie={
            'von': self.quelle.kennung, 'name': self.quelle.name, 'am': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
            'umfang': 'alles' if self.mit_allem else 'schlank', 'ohne': [] if self.mit_allem else ['arbeit/render', 'tmp', 'auftrag.log']})
        felder.update(pid=None, error_message='', modell='')
        return felder

    # ------------------------------------------------------------------ Ausführen

    def kopieren(self):
        """Dateien, dann die Zeile → `{'dateien', 'mb', 'umgeschrieben', 'von', 'nach'}`. Scheitert das Kopieren der Dateien, bleibt die Zeile unverändert."""
        self.pruefen()
        zahl, umgeschrieben, groesse = self._kopieren_dateien()
        with transaction.atomic():
            Engine2d3dKleiderauftrag.objects.filter(pk=self.ziel.pk).update(**self._zeile(), updated_at=timezone.now())
        return {'dateien': zahl, 'mb': round(groesse / 1e6, 1), 'umgeschrieben': umgeschrieben, 'von': str(self.von), 'nach': str(Path(self.nach))}

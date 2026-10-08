# -*- coding: utf-8 -*-
"""Gesichtsformquelle — wessen Gesicht die Seite „Gesichtsform" bearbeitet.

Zwei Quellen (Anfrage `auftrag` oder `modell`):

  * „Mesh to 3D"-Auftrag: Figur = `job.stellung()` (Regler, Eigenmorph, Kopf-Eigen), Zielkurven aus
    seinem Kopfnetz (`Gesichtsformziel`). „Morph rechnen" trägt den Kopf-Eigen-Morph in
    `ergebnis.kopfeigen` ein — die Auftragsseite zeigt ihn sofort, Textur/Vorschau/Speichern tragen ihn,
    und ein neuer Lauf rechnet ihn nach dem Eigenmorph mit denselben Zielkurven nach
    (`Meshfigurende.kopfeigen_nachziehen`).
  * Gespeichertes Modell (`data/models/<Name>.json`, Genesis 9): Figur = `figur.regler`; Zielkurven aus dem
    Auftrag, aus dem das Modell stammt (`figur.herkunft.auftrag`), sonst keine — dann wird gemalt.
    „Im Modell speichern" schreibt den Regler in DIESES Modell (ausdrücklicher Knopfdruck).
"""

import json
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Gesichtsformquelle']


class Gesichtsformquelle:
    #: „Kopf-Eigen" hing nur an `Meshfigurauftrag` — `Gesichtsformziel._ablage_fuer` kennt BlenderModel und
    #: „2D3D Kleider" schon (30.09.2026), die Auftragssuche hier aber noch nicht (07.10.2026, Edgar 8).
    @staticmethod
    def _modelle():
        from ..models import Blendermodellauftrag, Engine2d3dKleiderauftrag, Meshfigurauftrag

        return (Meshfigurauftrag, Engine2d3dKleiderauftrag, Blendermodellauftrag)

    def __init__(self, auftrag=None, modell=None):
        self.job, self.modellname, self.modelldaten = None, None, None
        if auftrag:
            for Modell in self._modelle():
                self.job = Modell.objects.filter(kennung=str(auftrag)).first()
                if self.job is not None:
                    break
            if self.job is None:
                raise ValueError('Auftrag %s gibt es nicht' % auftrag)
        elif modell:
            self.modellname = str(modell)
            with open(self.modellpfad(), encoding='utf-8') as f:
                self.modelldaten = json.load(f)
            if self.modelldaten.get('quelle') != 'genesis9':
                raise ValueError('„%s" ist keine Genesis-9-Figur' % modell)
        else:
            raise ValueError('auftrag oder modell fehlt')

    @classmethod
    def aus(cls, daten):
        return cls(daten.get('auftrag'), daten.get('modell'))

    def modellpfad(self):
        from ..daten.modellpfad import Modellpfad

        pfad = Modellpfad.geprueft(Path(settings.HUMANBODY_MODELS_DIR), self.modellname, '.json')
        if pfad is None or not Path(pfad).is_file():
            raise ValueError('Modell „%s" gibt es nicht' % self.modellname)
        return Path(pfad)

    # ---------------------------------------------------------------- Figur

    @staticmethod
    def auftragsname(job):
        """Der Name des Kopf-Eigen-Morphs eines Auftrags (wie der Eigenmorph: Name + Zeit der Kennung)."""
        return '%s %s' % (job.name, job.kennung[-8:].replace('.', ''))

    def name(self):
        """Der Name des Kopf-Eigen-Morphs (ohne Präfix)."""
        return self.auftragsname(self.job) if self.job is not None else self.modellname

    def titel(self):
        return self.job.name if self.job is not None else self.modellname

    def stellung(self):
        if self.job is not None:
            return self.job.stellung()
        return dict((self.modelldaten.get('figur') or {}).get('regler') or {})

    def fototextur(self):
        """Die Kacheln der Figur (für die 3D-Ansicht) — `{kachel: Adresse}`."""
        if self.job is not None:
            f = (self.job.ergebnis or {}).get('fototextur') or {}
            bilder = dict(f.get('kacheln') or {})
            if f.get('augen'):
                bilder['augen'] = f['augen']
            stamm, stand = '/api/meshfigur/%s/datei/ergebnis/' % self.job.id, f.get('stand') or ''
            return {k: '%s%s?t=%s' % (stamm, n, stand) for k, n in bilder.items()}
        return dict((self.modelldaten.get('figur') or {}).get('fototextur') or {})

    def zielauftrag(self):
        """Der Auftrag, dessen Netz die Zielkurven liefert — oder None."""
        if self.job is not None:
            return self.job
        kennung = ((self.modelldaten.get('figur') or {}).get('herkunft') or {}).get('auftrag')
        if not kennung:
            return None
        from ..models import Meshfigurauftrag

        return Meshfigurauftrag.objects.filter(kennung=kennung).first()

    # ------------------------------------------------------------- Ergebnis

    def uebernehmen(self, regler, ergebnis, wert=1.0):
        """Nach „Morph rechnen": beim Auftrag in `ergebnis.kopfeigen` eintragen."""
        if self.job is None:
            return
        self.job.ergebnis = dict(self.job.ergebnis or {})
        alt = self.job.ergebnis.get('kopfeigen') or {}
        self.job.ergebnis['kopfeigen'] = {
            'regler': regler,
            'wert': float(wert),
            'guete': ergebnis.get('guete'),
            'max_mm': ergebnis.get('max_mm', alt.get('max_mm')),
            'punkte': ergebnis.get('punkte', alt.get('punkte')),
        }
        self.job.save(update_fields=['ergebnis', 'updated_at'])

    def speichern(self, regler, wert=1.0):
        """„Im Modell speichern": Auftrag → sein Modell neu schreiben; Modell → Regler eintragen."""
        if self.job is not None:
            from .meshfigurspeichern import Meshfigurspeichern

            return Meshfigurspeichern.fuer(self.job).modell_speichern()
        daten = dict(self.modelldaten)
        figur = dict(daten.get('figur') or {})
        figur['regler'] = {**dict(figur.get('regler') or {}), regler: float(wert)}
        daten['figur'] = figur
        with open(self.modellpfad(), 'w', encoding='utf-8') as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)
        logger.info('Gesichtsform: %s = %.2f in Modell %s', regler, wert, self.modellname)
        return self.modellname

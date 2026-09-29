# -*- coding: utf-8 -*-
"""Meshfigurspeichern — Schritt „speichern" von „Mesh to 3D": Modell und Ablage.

MODELL (`data/models/<Name>.json`, Option `modell`): dieselbe Form wie „Modell speichern" der
Szene und `Bildmodellspeichern` (`{name, quelle: genesis9, figur: {regler, …}}`), damit
Figurwahl, Studio und Theatre die Figur laden — Regler samt Eigenmorph. Der Name bekommt den
Zusatz „Mesh" und wird nie über ein fremdes Modell geschrieben (Projektregel: Prüfungen über
die Oberfläche schreiben in Edgars Daten — am 10.09. wurde so `FemaleGarmentCode` überschrieben):
gehört eine gleichnamige Datei nicht zu DIESEM Auftrag, kommt eine Nummer dazu.

ABLAGE (`output/Export/MeshTo3D/<Name>_<JJJJ.MM.TT.HH.MM>/`, Edgar: „Das Ergebnis dann hier:
…\\output\\Export\\MeshTo3D"): das Modell als JSON mit relativen Texturnamen, die Kacheln, der
Eigenmorph (npz + Steckbrief), Vorschau- und Vergleichsbilder, `bericht.json` mit allen Zahlen.
Ordnername aus der ANLAGEZEIT (wie `Meshexportablage`): ein zweiter Lauf ersetzt seine eigene
Ablage. Die GLB mit Rig und Textur schreibt der Browser dazu (Knopf „Exportieren" der
Auftragsseite, `Modellexport` — derselbe Weg wie im Kontextmenü der Szene).
"""

import json
import logging
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.utils.timezone import template_localtime

logger = logging.getLogger('core')

__all__ = ['Meshfigurspeichern']


class Meshfigurspeichern:
    ZUSATZ = 'Mesh'
    BILDER = (
        'icon.png',
        'vorlage.png',
        'vorschau_vorn.png',
        'vorschau_seite.png',
        'vorschau_hinten.png',
        'vorschau_kopf.png',
        'vergleich.jpg',
        'erkennung_koerper.jpg',
        'erkennung_gesicht.jpg',
    )

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage
        self.optionen = lauf.optionen

    # --------------------------------------------------------------- Daten

    def modelldaten(self, name, kacheln):
        return {
            'name': name,
            'quelle': 'genesis9',
            'figur': {
                'figur': 'basis',
                'regler': self.job.stellung(),
                'haut': '',
                'augen': '01',
                'brauen': '',
                'brauenstil': '',
                'praesets': {},
                'pose': '',
                'ausdruck': '',
                # Die Frisur aus Schritt „frisur" (`Meshfigurfrisur`, 29.09.2026) — leer ohne Wahl.
                'kleidung': dict((self.job.ergebnis.get('frisur') or {}).get('kleidung') or {}),
                'fototextur': kacheln,
                'herkunft': {
                    'auftrag': self.job.kennung,
                    'art': 'mesh to 3d',
                    'netz': (self.job.eingang or {}).get('original'),
                },
            },
        }

    def _bilder(self):
        """`{1001: Datei, …, 'augen': Datei}` — die Kacheln und das gefärbte Augenbild
        (`Meshfiguraugenbild`; `Genesis9fototextur` legt es auf die Augäpfel)."""
        f = self.job.ergebnis.get('fototextur') or {}
        aus = dict(f.get('kacheln') or {})
        if f.get('augen'):
            aus['augen'] = f['augen']
        return aus

    def _adressen(self):
        stamm = '/api/meshfigur/%s/datei/ergebnis/' % self.job.id
        return {k: stamm + n for k, n in self._bilder().items()}

    # ------------------------------------------------------------- Ablauf

    def ausfuehren(self):
        aus = {}
        if self.optionen.get('modell') == 'an':
            aus['modell'] = self.modell_speichern()
        aus['ablage'] = self.ablegen()
        self.job.ergebnis['gespeichert'] = aus

    @classmethod
    def fuer(cls, job):
        """Ohne Lauf — für „Als Genesis-Figur speichern" auf der Auftragsseite."""
        from types import SimpleNamespace

        from ..daten.meshfigurablage import Meshfigurablage
        from .meshfiguroptionen import Meshfiguroptionen

        return cls(
            SimpleNamespace(
                job=job, ablage=Meshfigurablage(job.kennung), optionen=Meshfiguroptionen.pruefen(job.optionen)
            )
        )

    def modell_speichern(self, wunsch=None):
        """Modell `<Name> Mesh` (nächste freie Nummer, wenn der Name einer fremden Figur gehört) —
        oder genau `wunsch`: dann wird eine fremde Figur nicht überschrieben, sondern abgelehnt."""
        ordner = Path(settings.HUMANBODY_MODELS_DIR)
        ordner.mkdir(parents=True, exist_ok=True)
        if wunsch is not None:
            name = re.sub(r'[^\w\s\-]', '', str(wunsch)).strip()
            if not name:
                raise ValueError('Name fehlt')
            if (ordner / (name + '.json')).is_file() and not self._eigenes(ordner / (name + '.json')):
                raise ValueError('„%s" gibt es schon als andere Figur — bitte einen anderen Namen' % name)
            return self._schreiben(ordner, name)
        stamm = re.sub(r'[^\w\s\-]', '', '%s %s' % (self.job.name, self.ZUSATZ)).strip() or 'Modell Mesh'
        name, n = stamm, 2
        while (ordner / (name + '.json')).is_file() and not self._eigenes(ordner / (name + '.json')):
            name, n = '%s %d' % (stamm, n), n + 1
        return self._schreiben(ordner, name)

    def _schreiben(self, ordner, name):
        from .modelltexturen import Modelltexturen

        daten = self.modelldaten(name, self._adressen())
        # Die Kacheln neben das Modell (Szene, Export; überleben das Löschen des Auftrags).
        daten['figur'] = Modelltexturen.sichern(name, daten['figur'])
        with open(ordner / (name + '.json'), 'w', encoding='utf-8') as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)
        self.job.modell = name
        self.job.save(update_fields=['modell', 'updated_at'])
        return name

    def _eigenes(self, pfad):
        try:
            with open(pfad, encoding='utf-8') as f:
                return ((json.load(f).get('figur') or {}).get('herkunft') or {}).get(
                    'auftrag'
                ) == self.job.kennung
        except OSError, ValueError:
            return False

    # -------------------------------------------------------------- Ablage

    def zielordner(self):
        return self.zielordner_fuer(self.job)

    @staticmethod
    def zielordner_fuer(job):
        """`MeshTo3D/<Name>_<JJJJ.MM.TT.HH.MM>` (Anlagezeit) — auch das Ziel des Browser-Exports."""
        roh = (job.name or 'figur').strip()
        sauber = re.sub(r'[<>:"|?*\\/\x00-\x1f]', '_', roh).strip(' .') or 'figur'
        stamm = '%s_%s' % (sauber, template_localtime(job.created_at).strftime('%Y.%m.%d.%H.%M'))
        return Path(settings.MESHFIGUR_EXPORT_DIR) / stamm

    def ablegen(self):
        from Genesis9.eigenmorphe import G9eigenmorphe

        ziel = self.zielordner()
        ziel.mkdir(parents=True, exist_ok=True)
        dateien = []
        kacheln = self._bilder()
        for name in list(kacheln.values()) + list(self.BILDER):
            quelle = self.ablage.ergebnis(name)
            if quelle.is_file():
                shutil.copy2(quelle, ziel / name)
                dateien.append(name)
        rest = (self.job.ergebnis.get('rest') or {}).get('regler')
        if rest:
            kennung = rest[len(G9eigenmorphe.PRAEFIX) :]
            for endung in ('.npz', '.json'):
                quelle = G9eigenmorphe.ordner() / (kennung + endung)
                if quelle.is_file():
                    shutil.copy2(quelle, ziel / ('eigenmorph_' + kennung + endung))
                    dateien.append('eigenmorph_' + kennung + endung)
        modell = '%s.json' % self.zielordner().name
        (ziel / modell).write_text(
            json.dumps(self.modelldaten(self.job.name, kacheln), ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        bericht = {k: v for k, v in self.job.ergebnis.items() if k not in ('gespeichert',)}
        (ziel / 'bericht.json').write_text(
            json.dumps(bericht, ensure_ascii=False, indent=1, default=str), encoding='utf-8'
        )
        dateien += [modell, 'bericht.json']
        logger.info('Mesh to 3D %s: abgelegt unter %s (%d Dateien)', self.job.kennung, ziel, len(dateien))
        return {'ordner': str(ziel), 'dateien': dateien}

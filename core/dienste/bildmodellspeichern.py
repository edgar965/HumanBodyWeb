# -*- coding: utf-8 -*-
"""Bildmodellspeichern — das Ergebnis als Modell unter `data/models/<Name>.json`.

Aus `Bildmodellanpassung` herausgelöst (19.09.2026, die Datei stand bei 300
Zeilen). Dieselbe Form wie „Modell speichern" in der Szene (`{name, quelle,
figur}`), damit der Figurwahldialog, Studio und Theatre das Modell laden:
Regler samt Restmorph (`stellung`), das Haar aus den Personenangaben als
Kleidung, die Angaben selbst unter `herkunft.person`.
"""

import json

__all__ = ['Bildmodellspeichern']


class Bildmodellspeichern:
    def __init__(self, job, optionen, stellung):
        self.job = job
        self.optionen = optionen
        self.stellung = stellung

    def modelldaten(self):
        person = self.optionen.get('person') if isinstance(self.optionen.get('person'), dict) else {}
        return {
            'name': self.job.name,
            'quelle': 'genesis9',
            'figur': {
                'figur': 'basis',
                'regler': self.stellung,
                'haut': '',
                'augen': '01',
                'brauen': '',
                'brauenstil': '',
                'praesets': {},
                'pose': '',
                'ausdruck': '',
                'kleidung': {person['haar']: {}} if person.get('haar') else {},
                'fototextur': self.fototextur(),
                'hautverschiebung': self.fototextur('verschiebung'),
                'herkunft': {'auftrag': self.job.kennung, 'art': 'modell aus bildern', 'person': person},
            },
        }

    def fototextur(self, feld='kacheln'):
        """`{kachel: Adresse}` der gebackenen Kacheln (Stufe 2) bzw. der Verschiebungskacheln
        (`verschiebung`, Alter/Tonus/Masse) — leer ohne Fototextur."""
        f = self.job.ergebnis.get('fototextur') or {}
        return {
            k: '/api/bildmodell/%s/datei/ergebnis/%s' % (self.job.id, name)
            for k, name in (f.get(feld) or {}).items()
        }

    def speichern(self, melder=None):
        if self.optionen.get('modell', 'an') != 'an':
            return None
        import re

        from django.conf import settings

        daten = self.modelldaten()
        # Dieselbe Bereinigung wie „Modell speichern" (`Modelldateien.modell_sichern`).
        sauber = re.sub(r'[^\w\s\-]', '', daten['name']).strip() or 'Modell'
        daten['name'] = sauber
        ordner = settings.HUMANBODY_MODELS_DIR
        ordner.mkdir(parents=True, exist_ok=True)
        with open(ordner / (sauber + '.json'), 'w', encoding='utf-8') as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)
        self.job.modell = sauber
        self.job.save(update_fields=['modell', 'updated_at'])
        return sauber

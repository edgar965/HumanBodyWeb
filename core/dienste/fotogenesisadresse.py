# -*- coding: utf-8 -*-
"""Fotogenesisadresse — die Adresse eines Tests von Foto-Genesis folgt seinem Namen (07.11.2026, Edgar: „nach einer Umbenennung des Jobs soll sich auch die Adresse ändern“).

Nur die Seite heißt anders. Der Schlüssel bleibt die Kennung (`job['id']`, der Ordner unter `3DObjects/fotogenesis/`): `job.json` trägt absolute Pfade, Läufe und `/api/fotogenesis/<id>/…` hängen an ihr, darum
wird nichts umbenannt und nichts verschoben. Die alte Adresse leitet um (`Fotogenesisendpunkte.test`), Lesezeichen und Links anderer Seiten bleiben gültig.

Es zählt der angezeigte Name, ob er aus `name.json` (Stift auf der Seite) oder aus der `job.json` kommt: Session3dTools steht in der `job.json`, der Ordner heißt anders. Exporte (ohne `name_vorgabe`)
heißen wie ihr Ordner und behalten ihre Adresse. Ist die Adresse schon vergeben (Kennung oder Name eines anderen Jobs) oder bleibt vom Namen nichts übrig, gilt die Kennung; so zeigt jede Adresse auf
genau einen Job.

    Fotogenesisadresse.vergeben(jobs)    # setzt `adresse` je Zeile (`Fotogenesisjobs.alle`)
    Fotogenesisadresse.seite(job)        # '/foto-genesis/test/session3dtools/'
"""
from .kennungsstamm import Kennungsstamm

__all__ = ['Fotogenesisadresse']


class Fotogenesisadresse:
    LAENGE = 100

    @classmethod
    def vergeben(cls, jobs):
        belegt = {j['id'] for j in jobs}
        for job in jobs:
            job['adresse'] = job['id']
            if 'name_vorgabe' not in job:
                continue
            wunsch = Kennungsstamm.aus_name(job['name'], cls.LAENGE)
            if wunsch and wunsch not in belegt:
                belegt.add(wunsch)
                job['adresse'] = wunsch
        return jobs

    @staticmethod
    def seite(job):
        return '/foto-genesis/test/%s/' % (job.get('adresse') or job['id'])

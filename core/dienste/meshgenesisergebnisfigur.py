# -*- coding: utf-8 -*-
"""Meshgenesisergebnisfigur — welche Genesis-Figur das Feld „Ergebnis“ einer Jobseite zeigt: NUR was die KI ausgibt (19.10.2026 spätabends).

Edgar: „Hast du geschummelt …?“ → „das Ergebnis soll direkt aus der KI kommen“ → „alle jobs, alle test jobs, alle trainings sollen der WAHRHEIT entsprechen“. Bis hierher baute die Seite das Ergebnis
aus der gespeicherten Figur DES JOBS (`Meshgenesisgenesis.figur`: Form, Gesicht, Haut, Kleider, Haar des Ziels) und stellte sie nur in die vorhergesagte Pose — bei den Tripo-Jobs war damit alles außer
der Pose die Wahrheit. Jetzt:
    1. Tripo-Job mit KI-Lauf (`lauf_ergebnis.json` → `ergebnis_figur.modell`, geschrieben von `meshgenesis_paar_lauf.py`): die vom Formnetz vorhergesagte Figur des Tests (`_test/<kennung>/form_<g>/modell.json`).
    2. Sonst: die Formregler, die das Formnetz für DIESE Probe vorhersagte (`formen_vorhersagen.npz` des Vorgabelaufs, Zuordnung Probe ↔ Zeile wie `Meshgenesisformvariante`).
    3. Ohne Vorhersage: die Grundfigur des Geschlechts — und der Text sagt es.
Was die KI nicht ausgibt, kommt nicht hinein: Kleider, Haar, Haut des Ziels. Haut = Grundhaut des Geschlechts (`feminine`/`masculine`), dazu nur das Anatomie-Stück des Geschlechts (wie die Formfiguren
der Tests: Ursula1 `daz_anatomie_frau`, Matt0 `daz_anatomie_mann`) — beides Vorgaben, keine Vorhersage, und so beschriftet.

    Meshgenesisergebnisfigur.fuer(job, nr, lauf_ergebnis) -> {'figur': {...}, 'quelle': Text, 'form': 'ki'|'grundfigur'}
"""
import json
import logging
from pathlib import Path

import torch
from KoerperKI_alle.npztorch import Npztorch
from django.conf import settings

from .meshgenesisformtraining import Meshgenesisformtraining
from .meshgenesisformvariante import Meshgenesisformvariante
from .meshgenesisformvariantefigur import Meshgenesisformvariantefigur

logger = logging.getLogger('core')

__all__ = ['Meshgenesisergebnisfigur']


class Meshgenesisergebnisfigur:
    GRUNDHAUT = {'weiblich': 'feminine', 'maennlich': 'masculine'}
    ANATOMIE = {'weiblich': ('Ursula1', 'daz_anatomie_frau'), 'maennlich': ('Matt0', 'daz_anatomie_mann')}
    #: Vorgabe der Texte unter dem Feld (die Seite zeigt sie im Hinweis).
    #: Haut ohne Hautkopf — `Meshgenesisgenesis` ersetzt genau diesen Satz, wenn die Probe Hautkacheln aus der KI hat (`Meshgenesisprobenhaut`, 21.10.2026).
    TEXT_HAUT = 'Haut: Grundhaut des Geschlechts (Vorgabe, keine Vorhersage).'
    TEXT_VORGABEN = (TEXT_HAUT + ' Anatomie-Stück des Geschlechts (Vorgabe, keine Vorhersage); Kleider und Haar kommen getrennt aus der KI (`Meshgenesisergebniskleider`, '
                     '`Meshgenesisprobenkleider`), wo sie gerechnet sind.')

    @staticmethod
    def _json(pfad):
        try:
            return json.loads(Path(pfad).read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return None

    @classmethod
    def anatomie(cls, geschlecht):
        quelle, schluessel = cls.ANATOMIE.get(geschlecht, cls.ANATOMIE['weiblich'])
        kleidung = ((cls._json(Path(settings.HUMANBODY_MODELS_DIR) / ('%s.json' % quelle)) or {}).get('figur') or {}).get('kleidung') or {}
        return {schluessel: kleidung[schluessel]} if schluessel in kleidung else {}

    @classmethod
    def _figur(cls, geschlecht, regler):
        return {'figur': cls.GRUNDHAUT.get(geschlecht, 'feminine'), 'regler': regler, 'kleidung': cls.anatomie(geschlecht), 'garmentcode': [], 'pose': ''}

    @classmethod
    def fuer(cls, job, nr, ergebnis=None):
        geschlecht = job.get('geschlecht') if job.get('geschlecht') in cls.GRUNDHAUT else 'weiblich'
        # 1. Tripo-Job: die vorhergesagte Figur des Tests.
        e = (ergebnis or {}).get('ergebnis_figur') or {}
        if e.get('modell'):
            d = cls._json(e['modell'])
            regler = ((d or {}).get('figur') or {}).get('regler')
            if isinstance(regler, dict):
                return {'figur': cls._figur(geschlecht, regler), 'form': 'ki',
                        'quelle': 'Form: vom Formnetz %s vorhergesagt (%d Regler, Test %s). %s' % (e.get('formkopf') or '?', len(regler), e.get('test') or '?', cls.TEXT_VORGABEN)}
            logger.warning('Meshgenesisergebnisfigur: %s ohne Regler — Ergebnis mit der Grundfigur', e['modell'])
        # 2. Vorhersage des Formnetzes für diese Probe.
        try:
            info = Meshgenesisformvariante.lesen(job['ordner'])
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Meshgenesisergebnisfigur: Formlauf für %s nicht lesbar (%s)', job.get('ordner'), fehler)
            info = None
        if info and info.get('lauf') and info.get('proben'):
            lauf = Meshgenesisformtraining.ordner() / info['lauf']['name']
            liste = Meshgenesisformvariante.liste(lauf)
            if liste:
                with Npztorch.lesen(lauf / Meshgenesisformvariante.VORHERSAGEN) as z:
                    vektor = Meshgenesisformvariantefigur.vektor(z, job['ordner'], str(int(nr)), info['proben'])
                if vektor is not None and len(vektor) == len(liste):
                    regler = Meshgenesisformvariantefigur.regler(vektor, liste)
                    lauf_e = cls._json(lauf / 'lauf_ergebnis.json') or {}
                    trainiert = job['ordner'] in (lauf_e.get('training_daten') or []) or job['ordner'] in (lauf_e.get('paare') or [])
                    probe = next((p for p in info['proben'] if int(p['nr']) == int(nr)), {})
                    return {'figur': cls._figur(geschlecht, regler), 'form': 'ki',
                            'quelle': 'Form: vom Formnetz %s für diese Probe vorhergesagt (%d Regler; %s, Probe %s).%s %s' % (
                                info['lauf']['name'], len(regler), job.get('name'), 'Training' if probe.get('gruppe') == 'training' else 'Prüfpose',
                                ' %s ist Trainingsfigur dieses Formnetzes — die Form ist dort gelernt, nicht neu erkannt.' % job.get('name') if trainiert else '', cls.TEXT_VORGABEN)}
        # 3. Keine Vorhersage: Grundfigur.
        return {'figur': cls._figur(geschlecht, {}), 'form': 'grundfigur',
                'quelle': 'Form: KEINE Vorhersage für diese Probe — gezeigt ist die Grundfigur des Geschlechts (nicht die Figur des Jobs). %s' % cls.TEXT_VORGABEN}

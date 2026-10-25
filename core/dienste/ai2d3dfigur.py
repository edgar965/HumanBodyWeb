# -*- coding: utf-8 -*-
"""Ai2d3dfigur — die Genesis-Figur eines 2d-3d-AI-Jobs aus dem eigenen Ordner `<Job>/figur/` (25.10.2026; Edgar: „Warum mischst du diese ganzen Jobs? das ist doch eine andere
Pipeline??“ — „die 2d-3d-ai pipeline sollte erweitert werden mit Know how aus der mesh3d-ai“).

Bis dahin lag die Figur aus den Fotos von EdgarTrip als Mesh3D-AI-Test `_test/edgar_foto`, und die Jobseite holte sie über `/api/mesh3dai/test/edgar_foto/`. So stand sie in der
Mesh3D-AI-Liste, und Edgar löschte sie dort zweimal (10:44, 16:02). Jetzt hat sie einen eigenen Ordner und eigene Adressen `/api/2d3dai/<job>/figur/…`. Ausgeliefert wird mit dem Code von
Mesh3D-AI (Rig `Mesh3dairig`, Anzeigenetz `Mesh3daiflaechennetz`, KI-Stücke `Mesh3daitestkikleider`, Wahl `Mesh3daitestkleider.wirksam`) in derselben Form wie die Testschnittstelle,
damit `Ai2d3dtestfigur` im Browser unverändert baut.

Ablage (schreibt `ProjektTemp/_wegwerf/ai2d3d/nurfotos_koerper.py`): `form_<g>/` (modell.json, kinematik.json, anzeige/), `ergebnis_Form_<g>.npz` (rig, dreh; je Foto rig_<n>, dreh_<n>),
`haut_<g>/` (Kacheln, anzeige.json), `kleider_<g>/ki.json` mit `k/<id>/anzeige/`.

    Ai2d3dfigur.adresse(job)            # '/api/2d3dai/<id>/figur/' oder None (job: Eintrag aus `Ai2d3djobs`)
    Ai2d3dfigur.daten(kennung)          # Rig, Drehungen, Ruhezentren, Adresse des Anzeigenetzes — wie `Mesh3daitest.daten`
"""
import json
import logging
import re
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

__all__ = ['Ai2d3dfigur']


class Ai2d3dfigur:
    ORDNER = 'figur'
    GESCHLECHTER = ('maennlich', 'weiblich')
    ID = re.compile(r'^[a-z0-9_]{1,64}$')
    HAUTBILD = re.compile(r'^m\d{1,4}\.jpg$')
    KACHEL = re.compile(r'^10\d\d\.jpg$')

    @classmethod
    def ordner_von(cls, job):
        p = Path(job['ordner']) / cls.ORDNER if job and job.get('art') == 'foto' and job.get('ordner') else None
        return p if p is not None and p.is_dir() and not p.is_junction() else None

    @classmethod
    def ordner(cls, kennung):
        from .ai2d3djobs import Ai2d3djobs
        return cls.ordner_von(Ai2d3djobs.job(kennung))

    @classmethod
    def adresse(cls, job):
        return '/api/2d3dai/%s/figur/' % job['id'] if cls.ordner_von(job) and cls.geschlecht(cls.ordner_von(job)) else None

    @classmethod
    def geschlecht(cls, p):
        """Das Geschlecht der gebauten Figur (erstes `form_<g>` mit Anzeigenetz) oder None."""
        return next((g for g in cls.GESCHLECHTER if (p / ('form_%s' % g) / 'anzeige' / 'netz.npz').is_file()), None)

    @classmethod
    def _form(cls, kennung, geschlecht):
        """Ordner der Figur als Text für `Mesh3daiflaechennetz` (absolut — `Mesh3daidatensatz.ordner` hängt ihn an `mesh3dai/`, ein absoluter Pfad bleibt er selbst) oder None."""
        p = cls.ordner(kennung)
        if p is None or geschlecht not in cls.GESCHLECHTER or not (p / ('form_%s' % geschlecht) / 'anzeige' / 'netz.npz').is_file():
            return None
        return str(p / ('form_%s' % geschlecht))

    @classmethod
    def daten(cls, kennung):
        from .mesh3daidaten import Mesh3daidaten
        from .mesh3dairig import Mesh3dairig
        p = cls.ordner(kennung)
        g = cls.geschlecht(p) if p else None
        if g is None or not (p / ('ergebnis_Form_%s.npz' % g)).is_file():
            return None
        fig = p / ('form_%s' % g)
        kin = json.loads((fig / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
        beschr = Mesh3dairig.beschreibung()
        if [k['name'] for k in kin] != [k['name'] for k in beschr['knochen']]:
            logger.warning('Ai2d3dfigur: kinematik.json von %s passt nicht zum Rig', fig)
            return None
        modell = json.loads((fig / 'modell.json').read_text(encoding='utf-8'))
        with np.load(p / ('ergebnis_Form_%s.npz' % g)) as e:
            ausgabe, dreh = e['rig'].astype(float), e['dreh'].astype(float)
        name = (modell.get('kopfbild') or {}).get('quelle') or 'nur Fotos'
        return {'kennung': kennung, 'info': {'name': name, 'geschlecht': g, 'gerechnet': (modell.get('kopfbild') or {}).get('gerechnet')}, 'job': None, 'rig': beschr,
                'figur_netz': '/api/2d3dai/%s/figur/%s' % (kennung, g), 'form_regler': modell['figur']['regler'],
                'ausgabe': np.round(ausgabe, 4).tolist(), 'dreh': np.round(Mesh3daidaten._quaternionen(dreh), 5).tolist(),
                'ruhezentren': np.round(np.array([k['zentrum'] for k in kin]), 6).tolist()}

    @classmethod
    def figurnetz(cls, kennung, geschlecht):
        from .mesh3daiflaechennetz import Mesh3daiflaechennetz
        form = cls._form(kennung, geschlecht)
        return Mesh3daiflaechennetz.paket(form) if form else None

    @classmethod
    def figurbild(cls, kennung, geschlecht, name):
        """Die Kachel der Haut-KI, die auf diesem Bild der Figur liegt (`haut_<g>/anzeige.json`, wie `Mesh3daitesthaut`), sonst das Bild der Grundhaut."""
        from .mesh3daiflaechennetz import Mesh3daiflaechennetz
        form = cls._form(kennung, geschlecht)
        if form is None:
            return None
        haut = Path(form).parent / ('haut_%s' % geschlecht)
        if cls.HAUTBILD.match(str(name)):
            try:
                ziel = json.loads((haut / 'anzeige.json').read_text(encoding='utf-8')).get('bilder', {}).get(str(name))
            except (OSError, ValueError):
                ziel = None
            if ziel and cls.KACHEL.match(str(ziel)) and (haut / ziel).is_file():
                return haut / ziel
        return Mesh3daiflaechennetz.bild(form, name)

    @classmethod
    def kleider(cls, kennung, geschlecht):
        """Die Stücke aus den Fotos (`kleider_<g>/ki.json`), wirksam nach der Vorgabe „ki“ — dieselbe Liste wie `Mesh3daitestkleider.liste`, ohne Wahl des Nutzers."""
        from .mesh3daitestkikleider import Mesh3daitestkikleider
        from .mesh3daitestkleider import Mesh3daitestkleider
        p = cls.ordner(kennung)
        if p is None or geschlecht not in cls.GESCHLECHTER:
            return None
        zeilen, info = Mesh3daitestkikleider.zeilen(p / ('kleider_%s' % geschlecht), kennung, geschlecht, adresse='/api/2d3dai/%s/figur/kleid/%s/{weg}/{id}' % (kennung, geschlecht))
        for z in zeilen:
            z['eigene_wahl'] = None
            z['wahl'] = Mesh3daitestkleider.wirksam(z, None, 'ki')
        return {'vorgabe': 'ki', 'stuecke': zeilen, 'quelle': None, 'grund': None if zeilen else 'Keine Stücke in %s' % (p / ('kleider_%s' % geschlecht)), 'ki': info,
                'wege_texte': Mesh3daitestkikleider.TEXTE}

    @classmethod
    def stueck(cls, kennung, geschlecht, weg, stueck):
        """Ordner eines Stücks als Text für `Mesh3daiflaechennetz` oder None — alle Teile kommen aus der Adresse und werden geprüft."""
        from .mesh3daitestkikleider import Mesh3daitestkikleider
        p = cls.ordner(kennung)
        if p is None or geschlecht not in cls.GESCHLECHTER or weg not in Mesh3daitestkikleider.WEGE or not cls.ID.match(str(stueck)):
            return None
        o = p / ('kleider_%s' % geschlecht) / weg / stueck
        return str(o) if (o / 'anzeige' / 'netz.npz').is_file() else None

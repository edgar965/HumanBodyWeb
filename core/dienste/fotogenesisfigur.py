# -*- coding: utf-8 -*-
"""Fotogenesisfigur — die Genesis-Figur eines Foto-Genesis-Jobs aus dem eigenen Ordner `<Job>/figur/` (25.10.2026; Edgar: „Warum mischst du diese ganzen Jobs? das ist doch eine andere
Pipeline??“ — „die 2d-3d-ai pipeline sollte erweitert werden mit Know how aus der mesh3d-ai“).

Bis dahin lag die Figur aus den Fotos von EdgarTrip als Mesh-Genesis-Test `_test/edgar_foto`, und die Jobseite holte sie über `/api/meshgenesis/test/edgar_foto/`. So stand sie in der
Mesh-Genesis-Liste, und Edgar löschte sie dort zweimal (10:44, 16:02). Jetzt hat sie einen eigenen Ordner und eigene Adressen `/api/fotogenesis/<job>/figur/…`. Ausgeliefert wird mit dem Code von
Mesh-Genesis (Rig `Meshgenesisrig`, Anzeigenetz `Meshgenesisflaechennetz`, KI-Stücke `Meshgenesistestkikleider`, Wahl `Meshgenesistestkleider.wirksam`) in derselben Form wie die Testschnittstelle,
damit `Fotogenesistestfigur` im Browser unverändert baut.

Ablage (schreibt `ProjektTemp/_wegwerf/fotogenesis/nurfotos_koerper.py`): `form_<g>/` (modell.json, kinematik.json, anzeige/), `ergebnis_Form_<g>.npz` (rig, dreh; je Foto rig_<n>, dreh_<n>),
`haut_<g>/` (Kacheln, anzeige.json), `kleider_<g>/ki.json` mit `k/<id>/anzeige/`.

    Fotogenesisfigur.adresse(job)            # '/api/fotogenesis/<id>/figur/' oder None (job: Eintrag aus `Fotogenesisjobs`)
    Fotogenesisfigur.daten(kennung)          # Rig, Drehungen, Ruhezentren, Adresse des Anzeigenetzes — wie `Meshgenesistest.daten`
"""
import base64
import json
import logging
import re
from pathlib import Path

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch

logger = logging.getLogger(__name__)

__all__ = ['Fotogenesisfigur']


class Fotogenesisfigur:
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
        from .fotogenesisjobs import Fotogenesisjobs
        return cls.ordner_von(Fotogenesisjobs.job(kennung))

    @classmethod
    def adresse(cls, job):
        return '/api/fotogenesis/%s/figur/' % job['id'] if cls.ordner_von(job) and cls.geschlecht(cls.ordner_von(job)) else None

    @classmethod
    def geschlecht(cls, p):
        """Das Geschlecht der gebauten Figur (erstes `form_<g>` mit Anzeigenetz) oder None."""
        return next((g for g in cls.GESCHLECHTER if Npztorch.da(p / ('form_%s' % g) / 'anzeige' / 'netz.npz')), None)

    @classmethod
    def _form(cls, kennung, geschlecht):
        """Ordner der Figur als Text für `Meshgenesisflaechennetz` (absolut — `Meshgenesisdatensatz.ordner` hängt ihn an `meshgenesis/`, ein absoluter Pfad bleibt er selbst) oder None."""
        p = cls.ordner(kennung)
        if p is None or geschlecht not in cls.GESCHLECHTER or not Npztorch.da(p / ('form_%s' % geschlecht) / 'anzeige' / 'netz.npz'):
            return None
        return str(p / ('form_%s' % geschlecht))

    @classmethod
    def daten(cls, kennung):
        from .meshgenesisdaten import Meshgenesisdaten
        from .meshgenesisrig import Meshgenesisrig
        p = cls.ordner(kennung)
        g = cls.geschlecht(p) if p else None
        if g is None or not Npztorch.da(p / ('ergebnis_Form_%s.npz' % g)):
            return None
        fig = p / ('form_%s' % g)
        kin = json.loads((fig / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
        beschr = Meshgenesisrig.beschreibung()
        if [k['name'] for k in kin] != [k['name'] for k in beschr['knochen']]:
            logger.warning('Fotogenesisfigur: kinematik.json von %s passt nicht zum Rig', fig)
            return None
        modell = json.loads((fig / 'modell.json').read_text(encoding='utf-8'))
        with Npztorch.lesen(p / ('ergebnis_Form_%s.npz' % g)) as e:
            ausgabe, dreh = Torchfeld.astype(e['rig'], torch.float64), Torchfeld.astype(e['dreh'], torch.float64)
            # Form der Zeile 1 in der Ruhelage (`KoerperKI_Fotos.Zeile1versatz`, 31.10.2026 nachts) — die Abspielleiste der Zeile 1 legt sie auf die bewegte Figur (`Fotogenesiszeile1form`)
            zeile1 = {k: base64.b64encode(Torchfeld.als_bytes(Torchfeld.astype(e['zeile1_' + k], Torchfeld.dtype('<f4')))).decode('ascii') for k in ('ruhe', 'versatz')} if 'zeile1_versatz' in e.files else None
        name = (modell.get('kopfbild') or {}).get('quelle') or 'nur Fotos'
        from .meshgenesisergebnisfigur import Meshgenesisergebnisfigur
        # Die Figur als Genesis9Modell (31.10.2026, Exportleiste): dieselbe Angabe wie `Meshgenesistest.daten`, dazu die Kacheln der Haut aus den Fotos als `fototextur`
        figur = dict(Meshgenesisergebnisfigur._figur(g, modell['figur']['regler']), fototextur=cls._kacheln(kennung, p, g))
        return {'kennung': kennung, 'info': {'name': name, 'geschlecht': g, 'gerechnet': (modell.get('kopfbild') or {}).get('gerechnet')}, 'job': None, 'rig': beschr,
                'figur_netz': '/api/fotogenesis/%s/figur/%s' % (kennung, g), 'form_regler': modell['figur']['regler'], 'figur_genesis': figur,
                'ausgabe': Torchfeld.round(ausgabe, 4).tolist(), 'dreh': Torchfeld.round(Meshgenesisdaten._quaternionen(dreh), 5).tolist(),
                'ruhezentren': Torchfeld.round(Torchfeld.feld([k['zentrum'] for k in kin], copy=True), 6).tolist(), 'zeile1_ursprung': cls._ursprung(p.parent), 'zeile1_form': zeile1}

    @staticmethod
    def _ursprung(jobordner):
        """Käfigpunkt je Punkt des Anzeigenetzes (`G9basisnetz.netzstufe(0).ursprung`, base64 int32), wenn Zeile 1 eine Genesis-Figur auf demselben Käfig hat (`abnahme/training_figur.json`,
        Block `genesis`) — sonst None. Damit legt die Seite den Körper der Zeile 2 auf die Genesis-Figur der Zeile 1 (`Fotogenesiszeile1`; 31.10.2026, Edgar: „Zeile 2, die Vorlage von der
        ersten Zeile nehmen beim Körper und Genesis-Modell … die Arme völlig kaputt“)."""
        import base64
        try:
            with open(Path(jobordner) / 'abnahme' / 'training_figur.json', encoding='utf-8') as f:
                tf = json.load(f)
        except (OSError, ValueError):
            return None
        if not (tf.get('genesis') or {}).get('fotos'):
            return None
        from Genesis9.basisnetz import G9basisnetz
        ursprung = Torchfeld.feld(G9basisnetz.netzstufe(0).ursprung, dtype=torch.int32)
        if int(ursprung.max()) + 1 != int(tf.get('n_punkte') or -1):
            logger.warning('Fotogenesisfigur: Zeile 1 hat %s Punkte, der Käfig %d — keine Vorlage', tf.get('n_punkte'), int(ursprung.max()) + 1)
            return None
        return base64.b64encode(Torchfeld.als_bytes(ursprung)).decode('ascii')

    @classmethod
    def _kacheln(cls, kennung, p, g):
        """`{1001: Adresse, …}` der Kacheln in `haut_<g>/` (Genesis-UDIM, `Genesis9fototextur`); der Zeitstempel in der Adresse hält den Browser-Speicher frisch."""
        haut = p / ('haut_%s' % g)
        return {d.stem: '/api/fotogenesis/%s/figur/%s/bild/%s?t=%d' % (kennung, g, d.name, int(d.stat().st_mtime)) for d in sorted(haut.glob('10??.jpg')) if cls.KACHEL.match(d.name)}

    @classmethod
    def figurnetz(cls, kennung, geschlecht):
        from .meshgenesisflaechennetz import Meshgenesisflaechennetz
        form = cls._form(kennung, geschlecht)
        return Meshgenesisflaechennetz.paket(form) if form else None

    @classmethod
    def figurbild(cls, kennung, geschlecht, name):
        """Die Kachel der Haut-KI, die auf diesem Bild der Figur liegt (`haut_<g>/anzeige.json`, wie `Meshgenesistesthaut`), sonst das Bild der Grundhaut."""
        from .meshgenesisflaechennetz import Meshgenesisflaechennetz
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
        if cls.KACHEL.match(str(name)) and (haut / name).is_file():          # die Kachel selbst (`fototextur` der Genesis-Figur, `_kacheln`)
            return haut / name
        return Meshgenesisflaechennetz.bild(form, name)

    @classmethod
    def kleider(cls, kennung, geschlecht):
        """Die Stücke aus den Fotos (`kleider_<g>/ki.json`), wirksam nach der Vorgabe „ki“ — dieselbe Liste wie `Meshgenesistestkleider.liste`, ohne Wahl des Nutzers."""
        from .meshgenesistestkikleider import Meshgenesistestkikleider
        from .meshgenesistestkleider import Meshgenesistestkleider
        p = cls.ordner(kennung)
        if p is None or geschlecht not in cls.GESCHLECHTER:
            return None
        zeilen, info = Meshgenesistestkikleider.zeilen(p / ('kleider_%s' % geschlecht), kennung, geschlecht, adresse='/api/fotogenesis/%s/figur/kleid/%s/{weg}/{id}' % (kennung, geschlecht))
        for z in zeilen:
            z['eigene_wahl'] = None
            z['wahl'] = Meshgenesistestkleider.wirksam(z, None, 'ki')
        return {'vorgabe': 'ki', 'stuecke': zeilen, 'quelle': None, 'grund': None if zeilen else 'Keine Stücke in %s' % (p / ('kleider_%s' % geschlecht)), 'ki': info,
                'wege_texte': Meshgenesistestkikleider.TEXTE}

    @classmethod
    def stueck(cls, kennung, geschlecht, weg, stueck):
        """Ordner eines Stücks als Text für `Meshgenesisflaechennetz` oder None — alle Teile kommen aus der Adresse und werden geprüft."""
        from .meshgenesistestkikleider import Meshgenesistestkikleider
        p = cls.ordner(kennung)
        if p is None or geschlecht not in cls.GESCHLECHTER or weg not in Meshgenesistestkikleider.WEGE or not cls.ID.match(str(stueck)):
            return None
        o = p / ('kleider_%s' % geschlecht) / weg / stueck
        return str(o) if Npztorch.da(o / 'anzeige' / 'netz.npz') else None

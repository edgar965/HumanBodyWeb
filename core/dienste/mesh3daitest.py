# -*- coding: utf-8 -*-
"""Mesh3daitest — Reiter „Test“ von Mesh3D-AI: das Netz von Mesh3D-AI auf Netzen OHNE Trainingsdaten (16.10.2026).

Edgar: „mach auf /mesh-3D-AI/ einen zweiten Tab: Test, darin auch eine Jobliste, aber nur Mesh und Ausgabe. Darin möchte ich testen, wie das bei Meshes ausschaut, wo wir keine Trainingsdaten haben …
diese gleichen alten Jobs [Edgar, Zauberer, …] brauche ich im neuen Tab, aber mit dem neuen KI-Modell“.
Ein Test ist ein Ordner `3DObjects/mesh3dai/_test/<kennung>/` (gerechnet von `ProjektTemp/_wegwerf/mesh3dai_test_rechnen.py`, python10): `test.json` (Name, Quelle, Lauf, Maßstab, Rest je Figur),
`ergebnis_<Figur>.npz` je trainierter Figur (138 Gelenke, Drehung je Knochen gegen die Ruhelage, Daz-Winkel), `vorschau.glb` (das Netz im Rahmen des Datensatzes, auf `vorschau_hoehe_m`).
Ein Ziel gibt es nicht — darum nur Mesh und Ausgabe, und keine Fehlerzahl.

Geschlecht (16.10.2026 abends, Edgar: „ganz oben im Testjob soll die Einstellung änderbar sein, ob es weiblich oder männlich ist … Königin ist weiblich, Zauberer männlich usw“):
`einstellung.json` im Testordner (`{"geschlecht": "weiblich" | "maennlich"}`), ohne Datei gilt `geschlecht_vorgabe` aus `test.json` (die Grundfigur des gleichnamigen Mesh-3D-Auftrags).
Die Ausgabe nimmt unter den Figuren dieses Geschlechts (`Mesh3daiattrappe.STAMMDATEN`, Feld `geschlecht`) die mit dem kleinsten Rest der Anpassung. Das Umschalten rechnet nichts —
die Ergebnisse aller Figuren liegen schon da; die Vorschau wird auf die Höhe der Figur skaliert (`netz_skala`: der Rahmen ist eine reine Streckung um den Fußpunkt der Mitte).
Tests aus der Zeit davor tragen nur ein Ergebnis (`ergebnis.npz`, Figur `figur`); dann sagt `figur_hinweis`, dass für das andere Geschlecht neu gerechnet werden muss.

Vorhergesagte Form (16.10.2026 abends, Edgar: „das netz soll auch: die Form vorhersagt: die Genesis-Formregler (815) usw.“): rechnet ein Netz mit Formkopf den Test
(`ProjektTemp/_wegwerf/mesh3dai_test_form.py`, `mesh3dai_formfigur.py`), liegt je Geschlecht eine eigene Figur unter `form_<geschlecht>/` (Anzeigenetz, Skelett, `modell.json` mit den Reglern)
und `ergebnis_Form_<geschlecht>.npz`. Dann ist die Ausgabe diese Figur (`figur` = „Form“) statt einer Wahl unter den trainierten; das Anzeigenetz kommt über `/api/mesh3dai/test/<kennung>/figur/<geschlecht>/…`.
"""

import json
import logging
import re
from pathlib import Path

import numpy as np
from django.conf import settings

from ..atomic_write import AtomarSchreiber
from .mesh3daidaten import Mesh3daidaten
from .mesh3dairig import Mesh3dairig

logger = logging.getLogger(__name__)

__all__ = ['Mesh3daitest']


class Mesh3daitest:
    #: Die Figur der Ausgabe, wenn `test.json` keine nennt (Tests vor dem 16.10.2026 abends, gerechnet mit dem Netz von Ursula1 allein).
    MODELL = 'Ursula1'
    KENNUNG = re.compile(r'^[a-z0-9_]{1,64}$')
    GESCHLECHTER = {'weiblich': 'weiblich', 'maennlich': 'männlich'}

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_test'

    @classmethod
    def pfad(cls, kennung):
        """Ordner eines Tests oder `None` (unbekannt oder unzulässige Kennung — sie kommt aus der Adresse)."""
        if not cls.KENNUNG.match(str(kennung)):
            return None
        p = cls.ordner() / kennung
        return p if (p / 'test.json').is_file() else None

    @staticmethod
    def _stammdaten():
        from .mesh3daiattrappe import Mesh3daiattrappe
        return Mesh3daiattrappe.stammdaten()

    @classmethod
    def job_der_figur(cls, ordner):
        """Kennung des Jobs, dessen Datensatz `ordner` heißt (für das Anzeigenetz `/api/mesh3dai/<job>/…`)."""
        return next((j['id'] for j in cls._stammdaten() if j.get('ordner', j['name']) == ordner), None)

    @classmethod
    def geschlecht_der_figur(cls, ordner):
        return next((j.get('geschlecht') for j in cls._stammdaten() if j.get('ordner', j['name']) == ordner), None)

    @classmethod
    def geschlecht(cls, p, info):
        """Eingestelltes Geschlecht des Tests: `einstellung.json`, sonst die Vorgabe aus `test.json`, sonst das der gerechneten Figur."""
        try:
            wert = json.loads((p / 'einstellung.json').read_text(encoding='utf-8')).get('geschlecht')
        except (OSError, ValueError):
            wert = None
        if wert not in cls.GESCHLECHTER:
            wert = info.get('geschlecht_vorgabe') or cls.geschlecht_der_figur(info.get('figur') or cls.MODELL) or 'weiblich'
        return wert

    @classmethod
    def figuren(cls, p, info):
        """{Figur: Rest der Anpassung in mm} der Figuren, deren Ergebnis im Ordner liegt — neue Ablage `ergebnis_<Figur>.npz`, alte nur `ergebnis.npz` für `figur`."""
        aus = {}
        for name, wert in (info.get('figuren') or {}).items():
            if (p / ('ergebnis_%s.npz' % name)).is_file():
                aus[name] = wert['rest_mm'] if isinstance(wert, dict) else float(wert)
        if not aus and (p / 'ergebnis.npz').is_file():
            aus[info.get('figur') or cls.MODELL] = info.get('ik_rest_mm')
        return aus

    @classmethod
    def wahl(cls, p, info, geschlecht):
        """(Figur, Hinweis): unter den gerechneten Figuren des Geschlechts die mit dem kleinsten Rest; gibt es keine, die gerechnete mit einem Hinweis."""
        da = cls.figuren(p, info)
        passend = {n: r for n, r in da.items() if cls.geschlecht_der_figur(n) == geschlecht}
        if passend:
            return min(passend, key=lambda n: passend[n] if passend[n] is not None else 1e9), ''
        figur = next(iter(da), None)
        return figur, ('Für „%s“ ist keine Figur gerechnet (dieser Test kennt nur %s) — der Test muss neu gerechnet werden.' % (cls.GESCHLECHTER[geschlecht], ', '.join(da) or 'keine')) if figur else ''

    @classmethod
    def form(cls, p, info, geschlecht):
        """Die vorhergesagte Figur dieses Geschlechts, wenn gebaut und angepasst — `{ordner (relativ zu mesh3dai/), datei, kinematik, rest_mm, hoehe_m, regler}` — sonst `None`."""
        f = (info.get('form') or {}).get(geschlecht)
        fig = p / ('form_%s' % geschlecht)
        datei = p / ('ergebnis_Form_%s.npz' % geschlecht)
        if not isinstance(f, dict) or not datei.is_file() or not (fig / 'kinematik.json').is_file() or not (fig / 'anzeige' / 'netz.npz').is_file():
            return None
        try:
            regler = json.loads((fig / 'modell.json').read_text(encoding='utf-8'))['figur']['regler']
        except (OSError, ValueError, KeyError):
            regler = {}
        # Zahl der Formregler, die das Netz vorhersagt (Fassung des Laufs: 815, 911, 1.318 …) — die Seite schrieb bis 17.10.2026 fest „von 815“.
        try:
            with np.load(p / 'form.npz') as z:
                gesamt = int(z['regler'].shape[0])
        except (OSError, ValueError, KeyError):
            gesamt = None
        return {'ordner': '_test/%s/form_%s' % (p.name, geschlecht), 'datei': datei, 'kinematik': fig / 'kinematik.json', 'rest_mm': f.get('rest_mm'), 'hoehe_m': f.get('hoehe_m'), 'regler': regler,
                'regler_gesamt': gesamt}

    @classmethod
    def form_ordner(cls, kennung, geschlecht):
        """Ordner der vorhergesagten Figur relativ zu `mesh3dai/` (für `Mesh3daiflaechennetz`) oder `None`."""
        p = cls.pfad(kennung)
        if p is None or geschlecht not in cls.GESCHLECHTER or not (p / ('form_%s' % geschlecht) / 'anzeige' / 'netz.npz').is_file():
            return None
        return '_test/%s/form_%s' % (kennung, geschlecht)

    @classmethod
    def alle(cls):
        """Die Tests mit ihrem Stand (`test.json`), nach Name; ein unlesbarer steht mit Fehler in der Liste statt zu fehlen. `figur`/`geschlecht` sind die eingestellten."""
        if not cls.ordner().is_dir():
            return []
        aus = []
        for p in sorted(cls.ordner().iterdir()):
            if not (p / 'test.json').is_file():
                continue
            try:
                info = json.loads((p / 'test.json').read_text(encoding='utf-8'))
                info['geschlecht'] = cls.geschlecht(p, info)
                info['figur'] = 'Form (vorhergesagt)' if cls.form(p, info, info['geschlecht']) else cls.wahl(p, info, info['geschlecht'])[0]
            except (OSError, ValueError) as fehler:
                info = {'kennung': p.name, 'name': p.name, 'fehler': str(fehler)}
            info['fertig'] = bool(info.get('figur')) and (p / 'vorschau.glb').is_file()
            aus.append(info)
        return sorted(aus, key=lambda i: str(i.get('name', '')).lower())

    @classmethod
    def daten(cls, kennung):
        """Was die Testseite braucht: Rig (Beschreibung, 138 Gelenke, Drehungen als Quaternionen), Ruhezentren für die Häutung, Figur und Geschlecht. `None`, wenn der Test fehlt oder nicht fertig ist."""
        p = cls.pfad(kennung)
        if p is None:
            return None
        info = json.loads((p / 'test.json').read_text(encoding='utf-8'))
        geschlecht = cls.geschlecht(p, info)
        form = cls.form(p, info, geschlecht)
        if form:
            figur, hinweis, job, datei, kin_datei = 'Form', '', None, form['datei'], form['kinematik']
        else:
            figur, hinweis = cls.wahl(p, info, geschlecht)
            if figur is None:
                return None
            datei = p / ('ergebnis_%s.npz' % figur)
            if not datei.is_file():
                datei = p / 'ergebnis.npz'
            job = cls.job_der_figur(figur)
            if job is None:
                logger.warning('Mesh3daitest: Test %s nennt die Figur %s, es gibt keinen Job mit diesem Datensatz', kennung, figur)
                return None
            kin_datei = Path(settings.OBJECTS_ROOT) / 'mesh3dai' / figur / 'kinematik.json'
        e = np.load(datei)
        kin = json.loads(kin_datei.read_text(encoding='utf-8'))['knochen']
        beschr = Mesh3dairig.beschreibung()
        if [k['name'] for k in kin] != [k['name'] for k in beschr['knochen']]:
            logger.warning('Mesh3daitest: kinematik.json von %s passt nicht zum Rig', figur)
            return None
        f = form if form else (info.get('figuren') or {}).get(figur)
        hoehe = f['hoehe_m'] if isinstance(f, dict) else info.get('hoehe_m')
        skala = hoehe / info['vorschau_hoehe_m'] if hoehe and info.get('vorschau_hoehe_m') else 1.0
        rest = form['rest_mm'] if form else cls.figuren(p, info).get(figur, info.get('ik_rest_mm'))
        info.update({'figur': figur, 'geschlecht': geschlecht, 'hoehe_m': hoehe, 'ik_rest_mm': rest})
        return {
            'kennung': kennung, 'info': info, 'job': job, 'rig': beschr, 'figur_hinweis': hinweis, 'geschlechter': cls.GESCHLECHTER, 'netz_skala': round(float(skala), 6),
            'figur_netz': '/api/mesh3dai/test/%s/figur/%s' % (kennung, geschlecht) if form else None, 'form_regler': form['regler'] if form else None,
            'form_regler_gesamt': form.get('regler_gesamt') if form else None,
            'ausgabe': np.round(e['rig'].astype(float), 4).tolist(),
            'dreh': np.round(Mesh3daidaten._quaternionen(e['dreh'].astype(float)), 5).tolist(),
            'ruhezentren': np.round(np.array([k['zentrum'] for k in kin]), 6).tolist(),
            'netz': '/api/mesh3dai/test/%s/netz/?v=%d' % (kennung, int((p / 'vorschau.glb').stat().st_mtime)),
        }

    @classmethod
    def geschlecht_setzen(cls, kennung, wert):
        """Stellt das Geschlecht eines Tests ein (`einstellung.json`); `False`, wenn der Test fehlt oder der Wert keiner der beiden ist."""
        p = cls.pfad(kennung)
        if p is None or wert not in cls.GESCHLECHTER:
            return False
        # Die Datei trägt seit 17.10.2026 nachts auch die Kleiderwahl (`Mesh3daitestkleider`): lesen, ergänzen, schreiben — nicht ersetzen.
        try:
            alt = json.loads((p / 'einstellung.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            alt = {}
        AtomarSchreiber.json_schreiben(p / 'einstellung.json', {**(alt if isinstance(alt, dict) else {}), 'geschlecht': wert})
        return True

    @classmethod
    def vorschau(cls, kennung):
        p = cls.pfad(kennung)
        return p / 'vorschau.glb' if p is not None and (p / 'vorschau.glb').is_file() else None

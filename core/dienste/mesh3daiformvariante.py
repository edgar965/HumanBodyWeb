# -*- coding: utf-8 -*-
"""Mesh3daiformvariante — eine Formvariante (oder ein Job) als Seite mit Start · Ziel · Ergebnis des Formkopfs (18.10.2026 abends).

Edgar: „mach das: Formvariante als Jobseite“. Alles von der Platte, nichts gerechnet außer den Figuren (`Mesh3daiformvariantefigur`, G9formung, rund 0,1 s je Figur):

  * Lauf: ein Formlauf unter `_vorstufe/laeufe/` (`Mesh3daiformtraining.ordner()`), dessen `formen_vorhersagen.npz` die Figur trägt (`<Figur>_soll_form`). Vorgabe der jüngste fertige ohne Probelauf.
  * Start: die A-Pose-Wolke, die der Lauf gelesen hat (`lauf_ergebnis.json` → `eingang`, z. B. `apose_v9`; Wolken `wolken` „0,1,2“, ohne Angabe nur 0) — je Probe `proben/NNNN/<eingang>_<k>.npz`.
  * Ziel: die Figur aus den Soll-Reglern des Laufs (`<Figur>_soll_form` — nur Regler, die der Lauf kennt; die übrigen stehen in `fremde_regler`).
  * Ergebnis: die Figur aus den vorhergesagten Reglern EINER Probe (Zeile von `<Figur>_<gruppe>_form`) oder ihr Mittel über alle Proben (so misst `formen_pruefung_echt.json`).

Zeilen ↔ Proben: die Trainingsskripte legen je Gruppe eine Zeile je Probe in der Reihenfolge von `proben.json` ab (`mesh3dai_vorstufe_form.py`, `mesh3dai_formdaten2.py`) und lassen eine Probe nur aus,
wenn keine ihrer Wolken taugt (`ausgelassen` → „<Figur>/<nr>/k<k>“). Stimmt die nachgebaute Zuordnung nicht mit der Zahl der Zeilen überein, gibt es KEINE Zuordnung (nur das Mittel) — nie eine verschobene.

    Mesh3daiformvariante.finden(name)        -> Ordner unter 3DObjects/mesh3dai oder None (nur ein direkter Unterordner)
    Mesh3daiformvariante.laeufe(name)        -> [{name, kurz, zeit}] der Läufe, die die Figur tragen, der jüngste zuerst
    Mesh3daiformvariante.lesen(name, lauf)   -> {figur, modell, lauf, laeufe, proben, werte, echt, regler, fremde, hinweis} | None
"""

import json
import logging
import re
import zipfile

import numpy as np

from .mesh3daidatensatz import Mesh3daidatensatz
from .mesh3daiformlaufnamen import Mesh3daiformlaufnamen as N
from .mesh3daiformtraining import Mesh3daiformtraining

logger = logging.getLogger('core')

__all__ = ['Mesh3daiformvariante']


class Mesh3daiformvariante:
    NAME = re.compile(r'^[0-9A-Za-z][0-9A-Za-z_-]*$')
    VORHERSAGEN = 'formen_vorhersagen.npz'
    LISTE = 'formregler_liste.json'
    GRUPPEN = ('training', 'pruefung')
    #: Regler-Tabelle: so viele Zeilen, nach dem Betrag der Abweichung Soll ↔ Vorhersage (Mittel).
    REGLER_ZEILEN = 25
    _schluessel = {}

    @classmethod
    def finden(cls, name):
        if not name or not cls.NAME.match(str(name)):
            return None
        wurzel = Mesh3daidatensatz.ordner('')
        pfad = wurzel / str(name)
        return pfad if pfad.parent == wurzel and pfad.is_dir() else None

    @classmethod
    def _dateien(cls, lauf):
        """Die Schlüssel der Vorhersagedatei (nur das Verzeichnis des Zip-Archivs), gemerkt je Änderungszeit."""
        datei = lauf / cls.VORHERSAGEN
        try:
            stand = datei.stat().st_mtime_ns
        except OSError:
            return set()
        gemerkt = cls._schluessel.get(str(datei))
        if gemerkt and gemerkt[0] == stand:
            return gemerkt[1]
        try:
            with np.load(datei) as z:
                namen = set(z.files)
        except (OSError, ValueError, zipfile.BadZipFile) as fehler:
            logger.warning('Mesh3daiformvariante: %s nicht lesbar (%s)', datei, fehler)
            namen = set()
        cls._schluessel[str(datei)] = (stand, namen)
        return namen

    @classmethod
    def laeufe(cls, name):
        wurzel = Mesh3daiformtraining.ordner()
        if not wurzel.is_dir():
            return []
        aus = [p for p in wurzel.iterdir() if p.is_dir() and '%s_soll_form' % name in cls._dateien(p)]
        return [{'name': p.name, 'kurz': p.name[17:] if Mesh3daiformtraining._start(p.name) else p.name, 'pfad': p}
                for p in sorted(aus, key=lambda p: p.name, reverse=True)]

    @classmethod
    def mit_seite(cls, lauf):
        """Die Figuren, deren Seite diesen Lauf zeigen kann (`<Figur>_soll_form` in der Vorhersagedatei) — für die Links der Laufseite."""
        return {k[:-len('_soll_form')] for k in cls._dateien(lauf) if k.endswith('_soll_form')}

    @staticmethod
    def _json(pfad):
        try:
            return json.loads(pfad.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def liste(cls, lauf):
        """Die Formregler des Laufs (Kopie im Laufordner, `mesh3dai_formfassung.LAUFKOPIE`) — ohne sie keine Figur (nie eine andere Fassung raten)."""
        d = cls._json(lauf / cls.LISTE)
        return d.get('regler') if isinstance(d, dict) else None

    @staticmethod
    def wolken(ergebnis):
        roh = str((ergebnis or {}).get('wolken') or '0')
        return sorted({int(t) for t in re.findall(r'\d+', roh)}) or [0]

    @classmethod
    def zuordnung(cls, name, ordner, gruppe, zeilen, eingang, wolken, ausgelassen):
        """Proben der Gruppe in der Reihenfolge von `proben.json` → [(Eintrag, Wolken)]; None, wenn die Zahl nicht zu `zeilen` passt."""
        plan = cls._json(ordner / 'proben.json') or []
        aus = []
        for e in plan:
            # Formtraining 1 (`mesh3dai_vorstufe_form.py`) vermerkt eine durchgefallene Probe ohne Wolke: „<Figur>/<nr>“.
            if e.get('gruppe') != gruppe or '%s/%d' % (name, int(e['nr'])) in ausgelassen:
                continue
            d = ordner / 'proben' / ('%04d' % int(e['nr']))
            da = [k for k in wolken if (d / ('%s_%d.npz' % (eingang, k))).is_file() and '%s/%d/k%d' % (name, int(e['nr']), k) not in ausgelassen]
            if da:
                aus.append((e, da))
        return aus if len(aus) == zeilen else None

    @classmethod
    def lesen(cls, name, lauf_name=None):
        ordner = cls.finden(name)
        if ordner is None:
            return None
        laeufe = cls.laeufe(name)
        modell = cls._json(ordner / 'modell.json') or {}
        info = {'figur': name, 'modell': {k: modell.get(k) for k in ('grundlage', 'geschlecht', 'gruppe', 'mblab_vorlage', 'lebensalter_jahre', 'weites_stueck', 'formregler_fassung')},
                'laeufe': [{'name': x['name'], 'kurz': x['kurz']} for x in laeufe]}
        info['grundlage'] = modell.get('grundlage') or name
        if not laeufe:
            return dict(info, lauf=None, proben=[], hinweis='Kein Formlauf unter _vorstufe/laeufe trägt %s (formen_vorhersagen.npz → %s_soll_form).' % (name, name))
        # Vorgabe wie in der Tabelle der Formvarianten: der jüngste FERTIGE Lauf ohne Probelauf (`…_probe`), sonst der jüngste.
        vorgabe = next((x for x in laeufe if not x['kurz'].endswith('_probe') and (x['pfad'] / 'lauf_ergebnis.json').is_file()), laeufe[0])
        gewaehlt = next((x for x in laeufe if x['name'] == lauf_name), vorgabe)
        lauf = gewaehlt['pfad']
        e = cls._json(lauf / 'lauf_ergebnis.json') or {}
        f = cls._json(lauf / 'formen_ergebnis.json') or {}
        eingang = e.get('eingang') or f.get('eingang') or 'apose_v4'
        wolken = cls.wolken(e)
        ausgelassen = e.get('ausgelassen') if isinstance(e.get('ausgelassen'), dict) else {}
        dateien = cls._dateien(lauf)
        proben, gruppen = [], {}
        with np.load(lauf / cls.VORHERSAGEN) as z:
            for g in cls.GRUPPEN:
                schluessel = '%s_%s_form' % (name, g)
                if schluessel not in dateien:
                    continue
                zeilen = int(z[schluessel].shape[0])
                paare = cls.zuordnung(name, ordner, g, zeilen, eingang, wolken, ausgelassen)
                gruppen[g] = {'zeilen': zeilen, 'zugeordnet': paare is not None}
                for i, (eintrag, da) in enumerate(paare or []):
                    proben.append({'nr': int(eintrag['nr']), 'name': eintrag.get('name'), 'kategorie': eintrag.get('kategorie'), 'gruppe': g, 'zeile': i, 'wolken': da})
            regler = cls.regler(z, name, cls.liste(lauf))
        je = (e.get('je_figur') or {}).get(name) or {}
        # Zahlen des Laufs je Gruppe mit den Namen der Laufseite (`Mesh3daiformlaufnamen`) — die Seite rechnet nichts daran.
        werte = [{'gruppe': g, 'schluessel': k, 'name': N.name(k), 'wert': v, 'fehler': N.fehler(k)}
                 for g, w in je.items() if isinstance(w, dict) for k, v in N.flach(w).items() if isinstance(v, (int, float))]
        echt =((cls._json(lauf / 'formen_pruefung_echt.json') or {}).get('ergebnis') or {}).get(name)
        return dict(info, lauf={'name': lauf.name, 'kurz': gewaehlt['kurz'], 'eingang': eingang, 'wolken': wolken, 'epochen': e.get('epochen'), 'formregler': e.get('formkopf'),
                                'formregler_datei': e.get('formregler_datei') or f.get('formregler'), 'fertig': (lauf / 'lauf_ergebnis.json').is_file()},
                    gruppen=gruppen, proben=sorted(proben, key=lambda p: p['nr']), werte=werte, echt=echt, regler=regler,
                    fremde=list((e.get('fremde_regler') or {}).get(name) or []), hinweis='')

    @classmethod
    def regler(cls, z, name, liste):
        """Die Regler mit der größten Abweichung Soll ↔ Vorhersage (Mittel aller Proben), geklemmt wie die Figur — nur gesetzte (|Wert| ≥ 0,01 in Soll oder Vorhersage)."""
        if not liste:
            return None
        soll = z['%s_soll_form' % name].astype(np.float64)
        zeilen = [z[k] for k in ('%s_%s_form' % (name, g) for g in cls.GRUPPEN) if k in z.files]
        if len(soll) != len(liste) or not zeilen:
            return None
        vor = np.concatenate(zeilen).astype(np.float64).mean(axis=0)
        lo, hi = np.array([r['min'] for r in liste], dtype=float), np.array([r['max'] for r in liste], dtype=float)
        s, v = np.clip(soll, lo, hi), np.clip(vor, lo, hi)
        s[np.abs(s) < 0.01] = 0.0
        v[np.abs(v) < 0.01] = 0.0
        gesetzt = np.flatnonzero((s != 0) | (v != 0))
        reihe = gesetzt[np.argsort(-np.abs(v[gesetzt] - s[gesetzt]), kind='stable')][:cls.REGLER_ZEILEN]
        return {'gesetzt_soll': int((s != 0).sum()), 'gesetzt_vorhersage': int((v != 0).sum()), 'gesamt': len(liste),
                'zeilen': [{'name': liste[i]['name'], 'anzeige': liste[i].get('anzeige') or liste[i]['name'], 'bereich': liste[i].get('bereich_titel') or liste[i].get('bereich') or '',
                            'soll': round(float(s[i]), 3), 'vorhersage': round(float(v[i]), 3), 'delta': round(float(v[i] - s[i]), 3)} for i in reihe]}

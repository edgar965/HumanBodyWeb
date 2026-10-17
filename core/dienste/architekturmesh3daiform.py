# -*- coding: utf-8 -*-
"""Architekturmesh3daiform — der Formkopf von Mesh3D-AI auf Hilfe → Architektur → Mesh3DAI: Formregler, Formvarianten, Datensatz aller Jobs, Ergebnis (16.10.2026 abends).

Edgar: „das netz soll auch: die Form vorhersagt: die Genesis-Formregler (815) usw.“ — gebaut in `ProjektTemp/_wegwerf/` (`mesh3dai_formregler.py`, `mesh3dai_formvarianten.py`,
`mesh3dai_formnetz.py`, `mesh3dai_form_alle.py`, `mesh3dai_form_pruefen.py`; Lehren `.claude/rules/mesh3dai-form.md`).
GELESEN beim Aufruf aus `3DObjects/mesh3dai/`:
    formregler.json / formregler_v2.json   je Regler Bereich, Grenzen, Wirkung (mm je Einheit an 4.000 Körperpunkten) — die Liste, die der Lauf nennt (`regler_datei`)
    _formen/varianten.json          die Formvarianten: Grundlage, Geschlecht, Gruppe, Zahl der gestellten Regler
    <Job>/proben.json               Proben je Gruppe (alle Jobs und Varianten)
    <Job>/<Ablage>/<Lauf>/lauf_ergebnis.json   je Grundjob: Gelenke (gestimmt und nach der Anpassung), Form gegen „mittlere Form“ und „Grundfigur“, Verlauf je 20 Epochen
    Ursula1/<Ablage>/<Lauf>/formen_ergebnis.json, formen_pruefung_echt.json   Varianten (lineare Näherung) und die echte Nachrechnung mit der Genesis-Formung
Von Hand stehen nur die Setzungen des Variantenbaus (`BAU`, gelesen in `mesh3dai_formvarianten.py`).
"""

import json
from pathlib import Path

__all__ = ['Architekturmesh3daiform']


class Architekturmesh3daiform:
    JOBS = ('Ursula1', 'Damira0', 'Mann1', 'Matt0')
    #: Wie eine Formvariante entsteht — Setzungen aus `ProjektTemp/_wegwerf/mesh3dai_formvarianten.py` (GRUNDLAGEN, CHARAKTERE, ANIME_P, REGELN, AUSGENOMMEN, POSEN, PRUEF_JEDE).
    BAU = (
        ('Grundlage', 'reihum Ursula1, Damira0 (weiblich), Mann1, Matt0 (männlich): von ihr kommen Kleidung, Haar und Geschlecht'),
        ('Charaktere', 'ein Daz-Charakter des Geschlechts mit 0,5–1; mit Wahrscheinlichkeit 0,5 ein zweiter mit dem Rest; mit 0,1 ein Anime-Grundkörper (Amala, Base Feminine, Kat, Laura … bzw. Base Masculine, Fabrice, Matt, Ty)'),
        ('Regler dazu', 'je Bereich einige zufällige Form-Regler × Faktor: Körper 5 × 0,5 · Proportionen 8 × 0,5 · Kopf 10 × 0,5 · HB-Körper 4 × 0,4 · HB-Gesicht 4 × 0,4 (Setzung)'),
        ('Nie gewürfelt', 'die drei reinen Skalierungen ProportionSmaller, ProportionSmallerBO, ProportionLarger (430–493 mm je Einheit — sie machen die Figur nur größer oder kleiner)'),
        ('Posen', '12 je Variante: A-Pose + 11 aus dem Pool der 200 Trainingsposen der vier Jobs, als Daz-Winkel auf das Skelett der Variante gelegt (kein neuer Retarget; Gegenprobe 0,0001 mm)'),
        ('Prüfformen', 'jede 7. Variante wird nie trainiert — ganze Figuren, die das Netz nie gesehen hat'),
        ('Bau je Variante', 'Teile in der A-Pose (Kleidung folgt der Körperform über Auto-Follow) → 12 Proben (Häuten, Sichtbarkeit, Abtasten) → Skelett; dieselben Skripte wie bei den Jobs'),
    )

    @staticmethod
    def wurzel():
        from django.conf import settings
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai'

    @staticmethod
    def _json(datei):
        try:
            return json.loads(Path(datei).read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return None

    @classmethod
    def lauf(cls):
        """Der jüngste Lauf mit Formkopf (`formen_ergebnis.json` im Ordner von Ursula1, `_laeufe` oder `_diagnose`), ohne Probeläufe (`…_probe`); None, solange keiner fertig ist."""
        u = cls.wurzel() / 'Ursula1'
        laeufe = [p for a in ('_laeufe', '_diagnose') if (u / a).is_dir() for p in (u / a).iterdir()
                  if (p / 'formen_ergebnis.json').is_file() and not p.name.endswith('_probe')]
        return max(laeufe, key=lambda p: p.name) if laeufe else None

    @classmethod
    def regler_datei(cls, lauf=None):
        """Die Formregler-Liste, mit der `lauf` trainiert hat (`formen_ergebnis.json` → `formregler`; 17.10.2026: Fassung 2 `formregler_v2.json` mit 906 Reglern neben Fassung 1
        `formregler.json` mit 815). Ohne Lauf oder ohne Angabe die Liste vom 16.10.2026 — die Läufe von damals nennen keine."""
        if lauf and (lauf / 'formregler_liste.json').is_file():
            return lauf / 'formregler_liste.json'       # die Kopie genau dieses Laufs (seit 17.10.2026, `mesh3dai_formfassung.LAUFKOPIE`)
        name = ((cls._json(lauf / 'formen_ergebnis.json') or {}).get('formregler') if lauf else None) or 'formregler.json'
        return cls.wurzel() / name

    @classmethod
    def regler(cls, lauf=None):
        """Die Formregler je Bereich (der Liste des Laufs `lauf`, `regler_datei`): Zahl, ohne Wirkung (unter 0,01 mm je Einheit), Median und größte Wirkung."""
        datei = cls.regler_datei(lauf)
        d = cls._json(datei)
        if not d:
            return None
        bereiche = {}
        for r in d['regler']:
            b = bereiche.setdefault(r['bereich'], {'schluessel': r['bereich'], 'titel': r.get('bereich_titel', r['bereich']), 'wirkung': []})
            b['wirkung'].append(float(r.get('wirkung_mm') or 0.0))
        zeilen = []
        for b in bereiche.values():
            w = sorted(b['wirkung'])
            zeilen.append({'schluessel': b['schluessel'], 'titel': b['titel'], 'zahl': len(w), 'ohne_wirkung': sum(1 for x in w if x < 0.01),
                           'median_mm': round(w[len(w) // 2], 2), 'groesste_mm': round(w[-1], 1)})
        staerkste = sorted(d['regler'], key=lambda r: -float(r.get('wirkung_mm') or 0))[:5]
        return {'anzahl': d.get('anzahl', len(d['regler'])), 'ohne_wirkung': d.get('ohne_wirkung'), 'erzeugt': d.get('erzeugt'), 'punkte': d.get('probe_punkte'),
                'datei': datei.name, 'fassung': d.get('fassung', 1), 'namen': [r['name'] for r in d['regler']],
                'zeilen': zeilen, 'nach_schluessel': {z['schluessel']: z['zahl'] for z in zeilen},
                'staerkste': [{'name': r.get('anzeige') or r['name'], 'mm': round(float(r['wirkung_mm']), 1)} for r in staerkste]}

    @classmethod
    def varianten(cls):
        liste = cls._json(cls.wurzel() / '_formen' / 'varianten.json') or []
        je = {}
        for v in liste:
            z = je.setdefault(v['grundlage'], {'grundlage': v['grundlage'], 'geschlecht': 'männlich' if v['geschlecht'] == 'maennlich' else v['geschlecht'],
                                               'training': 0, 'pruefung': 0, 'regler': []})
            z[v['gruppe']] = z.get(v['gruppe'], 0) + 1
            z['regler'].append(int(v.get('regler') or 0))
        zeilen = [dict(z, regler='%d–%d' % (min(z['regler']), max(z['regler']))) for z in je.values() if z['regler']]
        return {'zahl': len(liste), 'pruefformen': [v['name'] for v in liste if v['gruppe'] == 'pruefung'], 'zeilen': zeilen, 'bau': cls.BAU}

    @classmethod
    def datensatz(cls):
        """Proben je Gruppe: die vier Jobs einzeln, die Formvarianten zusammen."""
        zeilen, varianten = [], {'name': 'Formvarianten', 'ordner': 0}
        for p in sorted(cls.wurzel().iterdir()):
            proben = cls._json(p / 'proben.json') if p.is_dir() else None
            if not isinstance(proben, list) or not (p.name in cls.JOBS or p.name.startswith('Form')):
                continue
            zaehler = {}
            for e in proben:
                zaehler[e.get('gruppe', '?')] = zaehler.get(e.get('gruppe', '?'), 0) + 1
            if p.name.startswith('Form'):
                varianten['ordner'] += 1
                for g, n in zaehler.items():
                    varianten[g] = varianten.get(g, 0) + n
            else:
                zeilen.append(dict(zaehler, name=p.name, ordner=1))
        if varianten['ordner']:
            zeilen.append(varianten)
        return zeilen

    @classmethod
    def ergebnis(cls, lauf):
        """Grundjobs je Gruppe, Varianten zusammen, echte Nachrechnung, Verlauf — oder None ohne Lauf."""
        if lauf is None:
            return None
        jobs, kopf = [], None
        for name in cls.JOBS:
            e = cls._json(cls.wurzel() / name / lauf.parent.name / lauf.name / 'lauf_ergebnis.json')
            if not e:
                continue
            kopf = kopf or e
            for g in ('training', 'pruefung', 'spagat'):
                m, ms, f = (e.get('maße') or {}).get(g), (e.get('maße_stimmen') or {}).get(g), (e.get('form') or {}).get(g)
                if m and f:
                    jobs.append({'job': name, 'gruppe': g, 'proben': (e.get('proben') or {}).get(g), 'gelenke_mm': m.get('netz_mm'), 'gestimmt_mm': (ms or {}).get('netz_mm'),
                                 'form_mm': f.get('form_mm'), 'mittlere_mm': f.get('mittlere_form_mm'), 'grund_mm': f.get('grundfigur_mm')})
        formen = cls._json(lauf / 'formen_ergebnis.json') or {}
        echt = (cls._json(lauf / 'formen_pruefung_echt.json') or {}).get('ergebnis') or {}
        pruefformen = [dict(v, name=k) for k, v in sorted(echt.items()) if not k.startswith('mittel_') and v.get('gruppe') == 'pruefung']
        verlauf = [v for v in (kopf or {}).get('verlauf') or [] if 'training_form_mm' in v]
        return {'lauf': lauf.name, 'ablage': lauf.parent.name, 'epochen': (kopf or {}).get('epochen'), 'dauer_s': (kopf or {}).get('dauer_s'), 'parameter': (kopf or {}).get('parameter'),
                'proben_alle': (kopf or {}).get('proben_alle'), 'farbe': (kopf or {}).get('farbe'), 'drehung': (kopf or {}).get('drehung_grad'), 'form_gewicht': (kopf or {}).get('form_gewicht'),
                'jobs': jobs, 'zusammen': formen.get('zusammen') or {}, 'echt_training': echt.get('mittel_training'), 'echt_pruefung': echt.get('mittel_pruefung'),
                'echt': [('Trainingsvarianten', echt.get('mittel_training')), ('Prüfformen (nie trainiert)', echt.get('mittel_pruefung'))],
                'pruefformen': pruefformen, 'verlauf': verlauf}

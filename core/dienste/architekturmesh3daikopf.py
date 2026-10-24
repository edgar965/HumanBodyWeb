# -*- coding: utf-8 -*-
"""Architekturmesh3daikopf — Abschnitt „Kopf aus der KI: Kopfnetz und Angleichung an das Mesh“ der Seite Hilfe → Architektur → Mesh3DAI (24.10.2026).

Edgar, 24.10.2026: „update /hilfe/architektur/mesh3dai/ mit dem genauen Code, inkl. Kopf KI“ und „wie kommt es, dass diese Kopf KI vergessen wurde??“.
Gelesen beim Aufruf: der Kopfnetz-Lauf der KI-Fassungen (`_kopfnetz/laeufe/<Lauf>/lauf_ergebnis.json`, `aufbau.json` — Bauart und Gewichte aus `netz.pt`, abgelegt von
`_wegwerf/kopfnetz_aufbau_ablegen.py`, weil die Seite kein torch lädt) und je Test der Bericht des Schritts „kopf“ (`_test/<k>/kopf/kopfangleich_<g>.json`, `mesh3dai_kopfangleich_lauf.py`).
Von Hand (mit Quelle): die Messung des Kopfnetzes gegen die Wahrheit der Tripo-Jobs (`WAHRHEIT`) und an Edgar (`EDGAR`).
"""

import json
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmesh3daikopf']


class Architekturmesh3daikopf:
    #: gemessen 24.10.2026, `ProjektTemp/_wegwerf/kopfnetz_tripo_wahrheit.py`: Kopfform (Lage abgezogen, Median über die Kopfpunkte, mm) gegen die Regler des Genesis-Exports — echt geformt (G9formung)
    WAHRHEIT = (('Matt1', 0.23, 4.63), ('OlesiaWalk', 0.59, 3.22), ('DamiraAlt', 1.19, 2.64), ('Damira0Tripo', 0.19, 0.97), ('Rainy', 0.90, 17.59))
    WAHRHEIT_GRUNDFIGUR = 'Grundfigur → Ziel 2,8–7,7 mm'
    #: gemessen 24.10.2026, `_wegwerf/kopfnetz_wirkung_edgar.py` und `kopfnetz_merkmal_edgar.py`
    EDGAR = ('An edgar_knopf bewegte das Kopfnetz die Kopfpunkte nur um Median 0,7 mm (höchstens 2,2 mm), obwohl sein eigenes Merkmal 3–4 mm Abstand zur Eingangshaut zeigt (p90 11–14 mm); '
             '„Gesicht wie der Eingang“ blieb rot.')
    VERGESSEN = ('Trainiert am 21.10.2026 abends (`mesh3dai_kopfnetz_training.py`, nur gewürfelte Köpfe), danach nur an Grundjob-Proben eingesetzt (`mesh3dai_kopfnetz_einsatz.py`), nie an einem '
                 'Test; nicht in `ki_fassungen.json`; beim Umzug der Kette ins Projekt (23.10.2026) kamen nur die Module mit, die ein Schritt erreicht — das Kopfnetz erreichte keiner. Seit 24.10.2026 '
                 'liegt es in `mesh3dai/`, steht in den KI-Fassungen (`kopfnetz`) und ist der Start des Schritts „kopf“.')
    #: (Größe, was gemessen wird) — wie `Kopfangleich` rechnet (Code: `mesh3dai/mesh3dai_kopfangleich.py`)
    GROESSEN = (
        ('Maße', 'die 11 Strecken der Prüfung „Gesicht wie der Eingang“ (Gesichtsbreite, Augen außen/innen, beide Augenbreiten, Nasenbreite, Mundbreite, Nasenhöhe, Nase bis Mund, Augen bis Mund, '
                 'Mund bis Kinn) — je Maß (Figur − Eingang) geteilt durch seine rote Grenze (8 % bzw. Rauschen des Detektors, mindestens 3 mm), quadriert'),
        ('Punkte', 'alle 478 Landmarken in der Bildebene der frontalen Kamera, Mittel abgezogen (die Lage des Kopfs zählt nicht); Eingang = MediaPipe am gerenderten Mesh, '
                   'Figur = dieselben Punkte auf ihrem Käfig (Dreieck + Anteile von `G9netzlandmarken`)'),
        ('Fläche', 'Kopfpunkte des Käfigs im Gesichtsoval (vorn) gegen 40.000 Punkte auf der HAUT des Eingangs (Art aus der Zerlegung), Punkt zu Ebene, Huber 2 mm, ohne Gegenstück über 15 mm; '
                   'der Kopf darf dafür starr rücken und sich drehen — die Lage des Kopfs ist kein Kopfregler'),
        ('Zug', 'Σ (Regler − Stand der Runde)² — Regler ohne Wirkung wandern nicht'),
    )
    ABLAUF = (
        'Start: Regler der Figur vorher (`regler_vorher` — ein zweiter Lauf geht von dort aus, nie vom eigenen Ergebnis), darauf das Kopfnetz (Δ der 523 Kopfregler).',
        'Eingang einmal messen: Tripo-Netz mit Textur frontal gerendert (pyrender, Achsen aus den Gelenken der KI), MediaPipe FaceLandmarker (python10), dazu vier um ±4° gedrehte Kameras für das Rauschen.',
        'Je Runde: 300 Adam-Schritte auf der Grafikkarte; die Figur linear um den Stand der Runde (`Kopfmodell.kopf`, Formmaß 2: zwei Geraden je Regler), in der Haltung der KI gehäutet wie im '
        'Browser (je Kopfpunkt x′ = A·x + b).',
        'Nach jeder Runde die echte Formung (G9formung, 0,12 s) und dieselben Größen daran; Schluss, wenn kein Maß mehr rot ist, nach 4 Runden oder wenn eine Runde nichts bessert.',
        'Übernommen wird nur ein Stand, der an der echten Formung besser ist als die Figur vorher; dann: Figur neu bauen, „anpassen“ und „haltung2“ neu, „Gesicht wie der Eingang“ an der gebauten Figur.',
    )

    @staticmethod
    def _json(p):
        try:
            return json.loads(Path(p).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    @classmethod
    def kontext(cls):
        from .mesh3daikifassungen import Mesh3daikifassungen
        wurzel = Path(settings.OBJECTS_ROOT) / 'mesh3dai'
        lauf = Mesh3daikifassungen.lesen().get('kopfnetz')
        ordner = wurzel / '_kopfnetz' / 'laeufe' / str(lauf)
        ergebnis = cls._json(ordner / 'lauf_ergebnis.json') or {}
        aufbau = cls._json(ordner / 'aufbau.json')
        a = (aufbau or {}).get('aufbau') or {}
        schichten = None
        if a:
            k, r, h, b = a['kopfpunkte'], a['regler'], a['kopfregler'], a['breite']
            schichten = [('Merkmal des Eingangs', '%d × 2 (Abstand entlang der Normale, Sicherheit je Kopfpunkt)' % k, 'Linear %d → %d, GELU, Linear %d → %d, GELU' % (2 * k, b, b, b)),
                         ('Regler der Figur', '%d (Formregler Fassung 6)' % r, 'Linear %d → 256, GELU' % r),
                         ('Kopf', '%d + 256' % b, 'Linear %d → %d, GELU, Linear %d → %d, GELU, Linear %d → %d (Δ Kopfregler, Start 0)' % (b + 256, b, b, b // 2, b // 2, h))]
        verlauf = ergebnis.get('verlauf') or []
        return {'lauf': lauf, 'aufbau': aufbau, 'schichten': schichten, 'kopfmodell': ergebnis.get('kopfmodell'),
                'training': {k: ergebnis.get(k) for k in ('schritte', 'stapel', 'dauer_s')} if ergebnis else None,
                'pruefung': verlauf[-1].get('pruefung') if verlauf else None, 'pruefung_schritt': verlauf[-1].get('schritt') if verlauf else None,
                'wahrheit': [{'job': j, 'formkopf': f, 'kopfnetz': n} for j, f, n in cls.WAHRHEIT], 'wahrheit_grundfigur': cls.WAHRHEIT_GRUNDFIGUR,
                'edgar': cls.EDGAR, 'vergessen': cls.VERGESSEN, 'groessen': cls.GROESSEN, 'ablauf': cls.ABLAUF, 'tests': cls.tests(wurzel / '_test')}

    @classmethod
    def tests(cls, tests):
        """Je Test und Geschlecht der Bericht des Schritts „kopf“ → Zeilen für die Seite."""
        aus = []
        for datei in sorted(tests.glob('*/kopf/kopfangleich_*.json')):
            b = cls._json(datei)
            if not b:
                continue
            an = b.get('angleich') or {}
            vor, nach = (b.get('gesicht_vorher') or {}).get('masse') or {}, (b.get('gesicht_nachher') or {}).get('masse') or {}
            masse = [{'name': n, 'eingang': m.get('eingang_mm'), 'vorher': m.get('figur_mm'), 'nachher': (nach.get(n) or {}).get('figur_mm'),
                      'rot_vorher': m.get('rot'), 'rot_nachher': (nach.get(n) or {}).get('rot')} for n, m in vor.items()]
            zeilen = [dict(an[n], name=n) for n in ('vorher', 'start') if n in an] + [dict(z, name='Runde %d' % z['runde']) for z in an.get('runden') or []]
            aus.append({'test': b.get('test'), 'geschlecht': b.get('geschlecht'), 'trocken': b.get('trocken'), 'uebernommen': an.get('uebernommen'), 'grund': an.get('grund'),
                        'geaendert': an.get('geaendert'), 'sekunden': an.get('sekunden'), 'gerechnet': an.get('gerechnet'), 'zeilen': zeilen, 'masse': masse,
                        'rot_vorher': sum(1 for m in masse if m['rot_vorher']), 'rot_nachher': sum(1 for m in masse if m['rot_nachher']) if nach else None,
                        'versatz_vorher': (b.get('gesicht_vorher') or {}).get('versatz_mm'), 'versatz_nachher': (b.get('gesicht_nachher') or {}).get('versatz_mm'),
                        'haut': an.get('haut'), 'kopfpunkte_vorn': an.get('kopfpunkte_vorn')})
        return aus

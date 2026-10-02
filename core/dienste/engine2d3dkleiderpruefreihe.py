# -*- coding: utf-8 -*-
u"""Engine2d3dKleiderpruefreihe — feste Aufträge „2D3D Kleider" mit Sollbereichen (01.10.2026, Punkt 6 des Plans).

Edgar: „ohne dass ich deine Gaga Fehler korrigiere". Jede Änderung an der Pipeline läuft — auf Ansage — über diese
Aufträge, bevor Edgar ein Ergebnis sieht. Die Sollbereiche stehen in `core/daten/engine2d3dkleiderpruefreihe.json`:

    gesamt_hoechstens            Gesamtnote der besten Runde (`kreislauf.note.gesamt`, `Gesamtnote`)
    farbe_teile_hoechstens       Farbfehler je Teil der besten Runde (`kreislauf.note.teilnoten.farbe_teile`)
    anschlag_hoechstens          so viele Regler des Modells dürfen am Anschlag stehen (±1, Ortsregler ±2) — `.51`
                                 hatte sieben (Waden, Oberschenkel, drei Gesichtsregler)
    messguete                    der Befund des Stands hat `messguete.gueltig` (Selbsttest der Projektion)
    fotos_ausgelassen            genau diese Fotos ließ die Fotoprüfung aus (`ergebnis.fotopruefung.ausgelassen`)
    frisur_kandidaten_mindestens so viele Frisuren hat der Schritt „Körper" gemessen
    standmodell                  das Modell des Stands ist gebaut und aktuell (`Engine2d3dKleiderstandmodell.eintrag`)
    ohne_fehler                  der Auftrag ist nicht gescheitert

`bewerten` liest nur gespeicherte Daten (kein Rechnen); `manage.py engine2d3dkleider_pruefreihe` druckt die Tabelle und
startet mit `--starten` die Läufe über die Server-API (`Engine2d3dKleiderserverstart`).
"""

import json

from django.conf import settings

__all__ = ['Engine2d3dKleiderpruefreihe']


class Engine2d3dKleiderpruefreihe:
    DATEI = ('core', 'daten', 'engine2d3dkleiderpruefreihe.json')
    ANSCHLAG = 0.999

    @classmethod
    def laden(cls):
        pfad = settings.BASE_DIR.joinpath(*cls.DATEI)
        return json.loads(pfad.read_text(encoding='utf-8')).get('auftraege') or []

    @classmethod
    def anschlaege(cls, koerper):
        """Die Regler des Modells am Anschlag: ±1, Ortsregler (`eigen:ort_…`) ±2."""
        aus = []
        for name, wert in (koerper or {}).items():
            if not isinstance(wert, (int, float)) or isinstance(wert, bool):
                continue
            grenze = 2.0 if str(name).startswith('eigen:ort_') else 1.0
            if abs(float(wert)) >= cls.ANSCHLAG * grenze:
                aus.append(name)
        return sorted(aus)

    @classmethod
    def istwerte(cls, job):
        from .engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell
        e = job.ergebnis or {}
        k = e.get('kreislauf') or {}
        note = k.get('note') or {}
        stand = Engine2d3dKleiderstandmodell(job).eintrag() or {}
        # Dictionary gewollt: geht als JSON in die Ausgabe des Befehls.
        return {'gesamt': note.get('gesamt'), 'farbe_teile': (note.get('teilnoten') or {}).get('farbe_teile'),
                'anschlag': cls.anschlaege((k.get('modell') or {}).get('koerper')),
                'messguete': ((k.get('befund') or {}).get('messguete') or {}).get('gueltig'),
                'fotos_ausgelassen': sorted((e.get('fotopruefung') or {}).get('ausgelassen') or []),
                'frisur_kandidaten': len((e.get('frisur') or {}).get('kandidaten') or []),
                'standmodell': bool(stand.get('aktuell')) and not stand.get('fehler'),
                'fehler': job.error_message or None, 'status': job.status, 'beste_runde': k.get('runde_bester'),
                'letzte_runde': k.get('letzte_runde')}

    @staticmethod
    def _kleiner(ist, soll):
        return ist is not None and float(ist) <= float(soll)

    @classmethod
    def bewerten(cls, job, soll):
        """→ [(prüfung, ist, soll, ok)] für die Sollbereiche eines Auftrags."""
        ist = cls.istwerte(job)
        regeln = {
            'gesamt_hoechstens': (ist['gesamt'], lambda s: cls._kleiner(ist['gesamt'], s)),
            'farbe_teile_hoechstens': (ist['farbe_teile'], lambda s: cls._kleiner(ist['farbe_teile'], s)),
            'anschlag_hoechstens': (ist['anschlag'], lambda s: len(ist['anschlag']) <= int(s)),
            'messguete': (ist['messguete'], lambda s: ist['messguete'] is bool(s)),
            'fotos_ausgelassen': (ist['fotos_ausgelassen'], lambda s: ist['fotos_ausgelassen'] == sorted(s)),
            'frisur_kandidaten_mindestens': (ist['frisur_kandidaten'], lambda s: ist['frisur_kandidaten'] >= int(s)),
            'standmodell': (ist['standmodell'], lambda s: ist['standmodell'] is bool(s)),
            'ohne_fehler': (ist['fehler'] or ist['status'],
                            lambda s: (not ist['fehler'] and ist['status'] != 'gescheitert') is bool(s)),
        }
        aus = []
        for name, wert in soll.items():
            if name not in regeln:
                aus.append((name, None, wert, False))
                continue
            ist_wert, pruefen = regeln[name]
            aus.append((name, ist_wert, wert, bool(pruefen(wert))))
        return aus

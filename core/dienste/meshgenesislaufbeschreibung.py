# -*- coding: utf-8 -*-
"""Meshgenesislaufbeschreibung — welcher Job, welcher Schritt: die Zeile eines laufenden Prozesses in der Liste „Laufende Jobs“ (Reiter „Lauf Aktuell“ auf /mesh-genesis/, 20.10.2026).

Edgar: „warum sind das denn ‚unbekannte Jobs‘??? Mach eine klare Liste der Jobs, ohne gaga Texte, die gerade laufen, welcher Job, welcher Schritt“. Zwei Fehler der Fassung vom 18.10.2026:
  * Gesucht wurde im GANZEN Befehl — ein GPU-Lauf startet als `meshgenesis_stimmen_lauf.py <Skript> …`, und der Starter traf die Regel „meshgenesis_stimmen“: jeder Lauf über ihn hieß
    „Die KI lernt das Skelett“ (gesehen 20.10.2026 22:44: es lief `meshgenesis_test_form_haltung.py`). Jetzt zählt das Skript, das der Starter startet (`STARTER`).
  * Skripte ohne Regel hießen „Unbekannter Lauf (…)“ (`meshgenesis_schnitt_katalogdaten.py`, `meshgenesis_nachstellen_lauf.py`). Die Regeln decken jetzt alle Skripte der Ketten in
    `ProjektTemp/_wegwerf/*.sh`; ein Skript ohne Regel steht mit seinem Namen ohne „meshgenesis_“ da, und das Log nennt es einmal.
Der Job kommt aus den Argumenten (`--jobs`, `--figur`, `--nur` … und frei stehende Namen) gegen die Namen der Jobs und Testfiguren; nichts gefunden heißt „alle Jobs“.

    Meshgenesislaufbeschreibung.beschreiben(job, Meshgenesislaufbeschreibung.namen()) -> {art, titel, fortschritt_art, skript_echt, job_text, job_titel, job_adresse, wartet_gpu}
"""

import json
import logging
import threading
import time

logger = logging.getLogger('core')

__all__ = ['Meshgenesislaufbeschreibung']


class Meshgenesislaufbeschreibung:
    #: Starter, die ein anderes Skript unter der GPU-Sperre starten: das erste `*.py` ihrer Argumente, sonst ihr fester Lauf.
    STARTER = {'meshgenesis_stimmen_lauf.py': 'meshgenesis_stimmen_netz.py', 'meshgenesis_test_lauf.py': 'meshgenesis_test_rechnen.py'}
    #: (Teil des Skriptnamens bzw. der Argumente, Art, Schritt in wenigen Worten, Fortschritt) — die erste passende Zeile gilt, darum das Genauere vor dem Allgemeinen.
    #: Fortschritt: `training` = Durchgang aus dem Laufordner, `daten` = Proben der Formvarianten (`Meshgenesislaufaktuell`).
    REGELN = (
        ('form2_kurz30', 'Probe', 'Körperform kurz trainieren (30 Durchgänge)', 'training'),
        ('formtraining_netz_messen', 'Probe', 'Zeit je Trainingsschritt messen', None),
        ('form2_tempo_probe', 'Probe', 'Tempo des Formtrainings messen', 'training'),
        ('tempoprobe', 'Probe', 'Schnellen Weg in die Grundhaltung prüfen', None),
        ('gpu_sperre', 'Warten', 'Wartet auf die Grafikkarte', None),
        ('meshgenesis_rechnen', 'Lauf', 'Rechnen per Knopf: alle Schritte eines Tests', None),          # 23.10.2026, `Meshgenesisrechenlauf` (Arbeitsprozess `manage.py meshgenesis_rechnen`)
        # Kleider und Haar
        ('meshgenesis_stufe2_alle', 'Training', 'KI lernt Kleider, Haar und Haut an allen Tripo-Jobs, danach die Testjobs', None),
        ('meshgenesis_stufe2_lauf', 'Training', 'KI lernt Kleider, Haar und Haut an diesem Job', None),
        ('meshgenesis_hautwechsel_lauf', 'Training', 'KI lernt die Haut (wechselnde Haut, scharfe und unscharfe Eingänge)', None),        # 24.10.2026
        ('meshgenesis_hautki_lauf', 'Training', 'KI lernt die Haut aus Kachelstücken (übernimmt Gesehenes, erzeugt Ungesehenes)', None),        # 24.10.2026 abends
        ('meshgenesis_hautki_einsatz', 'Haut', 'Haut der neuen KI für diesen Test', None),
        ('meshgenesis_hautton_lauf', 'Training', 'KI lernt den Hautton je Körperteil, Licht herausgerechnet', None),        # 25.10.2026, `Hauttontraining`
        ('meshgenesis_nachstellen_lauf', 'Kleider', 'Schnittmuster an das ausgeschnittene Stück anpassen', None),
        ('meshgenesis_flaeche_lauf', 'Kleider', 'Schnitt aus der Fläche: Teile flachlegen, nähen und drapieren', None),
        ('meshgenesis_schnitt_katalogdaten', 'Daten', 'Schnittmuster-Beispiele aus dem Katalog nähen', None),
        ('meshgenesis_schnitt_daten_aussortieren', 'Daten', 'Schnittmuster-Beispiele aussortieren', None),
        ('meshgenesis_schnitt_daten', 'Daten', 'Schnittmuster-Beispiele nähen', None),
        ('meshgenesis_schnitt_training', 'Training', 'KI lernt Schnittmuster', None),
        ('meshgenesis_schnitt_anwenden', 'Kleider', 'Schnittmuster nähen und anziehen', None),
        ('meshgenesis_schnitt_waehlen', 'Kleider', 'Schnittmuster wählen', None),
        ('meshgenesis_schnitt_regelwahl', 'Kleider', 'Schnittmuster nach Regeln wählen', None),
        ('meshgenesis_schnittvergleich', 'Vergleich', 'Schnittmuster auf drei Wegen vergleichen', None),
        ('meshgenesis_zerlegung_training', 'Training', 'KI lernt Kleider und Haar erkennen', None),
        ('meshgenesis_zerlegung_arten', 'Daten', 'Kleiderarten der Trainingsfiguren festhalten', None),
        ('meshgenesis_kleidervarianten', 'Daten', 'Trainingsfiguren in neuen Kleidern anlegen', None),
        ('meshgenesis_haarkatalog', 'Daten', 'Frisuren der Garderobe vermessen', None),
        ('meshgenesis_probenzerlegung', 'Kleider', 'Kleider und Haar erkennen', None),
        ('meshgenesis_kostuem_lauf', 'Kostüme', 'Kostüm erkennen, ausschneiden, auf die Figur legen und prüfen', None),
        ('meshgenesis_kopfangleich_lauf', 'Form', 'Kopf an das Mesh angleichen: Gesichtsmaße und Haut, in Runden', None),          # 24.10.2026, `Kopfangleich`
        ('meshgenesis_koerperangleich_lauf', 'Form', 'Körper in die Außenmaße des Mesh: Form, Proportionen, Haltung, in Runden', None),  # 25.10.2026, `Koerperangleich`
        ('meshgenesis_kostuem_segmentierung', 'Kostüme', 'Bildmodelle zerlegen das Netz (Sapiens2, SAM 3)', None),
        ('meshgenesis_kostuem_einpassen', 'Kostüme', 'Körper der KI ins Kostüm einpassen (Variante C)', None),
        ('meshgenesis_kostuem_sichtbar', 'Kostüme', 'Körper-KI sieht nur sichtbaren Körper (Variante B)', None),
        ('meshgenesis_kikleider_proben', 'Kleider', 'Figur bauen, Kleider ausschneiden und anziehen', None),
        ('meshgenesis_kleider_zerlegung', 'Kleider', 'Kleider und Haar erkennen', None),
        ('meshgenesis_kikleider', 'Kleider', 'Kleider ausschneiden und anziehen', None),
        ('meshgenesis_kleider.py', 'Kleider', 'Kleider aus Katalog und Mesh-3D-Lauf', None),
        # Künstliche Tripo-Netze und Tripo-Jobs
        ('meshgenesis_bild3d_bilder', 'Daten', 'Bilder für künstliche Tripo-Netze rendern', None),
        ('meshgenesis_bild3d_auswahl', 'Daten', 'Posen für künstliche Tripo-Netze wählen', None),
        ('meshgenesis_bild3d_netz', 'Daten', 'Künstliche Tripo-Netze rechnen', None),
        ('meshgenesis_bild3d_wolke', 'Daten', 'Trainingswolken aus künstlichen Tripo-Netzen', None),
        ('meshgenesis_bild3d', 'Daten', 'Künstliche Tripo-Netze', None),
        ('meshgenesis_paar_wolke', 'Daten', 'Trainingswolke aus dem Tripo-Netz', None),
        ('meshgenesis_paar_mesh3d', 'Testfigur', 'Mesh-3D-Lauf für das Tripo-Netz', None),
        ('meshgenesis_paar_messen', 'Prüfung', 'Gegen die Wahrheit messen', None),
        ('meshgenesis_paar_job', 'Daten', 'Tripo-Job anlegen', None),
        ('meshgenesis_paar_lauf', 'Testfigur', 'Tripo-Job rechnen', None),
        ('meshgenesis_paar_ziel', 'Daten', 'Ziel des Tripo-Jobs bauen', None),
        ('meshgenesis_paar_mia', 'Daten', 'Tripo-Netz riggen (MIA)', None),
        ('meshgenesis_pruefsatz_entscheiden', 'Prüfung', 'Neue KI übernehmen oder nicht', None),
        ('meshgenesis_pruefsatz', 'Prüfung', 'Tripo-Jobs gegen die Wahrheit messen', None),
        # Vorstufe, Körperform, Skelett
        ('meshgenesis_vorstufe_glieder_daten', 'Daten', 'Trainingsdaten nachbessern (Arme, Beine)', None),
        ('meshgenesis_vorstufe_mia_daten_lauf', 'Daten', 'Trainingsfiguren in die Grundhaltung bringen', 'daten'),
        ('meshgenesis_vorstufe_formen_daten', 'Daten', 'Formvarianten in die Grundhaltung bringen', None),
        ('meshgenesis_vorstufe_daten', 'Daten', 'Trainingsdaten der Vorstufe', None),
        ('meshgenesis_vorstufe_form', 'Training', 'KI lernt die Körperform', 'training'),
        ('meshgenesis_vorstufe_training', 'Training', 'KI lernt das Skelett in der Grundhaltung', 'training'),
        ('meshgenesis_vorstufe_netz', 'Training', 'KI lernt das Skelett in der Grundhaltung', 'training'),
        ('meshgenesis_vorstufe.py', 'Testfigur', 'Testmodell riggen und in die Grundhaltung bringen', None),
        ('meshgenesis_form2_entscheiden', 'Prüfung', 'Neuen Formkopf übernehmen oder nicht', None),
        ('meshgenesis_kopffehler_messen', 'Prüfung', 'Kopf und Körper der KI messen', None),
        ('meshgenesis_form_pruefen', 'Prüfung', 'Körperform prüfen', None),
        ('meshgenesis_form_vergleich', 'Prüfung', 'Formläufe vergleichen', None),
        ('meshgenesis_form_alle', 'Training', 'KI lernt die Körperform', 'training'),
        ('meshgenesis_formfigur', 'Testfigur', 'Vorhergesagte Figur bauen', None),
        ('meshgenesis_formen_kette', 'Daten', 'Formvarianten bauen und posieren', None),
        ('meshgenesis_formvarianten', 'Daten', 'Formvarianten anlegen', None),
        ('meshgenesis_formregler', 'Daten', 'Wirkung der Formregler messen', None),
        ('meshgenesis_mia_stapel', 'Daten', 'Figuren riggen (MIA)', None),
        # Testfiguren
        ('meshgenesis_test_form_haltung', 'Testfigur', 'Figur in die Haltung der KI stellen', None),
        ('meshgenesis_test_form_apose', 'Testfigur', 'Testfigur in die Grundhaltung bringen', None),
        ('meshgenesis_test_form', 'Testfigur', 'Körperform der Testfiguren vorhersagen', None),
        ('meshgenesis_test_rechnen', 'Testfigur', 'Testfiguren mit der KI rechnen', None),
        ('meshgenesis_test', 'Testfigur', 'Testfiguren mit der KI rechnen', None),
        # Netz auf Posen
        ('meshgenesis_stimmen_alle', 'Training', 'KI lernt das Skelett (alle Jobs)', 'training'),
        ('meshgenesis_stimmen_netz', 'Training', 'KI lernt das Skelett', 'training'),
    )
    NAMEN_S = 60
    _namen, _namen_zeit = None, 0.0
    _gemeldet = set()
    _sperre = threading.Lock()

    @classmethod
    def namen(cls):
        """{kleingeschriebener Name: (Anzeige, Adresse, 'job'|'test')} — Jobs mit Kennung, Name, Ordner, Modell; Testfiguren mit Ordner und Namen. 60 s gemerkt (die Messung läuft alle 5 s)."""
        with cls._sperre:
            if cls._namen is not None and time.time() - cls._namen_zeit < cls.NAMEN_S:
                return cls._namen
        from .meshgenesisattrappe import Meshgenesisattrappe
        from .meshgenesistest import Meshgenesistest

        aus = {}
        for s in Meshgenesisattrappe.stammdaten():
            eintrag = (s['name'], '/mesh-genesis/%s/' % s['id'], 'job')
            for k in (s.get('id'), s.get('name'), s.get('ordner'), s.get('modell')):
                if k:
                    aus.setdefault(str(k).lower(), eintrag)
        ordner = Meshgenesistest.ordner()
        for p in sorted(ordner.iterdir()) if ordner.is_dir() else ():
            if not (p / 'test.json').is_file():
                continue
            try:
                name = json.loads((p / 'test.json').read_text(encoding='utf-8')).get('name') or p.name
            except (OSError, ValueError):
                name = p.name
            aus.setdefault(p.name.lower(), (str(name), '/mesh-genesis/test/%s/' % p.name, 'test'))
        with cls._sperre:
            cls._namen, cls._namen_zeit = aus, time.time()
        return aus

    @classmethod
    def skript(cls, job):
        """(Skript, Argumente) des Laufs selbst — bei einem Starter das Skript, das er startet."""
        skript, argumente = job.get('skript', ''), list(job.get('argumente') or ())
        if skript in cls.STARTER:
            i = next((n for n, t in enumerate(argumente) if t.lower().endswith('.py')), None)
            return (argumente[i].replace('\\', '/').rsplit('/', 1)[-1], argumente[i + 1:]) if i is not None else (cls.STARTER[skript], argumente)
        return skript, argumente

    @classmethod
    def beschreiben(cls, job, namen):
        skript, argumente = cls.skript(job)
        regel = next((r for r in cls.REGELN if r[0] in skript), None) or next((r for r in cls.REGELN if r[0] in ' '.join(argumente)), None)
        if regel is None:
            with cls._sperre:
                neu = skript not in cls._gemeldet
                cls._gemeldet.add(skript)
            if neu:
                logger.warning('Meshgenesislaufbeschreibung: keine Regel für %s — Zeile in REGELN nachtragen', skript)
            stamm = skript[:-3] if skript.endswith('.py') else skript
            regel = (None, 'Lauf', stamm.removeprefix('meshgenesis_').replace('_', ' '), None)
        return {'art': regel[1], 'titel': regel[2], 'fortschritt_art': regel[3], 'skript_echt': skript, **cls._job(argumente, namen)}

    @staticmethod
    def _job(argumente, namen):
        treffer = []
        for t in argumente:
            if t.startswith('-'):
                continue
            for wert in t.split(','):
                e = namen.get(wert.strip().lower())
                if e and e not in treffer:
                    treffer.append(e)
        if not treffer:
            return {'job_text': 'alle Jobs', 'job_titel': 'Im Befehl steht kein einzelner Job.', 'job_adresse': None}
        if len(treffer) == 1:
            return {'job_text': treffer[0][0], 'job_titel': '', 'job_adresse': treffer[0][1]}
        tests = all(e[2] == 'test' for e in treffer)
        return {'job_text': '%s (%d)' % ('Testfiguren' if tests else 'Jobs', len(treffer)) if len(treffer) > 3 else ', '.join(e[0] for e in treffer),
                'job_titel': ', '.join(e[0] for e in treffer), 'job_adresse': None}

# -*- coding: utf-8 -*-
"""Mesh3dailaufbeschreibung — welcher Job, welcher Schritt: die Zeile eines laufenden Prozesses in der Liste „Laufende Jobs“ (Reiter „Lauf Aktuell“ auf /mesh-3D-AI/, 20.10.2026).

Edgar: „warum sind das denn ‚unbekannte Jobs‘??? Mach eine klare Liste der Jobs, ohne gaga Texte, die gerade laufen, welcher Job, welcher Schritt“. Zwei Fehler der Fassung vom 18.10.2026:
  * Gesucht wurde im GANZEN Befehl — ein GPU-Lauf startet als `mesh3dai_stimmen_lauf.py <Skript> …`, und der Starter traf die Regel „mesh3dai_stimmen“: jeder Lauf über ihn hieß
    „Die KI lernt das Skelett“ (gesehen 20.10.2026 22:44: es lief `mesh3dai_test_form_haltung.py`). Jetzt zählt das Skript, das der Starter startet (`STARTER`).
  * Skripte ohne Regel hießen „Unbekannter Lauf (…)“ (`mesh3dai_schnitt_katalogdaten.py`, `mesh3dai_nachstellen_lauf.py`). Die Regeln decken jetzt alle Skripte der Ketten in
    `ProjektTemp/_wegwerf/*.sh`; ein Skript ohne Regel steht mit seinem Namen ohne „mesh3dai_“ da, und das Log nennt es einmal.
Der Job kommt aus den Argumenten (`--jobs`, `--figur`, `--nur` … und frei stehende Namen) gegen die Namen der Jobs und Testfiguren; nichts gefunden heißt „alle Jobs“.

    Mesh3dailaufbeschreibung.beschreiben(job, Mesh3dailaufbeschreibung.namen()) -> {art, titel, fortschritt_art, skript_echt, job_text, job_titel, job_adresse, wartet_gpu}
"""

import json
import logging
import threading
import time

logger = logging.getLogger('core')

__all__ = ['Mesh3dailaufbeschreibung']


class Mesh3dailaufbeschreibung:
    #: Starter, die ein anderes Skript unter der GPU-Sperre starten: das erste `*.py` ihrer Argumente, sonst ihr fester Lauf.
    STARTER = {'mesh3dai_stimmen_lauf.py': 'mesh3dai_stimmen_netz.py', 'mesh3dai_test_lauf.py': 'mesh3dai_test_rechnen.py'}
    #: (Teil des Skriptnamens bzw. der Argumente, Art, Schritt in wenigen Worten, Fortschritt) — die erste passende Zeile gilt, darum das Genauere vor dem Allgemeinen.
    #: Fortschritt: `training` = Durchgang aus dem Laufordner, `daten` = Proben der Formvarianten (`Mesh3dailaufaktuell`).
    REGELN = (
        ('form2_kurz30', 'Probe', 'Körperform kurz trainieren (30 Durchgänge)', 'training'),
        ('formtraining_netz_messen', 'Probe', 'Zeit je Trainingsschritt messen', None),
        ('form2_tempo_probe', 'Probe', 'Tempo des Formtrainings messen', 'training'),
        ('tempoprobe', 'Probe', 'Schnellen Weg in die Grundhaltung prüfen', None),
        ('gpu_sperre', 'Warten', 'Wartet auf die Grafikkarte', None),
        ('mesh3dai_rechnen', 'Lauf', 'Rechnen per Knopf: alle Schritte eines Tests', None),          # 23.10.2026, `Mesh3dairechenlauf` (Arbeitsprozess `manage.py mesh3dai_rechnen`)
        # Kleider und Haar
        ('mesh3dai_stufe2_alle', 'Training', 'KI lernt Kleider, Haar und Haut an allen Tripo-Jobs, danach die Testjobs', None),
        ('mesh3dai_stufe2_lauf', 'Training', 'KI lernt Kleider, Haar und Haut an diesem Job', None),
        ('mesh3dai_nachstellen_lauf', 'Kleider', 'Schnittmuster an das ausgeschnittene Stück anpassen', None),
        ('mesh3dai_flaeche_lauf', 'Kleider', 'Schnitt aus der Fläche: Teile flachlegen, nähen und drapieren', None),
        ('mesh3dai_schnitt_katalogdaten', 'Daten', 'Schnittmuster-Beispiele aus dem Katalog nähen', None),
        ('mesh3dai_schnitt_daten_aussortieren', 'Daten', 'Schnittmuster-Beispiele aussortieren', None),
        ('mesh3dai_schnitt_daten', 'Daten', 'Schnittmuster-Beispiele nähen', None),
        ('mesh3dai_schnitt_training', 'Training', 'KI lernt Schnittmuster', None),
        ('mesh3dai_schnitt_anwenden', 'Kleider', 'Schnittmuster nähen und anziehen', None),
        ('mesh3dai_schnitt_waehlen', 'Kleider', 'Schnittmuster wählen', None),
        ('mesh3dai_schnitt_regelwahl', 'Kleider', 'Schnittmuster nach Regeln wählen', None),
        ('mesh3dai_schnittvergleich', 'Vergleich', 'Schnittmuster auf drei Wegen vergleichen', None),
        ('mesh3dai_zerlegung_training', 'Training', 'KI lernt Kleider und Haar erkennen', None),
        ('mesh3dai_zerlegung_arten', 'Daten', 'Kleiderarten der Trainingsfiguren festhalten', None),
        ('mesh3dai_kleidervarianten', 'Daten', 'Trainingsfiguren in neuen Kleidern anlegen', None),
        ('mesh3dai_haarkatalog', 'Daten', 'Frisuren der Garderobe vermessen', None),
        ('mesh3dai_probenzerlegung', 'Kleider', 'Kleider und Haar erkennen', None),
        ('mesh3dai_kostuem_lauf', 'Kostüme', 'Kostüm erkennen, ausschneiden, auf die Figur legen und prüfen', None),
        ('mesh3dai_kopfangleich_lauf', 'Form', 'Kopf an das Mesh angleichen: Gesichtsmaße und Haut, in Runden', None),          # 24.10.2026, `Kopfangleich`
        ('mesh3dai_kostuem_segmentierung', 'Kostüme', 'Bildmodelle zerlegen das Netz (Sapiens2, SAM 3)', None),
        ('mesh3dai_kostuem_einpassen', 'Kostüme', 'Körper der KI ins Kostüm einpassen (Variante C)', None),
        ('mesh3dai_kostuem_sichtbar', 'Kostüme', 'Körper-KI sieht nur sichtbaren Körper (Variante B)', None),
        ('mesh3dai_kikleider_proben', 'Kleider', 'Figur bauen, Kleider ausschneiden und anziehen', None),
        ('mesh3dai_kleider_zerlegung', 'Kleider', 'Kleider und Haar erkennen', None),
        ('mesh3dai_kikleider', 'Kleider', 'Kleider ausschneiden und anziehen', None),
        ('mesh3dai_kleider.py', 'Kleider', 'Kleider aus Katalog und Mesh-3D-Lauf', None),
        # Künstliche Tripo-Netze und Tripo-Jobs
        ('mesh3dai_bild3d_bilder', 'Daten', 'Bilder für künstliche Tripo-Netze rendern', None),
        ('mesh3dai_bild3d_auswahl', 'Daten', 'Posen für künstliche Tripo-Netze wählen', None),
        ('mesh3dai_bild3d_netz', 'Daten', 'Künstliche Tripo-Netze rechnen', None),
        ('mesh3dai_bild3d_wolke', 'Daten', 'Trainingswolken aus künstlichen Tripo-Netzen', None),
        ('mesh3dai_bild3d', 'Daten', 'Künstliche Tripo-Netze', None),
        ('mesh3dai_paar_wolke', 'Daten', 'Trainingswolke aus dem Tripo-Netz', None),
        ('mesh3dai_paar_mesh3d', 'Testfigur', 'Mesh-3D-Lauf für das Tripo-Netz', None),
        ('mesh3dai_paar_messen', 'Prüfung', 'Gegen die Wahrheit messen', None),
        ('mesh3dai_paar_job', 'Daten', 'Tripo-Job anlegen', None),
        ('mesh3dai_paar_lauf', 'Testfigur', 'Tripo-Job rechnen', None),
        ('mesh3dai_paar_ziel', 'Daten', 'Ziel des Tripo-Jobs bauen', None),
        ('mesh3dai_paar_mia', 'Daten', 'Tripo-Netz riggen (MIA)', None),
        ('mesh3dai_pruefsatz_entscheiden', 'Prüfung', 'Neue KI übernehmen oder nicht', None),
        ('mesh3dai_pruefsatz', 'Prüfung', 'Tripo-Jobs gegen die Wahrheit messen', None),
        # Vorstufe, Körperform, Skelett
        ('mesh3dai_vorstufe_glieder_daten', 'Daten', 'Trainingsdaten nachbessern (Arme, Beine)', None),
        ('mesh3dai_vorstufe_mia_daten_lauf', 'Daten', 'Trainingsfiguren in die Grundhaltung bringen', 'daten'),
        ('mesh3dai_vorstufe_formen_daten', 'Daten', 'Formvarianten in die Grundhaltung bringen', None),
        ('mesh3dai_vorstufe_daten', 'Daten', 'Trainingsdaten der Vorstufe', None),
        ('mesh3dai_vorstufe_form', 'Training', 'KI lernt die Körperform', 'training'),
        ('mesh3dai_vorstufe_training', 'Training', 'KI lernt das Skelett in der Grundhaltung', 'training'),
        ('mesh3dai_vorstufe_netz', 'Training', 'KI lernt das Skelett in der Grundhaltung', 'training'),
        ('mesh3dai_vorstufe.py', 'Testfigur', 'Testmodell riggen und in die Grundhaltung bringen', None),
        ('mesh3dai_form2_entscheiden', 'Prüfung', 'Neuen Formkopf übernehmen oder nicht', None),
        ('mesh3dai_kopffehler_messen', 'Prüfung', 'Kopf und Körper der KI messen', None),
        ('mesh3dai_form_pruefen', 'Prüfung', 'Körperform prüfen', None),
        ('mesh3dai_form_vergleich', 'Prüfung', 'Formläufe vergleichen', None),
        ('mesh3dai_form_alle', 'Training', 'KI lernt die Körperform', 'training'),
        ('mesh3dai_formfigur', 'Testfigur', 'Vorhergesagte Figur bauen', None),
        ('mesh3dai_formen_kette', 'Daten', 'Formvarianten bauen und posieren', None),
        ('mesh3dai_formvarianten', 'Daten', 'Formvarianten anlegen', None),
        ('mesh3dai_formregler', 'Daten', 'Wirkung der Formregler messen', None),
        ('mesh3dai_mia_stapel', 'Daten', 'Figuren riggen (MIA)', None),
        # Testfiguren
        ('mesh3dai_test_form_haltung', 'Testfigur', 'Figur in die Haltung der KI stellen', None),
        ('mesh3dai_test_form_apose', 'Testfigur', 'Testfigur in die Grundhaltung bringen', None),
        ('mesh3dai_test_form', 'Testfigur', 'Körperform der Testfiguren vorhersagen', None),
        ('mesh3dai_test_rechnen', 'Testfigur', 'Testfiguren mit der KI rechnen', None),
        ('mesh3dai_test', 'Testfigur', 'Testfiguren mit der KI rechnen', None),
        # Netz auf Posen
        ('mesh3dai_stimmen_alle', 'Training', 'KI lernt das Skelett (alle Jobs)', 'training'),
        ('mesh3dai_stimmen_netz', 'Training', 'KI lernt das Skelett', 'training'),
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
        from .mesh3daiattrappe import Mesh3daiattrappe
        from .mesh3daitest import Mesh3daitest

        aus = {}
        for s in Mesh3daiattrappe.stammdaten():
            eintrag = (s['name'], '/mesh-3D-AI/%s/' % s['id'], 'job')
            for k in (s.get('id'), s.get('name'), s.get('ordner'), s.get('modell')):
                if k:
                    aus.setdefault(str(k).lower(), eintrag)
        ordner = Mesh3daitest.ordner()
        for p in sorted(ordner.iterdir()) if ordner.is_dir() else ():
            if not (p / 'test.json').is_file():
                continue
            try:
                name = json.loads((p / 'test.json').read_text(encoding='utf-8')).get('name') or p.name
            except (OSError, ValueError):
                name = p.name
            aus.setdefault(p.name.lower(), (str(name), '/mesh-3D-AI/test/%s/' % p.name, 'test'))
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
                logger.warning('Mesh3dailaufbeschreibung: keine Regel für %s — Zeile in REGELN nachtragen', skript)
            stamm = skript[:-3] if skript.endswith('.py') else skript
            regel = (None, 'Lauf', stamm.removeprefix('mesh3dai_').replace('_', ' '), None)
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

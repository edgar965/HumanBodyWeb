# -*- coding: utf-8 -*-
"""Architekturmeshgenesis — die Daten der Seite Hilfe → Architektur → Mesh-Genesis (16.10.2026).

Edgar: „Mach erstmal einen Plan des Netzes, ich bin Entwickler und möchte alles verstehen … Mach eine Seite Hilfe - Architektur - Mesh-Genesis, wo du das Netz beschreibst, Eingabe, Netz, wieviele Neuronen,
wieviele Schichten, welcher Netztyp, dann rechts die Genesis-Regler; schreibe deine Vorgehensweise darunter … Darunter auch die Kleider-Morphs, Entscheidungen welche Kleidertypen oder ob Sapiens-Kleider".
Abends: „passe auch /hilfe/architektur/mesh-genesis/ an, die ganze Seite mit dem aktuellen Stand“ — dazu Vorstufe Rig-Generierung (`…vorstufe`), Formkopf (`…form`), Testnetze (`…testnetze`),
Köpfe am selben Rückgrat (`Architekturmeshgenesisplan.koepfe`, auch die Frage nach einem eigenen Kleidernetz).
Die Teile kommen aus eigenen Klassen. Scheitert ein Teil, steht sein Grund als Befund oben und die übrigen bleiben ganz.
Bezugslauf = der jüngste Lauf mit Formkopf (`Architekturmeshgenesisform.lauf()`, liegt unter `_diagnose`), sonst der jüngste Lauf der Jobseite von Ursula1 (`Meshgenesisdaten.lauf`).
"""

import logging

from .architekturmeshgenesisbild import Architekturmeshgenesisbild
from .architekturmeshgenesisergebnis import Architekturmeshgenesisergebnis
from .architekturmeshgenesisform import Architekturmeshgenesisform
from .architekturmeshgenesisformvergleich import Architekturmeshgenesisformvergleich
from .architekturmeshgenesisgarmentcode import Architekturmeshgenesisgarmentcode
from .architekturmeshgenesiskarte import Architekturmeshgenesiskarte
from .architekturmeshgenesiskette import Architekturmeshgenesiskette
from .architekturmeshgenesiskis import Architekturmeshgenesiskis
from .architekturmeshgenesiskopf import Architekturmeshgenesiskopf
from .architekturmeshgenesisrechenlauf import Architekturmeshgenesisrechenlauf
from .architekturmeshgenesisgrenzen import Architekturmeshgenesisgrenzen
from .architekturmeshgenesisgroesse import Architekturmeshgenesisgroesse
from .architekturmeshgenesiskleider import Architekturmeshgenesiskleider
from .architekturmeshgenesismia import Architekturmeshgenesismia
from .meshgenesisaposewahl import Meshgenesisaposewahl
from .architekturmeshgenesisnetz import Architekturmeshgenesisnetz
from .architekturmeshgenesisplan import Architekturmeshgenesisplan
from .architekturmeshgenesisregler import Architekturmeshgenesisregler
from .architekturmeshgenesisschicht import Architekturmeshgenesisschicht
from .architekturmeshgenesistestnetze import Architekturmeshgenesistestnetze
from .architekturmeshgenesisvorgehen import Architekturmeshgenesisvorgehen
from .architekturmeshgenesisvorstufe import Architekturmeshgenesisvorstufe

logger = logging.getLogger('core')

__all__ = ['Architekturmeshgenesis']


class Architekturmeshgenesis:
    JOB = 'ursula1'

    @classmethod
    def kontext(cls):
        from .meshgenesisattrappe import Meshgenesisattrappe
        from .meshgenesisdaten import Meshgenesisdaten
        from .meshgenesisdatensatz import Meshgenesisdatensatz

        befunde = []

        def teil(name, rechnung):
            try:
                return rechnung()
            except Exception as fehler:     # noqa: BLE001 - ein Teil darf die Seite nicht mitnehmen; der Grund steht auf der Seite und im Log
                logger.exception('Hilfe Mesh-Genesis: Teil %s', name)
                befunde.append('%s: %s: %s' % (name, type(fehler).__name__, fehler))
                return None

        stammdaten = Meshgenesisattrappe.stammdaten()
        job = next(j for j in stammdaten if j['id'] == cls.JOB)
        ordner = Meshgenesisdatensatz.ordner(job['ordner'])
        form_lauf = teil('Formlauf', Architekturmeshgenesisform.lauf)
        lauf = form_lauf or Meshgenesisdaten.lauf(job['ordner'])
        ergebnis = Architekturmeshgenesisnetz.lauf_lesen(lauf) if lauf else None
        form_regler = teil('Formregler', lambda: Architekturmeshgenesisform.regler(form_lauf))
        regler = teil('Regler', lambda: Architekturmeshgenesisregler.kontext((form_regler or {}).get('namen')))
        if regler and regler.get('abweichung'):
            befunde.append('Regler: ' + regler['abweichung'])
        heute = Architekturmeshgenesisnetz.heute(ergebnis)
        if heute['befund']:
            befunde.append('Netz: ' + heute['befund'])
        grenzen = teil('Grenzen', lambda: Architekturmeshgenesisgrenzen.kontext(ordner))
        groesse = teil('Größe', Architekturmeshgenesisgroesse.lesen)
        jobs = teil('Jobs', lambda: Architekturmeshgenesisregler.jobs(stammdaten)) or []
        vorstufe = teil('Vorstufe', lambda: Architekturmeshgenesisvorstufe.kontext(ordner, form_lauf))
        # 17.10.2026: die Vorstufe als Kette VOR dem Netz (Edgar: „baue das ein!“) — gemessen an den Prüfposen-Jobs und den Testnetzen.
        kette = teil('Kette', lambda: Architekturmeshgenesiskette.kontext(ordner.parent))
        # 18.10.2026: der Schritt MIA gegen den alten Weg (Edgar: „schreibe einen neuen Absatz, was mit diesem MIA Schritt anders ist als davor“) und die Einstellung „Zwischenschritt A-Pose“.
        mia = teil('MIA', lambda: Architekturmeshgenesismia.kontext(ordner.parent))
        return {
            'mia': mia, 'aposewahl': teil('Einstellung A-Pose', lambda: Meshgenesisaposewahl.text(Meshgenesisaposewahl.gewaehlt())),
            'job': job, 'lauf_name': lauf.name if lauf else None,
            # „Kurz erklärt“: Bild der Schichten (mit Formkopf, wenn der Bezugslauf einen hat; unten links grau die Rig-Generierung, nicht angeschlossen) und die Läufe nebeneinander;
            # darunter Größe und Grafikspeicher (gemessen, `Architekturmeshgenesisgroesse`).
            'bild': teil('Bild', lambda: Architekturmeshgenesisbild.svg(groesse['regler'] if groesse else None, groesse, heute.get('form') or None, vorstufe, kette)), 'groesse': groesse,
            'ergebnisse': teil('Ergebnisse', lambda: Architekturmeshgenesisergebnis.zeilen(form_lauf=form_lauf)),
            'vorstufe': vorstufe, 'kette': kette,
            'netz': heute, 'koepfe': Architekturmeshgenesisplan.koepfe(heute, regler, groesse), 'regler': regler, 'jobs': jobs,
            'form_regler': form_regler, 'form_varianten': teil('Formvarianten', Architekturmeshgenesisform.varianten),
            'form_datensatz': teil('Datensatz', Architekturmeshgenesisform.datensatz), 'form_ergebnis': teil('Formergebnis', lambda: Architekturmeshgenesisform.ergebnis(form_lauf)),
            # 17.10.2026: Form in der Pose gegen auf der A-Pose-Wolke (Edgar: „BAUE das“).
            'form_vergleich': teil('Formvergleich', Architekturmeshgenesisformvergleich.lesen),
            'testnetze': teil('Testnetze', Architekturmeshgenesistestnetze.kontext),
            'grenzen': grenzen,
            'posenwahl': teil('Posenwahl', lambda: Architekturmeshgenesisplan.posenwahl(ordner)),
            'zeiten_plan': Architekturmeshgenesisplan.ZEITEN, 'hebel': Architekturmeshgenesisplan.HEBEL, 'offen': Architekturmeshgenesisplan.OFFEN,
            'posen': teil('Posen', lambda: Architekturmeshgenesisvorgehen.posen(ordner)),
            'training': Architekturmeshgenesisvorgehen.TRAINING, 'schritte': Architekturmeshgenesisvorgehen.SCHRITTE, 'befunde_weg': Architekturmeshgenesisvorgehen.BEFUNDE,
            'lauf': teil('Lauf', lambda: Architekturmeshgenesisvorgehen.lauf(lauf, ergebnis)),
            'analyse': teil('Analyse', lambda: Architekturmeshgenesisvorgehen.analyse(Meshgenesisdaten.proben(job))),
            'kleider': teil('Kleider', lambda: Architekturmeshgenesiskleider.kontext(jobs)),
            # 20.10.2026: wie die KI ein Kleidungsstück über GarmentCode baut, was gemessen wird, was fehlt (Edgar: „Kleider-GarmentCode … da ist noch ein Widerspruch drin“)
            'garmentcode': teil('Kleider-GarmentCode', Architekturmeshgenesisgarmentcode.kontext),
            # 21.10.2026: Kleider wie das Ziel — der Schichtkopf, trainiert gegen die Zielstücke (Edgar: „wie sieht die KI nicht, welches Zielstück sie bauen soll??“)
            'schicht': teil('Kleider wie das Ziel', Architekturmeshgenesisschicht.kontext),
            # 24.10.2026: Rechnen per Knopf (Schritte, Netze, Testfälle, Klassen mit Aufruf-Logik aus dem Code) und der Kopf aus der KI (Edgar: „update … mit dem genauen Code, inkl. Kopf KI“)
            'rechenlauf': teil('Rechenlauf', Architekturmeshgenesisrechenlauf.kontext),
            'kopf': teil('Kopf aus der KI', Architekturmeshgenesiskopf.kontext),
            # 24.10.2026 abends: wer wann rechnet (Übersicht) und je KI eine Grafik aus dem Steckbrief ihrer Gewichtsdatei (Edgar: „für alle KIs eine einzelne Grafik“)
            'kis': teil('Die KIs der Kette', Architekturmeshgenesiskis.kontext),
            # 26.10.2026: auf der Karte, ohne Wartepunkte, als CUDA-Graph und reproduzierbar (Edgar: „aktualisiere … mit den neuen Sachen“)
            'karte': teil('Auf der Karte', Architekturmeshgenesiskarte.kontext),
            'befunde': befunde,
        }

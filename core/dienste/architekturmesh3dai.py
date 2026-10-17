# -*- coding: utf-8 -*-
"""Architekturmesh3dai — die Daten der Seite Hilfe → Architektur → Mesh3DAI (16.10.2026).

Edgar: „Mach erstmal einen Plan des Netzes, ich bin Entwickler und möchte alles verstehen … Mach eine Seite Hilfe - Architektur - Mesh3DAI, wo du das Netz beschreibst, Eingabe, Netz, wieviele Neuronen,
wieviele Schichten, welcher Netztyp, dann rechts die Genesis-Regler; schreibe deine Vorgehensweise darunter … Darunter auch die Kleider-Morphs, Entscheidungen welche Kleidertypen oder ob Sapiens-Kleider".
Abends: „passe auch /hilfe/architektur/mesh3dai/ an, die ganze Seite mit dem aktuellen Stand“ — dazu Vorstufe Rig-Generierung (`…vorstufe`), Formkopf (`…form`), Testnetze (`…testnetze`),
Köpfe am selben Rückgrat (`Architekturmesh3daiplan.koepfe`, auch die Frage nach einem eigenen Kleidernetz).
Die Teile kommen aus eigenen Klassen. Scheitert ein Teil, steht sein Grund als Befund oben und die übrigen bleiben ganz.
Bezugslauf = der jüngste Lauf mit Formkopf (`Architekturmesh3daiform.lauf()`, liegt unter `_diagnose`), sonst der jüngste Lauf der Jobseite von Ursula1 (`Mesh3daidaten.lauf`).
"""

import logging

from .architekturmesh3daibild import Architekturmesh3daibild
from .architekturmesh3daiergebnis import Architekturmesh3daiergebnis
from .architekturmesh3daiform import Architekturmesh3daiform
from .architekturmesh3daiformvergleich import Architekturmesh3daiformvergleich
from .architekturmesh3daikette import Architekturmesh3daikette
from .architekturmesh3daigrenzen import Architekturmesh3daigrenzen
from .architekturmesh3daigroesse import Architekturmesh3daigroesse
from .architekturmesh3daikleider import Architekturmesh3daikleider
from .architekturmesh3dainetz import Architekturmesh3dainetz
from .architekturmesh3daiplan import Architekturmesh3daiplan
from .architekturmesh3dairegler import Architekturmesh3dairegler
from .architekturmesh3daitestnetze import Architekturmesh3daitestnetze
from .architekturmesh3daivorgehen import Architekturmesh3daivorgehen
from .architekturmesh3daivorstufe import Architekturmesh3daivorstufe

logger = logging.getLogger('core')

__all__ = ['Architekturmesh3dai']


class Architekturmesh3dai:
    JOB = 'ursula1'

    @classmethod
    def kontext(cls):
        from .mesh3daiattrappe import Mesh3daiattrappe
        from .mesh3daidaten import Mesh3daidaten
        from .mesh3daidatensatz import Mesh3daidatensatz

        befunde = []

        def teil(name, rechnung):
            try:
                return rechnung()
            except Exception as fehler:     # noqa: BLE001 - ein Teil darf die Seite nicht mitnehmen; der Grund steht auf der Seite und im Log
                logger.exception('Hilfe Mesh3DAI: Teil %s', name)
                befunde.append('%s: %s: %s' % (name, type(fehler).__name__, fehler))
                return None

        stammdaten = Mesh3daiattrappe.stammdaten()
        job = next(j for j in stammdaten if j['id'] == cls.JOB)
        ordner = Mesh3daidatensatz.ordner(job['ordner'])
        form_lauf = teil('Formlauf', Architekturmesh3daiform.lauf)
        lauf = form_lauf or Mesh3daidaten.lauf(job['ordner'])
        ergebnis = Architekturmesh3dainetz.lauf_lesen(lauf) if lauf else None
        form_regler = teil('Formregler', lambda: Architekturmesh3daiform.regler(form_lauf))
        regler = teil('Regler', lambda: Architekturmesh3dairegler.kontext((form_regler or {}).get('namen')))
        if regler and regler.get('abweichung'):
            befunde.append('Regler: ' + regler['abweichung'])
        heute = Architekturmesh3dainetz.heute(ergebnis)
        if heute['befund']:
            befunde.append('Netz: ' + heute['befund'])
        grenzen = teil('Grenzen', lambda: Architekturmesh3daigrenzen.kontext(ordner))
        groesse = teil('Größe', Architekturmesh3daigroesse.lesen)
        jobs = teil('Jobs', lambda: Architekturmesh3dairegler.jobs(stammdaten)) or []
        vorstufe = teil('Vorstufe', lambda: Architekturmesh3daivorstufe.kontext(ordner, form_lauf))
        # 17.10.2026: die Vorstufe als Kette VOR dem Netz (Edgar: „baue das ein!“) — gemessen an den Prüfposen-Jobs und den Testnetzen.
        kette = teil('Kette', lambda: Architekturmesh3daikette.kontext(ordner.parent))
        return {
            'job': job, 'lauf_name': lauf.name if lauf else None,
            # „Kurz erklärt“: Bild der Schichten (mit Formkopf, wenn der Bezugslauf einen hat; unten links grau die Rig-Generierung, nicht angeschlossen) und die Läufe nebeneinander;
            # darunter Größe und Grafikspeicher (gemessen, `Architekturmesh3daigroesse`).
            'bild': teil('Bild', lambda: Architekturmesh3daibild.svg(groesse['regler'] if groesse else None, groesse, heute.get('form') or None, vorstufe, kette)), 'groesse': groesse,
            'ergebnisse': teil('Ergebnisse', lambda: Architekturmesh3daiergebnis.zeilen(form_lauf=form_lauf)),
            'vorstufe': vorstufe, 'kette': kette,
            'netz': heute, 'koepfe': Architekturmesh3daiplan.koepfe(heute, regler, groesse), 'regler': regler, 'jobs': jobs,
            'form_regler': form_regler, 'form_varianten': teil('Formvarianten', Architekturmesh3daiform.varianten),
            'form_datensatz': teil('Datensatz', Architekturmesh3daiform.datensatz), 'form_ergebnis': teil('Formergebnis', lambda: Architekturmesh3daiform.ergebnis(form_lauf)),
            # 17.10.2026: Form in der Pose gegen auf der A-Pose-Wolke (Edgar: „BAUE das“).
            'form_vergleich': teil('Formvergleich', Architekturmesh3daiformvergleich.lesen),
            'testnetze': teil('Testnetze', Architekturmesh3daitestnetze.kontext),
            'grenzen': grenzen,
            'posenwahl': teil('Posenwahl', lambda: Architekturmesh3daiplan.posenwahl(ordner)),
            'zeiten_plan': Architekturmesh3daiplan.ZEITEN, 'hebel': Architekturmesh3daiplan.HEBEL, 'offen': Architekturmesh3daiplan.OFFEN,
            'posen': teil('Posen', lambda: Architekturmesh3daivorgehen.posen(ordner)),
            'training': Architekturmesh3daivorgehen.TRAINING, 'schritte': Architekturmesh3daivorgehen.SCHRITTE, 'befunde_weg': Architekturmesh3daivorgehen.BEFUNDE,
            'lauf': teil('Lauf', lambda: Architekturmesh3daivorgehen.lauf(lauf, ergebnis)),
            'analyse': teil('Analyse', lambda: Architekturmesh3daivorgehen.analyse(Mesh3daidaten.proben(job))),
            'kleider': teil('Kleider', lambda: Architekturmesh3daikleider.kontext(jobs)),
            'befunde': befunde,
        }

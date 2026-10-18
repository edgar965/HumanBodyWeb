# -*- coding: utf-8 -*-
"""Mesh3daiattrappe — die Daten der Seite „Mesh3D-AI" für „Ursula1" (14.10.2026): echte Posen am echten Rig, erfundene Flächen und eine erfundene Ausgabe des Netzes.

Edgar: „mach das Menü Dashboard – Mesh3D-AI und zeige mir den Input, gewünschten Trainingsoutput und Output, mit Dummies für Ursula1" und „ich möchte das volle Skelett mit allen Gesichts- und Handknochen".
Was ECHT ist: die 50 Posen (Retarget BVH → Genesis 9 auf der Stellung von Ursula1) und das Rig mit 138 Knochen (`Mesh3dairig`). Was ERFUNDEN ist: die Flächen (Kapseln um 22 Gelenke, Kleider, Gesicht, Hände — aus dem Rig
abgeleitet), die Eingabe-Punktwolke und die „Ausgabe des Netzes" (= Soll plus Rauschen). Nichts ist exportiert, nichts trainiert. Die Aufteilung folgt dem Plan vom 14.10.2026: 1 A-Pose (die Ruhelage), 10 Standposen und
29 Bilder aus Spagat zum Training (40; bis 14.10.2026 abends DanceKurz), dazu 10 Prüfposen aus anderen Clips (Walk, Sport, StayStill), die nie trainiert werden. Die Standposen sind Bilder aus Idle-StayStill-Clips (Ersatz für Genesis-Standposen).
Die Form der Antwort (`jobs`, `proben`, `animation`) ist die, die später die echte Seite bekommt — dann ersetzt eine Klasse mit denselben Methoden diese hier. Alles ist deterministisch (feste Zufallszahlen).

    Mesh3daiattrappe.jobs()             -> [{id, name, modell, proben, training, pruefung, status, …}]
    Mesh3daiattrappe.proben('ursula1')  -> {job, attrappe, hinweis, gelenke, rig: Beschreibung, teile: {schluessel: Beschreibung}, proben: [{id, name, quelle, aufteilung, soll, ausgabe, kennzahlen, eingabe, rig,
                                            teile: {schluessel: {soll, ausgabe, kennzahlen, eingabe, rig, …}}}], zusammenfassung} | None
    Mesh3daiattrappe.animation('ursula1') -> die Bewegung Spagat als Bilder in der Form einer Probe (`Mesh3daianimation`)
    Die Zeilen unter dem ganzen Körper (`TEILE`: nur Körper, Gesicht, Hände/Füße, Kleider) liefern je eine eigene Klasse (`Mesh3daikoerper`, `Mesh3daigesicht`, `Mesh3daihaende`, `Mesh3daikleider`).
"""

import random
from pathlib import Path

from .mesh3daigeruest import Mesh3daigeruest
from .mesh3daigesicht import Mesh3daigesicht
from .mesh3daihaende import Mesh3daihaende
from .mesh3daikleider import Mesh3daikleider
from .mesh3daikoerper import Mesh3daikoerper

__all__ = ['Mesh3daiattrappe']


class Mesh3daiattrappe:
    JOB = 'ursula1'
    NAME = 'Ursula1'
    #: Die Zeilen unter dem ganzen Körper (14.10.2026, Edgar: „… Vergleichs-Zeilen für Gesicht, Hände/Füße, Kleider“ und „NUR Körper, also ohne Kleider“), je mit eigenen Punkten, Rauschen und Kennzahlen.
    TEILE = (Mesh3daikoerper, Mesh3daigesicht, Mesh3daihaende, Mesh3daikleider)
    #: Anzahl je Art (Summe 50) und die Prüfposen je Ordner der BVH-Bibliothek: (Ordner, Zahl der Clips).
    STAND, BEWEGUNG = 10, 29
    PRUEFUNG = (('Walk', 4), ('Sport', 3), ('Idle StayStill', 3))
    STANDCLIPS = 5
    #: Die Bewegung der Trainingsposen (Edgar, 14.10.2026: „für die Posen den Spagat BVH, nicht den DanceKurz“; vorher DanceKurz.bvh). Spagat hat nur 125 Bilder, die ersten `BEWEGUNG_TRAINING` davon sind Trainingsposen,
    #: die übrigen werden nie trainiert (im Datensatz die Gruppe „spagat“, `ProjektTemp/_wegwerf/mesh3dai_ursula_lauf.py`). Setzung, nicht gemessen: ein Fünftel zurückgehalten, zusammenhängend (benachbarte Bilder sind fast gleich).
    BEWEGUNGSDATEI = ('A_Results', 'Spagat.bvh')
    BEWEGUNG_TRAINING = 100
    #: Rauschen des Dummy-„Netzes“ in m: Training klein, Prüfposen groß; Arme und Beine streuen mehr als der Rumpf.
    RAUSCHEN = {'training': 0.003, 'pruefung': 0.014}
    GRUPPENFAKTOR = {'rumpf': 1.0, 'kopf': 1.0, 'arm': 1.6, 'hand': 2.2, 'bein': 1.5, 'fuss': 2.0}
    HINWEIS = ('Die Posen sind echt (Retarget BVH → Genesis 9 auf dem Skelett von Ursula1, 138 Knochen), die Flächen, Kleider und die Ausgabe des Netzes sind erfunden. '
               'Nichts ist exportiert, nichts gerechnet, nichts trainiert — die Seite zeigt nur, wo Eingabe, gewünschte Ausgabe und Ausgabe des Netzes später stehen.')
    _ablage = {}

    # ------------------------------------------------------------------ Beschreibungen und Plan

    @classmethod
    def beschreibungen(cls):
        """`{Zeile: Beschreibung}` der Zeilen unter dem ganzen Körper — einmal je Prozess."""
        if 'beschreibungen' not in cls._ablage:
            cls._ablage['beschreibungen'] = {klasse.SCHLUESSEL: klasse.beschreibung() for klasse in cls.TEILE}
        return cls._ablage['beschreibungen']

    @staticmethod
    def bvh(*pfad):
        from django.conf import settings

        return Path(settings.OBJECTS_ROOT).joinpath('animations', 'bvh', *pfad)

    @classmethod
    def _clips(cls, ordner, von, bis):
        """Die BVH-Dateien eines Ordners in Namensreihenfolge, `[von:bis]`."""
        return sorted(p for p in cls.bvh(ordner).glob('*.bvh') if '_retarget' not in p.name)[von:bis]

    @classmethod
    def _plan(cls):
        """`[(name, quelle, aufteilung, (BVH-Datei, Bild) oder None für die Ruhelage)]` in der Reihenfolge der Proben."""
        from .mesh3dairig import Mesh3dairig

        zufall = random.Random(2026)
        plan = [('A-Pose', 'Genesis A-Pose (Ruhelage)', 'training', None)]
        stand = cls._clips('Idle StayStill', 0, cls.STANDCLIPS)
        for i in range(cls.STAND):
            datei = stand[i % len(stand)]
            plan.append(('Stand %02d' % (i + 1), 'Idle StayStill/%s (Ersatz für eine Genesis-Standpose)' % datei.name, 'training', (datei, zufall.randrange(Mesh3dairig.bewegung(datei)[0]))))
        bewegung = cls.bvh(*cls.BEWEGUNGSDATEI)
        anzahl = min(Mesh3dairig.bewegung(bewegung)[0], cls.BEWEGUNG_TRAINING)
        plan += [('%s Bild %d' % (bewegung.stem, b + 1), '%s.bvh' % bewegung.stem, 'training', (bewegung, b)) for b in sorted(zufall.sample(range(anzahl), cls.BEWEGUNG))]
        for ordner, zahl in cls.PRUEFUNG:
            dateien = cls._clips(ordner, -zahl, None) if ordner == 'Idle StayStill' else cls._clips(ordner, 0, zahl)
            for datei in dateien:
                b = zufall.randrange(Mesh3dairig.bewegung(datei)[0])
                plan.append(('%s %s Bild %d' % (ordner.replace('Idle ', ''), datei.stem, b), '%s/%s' % (ordner, datei.name), 'pruefung', (datei, b)))
        return plan

    # ------------------------------------------------------------------ Schnittstelle

    #: Die Jobs: `modell` = das Genesis-Modell (Rig, Häutung), `ordner` = der Datensatz unter `3DObjects/mesh3dai/` (Proben, Läufe, Anzeigenetz). Ursula_Pose1 (15.10.2026, Edgar: „mache einen neuen Job
    #: Ursula_Pose1 … obj file für Ursula einer komplizierten Spagat Pose, und trainiere damit") ist dasselbe Modell mit eigenem Datensatz: Probe 1 = Spagat Bild 47 als OBJ-Datei
    #: (`ProjektTemp/_wegwerf/mesh3dai_pose1_bauen.py`), die übrigen Proben die von Ursula1.
    #: `geschlecht` (16.10.2026 abends, Edgar: „ganz oben im Testjob soll die Einstellung änderbar sein, ob es weiblich oder männlich ist“): welche Figuren ein Test als Ausgabe nehmen darf (`Mesh3daitest`).
    STAMMDATEN = ({'id': 'ursula1', 'name': 'Ursula1', 'modell': 'Ursula1', 'ordner': 'Ursula1', 'geschlecht': 'weiblich'},
                  {'id': 'ursula_pose1', 'name': 'Ursula_Pose1', 'modell': 'Ursula1', 'ordner': 'Ursula_Pose1', 'geschlecht': 'weiblich'},
                  # 16.10.2026, Edgar: „Erstelle 3 neue Trainingsjobs: Damira0, Mann1 und Matt0 … trainier das Netz auf alle" (Datensatz `ProjektTemp/_wegwerf/mesh3dai_modell_kette.py`).
                  {'id': 'damira0', 'name': 'Damira0', 'modell': 'Damira0', 'ordner': 'Damira0', 'geschlecht': 'weiblich'},
                  {'id': 'mann1', 'name': 'Mann1', 'modell': 'Mann1', 'ordner': 'Mann1', 'geschlecht': 'maennlich'},
                  {'id': 'matt0', 'name': 'Matt0', 'modell': 'Matt0', 'ordner': 'Matt0', 'geschlecht': 'maennlich'},
                  # 16.10.2026, Edgar: „Erstelle ein Training UrsulaSpagat, wo du die Ursula 1 in eine komplizierte Spagatposition bringst" — Probe 1 Standspagat (Prüfpose), 2–191 = Ursula1
                  # (`ProjektTemp/_wegwerf/mesh3dai_spagat_bauen.py`).
                  {'id': 'ursulaspagat', 'name': 'UrsulaSpagat', 'modell': 'Ursula1', 'ordner': 'UrsulaSpagat', 'geschlecht': 'weiblich'},
                  # 16.10.2026 nachts, Edgar: „mach jetzt noch 3 weitere Posen mit Damira0: sitzen, Matt0 in liegen, und Mann1 beim Laufen und trainiere" — Probe 1 je eine Prüfpose als OBJ,
                  # 2–66 = der Grundjob (`ProjektTemp/_wegwerf/mesh3dai_neupose_bauen.py`).
                  {'id': 'damirasitzen', 'name': 'DamiraSitzen', 'modell': 'Damira0', 'ordner': 'DamiraSitzen', 'geschlecht': 'weiblich'},
                  {'id': 'mattliegen', 'name': 'MattLiegen', 'modell': 'Matt0', 'ordner': 'MattLiegen', 'geschlecht': 'maennlich'},
                  {'id': 'mannlaufen', 'name': 'MannLaufen', 'modell': 'Mann1', 'ordner': 'MannLaufen', 'geschlecht': 'maennlich'})

    @classmethod
    def stammdaten(cls):
        """`[{id, name, modell, ordner}]` — nur, wer die Jobs ist. Billig: das Menü der Seitenleiste fragt es auf JEDER Seite der Anwendung (`Mesh3daimenue`), `jobs()` liest dafür erst den Plan (BVH-Dateien).
        Dazu die gebauten Trainingspaare (18.10.2026 abends, `Mesh3daipaare`: Tripo-Netz + Genesis-Export, Marke `paar.json` im Jobordner)."""
        from .mesh3daipaare import Mesh3daipaare

        feste = [dict(s) for s in cls.STAMMDATEN]
        ids = {s['id'] for s in feste}
        return feste + [p for p in Mesh3daipaare.stammdaten() if p['id'] not in ids]

    @classmethod
    def jobs(cls):
        plan = cls._plan_gemerkt()
        return [dict(s, proben=len(plan), training=sum(1 for p in plan if p[2] == 'training'), pruefung=sum(1 for p in plan if p[2] == 'pruefung'),
                     status='Attrappe', hinweis=cls.HINWEIS) for s in cls.stammdaten()]

    @classmethod
    def job(cls, kennung):
        """Die Zeile eines Jobs aus `jobs()` — ohne Rücksicht auf Groß- und Kleinschreibung der Kennung; `None`, wenn es ihn nicht gibt."""
        return next((j for j in cls.jobs() if j['id'] == str(kennung).lower()), None)

    @classmethod
    def _plan_gemerkt(cls):
        if 'plan' not in cls._ablage:
            cls._ablage['plan'] = cls._plan()
        return cls._ablage['plan']

    @classmethod
    def proben(cls, job):
        if job != cls.JOB:
            return None
        if 'proben' in cls._ablage:
            return cls._ablage['proben']
        from .mesh3daibild import Mesh3daibild
        from .mesh3dairausch import Mesh3dairausch
        from .mesh3dairig import Mesh3dairig

        proben = []
        for i, (name, quelle, aufteilung, ort) in enumerate(cls._plan_gemerkt()):
            roh = Mesh3dairig.ruhe() if ort is None else Mesh3dairig.bewegung(ort[0])[1](ort[1])
            pose, _p = Mesh3dairig.ausrichten(roh)
            proben.append({'id': i + 1, 'name': name, 'quelle': quelle, 'aufteilung': aufteilung, **Mesh3daibild.bauen(pose, aufteilung, Mesh3dairausch(1000 + i))})
        cls._ablage['proben'] = {'job': cls.JOB, 'attrappe': True, 'hinweis': cls.HINWEIS, 'gelenke': Mesh3daigeruest.beschreibung(), 'rig': Mesh3dairig.beschreibung(),
                                 'teile': cls.beschreibungen(), 'proben': proben, 'zusammenfassung': cls._zusammenfassung(proben)}
        return cls._ablage['proben']

    @classmethod
    def animation(cls, job):
        """Die Standardanimation (Spagat) als Bilder in der Form einer Probe — `Mesh3daianimation`; `None` bei einem unbekannten Job."""
        if job != cls.JOB:
            return None
        from .mesh3daianimation import Mesh3daianimation

        return Mesh3daianimation.bilder()

    @staticmethod
    def _zusammenfassung(proben):
        def mittel(art):
            werte = [p['kennzahlen']['mittel_mm'] for p in proben if p['aufteilung'] == art]
            return round(sum(werte) / len(werte), 1) if werte else None
        return {'training_mittel_mm': mittel('training'), 'pruefung_mittel_mm': mittel('pruefung')}

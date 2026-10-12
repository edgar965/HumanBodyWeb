# -*- coding: utf-8 -*-
"""Architekturmeshto3dklassen — das Klassenmodell von „Mesh to 3D": Gruppen, Klassen, Beziehungen (Reiter „MeshTo3D", 11.10.2026).

Die LISTE der Klassen steht hier von Hand (`GRUPPEN`); Datei, Zeilenzahl, Aufgabe (erster Satz des Modul-Docstrings) und öffentliche Methoden liest
`Architektur2d3dklassen.zeile` beim Aufruf der Seite aus dem Code — fehlt eine Datei oder Klasse, steht es als Befund auf der Seite. Die Beziehungen kommen aus zwei Quellen:
`BEZIEHUNGEN` (von Hand beschriftet: wer ruft wen womit, auch über die Grenze der Prozesse, wo es kein `import` gibt) und `importiert()` (aus den Anweisungen `import` und
`from … import` der Dateien gelesen — so fehlt keine Kante und keine ist erfunden). Das Modell der Karten baut `Architektur2d3dwerkzeuge.modell`, das auch der Reiter „Tools" benutzt.
"""

import ast
import logging
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmeshto3dklassen']

logger = logging.getLogger('core')


class Architekturmeshto3dklassen:
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    M = 'meshto3d/'
    G = 'Genesis9/'

    #: (Kennung, Titel, Hinweis, [(Rolle, [(Datei, Klasse), …]), …]) — die Rolle erscheint als „beteiligt an" in den Karten.
    GRUPPEN = [
        ('eingang', 'Eingang, Auftrag, Ablage', 'Django (python14): Netz und Optionen annehmen, den Auftrag führen, die Dateien ablegen', [
            ('Auftrag anlegen und starten', [(A + 'meshfigur.py', 'Meshfigurendpunkte'), (A + 'meshfigureinstellungen.py', 'Meshfigureinstellungen'),
                                             (D + 'meshfigureingang.py', 'Meshfigureingang'), ('HumanBodyWeb/core/models/meshfigurauftrag.py', 'Meshfigurauftrag'),
                                             ('HumanBodyWeb/core/daten/meshfigurablage.py', 'Meshfigurablage'), (D + 'meshfigurtabelle.py', 'Meshfigurtabelle')]),
            ('Optionen', [(D + 'meshfiguroptionen.py', 'Meshfiguroptionen'), (D + 'meshfigurtexturoptionen.py', 'Meshfigurtexturoptionen'),
                          (D + 'meshfigurkleidungsoptionen.py', 'Meshfigurkleidungsoptionen'), (D + 'meshfigurregionenoptionen.py', 'Meshfigurregionenoptionen')])]),
        ('lauf', 'Lauf und Prozess', 'Django (python14): der abgelöste Prozess, die Schrittfolge, die Brücke zum Runner', [
            ('Lauf führen', [(D + 'meshfigurarbeiter.py', 'Meshfigurarbeiter'), (D + 'meshfigurlauf.py', 'Meshfigurlauf'),
                             ('HumanBodyWeb/core/pipeline_process.py', 'PipelineProzess')]),
            ('Runner-Schritt rechnen (ein Prozess für alle Schritte, 12.10.2026)', [(D + 'meshfigurrunnerbahn.py', 'Meshfigurrunnerbahn'), (D + 'meshfigurdauerprozess.py', 'Meshfigurdauerprozess')]),
            ('Nebenläufe: haar, kleidung, frisur als Fäden', [(D + 'meshfigurnebenlauf.py', 'Meshfigurnebenlauf')])]),
        ('schritte', 'Schritte auf der python14-Seite', 'Genesis 9 echt rechnen, ablegen, backen, speichern', [
            ('haar, kleidung', [(D + 'meshfigurhaar.py', 'Meshfigurhaar'), (D + 'meshfigurkleidung.py', 'Meshfigurkleidung'),
                                       (D + 'meshfigurkleidungsruhelage.py', 'Meshfigurkleidungsruhelage')]),
            ('koerper, gesicht', [(D + 'meshfigurkette.py', 'Meshfigurkette'), (D + 'meshfigurregler.py', 'Meshfigurregler'), (D + 'meshfigurgenesis.py', 'Meshfigurgenesis')]),
            ('rest, textur', [(D + 'meshfigurende.py', 'Meshfigurende'), (D + 'meshfiguraugenhoehle.py', 'Meshfiguraugenhoehle'), (D + 'meshfigurlandmarkmorphe.py', 'Meshfigurlandmarkmorphe'),
                              (D + 'meshfigurtexelpruefung.py', 'Meshfigurtexelpruefung'), (D + 'meshfiguraugenbild.py', 'Meshfiguraugenbild')]),
            ('vorschau, frisur, speichern', [(D + 'meshfigurvorschau.py', 'Meshfigurvorschau'), (D + 'meshfigurschammessung.py', 'Meshfigurschammessung'), (D + 'meshfigurfrisur.py', 'Meshfigurfrisur'),
                                             (D + 'meshfigurfrisurstueck.py', 'Meshfigurfrisurstueck'), (D + 'meshfigurfrisurdeltas.py', 'Meshfigurfrisurdeltas'),
                                             (D + 'meshfigurspeichern.py', 'Meshfigurspeichern')])]),
        ('runner', 'Runner und Registrierung', 'python10 (GPU): ein Schritt je Aufruf von _run_meshfigur.py; Regler und Haltung stellen', [
            ('Registrierung', [(M + '_run_meshfigur.py', 'Meshfigurrunner'), (M + 'meshfigur_daten.py', 'Meshfigurdaten'), (M + 'meshfigur_registrierung.py', 'Meshfigurregistrierung'),
                               (M + 'meshfigur_registrierungruhe.py', 'Meshfigurregistrierungruhe'), (M + 'meshfigur_runnertextur.py', 'Meshfigurrunnertextur'), (M + 'meshfigur_abstandstoff.py', 'Meshfigurabstandstoff'),
                               (M + 'meshfigur_modell.py', 'Meshfigurmodell'), (M + 'meshfigur_kinematik.py', 'Meshfigurkinematik'), (M + 'meshfigur_abstand.py', 'Meshfigurabstand'),
                               (M + 'meshfigur_landmarken.py', 'Meshfigurlandmarken'), (M + 'meshfigur_rumpfpruefung.py', 'Meshfigurrumpfpruefung'),
                               (M + 'meshfigur_stufenlauf.py', 'Meshfigurstufenlauf'), (M + 'meshfigur_massterm.py', 'Meshfigurmassterm')]),
            ('Dauerprozess und Ablagen (12.10.2026)', [(M + 'meshfigur_dauerlauf.py', 'Meshfigurdauerlauf'), (M + 'meshfigur_datenablage.py', 'Meshfigurdatenablage'),
                                                       (M + 'meshfigur_scanablage.py', 'Meshfigurscanablage'), (M + 'meshfigur_ablegen.py', 'Meshfigurablegen'),
                                                       (M + 'meshfigur_gpusuche.py', 'Meshfigurgpusuche')])]),
        ('erkennung', 'Erkennung', 'python10: das Netz laden, ausrichten, Landmarken in 3D, Bilder für die Seite', [
            ('erkennung, kalibrierung', [(M + 'meshfigur_erkennungsschritt.py', 'Meshfigurerkennungsschritt'), (M + 'meshfigur_scan.py', 'Meshfigurscan'),
                                         (M + 'meshfigur_erkennung.py', 'Meshfigurerkennung'), (M + 'meshfigur_ansichten.py', 'Meshfiguransichten'), (M + 'meshfigur_punkte.py', 'Meshfigurpunkte'),
                                         (M + 'meshfigur_triangulation.py', 'Meshfigurtriangulation'), (M + 'meshfigur_landmarkenflaeche.py', 'Meshfigurlandmarkenflaeche'),
                                         (M + 'meshfigur_uebersicht.py', 'Meshfiguruebersicht'), (M + 'meshfigur_vergleichsbild.py', 'Meshfigurvergleichsbild')])]),
        ('kopf', 'Eigenes Kopfnetz', 'python10: ein zweites Netz für den Kopf finden, an den Körper legen, Farbe angleichen, nähen', [
            ('Kopfnetz', [(M + 'meshfigur_kopfnetz.py', 'Meshfigurkopfnetz'), (M + 'meshfigur_kopfabgleich.py', 'Meshfigurkopfabgleich'), (M + 'meshfigur_zielnetz.py', 'Meshfigurzielnetz'),
                          (M + 'meshfigur_farbangleich.py', 'Meshfigurfarbangleich'), (M + 'meshfigur_naht.py', 'Meshfigurnaht')])]),
        ('haut', 'Haut, Farbe, Textur', 'python10: welche Netzfläche Haut ist, welche Farbe sie hat, Licht und Iris', [
            ('Hautmodell', [(M + 'meshfigur_hautmodell.py', 'Meshfigurhautmodell'), (M + 'meshfigur_hautkarte.py', 'Meshfigurhautkarte'), (M + 'meshfigur_hautteilung.py', 'Meshfigurhautteilung'),
                            (M + 'meshfigur_hautbaender.py', 'Meshfigurhautbaender')]),
            ('Textur', [(M + 'meshfigur_textur.py', 'Meshfigurtextur'), (M + 'meshfigur_entlichtung.py', 'Meshfigurentlichtung'), (M + 'meshfigur_iris.py', 'Meshfiguriris')])]),
        ('genesis', 'Genesis 9 (Paket Genesis9)', 'Die Figur-Seite: Bereiche, Landmarkentabelle, Ableitung der Regler, Eigenmorph, Backen', [
            ('Figur', [(G + 'netzbereiche.py', 'G9netzbereiche'), (G + 'netzlandmarken.py', 'G9netzlandmarken'), (G + 'netzlandmarkensam.py', 'G9netzlandmarkensam'), (G + 'figurglb.py', 'G9figurglb'),
                       (G + 'reglerableitung.py', 'G9reglerableitung'), (G + 'restmorph.py', 'G9restmorph'), (G + 'eigenmorphe.py', 'G9eigenmorphe'),
                       (G + 'texturbacken.py', 'G9texturbacken'), (G + 'teileablage.py', 'G9teileablage'), (G + 'zeileneindeutig.py', 'G9zeileneindeutig')])]),
        ('verwender', 'Wer Mesh to 3D benutzt', 'Der Blender-Import und „2D3D Kleider" setzen den Lauf ein', [
            ('Blender-Import, Schritt figur', [(D + 'blendimportfigur.py', 'Blendimportfigur'), (D + 'blendimportkoerper.py', 'Blendimportkoerper')]),
            ('2D3D Kleider, Schritt koerper', [(D + 'engine2d3dkleiderkoerper.py', 'Engine2d3dKleiderkoerper'), (D + 'engine2d3dkleiderkoerperlauf.py', 'Engine2d3dKleiderkoerperlauf')])]),
    ]

    #: (von, 'ruft', nach, womit) — beschriftet, gegen den Code gelesen (Werkzeugtabelle „Mesh to 3D", 03.10.2026, und Meshfigurlauf, 11.10.2026); über die Prozessgrenze ohne `import`.
    BEZIEHUNGEN = [
        ('Meshfigurendpunkte', 'ruft', 'Meshfigurarbeiter', 'starten(job, ab): eigener Prozess manage.py meshfigur_fahren'),
        ('Meshfigurarbeiter', 'ruft', 'Meshfigurlauf', 'meshfigur_fahren: Meshfigurlauf(id).ausfuehren(ab)'),
        ('Meshfigurlauf', 'ruft', 'Meshfigurrunnerbahn', 'runner(schritt, runde): Befehl, Zeilen deuten, Ergebnis oder Fehler zurückgeben'),
        ('Meshfigurrunnerbahn', 'ruft', 'Meshfigurdauerprozess', 'rechnen(befehl, auftrag, schritt, runde): EIN python10-Prozess für alle Schritte (MESHFIGUR_DAUER=0: einer je Schritt)'),
        ('Meshfigurdauerprozess', 'ruft', 'PipelineProzess', 'starten([python10, _run_meshfigur.py, --dauer], stdin_offen=True), senden(JSON-Zeile {auftrag, schritt, runde})'),
        ('Meshfigurrunnerbahn', 'ruft', 'PipelineProzess', 'Rückfall: starten([python10, _run_meshfigur.py, auftrag.json, schritt, runde]) je Schritt'),
        ('PipelineProzess', 'ruft', 'Meshfigurdauerlauf', 'Unterprozess python10 --dauer: Befehle von stdin, Antwort wie im Einzelaufruf plus [ende] <schritt>'),
        ('PipelineProzess', 'ruft', 'Meshfigurrunner', 'Unterprozess python10; Antwort als Zeilen [fortschritt], [ergebnis], [fehler] auf stdout'),
        ('Meshfigurdauerlauf', 'ruft', 'Meshfigurrunner', 'laufen(Meshfigurrunner): ein Schritt je Befehl, danach gc und CUDA-Speicher freigeben'),
        ('Meshfigurlauf', 'ruft', 'Meshfigurnebenlauf', 'starten/abwarten/frueh: haar, kleidung und frisur in Fäden mit einer Kopie des Auftrags'),
        ('Meshfigurende', 'ruft', 'Meshfigurnebenlauf', 'frueh(lauf, frisur): die Frisurwahl startet nach dem Runner der Textur, neben Backen und Vorschau'),
        ('Meshfigurfrisurstueck', 'ruft', 'Meshfigurfrisurdeltas', 'delta(regler): Wirkung eines Reglers bei Wert 1 direkt auf den Punkten seines Morphs'),
        ('Meshfigurgenesis', 'ruft', 'Meshfigurablegen', 'inhaltsgleiche Datei bleibt liegen (genesis_ende.npz, posiert.npy)'),
        ('Meshfigurrunner', 'ruft', 'Meshfigurablegen', 'npy(posiert.npy, array): schreibt nur bei geändertem Inhalt'),
        ('Meshfigurdaten', 'ruft', 'Meshfigurdatenablage', 'holen/ablegen: Proben, Gesichtspunkte, Hautkarte einmal je Auftrag'),
        ('Meshfigurscan', 'ruft', 'Meshfigurscanablage', 'laden(pfad): das hergerichtete Netz einmal neben die Datei legen'),
        ('Meshfigurtextur', 'ruft', 'Meshfigurgpusuche', 'naechster(orte): nächste Probe je Texel auf der GPU, Kasten-Vorauswahl'),
        ('Meshfigurregistrierung', 'ruft', 'Meshfigurstufenlauf', 'laufen(schritte, nach): ein Schritt als CUDA-Graph'),
        ('Meshfigurfrisurstueck', 'ruft', 'G9teileablage', 'über G9garderobe.teile: die Netze der Frisur als pickle'),
        ('Meshfigurlauf', 'ruft', 'Meshfigurkette', 'koerper() und gesicht()'),
        ('Meshfigurlauf', 'ruft', 'Meshfigurende', 'rest() und textur()'),
        ('Meshfigurkette', 'ruft', 'Meshfigurrunner', 'lauf.runner(koerper|gesicht|skalieren): über Meshfigurlauf'),
        ('Meshfigurende', 'ruft', 'Meshfigurrunner', 'lauf.runner(rest|textur): über Meshfigurlauf'),
        ('Meshfigurvorschau', 'ruft', 'Meshfigurrunner', 'lauf.runner(bewertung): über Meshfigurlauf'),
        ('Meshfigurvorschau', 'ruft', 'Meshfigurschammessung', 'sicher(lauf): Scham-Messung im Beckenkasten bei jedem Auftrag, Ergebnis in ergebnis.schammessung'),
        ('Meshfigurrunner', 'ruft', 'Meshfigurregistrierung', 'kette(art, runde): Stufen der Körper- und Gesichtskette'),
        ('Meshfigurrunner', 'ruft', 'Meshfigurmodell', 'Meshfigurmodell(genesis, jacobi, geraet, theta, lage)'),
        ('Meshfigurmodell', 'ruft', 'Meshfigurkinematik', 'Haltung: Hautmischung mit Daz-Winkeln'),
        ('Meshfigurkette', 'ruft', 'Meshfigurregler', 'speichern(pfad, teil, stellung) und stellung(teil, werte, alt)'),
        ('Meshfigurkette', 'ruft', 'Meshfigurgenesis', 'speichern(pfad): Käfig, Skelett, Haut, Landmarken, Gelenkkorrekturen der Haltung — je Runde ECHT gerechnet'),
        ('Meshfigurgenesis', 'ruft', 'G9netzbereiche', 'bereiche(), gesichtskern(), spiegel(): Gewichte je Käfigpunkt'),
        ('Meshfigurregler', 'ruft', 'G9reglerableitung', 'holen(satz, grund, teil): Jacobi-Matrix Regler → Punkte und Gelenke'),
        ('Meshfigurende', 'ruft', 'G9restmorph', 'ablegen(name, rest, gewicht): Eigenmorph aus dem Rest'),
        ('G9restmorph', 'ruft', 'G9eigenmorphe', 'ablegen(name, nummern, deltas, brief)'),
        ('Meshfigurende', 'ruft', 'G9texturbacken', 'Kacheln backen über der auf den Hautton getönten Daz-Haut'),
        ('Meshfigurlauf', 'ruft', 'G9netzlandmarken', '_kalibrierung(): holen(), sonst die Tabelle bauen (G9figurglb → derselbe Erkennungsweg)'),
        ('Meshfigurregistrierung', 'ruft', 'Meshfigurmassterm', 'gewicht_der(stufe), verlust(punkte), messen(punkte): Segmentlängen der Gelenkpunkte als Ziel der Größenregler (12.10.2026)'),
        ('Meshfigurstufenlauf', 'ruft', 'Meshfigurmassterm', 'verlust(gelenkpunkte) mit dem Gewicht der Stufe, im CUDA-Graph'),
        ('Meshfigurkleidung', 'ruft', 'Meshfigurkleidungsruhelage', 'objekt(): punkte(netz, dreiecke) — Kleidung mit Körperteilen und Entzerren in die Ruhelage (12.10.2026)'),
        ('Meshfigurdaten', 'ruft', 'G9netzlandmarkensam', 'liest meshfigur_landmarken_sam_v1.npz selbst (ohne das Paket): mit landmarken_hand gilt der Versatz von SAM, sonst der von MediaPipe'),
        ('Blendimportfigur', 'ruft', 'Meshfigurlauf', 'rechnen(job): Meshfigurlauf(id) mit tor = „melden" im Prozess des Imports'),
        ('Blendimportfigur', 'ruft', 'Meshfigurauftrag', 'anlegen(glb): Auftrag mit den Optionen aus Blendimportfigur.OPTIONEN'),
        ('Engine2d3dKleiderkoerperlauf', 'ruft', 'Meshfigurlauf', 'erbt: auftrag(), runner(), _erkennung, _kalibrierung bleiben; Auftrag und Ablage sind die von 2D3D Kleider'),
    ]

    @classmethod
    def zeilen(cls):
        """Die Gruppen im Schema der Werkzeugtabellen: (Rolle, wofür, Art, Aufruf, [(Datei, Klasse)], Hinweis) — das Klassenmodell liest daraus die Klassen und ihre Rollen."""
        return [(rolle, '', 'python', '', klassen, '') for _k, _t, _h, rollen in cls.GRUPPEN for rolle, klassen in rollen]

    @classmethod
    def gruppe_von(cls):
        """Klassenname → (Kennung, Titel) der Gruppe."""
        return {klasse: (kennung, titel) for kennung, titel, _h, rollen in cls.GRUPPEN for _r, klassen in rollen for _d, klasse in klassen}

    @classmethod
    def importiert(cls, bekannt):
        """Kanten aus den Importen: `{(von, nach)}` für Klassen aus `bekannt` (Name → Datei), deren Name in einer `import`-Anweisung der Datei von `von` steht."""
        kanten = set()
        wurzel = Path(settings.TOOLS_ROOT)
        for von, datei in bekannt.items():
            try:
                baum = ast.parse((wurzel / datei).read_text(encoding='utf-8'))
            except (OSError, SyntaxError) as fehler:
                logger.warning('Architektur MeshTo3D: %s nicht lesbar: %s', datei, fehler)
                continue
            for knoten in ast.walk(baum):
                if isinstance(knoten, ast.ImportFrom):
                    namen = {a.name for a in knoten.names}
                elif isinstance(knoten, ast.Import):
                    namen = {a.name.rsplit('.', 1)[-1] for a in knoten.names}
                else:
                    continue
                kanten.update((von, nach) for nach in namen if nach in bekannt and nach != von)
        return kanten

    @classmethod
    def alle_beziehungen(cls):
        """Die beschrifteten Kanten plus die aus den Importen, die noch nicht beschriftet sind (Text „importiert")."""
        bekannt = {klasse: datei for _k, _t, _h, rollen in cls.GRUPPEN for _r, klassen in rollen for datei, klasse in klassen}
        beschriftet = {(von, nach) for von, _w, nach, _m in cls.BEZIEHUNGEN}
        rest = sorted(cls.importiert(bekannt) - beschriftet)
        return list(cls.BEZIEHUNGEN) + [(von, 'ruft', nach, 'importiert') for von, nach in rest]

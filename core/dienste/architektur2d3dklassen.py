# -*- coding: utf-8 -*-
"""Architektur2d3dklassen — die Klassen der Iterationen von „2D3D Kleider", gelesen aus dem Code (02.10.2026).

Je Gruppe (Modul relativ zu `TOOLS_ROOT`, Klasse). Die Seite zeigt zu jeder Klasse den ersten Satz ihres Modul-
Docstrings und die Zeilenzahl der Datei — so steht dort, was der Code heute sagt, nicht was beim Schreiben der Seite
galt. Fehlt eine Datei oder Klasse, steht das in der Zeile (`fehlt`), statt dass die Zeile still verschwindet.
"""

import ast
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Architektur2d3dklassen']


class Architektur2d3dklassen:
    D = 'HumanBodyWeb/core/dienste/'
    P = '2d3DIterationen/iterationen2d3d/'
    G = 'Genesis9/'
    SATZ_HOECHSTENS = 260
    X = 'HumanBodyWeb/effekte/figur/'
    S = 'Stoffsolver/'
    GRUPPEN = [
        ('Ablauf', 'Prozess, Lauf und Runde', [
            (D + 'engine2d3dkleiderarbeiter.py', 'Engine2d3dKleiderarbeiter'), (D + 'engine2d3dkleiderlauf.py', 'Engine2d3dKleiderlauf'),
            (D + 'iterationskreislauf.py', 'Iterationskreislauf'), (D + 'begutachtungsrunde.py', 'Begutachtungsrunde'),
            (D + 'begutachtungsstand.py', 'Begutachtungsstand'),
            (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug'),
            (D + 'aufloesungsstufe.py', 'Aufloesungsstufe'), (D + 'pruefbilder.py', 'Pruefbilder'),
            ('HumanBodyWeb/core/api/engine2d3dkleiderbegutachtung.py', 'Engine2d3dKleiderbegutachtungsendpunkte')]),
        ('Rezept schreiben', 'Regeln aus dem Befund — Ordner 2d3DIterationen', [
            (P + 'iterationmodell.py', 'IterationModell'), (P + 'iterationkleider.py', 'IterationKleider'),
            (P + 'iterationkleidring.py', 'IterationKleidring'), (P + 'iterationtextur.py', 'IterationTextur'),
            (P + 'iterationhaare.py', 'IterationHaare'), (P + 'iterationkoerper.py', 'IterationKoerper'),
            (P + 'iterationgesicht.py', 'IterationGesicht'), (P + 'kleiderwahl.py', 'Kleiderwahl'),
            (P + 'farbangleich.py', 'Farbangleich'), (P + 'schrittsuche.py', 'Schrittsuche'),
            (P + 'reglerpruefung.py', 'Reglerpruefung'), (P + 'rundenauswahl.py', 'Rundenauswahl')]),
        ('Prüf-KI', 'nur bei Option „Prüf-KI" ≠ aus', [
            (D + 'begutachtungskritik.py', 'Begutachtungskritik'),
            (D + 'begutachtungsprompt.py', 'Begutachtungsprompt'), (D + 'ollamamodelle.py', 'Ollamamodelle')]),
        ('Modell und Rezept', 'Genesis9 — der Zustand und die erlaubten Aufrufe', [
            (G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellkoerper.py', 'ModellKoerperMixin'),
            (G + 'modellform.py', 'ModellFormMixin'), (G + 'modellhaar.py', 'ModellHaarMixin'),
            (G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'modellrezept.py', 'G9rezept'),
            (G + 'rezeptumgebung.py', 'Rezeptumgebung'), (G + 'haltungshaut.py', 'G9haltungshaut')]),
        ('Bauen', 'Figur, Kleider, Haar, Stücke aus den Fotos', [
            (D + 'kleidermodellbau.py', 'Kleidermodellbau'), (D + 'koerperanhaenge.py', 'Koerperanhaenge'),
            (D + 'teilevorrat.py', 'Teilevorrat'),
            (D + 'fotostuecke.py', 'Fotostuecke'), (D + 'fotohuelle.py', 'Fotohuelle'),
            (D + 'huellenschnitt.py', 'Huellenschnitt'), (D + 'uhrerkennung.py', 'Uhrerkennung'),
            (D + 'haarzonen.py', 'Haarzonen'), (D + 'koerperfotoprojektion.py', 'Koerperfotoprojektion'),
            (D + 'kleidfotoprojektion.py', 'Kleidfotoprojektion')]),
        ('Rendern und benoten', 'gegen die Fotos und gegen das Netz', [
            (D + 'genesishaarrender.py', 'Genesishaarrender'), (D + 'mitsubaszene.py', 'Mitsubaszene'),
            (D + 'iterationsreferenz.py', 'Iterationsreferenz'), (D + 'iterationsbild.py', 'Iterationsbild'),
            (D + 'iterationsnote.py', 'Iterationsnote'), (D + 'iterationsnetznote.py', 'Iterationsnetznote'),
            (P + 'gesamtnote.py', 'Gesamtnote'), (D + 'gesichtsmasse.py', 'Gesichtsmasse')]),
        ('Messen', 'der Befund, aus dem die Regeln lesen', [
            (D + 'begutachtungsbefund.py', 'Begutachtungsbefund'), (P + 'befundmessung.py', 'Befundmessung'),
            (P + 'teilmasken.py', 'Teilmasken'), (P + 'sichtkoerper.py', 'Sichtkoerper'),
            (P + 'netzmengen.py', 'Netzmengen'), (P + 'bandbreite.py', 'Bandbreite'),
            (P + 'hautabstand.py', 'Hautabstand'), (P + 'messpruefung.py', 'Messpruefung'),
            (D + 'blickwinkelschaetzung.py', 'Blickwinkelschaetzung'), (P + 'blickwinkel.py', 'Blickwinkel'),
            (D + 'haltungsfotos.py', 'Haltungsfotos'), (P + 'haltungsschaetzung.py', 'Haltungsschaetzung')]),
        ('Ablegen und anzeigen', 'Dateien je Runde', [
            (D + 'iterationstafel.py', 'Iterationstafel'), (D + 'iterationsrunde.py', 'Iterationsrunde')]),
        # Ergänzt am 02.10.2026 für den Reiter „Workflow": die Schritte des Laufs, die Optionen und die Motoren.
        ('Lauf und Schritte', 'Die Schritte eines Auftrags (Engine2d3dKleiderlauf.SCHRITTE)', [
            (D + 'engine2d3dkleidervorbereitung.py', 'Engine2d3dKleidervorbereitung'),
            (D + 'engine2d3dkleidernetz.py', 'Engine2d3dKleidernetz'), (D + 'engine2d3dkleidersegmentierung.py', 'Engine2d3dKleidersegmentierung'),
            (D + 'engine2d3dkleiderkoerper.py', 'Engine2d3dKleiderkoerper'),
            (D + 'engine2d3dkleiderkoerperlauf.py', 'Engine2d3dKleiderkoerperlauf'), (D + 'engine2d3dkleidergrundfigur.py', 'Engine2d3dKleidergrundfigur'),
            (D + 'engine2d3dkleiderstuecke.py', 'Engine2d3dKleiderstuecke'), (D + 'kleiderstuecknote.py', 'Kleiderstuecknote'),
            (D + 'kleiderstueckbezug.py', 'Kleiderstueckbezug'), (D + 'kleiderstueckmessung.py', 'Kleiderstueckmessung'),
            (D + 'kleiderstueckobjekt.py', 'Kleiderstueckobjekt'), (D + 'standvorabkleider.py', 'Standvorabkleider'),
            (D + 'engine2d3dkleiderexport.py', 'Engine2d3dKleiderexport'), (D + 'engine2d3dkleiderfilm.py', 'Engine2d3dKleiderfilm'),
            (D + 'engine2d3dkleiderbewegung.py', 'Engine2d3dKleiderbewegung'), (D + 'standbewegung.py', 'Standbewegung'),
            (D + 'netztiefe.py', 'Netztiefe'), (D + 'seitentiefe.py', 'Seitentiefe'), (D + 'seitentiefemessung.py', 'Seitentiefemessung'),
            (D + 'sapienshaar.py', 'Sapienshaar'),
            (D + 'genesisengine2d3dkleider.py', 'Genesisengine2d3dkleider'),
            (D + 'engine2d3dkleiderspeichern.py', 'Engine2d3dKleiderspeichern')]),
        ('Optionen', 'Was ein Auftrag einstellen lässt — Kataloge mit Vorgaben', [
            (D + 'engine2d3dkleideroptionen.py', 'Engine2d3dKleideroptionen'), (D + 'meshoptionen.py', 'Meshoptionen'),
            (D + 'engine2d3dkleiderkoerperoptionen.py', 'Engine2d3dKleiderkoerperoptionen'),
            (D + 'engine2d3dkleidersegmentierungsoptionen.py', 'Engine2d3dKleidersegmentierungsoptionen'),
            (D + 'iterationsoptionen.py', 'Iterationsoptionen'), (D + 'engine2d3dkleiderfilmoptionen.py', 'Engine2d3dKleiderfilmoptionen'),
            (D + 'renderwahl.py', 'Renderwahl')]),
        ('Blender und Stoff', 'Drapieren, Haar-Knoten und Haar-Dynamik: Newton, Blender oder Stoffsolver', [
            (D + 'engine2d3dkleiderblender.py', 'Engine2d3dKleiderblender'), (D + 'haarknotenauftrag.py', 'Haarknotenauftrag'),
            (D + 'kleiddrapierung.py', 'Kleiddrapierung'), (X + 'stoffnewton.py', 'Stoffnewton'),
            (D + 'stoffsolverdrapierung.py', 'Stoffsolverdrapierung'),
            (D + 'haardynamik.py', 'Haardynamik'), (D + 'haarstraehnen.py', 'Haarstraehnen'),
            (G + 'kleidmorphe.py', 'G9kleidmorphe'), (G + 'haarzusatz.py', 'G9haarzusatz')]),
        # Der Stoffsolver (02.10.2026, `Stoffsolver/README.md`): Blenders Cloth und Haar-Dynamik als Warp-Löser, ein eigenes Paket.
        ('Stoffsolver', 'Blenders Cloth als Python/Warp-Paket (Einstieg Drapierauftrag, Ablauf Stoffsimulation)', [
            (S + 'drapierauftrag.py', 'Drapierauftrag'), (S + 'stoffsimulation.py', 'Stoffsimulation'),
            (S + 'kollisionsablauf.py', 'Kollisionsablauf'), (S + 'warpmotor.py', 'WarpMotor'),
            (S + 'implizitesverfahren.py', 'ImplizitesVerfahren'), (S + 'haarsimulation.py', 'Haarsimulation'),
            (S + 'haarauftrag.py', 'Haarauftrag'), (S + 'stoffoptionen.py', 'Stoffoptionen'),
            (S + 'auftragsoptionen.py', 'Auftragsoptionen')]),
        # Der Ausbau des Stoffsolvers (02.10.2026, Edgar: „implementiere alles, was am Solver fehlt"): je Bereich eine Gruppe.
        ('Stoffsolver: Federn und Kräfte', 'Federn, Biegung (Winkel, linear, Vielecke), Ruhegestalt, Vertexgruppen, Schrumpfen, Innenfedern, Nähte, Anheften, Wind, Druck', [
            (S + 'federn.py', 'Federn'), (S + 'federkraefte.py', 'Federkraefte'), (S + 'winkelbiegung.py', 'Winkelbiegung'),
            (S + 'polygonflaechen.py', 'Polygonflaechen'), (S + 'polygonbiegung.py', 'Polygonbiegung'),
            (S + 'linearbiegung.py', 'Linearbiegung'), (S + 'ruhegestalt.py', 'Ruhegestalt'),
            (S + 'federnachfuehrung.py', 'Federnachfuehrung'), (S + 'federverlauf.py', 'Federverlauf'),
            (S + 'stoffmaterial.py', 'StoffMaterial'), (S + 'schrittzahl.py', 'Schrittzahl'), (S + 'geraeteruhe.py', 'Geraeteruhe'),
            (S + 'aussenkraefte.py', 'Aussenkraefte'), (S + 'federsteifigkeit.py', 'Federsteifigkeit'),
            (S + 'federgewichte.py', 'Federgewichte'), (S + 'schrumpfen.py', 'Schrumpfen'),
            (S + 'innenfedern.py', 'Innenfedern'), (S + 'naehte.py', 'Naehte'), (S + 'zielfedern.py', 'Zielfedern'),
            (S + 'pinbewegung.py', 'Pinbewegung'), (S + 'windkraft.py', 'Windkraft'), (S + 'kraftfeld.py', 'Kraftfeld'),
            (S + 'feldkraefte.py', 'Feldkraefte'), (S + 'feldnetz.py', 'Feldnetz'), (S + 'feldsicht.py', 'Feldsicht'),
            (S + 'feldtextur.py', 'Feldtextur'), (S + 'windfelder.py', 'Windfelder'),
            (S + 'feldtexbild.py', 'Feldtexbild'), (S + 'feldtexfarbband.py', 'Feldtexfarbband'), (S + 'feldtexzufall.py', 'Feldtexzufall'),
            (S + 'feldtexknotenbaum.py', 'Feldtexknotenbaum'), (S + 'feldbahn.py', 'Feldbahn'),
            (S + 'windkraftbewegt.py', 'Windkraftbewegt'), (S + 'warpfeldbewegung.py', 'Warpfeldbewegung'),
            (S + 'choiko.py', 'Choiko'), (S + 'kubischfedern.py', 'Kubischfedern'),
            (S + 'hydrostatik.py', 'Hydrostatik'), (S + 'druckgruppe.py', 'Druckgruppe')]),
        ('Stoffsolver: Kollision', 'mehrere Körper, Qualität, bewegter Körper im GPU-Graph', [
            (S + 'kollisionseinstellungen.py', 'Kollisionseinstellungen'), (S + 'koerperantwort.py', 'Koerperantwort'),
            (S + 'warpkoerpersatz.py', 'WarpKoerpersatz'), (S + 'warppinbewegung.py', 'WarpPinbewegung')]),
        ('Stoffsolver: Haar', 'Dynamik, Kontinuum, Pins, Gewichte, Kopf, Erzeugen (Dreiecke bis Vielecke), Kämmen, Kinder, Effektoren, Kurven, Texturen', [
            (S + 'haarnetz.py', 'HaarNetz'), (S + 'haarnetzgewicht.py', 'HaarNetzGewicht'), (S + 'haargewicht.py', 'Haargewicht'),
            (S + 'haarkontinuum.py', 'Haarkontinuum'), (S + 'haarzufall.py', 'Haarzufall'),
            (S + 'haarpin.py', 'Haarpin'), (S + 'haarkopf.py', 'Haarkopf'),
            (S + 'haarsystem.py', 'Haarsystem'), (S + 'haarverteilung.py', 'Haarverteilung'),
            (S + 'haarflaechen.py', 'Haarflaechen'), (S + 'haarpolygone.py', 'Haarpolygone'),
            (S + 'haareckenverteilung.py', 'Haareckenverteilung'), (S + 'haarvolumen.py', 'Haarvolumen'),
            (S + 'kinderpfade.py', 'Kinderpfade'), (S + 'kinderverteilung.py', 'Kinderverteilung'),
            (S + 'pfadeffektoren.py', 'Pfadeffektoren'), (S + 'kurvenfuehrung.py', 'Kurvenfuehrung'),
            (S + 'kurvenspline.py', 'Kurvenspline'), (S + 'kurvenbezier.py', 'Kurvenbezier'), (S + 'kurvennurbs.py', 'Kurvennurbs'),
            (S + 'haartexturen.py', 'Haartexturen'), (S + 'haarkamm.py', 'Haarkamm'), (S + 'bildschirmkamm.py', 'Bildschirmkamm')]),
        ('Stoffsolver: UV und Textur', 'UV abwickeln (LSCM, ABF, SLIM, Henkel), packen (Kasten, Form, xatlas), prüfen, Texturen backen, UDIM, Mipmaps', [
            (S + 'uvabwicklung.py', 'Uvabwicklung'), (S + 'uvloecher.py', 'Uvloecher'), (S + 'uvsymmetrie.py', 'Uvsymmetrie'),
            (S + 'uvaspekt.py', 'Uvaspekt'), (S + 'uvslim.py', 'Uvslim'), (S + 'uvhenkelschnitt.py', 'Uvhenkelschnitt'),
            (S + 'uvpacker.py', 'Uvpacker'), (S + 'uvxatlas.py', 'Uvxatlas'), (S + 'uvoptimalpack.py', 'Uvoptimalpack'),
            (S + 'uvkonvex.py', 'Uvkonvex'), (S + 'uvpackpins.py', 'Uvpackpins'), (S + 'uvpackverschmelzung.py', 'Uvpackverschmelzung'),
            (S + 'uvpackziel.py', 'Uvpackziel'), (S + 'uvpackweg.py', 'Uvpackweg'), (S + 'uvpruefung.py', 'Uvpruefung'),
            (S + 'texturraster.py', 'Texturraster'), (S + 'texturbacker.py', 'Texturbacker'), (S + 'texturudim.py', 'Texturudim'),
            (S + 'texturmip.py', 'Texturmip'), (S + 'texturrandgewicht.py', 'Texturrandgewicht')]),
        ('Optimierer-Schleife', 'Die frühere Schleife, Modus „automatisch" (in keinem Auftrag gewählt)', [
            (D + 'iterationsoptimierer.py', 'Iterationsoptimierer'), (D + 'iterationswahl.py', 'Iterationswahl'),
            (D + 'iterationskritik.py', 'Iterationskritik')]),
    ]

    @classmethod
    def zeile(cls, modul, klasse):
        """{modul, klasse, satz, zeilen, fehlt, methoden} — `satz` ist der erste Satz des Modul-Docstrings, `methoden` die
        öffentlichen Methoden der Klasse in Reihenfolge des Quelltexts."""
        pfad = Path(settings.TOOLS_ROOT) / modul
        aus = {'modul': modul, 'klasse': klasse, 'satz': '', 'zeilen': 0, 'fehlt': '', 'methoden': []}
        try:
            text = pfad.read_text(encoding='utf-8')
            baum = ast.parse(text)
        except (OSError, SyntaxError) as fehler:
            logger.warning('Architektur 2D3D: %s nicht lesbar: %s', modul, fehler)
            return dict(aus, fehlt='Datei nicht lesbar')
        aus['zeilen'] = text.count('\n') + 1
        knoten = next((k for k in baum.body if isinstance(k, ast.ClassDef) and k.name == klasse), None)
        if knoten is None:
            aus['fehlt'] = 'Klasse %s nicht in der Datei' % klasse
        else:
            aus['methoden'] = [f.name for f in knoten.body
                               if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and not f.name.startswith('_')]
        aus['satz'] = cls.satz(ast.get_docstring(baum) or '', klasse)
        return aus

    @classmethod
    def satz(cls, doc, klasse):
        """Der erste Absatz ohne den Klassennamen vorn („Klasse — …"), bis zum ersten Satzende."""
        absatz = ' '.join(doc.split('\n\n')[0].replace('`', '').split())     # Markdown-Zeichen nicht auf die Seite
        for strich in (' — ', ' - ', ': '):
            kopf, _, rest = absatz.partition(strich)
            if rest and len(kopf) < 60:
                absatz = rest
                break
        ende = absatz.find('. ')
        satz = absatz[:ende + 1] if ende > 0 else absatz
        return satz if len(satz) <= cls.SATZ_HOECHSTENS else satz[:cls.SATZ_HOECHSTENS - 1].rstrip() + '…'

    @classmethod
    def gruppen(cls):
        return [{'gruppe': g, 'hinweis': h, 'klassen': [cls.zeile(m, k) for m, k in eintraege]}
                for g, h, eintraege in cls.GRUPPEN]

    @classmethod
    def alle(cls):
        return [(m, k) for _g, _h, eintraege in cls.GRUPPEN for m, k in eintraege]

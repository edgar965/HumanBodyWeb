# -*- coding: utf-8 -*-
"""Iterationsoptionen — die Gruppe `iterationen` der Optionen von „2D3D Kleider": wie lange und womit iteriert
wird (30.09.2026).

Dieselbe Katalogform wie `Engine2d3dKleiderfilmoptionen` (`schluessel`, `titel`, `art`, `vorgabe`, `werte`,
`hinweis`). Die Prüf-KI ist wählbar: die Liste kommt beim Aufbau der Seite aus Ollama
(`Ollamamodelle.mit_bildern`) — nur Modelle, die Bilder lesen können. Ein gespeichertes Modell bleibt
gültig, auch wenn Ollama gerade nicht antwortet (sonst fiele die Wahl still auf die Vorgabe zurück); geprüft
wird nur, dass der Name wie ein Ollama-Name aussieht.

Gegenüber BlenderModel fehlen die Optionen, die zum Bau in Blender gehörten (Fototextur, Umriss-Hülle,
Sichtmodell): Was die Engine an Einstellungen bekommt, steht mit ihren Einzelheiten hier.
"""

import re

from .ollamamodelle import Ollamamodelle

__all__ = ['Iterationsoptionen']


class Iterationsoptionen:
    AUS = 'aus'
    VORGABE_KI = 'qwen3.8:27b'
    OLLAMANAME = re.compile(r'^[\w.\-:/]{1,120}$')
    BEGUTACHTUNG, AUTOMATISCH = 'begutachtung', 'automatisch'
    KATALOG = [
        {
            'schluessel': 'modus',
            'titel': 'Iterationen',
            'art': 'wahl',
            'vorgabe': BEGUTACHTUNG,
            'werte': [
                (BEGUTACHTUNG, 'Begutachtung — je Runde ein Rezept (Aufrufe an ModellMitKleidern), danach wartet der Auftrag'),
                (AUTOMATISCH, 'Automatisch — Optimierer und Prüf-KI über die Haarparameter (die frühere Schleife)'),
            ],
            'hinweis': 'Begutachtung (Edgar, 30.09.2026): jede Runde wird angesehen, dann kommt neuer Code; der Auftrag steht '
            'mit „Wartet auf Begutachtung", bis das nächste Rezept kommt (Reiter „Iterationen").',
        },
        {
            'schluessel': 'bildbreite',
            'titel': 'Start-Auflösung der Note (px)',
            'art': 'zahl',
            # Stufen seit 02.10.2026 (Edgar: „am Anfang kleinere Auflösung … immer höher bis zur maximalen Auflösung, in
            # der die Vorlagen vorhanden sind", `Aufloesungsstufe`).
            'vorgabe': 128,
            'min': 96,
            'max': 1024,
            'hinweis': 'Breite der ersten Stufe (Höhe = 1,5 × Breite). Die Note verdoppelt die Auflösung, wenn eine Stufe '
            'nichts mehr verbessert, bis zur Auflösung der Figur in den Fotos.',
        },
        {
            'schluessel': 'stufe_stillstand',
            'titel': 'Höhere Auflösung nach … Runden ohne Besserung',
            'art': 'zahl',
            'vorgabe': 3,
            'min': 1,
            'max': 100,
            'hinweis': 'Dann rechnet die nächste Runde die beste Runde in doppelter Auflösung neu (Messrunde) — auch, wenn '
            'die Automatik keine Änderung mehr findet.',
        },
        {
            'schluessel': 'tafelbreite',
            'titel': 'Prüfbilder (px)',
            'art': 'zahl',
            'vorgabe': 384,
            'min': 128,
            'max': 1024,
            'hinweis': 'Mindestbreite der Vergleichstafel je Blickwinkel, an der Fable jede Runde prüft (Kopftafel: '
            '384 × 384). Gerendert wird in der größeren von Stufe und Prüfbreite.',
        },
        {
            'schluessel': 'runden',
            'titel': 'Runden je Lauf',
            'art': 'zahl',
            'vorgabe': 20,
            'min': 1,
            'max': 5000,
            'hinweis': 'So viele Runden rechnet ein Druck auf „Weiter iterieren" (oder der Schritt im ganzen Lauf). Jeder Lauf '
            'setzt beim besten bisherigen Modell an.',
        },
        {
            'schluessel': 'form',
            'titel': 'Körper- und Gesichtsform in den Runden',
            'art': 'wahl',
            'vorgabe': 'aus',
            'werte': [
                ('aus', 'Aus — die Form kommt aus dem Schritt „Körper"'),
                ('an', 'An — Körper- und Gesichtsregler nachführen (mit Rückschritt)'),
            ],
            'hinweis': 'Der Schritt „Körper" fittet die Figur mit Verlustfunktion an das Netz. Die Regeln der Runden '
            'schoben die Beine von „.51" 40 Runden lang an den Anschlag (01.10.2026) — deshalb sind sie aus.',
        },
        {
            'schluessel': 'haarumbau',
            'titel': 'Frisur an das Haar der Vorlage anpassen',
            'art': 'wahl',
            'vorgabe': 'herren',
            'werte': [
                ('herren', 'Herrenhaar — ein eigenes Kurzhaar für einen normalen Herrenschnitt: Strähnen auf der Kopfhaut in der Haarfarbe der Fotos, Umriss und Haarlinie aus dem Fotohaar; die Frisur der Garderobe wird nicht gebaut'),
                ('an', 'An — die Frisur wird an der Haarlinie des Fotohaars geschnitten und sitzt auf einer Haarkappe in der Haarfarbe'),
                ('aus', 'Aus — die Frisur bleibt, wie Garderobe und Rezept sie wählen'),
            ],
            'hinweis': 'Haarumbau (Edgar, 05.10.2026: „das Haar der Vorlage perfekt auf ein Haar aus Genesis umbauen"): Stirn, Schläfen, Ohren und Hals bleiben frei, Lücken der Haarkarten füllt die Kappe in der '
            'Haarfarbe. Gilt nur für kurzes Haar mit Hülle des Fotohaars (Schritt „Frisur"); sonst bleibt die Frisur, wie sie ist.',
        },
        {
            'schluessel': 'rumpftiefe',
            'titel': 'Rumpf an die Seitenansicht der Fotos angleichen',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — Iteration 0 gibt dem Rumpf (Brust, Bauch, Rücken) die Tiefe der Silhouette im Seitenfoto und legt Kleidung enger an'),
                ('aus', 'Aus — der Rumpf bleibt, wie der Schritt „Körper" ihn fittet'),
            ],
            'hinweis': 'Rumpftiefe (Edgar, 05.10.2026: „Bauch ist bei dir sehr dick"): Im Modell der Iteration 0 war der Körper 20–45 mm flacher als die Silhouette des Seitenfotos (der Schritt „Körper" zieht ihn unter Kleidung nur zu 60 % '
            'ans Netz), das Hemd darüber stand am Unterbauch bis 41 mm zu tief — flache Brust, dicker Bauch. `koerper_rumpftiefe` vertieft den Körper dort, wo er flacher ist als der Sichtkörper der Fotos (abzüglich 8 mm Hemd), `passform` legt die Kleider enger.',
        },
        {
            'schluessel': 'gesichtsprofil',
            'titel': 'Lippen und Kinn an das Seitenfoto angleichen',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — Iteration 0 rückt Lippen und Kinn so weit nach vorn wie im Seitenfoto (bezogen auf Augen und Nasenwurzel)'),
                ('aus', 'Aus — das Gesicht bleibt, wie der Schritt „Körper" es fittet'),
            ],
            'hinweis': 'Eingedrücktes Kinn (Edgar, 05.10.2026: „Kinn über dem Mund ist bei dir eingedrückt"): Im Profil standen Lippen und Kinn 5–13 mm weiter hinter dem Seitenfoto als Augen und Nasenwurzel. '
            '`koerper_gesichtsprofil` misst die Kante des Seitenfotos fein (≈ 1 mm) und rückt die Vorderseite von Kinn bis unter die Nase um den Unterschied nach vorn (höchstens 30 mm; die Nase bleibt). Zeigt das Foto einen Bart, steht die Lippe um dessen Dicke zu weit vorn.',
        },
        {
            'schluessel': 'licht',
            'titel': 'Licht der Fotos herausrechnen',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — die Beleuchtung der Fotos wird je Ansicht geschätzt und aus der projizierten Farbe geteilt (Haut aus den Fotos, Kleidung, Haar)'),
                ('aus', 'Aus — die Farbe der Fotos wird genommen, wie sie ist'),
            ],
            'hinweis': 'Fotolicht (Edgar, 05.10.2026: „Die Textur hat die Schatten des Lichtes drin"): Jede Ansicht hat ihr Licht — Oberschenkel hell, Waden dunkler, Seiten im Schatten. Es wird als einfaches Polynom '
            'in Normale und Lage geschätzt (sieben Zahlen je Ansicht) und mit Stärke 0,85 herausgerechnet. Haare, Muttermale und Glanzlichter bleiben; es ist eine Näherung, keine Zerlegung in Albedo und Licht.',
        },
        {
            'schluessel': 'belichtung',
            'titel': 'Belichtung je Ansicht angleichen',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — der Render jeder Ansicht wird so hell wie sein Foto, das Mittel über alle Ansichten bleibt (Note, Befund und Tafel sehen dasselbe)'),
                ('aus', 'Aus — der Render bleibt, wie das feste Licht der Szene ihn macht'),
            ],
            'hinweis': 'Belichtung (Edgar, 06.10.2026: „der Render ist insgesamt dunkler als das Foto"): Render geteilt durch Foto war vorn 1,07, hinten 0,95, Seite 0,86 — das Licht der Szene steht fest, die Fotos sind verschieden belichtet. Der Faktor je Ansicht '
            '(Foto ÷ Render in linearem Licht, geteilt durch das geometrische Mittel aller) nimmt nur diesen Unterschied weg; ist das Modell überall zu dunkel, bleibt es das. Runden VOR dieser Option wurden ohne Abgleich benotet — ihre Noten sind nicht gleich zu lesen.',
        },
        {
            'schluessel': 'kandidaten',
            'titel': 'Kandidaten je Runde',
            'art': 'zahl',
            'vorgabe': 4,
            'min': 1,
            'max': 16,
            'hinweis': 'So viele Abwandlungen des besten Modells baut und rendert die Engine je Runde.',
        },
        {
            'schluessel': 'parallel',
            'titel': 'Engine-Prozesse parallel',
            'art': 'zahl',
            'vorgabe': 1,
            'min': 1,
            'max': 8,
            'hinweis': 'So viele Prozesse der Engine rechnen die Kandidaten einer Runde gleichzeitig. Mehr Prozesse belasten '
            'den Rechner stärker.',
        },
        {
            'schluessel': 'stillstand',
            'titel': 'Halt nach Runden ohne Besserung',
            'art': 'zahl',
            'vorgabe': 15,
            'min': 0,
            'max': 1000,
            'hinweis': '0 = nie vorzeitig anhalten.',
        },
        {
            'schluessel': 'pruefki',
            'titel': 'Prüf-KI (lokal, Ollama)',
            'art': 'wahl',
            'vorgabe': AUS,
            'werte': [],
            'hinweis': 'Sieht Vorlage und Render und schlägt Werte vor (Teile an/aus, Längen, Farben). Nur Modelle, die Bilder '
            'lesen können. Vorgabe „Aus" (Edgar, 01.10.2026: „keine Prüfung über lokale KI") — die Begutachtung der '
            'Runden macht Fable anhand der Vergleichstafeln, die Automatik rechnet ohne Prüf-KI weiter.',
        },
        {
            'schluessel': 'pruefki_alle',
            'titel': 'Prüf-KI alle … Runden',
            'art': 'zahl',
            'vorgabe': 5,
            'min': 1,
            'max': 1000,
            'hinweis': 'Die Prüf-KI sieht sich alle so viele Runden die Tafel an (dazu bei einer Flaute, siehe nächste Option). '
            'Ein Aufruf kostet 1–3 Minuten — in einer langen Suche alle 250 Runden.',
        },
        {
            'schluessel': 'pruefki_stillstand',
            'titel': 'Prüf-KI nach … Runden ohne Besserung',
            'art': 'zahl',
            'vorgabe': 3,
            'min': 1,
            'max': 1000,
            'hinweis': 'Eine Runde der Prüf-KI dauert je nach Modell 20–60 s; bei 3 Runden Flaute würde sie in einer langen '
            'Flaute fast jede dritte Runde des Optimierers verdrängen.',
        },
        {
            'schluessel': 'toleranz',
            'titel': 'Toleranz der Prüf-KI (%)',
            'art': 'zahl',
            'vorgabe': 2,
            'min': 0,
            'max': 20,
            'hinweis': 'Ein Vorschlag der Prüf-KI wird übernommen, solange die Abweichung um höchstens so viel Prozent '
            'schlechter wird — ein Detail, das den Umriss kaum ändert, gehört trotzdem dazu.',
        },
    ]

    @classmethod
    def vorgaben(cls):
        return {e['schluessel']: e['vorgabe'] for e in cls.KATALOG}

    @classmethod
    def haarumbau(cls, job):
        """Wie das Haar an die Vorlage angepasst wird (`Haarumbau`, `Herrenhaar`): Option `iterationen.haarumbau` des Auftrags, Vorgabe Herrenhaar — `False`, `True` oder `'herren'` (`haarart`)."""
        return cls.haarart(cls.pruefen((job.optionen or {}).get('iterationen')).get('haarumbau'))

    @classmethod
    def rumpftiefe(cls, job):
        """Ob Iteration 0 dem Rumpf die Tiefe der Seitenansicht gibt (`koerper_rumpftiefe`, `passform`): Option `iterationen.rumpftiefe` des Auftrags, Vorgabe an."""
        return cls.pruefen((job.optionen or {}).get('iterationen')).get('rumpftiefe') != 'aus'

    @classmethod
    def gesichtsprofil(cls, job):
        """Ob Iteration 0 Lippen und Kinn nach dem Seitenfoto vorrückt (`koerper_gesichtsprofil`): Option `iterationen.gesichtsprofil`, Vorgabe an."""
        return cls.pruefen((job.optionen or {}).get('iterationen')).get('gesichtsprofil') != 'aus'

    @classmethod
    def licht(cls, job):
        """Stärke, mit der das Licht der Fotos aus der projizierten Farbe herausgerechnet wird (`Fotolicht`, `Fotoprojektion.licht`): Option `iterationen.licht` des Auftrags, Vorgabe an → `Fotolicht.STAERKE`, aus → 0."""
        from iterationen2d3d.fotolicht import Fotolicht
        return 0.0 if cls.pruefen((job.optionen or {}).get('iterationen')).get('licht') == 'aus' else Fotolicht.STAERKE

    @staticmethod
    def haarart(wert):
        """Aus dem Wert der Option haarumbau: 'herren' (eigenes Kurzhaar, Herrenhaar), True (die Frisur umbauen, Haarumbau) oder False (aus) — so nimmt Kleidermodellbau den Parameter haarumbau."""
        return 'herren' if wert == 'herren' else wert != 'aus'

    @classmethod
    def katalog(cls):
        modelle = Ollamamodelle.mit_bildern()
        aus = []
        for e in cls.KATALOG:
            werte = e.get('werte', [])
            if e['schluessel'] == 'pruefki':
                # Die Vorgabe bleibt wählbar, auch wenn Ollama gerade schweigt — sonst zeigte das Feld „Aus", und das
                # nächste Speichern schriebe es.
                if cls.VORGABE_KI not in [n for n, _ in modelle]:
                    modelle = [
                        (cls.VORGABE_KI, '%s (Ollama antwortet gerade nicht)' % cls.VORGABE_KI)
                    ] + modelle
                werte = [(cls.AUS, 'Aus — nur der Optimierer')] + modelle
            aus.append(dict(e, werte=[{'wert': w, 'text': t} for w, t in werte], fein=False))
        return {'optionen': aus}

    @classmethod
    def pruefen(cls, roh):
        roh = roh if isinstance(roh, dict) else {}
        aus = cls.vorgaben()
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'])
            if wert is None:
                continue
            if e['schluessel'] == 'pruefki':
                if str(wert) == cls.AUS or cls.OLLAMANAME.match(str(wert)):
                    aus['pruefki'] = str(wert)
            elif e['art'] == 'wahl':
                if str(wert) in [w for w, _ in e.get('werte', [])]:
                    aus[e['schluessel']] = str(wert)
            elif e['art'] == 'zahl':
                try:
                    zahl = float(wert)
                except TypeError, ValueError:
                    continue
                if e['min'] <= zahl <= e['max']:
                    aus[e['schluessel']] = int(zahl) if zahl.is_integer() else zahl
        return aus

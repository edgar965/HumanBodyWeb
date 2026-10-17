# -*- coding: utf-8 -*-
"""Architekturmesh3daiplan — der Plan für Mesh3D-AI: Köpfe des Netzes, Posen aus Pool und Saat, Zeiten, Hebel, offene Entscheidungen (Hilfe → Architektur → Mesh3DAI, 16.10.2026).

Edgar, 16.10.2026: „Ich brauche keine Hunderte Posen, maximal 50 Posen, ein Training für ein Modell soll Minuten dauern. Ich werde 100 Modelle haben in 10 unterschiedlichen Posen" —
„Pools aus 200 Posen und du nimmst 50 davon, random. Oder die gleichen Posen, damit das Ergebnis nachvollziehbar ist?" — „such dir selber Posen aus, mit Sitzen, Liegen, Spagat usw."
GELESEN beim Aufruf: die Posenwahl (`posenwahl_saat<N>.json`, `posenpool.json` im Datensatzordner, geschrieben von `ProjektTemp/_wegwerf/mesh3dai_posen_pool.py`). Alles andere ist Plan oder
Hochrechnung und steht so da; gemessene Zahlen tragen ihre Quelle.
"""

import json

__all__ = ['Architekturmesh3daiplan']


class Architekturmesh3daiplan:
    #: Zeiten — gemessen oder hochgerechnet aus Messungen. (Was, Dauer, Grundlage)
    ZEITEN = (
        ('Formvarianten: 40 Körper × 12 Posen', '1.411 s für alle 40 (4 nebeneinander); je Variante Teile 5–17 s, 12 Proben 107–175 s, Skelett 4–7 s', 'gemessen 16.10.2026, mesh3dai_formen_kette.log'),
        ('Wirkung der 815 Formregler', '106 s', 'gemessen 16.10.2026, mesh3dai_formregler.py'),
        ('Neuer Job (50 Training + 15 Prüfposen)', '33–45 s je Probe und Arbeiter (4 Arbeiter, daneben rechnete Mesh-3D)', 'gemessen 16.10.2026, Damira0/Mann1/Matt0'),
        ('Datensatz je Modell, 10 Posen', '≈ 31 s mit 5 Arbeitern · ≈ 80–90 s in einem Prozess', 'Hochrechnung: 3,1 s je Probe Wandzeit (176 Proben in 553 s, 15.10.) bzw. 7,6–8,9 s je Probe allein (16.10.)'),
        ('Datensatz je Modell, 50 Posen', '≈ 2,6 min mit 5 Arbeitern', 'wie oben'),
        ('100 Modelle × 10 Posen = 1.000 Proben', '≈ 52 min mit 5 Arbeitern', 'wie oben; die Anzeigeflächen kosten seit 16.10. kaum noch etwas (Sichtbarkeit wird übernommen)'),
        ('Ein Modell bauen (Teile in der A-Pose)', '5–17 s je Formvariante', 'gemessen 16.10.2026 (`mesh3dai_ursula_teile.py` je Variante); das Anzeigenetz mit Bildern ist nicht einzeln gemessen'),
        ('Training mit Formkopf (620 Proben, 200 Epochen)', 'Abschnitt 3 (Dauer aus dem Lauf gelesen); Zwischenstand: 631 s nach 100 Epochen, ≈ 6,3 s je Epoche mit Auswertung', 'lauf.log des Formlaufs, 16.10.2026'),
        ('Training über 1.000 Proben', '≈ 10 min (60 Epochen) · ≈ 20 min (120 Epochen)', 'Hochrechnung aus dem Formlauf: 77 Schritte je Epoche in ≈ 6 s; nicht gemessen'),
    )

    #: Hebel gegen die Datenzeit — die Sichtbarkeit ist 94–96 % einer Probe. (Hebel, Wirkung, Stand)
    HEBEL = (
        ('Sichtbarkeit nur einmal rechnen', 'die Anzeigeflächen rechneten sie ein zweites Mal: 521 von 1.074 s bei 176 Proben (15.10.); seither 8 s für 54 Proben (gemessen 16.10.)',
         'GEBAUT 16.10.: `sicht.npz` je Probe, `mesh3dai_ursula_flaechen.py` übernimmt sie'),
        ('1.024 statt 2.048 Bildpunkte je Ansicht', 'Genauigkeit gemessen (15.10.): Haut fehlt bei 513/629 statt 333/256 Dreiecken (Proben 1/45, Referenz 4.096); Zeit NICHT gemessen', 'Vorschlag'),
        ('Strähnenhaar für die Sichtbarkeit vereinfachen', '80,6 % aller Dreiecke sind Strähnen (359.968 von 446.852); eine Hülle des Haars statt der Strähnen', 'Idee, nicht gemessen'),
        ('Weniger Richtungen (26 → 14: Flächen und Ecken des Würfels)', 'Wirkung auf die Außenfläche nicht gemessen', 'Idee'),
    )

    #: Offene Entscheidungen für Edgar. (Frage, Stand, Vorschlag)
    OFFEN = (
        ('Woher kommen die Modelle?', 'GEBAUT: vier Jobs (Ursula1, Damira0, Mann1, Matt0) + 40 Formvarianten aus Charaktermischung und Reglern (Abschnitt 3); 99 gespeicherte Genesis-Modelle ungenutzt',
         'mehr Varianten; Modelle mit den fehlenden Kleidertypen (Kleid, Rock, Robe, Mantel, Hut, Schuhe) als neue Grundlagen'),
        ('Gleiche oder andere Posen je Modell?', 'GEBAUT: je Job ein eigener Plan (Saat), je Formvariante A-Pose + 11 aus dem Pool der 200 Trainingsposen (eigene Saat)', '—'),
        ('Welche Regler gibt das Netz aus?', 'GEBAUT: Haltung (Daz-Winkel in den Grenzen, Abschnitt 5) und 815 Formregler (Abschnitt 3)', 'Mimik erst mit Ausdrücken im Datensatz; Kleider siehe unten'),
        ('Zielposen in den Daz-Grenzen?', 'Der Retarget legt Drehung auf gesperrte Achsen (Fingerglieder verdreht, Ellbogen seitlich, Handgelenk bis 138°); 189 von 190 Proben von Ursula1 verletzen Grenzen (Abschnitt 5). '
         'Die Formvarianten nehmen die angepassten Daz-Winkel — ihre Ziele liegen in den Grenzen.',
         'Retarget auf Genesis so ändern, dass er die Grenzen achtet (Verdrehung in den Unterarm, Seitbeuge weg) — betrifft auch Studio und Charakter; oder das Ziel im Datensatz auf die Grenzen ziehen'),
        ('Wie wird geprüft?', 'GEBAUT: 15 Prüfposen je Job + 5 Prüfformen (ganze Figuren nie trainiert) + 125 Spagat-Bilder; Testnetze ohne Soll (Abschnitt 4)',
         'für die Testnetze eine Bezugsgröße — etwa das generierte Rig (Abschnitt 1)'),
        ('Farbe und Blickrichtung?', 'Gemessen: das Netz las die Teile an ihrer flachen Farbe ab und kannte nur Figuren, die zur Kamera schauen (Abschnitt 7). Training jetzt mit Zufallsfarben; ±180° um die Hochachse '
         'machte alles viel schlechter (93,7 statt 11,0 mm Training)', 'Blickrichtung je Testnetz vorab bestimmen statt lernen; oder länger trainieren'),
        ('Kleider: im Netz oder eigenes Netz?', 'NICHT GEBAUT: das Netz gibt keine Kleider aus; die vier Jobs tragen drei Outfits mit Kleidung', 'Köpfe am selben Rückgrat (Teile je Punkt, Katalogwahl je Region), Abschnitt 8'),
    )

    @classmethod
    def koepfe(cls, netz, regler=None, groesse=None):
        """Die Köpfe am selben Rückgrat — gebaut (Gewichte aus der Schichttabelle `netz` = `Architekturmesh3dainetz.heute`) und vorgeschlagen.
        (Kopf, liest, gibt aus, Gewichte oder None, Stand, Text)"""
        zeilen = {z['name']: z for z in (netz or {}).get('zeilen') or []}
        stimmen = sum(zeilen[n]['gewichte'] for n in ('Kopf 1', 'Kopf 2', 'Stimmen') if n in zeilen) or None
        form = (netz or {}).get('form') or 815
        mimik = ((regler or {}).get('koepfe') or {}).get('Mimik')
        r = (groesse or {}).get('regler') or {}
        art = r.get('stuecke_je_art') or {}
        katalog = '%s Stücke der Garderobe (%s Kleidung, %s Haar, %s Requisit)' % (r.get('stuecke', '700'), art.get('kleidung', '—'), art.get('haar', '—'), art.get('requisit', '—'))
        return (
            ('Stimmen (Haltung)', 'je Punkt: eigene Merkmale + ganze Figur', '276 Ziele × (Versatz + Gewicht) je Punkt → 138 Gelenke → Daz-Winkel', stimmen, 'GEBAUT',
             'Abschnitt 2; die Winkel passt eine Rechnung ohne Gewichte an (Abschnitt 5)'),
            ('Formregler', 'ganze Figur (1.024)', '%d Genesis-Form-Regler' % form, (netz or {}).get('gewichte_form') or None, 'GEBAUT 16.10.2026 abends', 'Abschnitt 3'),
            ('Teile je Punkt', 'je Punkt (256 nach Schicht 6)', 'Körper · Haar · Oberteil · Hose/Rock · Schuhe · Zubehör je Punkt', None, 'VORSCHLAG',
             'Die Etiketten liegen im Datensatz exakt vor (jedes Dreieck weiß aus dem Bau sein Teil). Grundlage, um Kleider aus dem Netz zu schneiden und für den Katalogkopf.'),
            ('Kleider je Region', 'ganze Figur (1.024)', 'Wahl unter %s, die besten k je Region' % katalog, None, 'VORSCHLAG',
             'Unter den Kandidaten entscheidet eine Messung (Abstand zum Netz, wie die Frisurwahl). Braucht Modelle mit mehr Kleidertypen — die vier Jobs haben drei Outfits.'),
            ('Passform je Stück', '—', 'Länge, Weite des gewählten Stücks', None, 'VORSCHLAG (ohne Netz)', 'nach der Wahl an das Netz angepasst, nicht vom Netz geraten'),
            ('Mimik', 'ganze Figur (1.024)', '%s Mimik-Regler' % (mimik if mimik else '—'), None, 'SPÄTER', 'erst wenn der Datensatz Ausdrücke enthält — heute ist das Gesicht in allen Proben starr'),
        )

    @staticmethod
    def posenwahl(ordner, saat=1):
        """Die gewählten Posen (`posenwahl_saat<N>.json`) und der Pool je Kategorie; None ohne Datei."""
        datei = ordner / ('posenwahl_saat%d.json' % saat)
        if not datei.is_file():
            return None
        wahl = json.loads(datei.read_text(encoding='utf-8'))
        pool = json.loads((ordner / 'posenpool.json').read_text(encoding='utf-8')) if (ordner / 'posenpool.json').is_file() else []
        kategorien = {}
        for e in pool:
            kategorien.setdefault(e['kategorie'], {'kategorie': e['kategorie'], 'pool': 0, 'dateien': set(), 'wahl': 0, 'pruefung': 0})
            kategorien[e['kategorie']]['pool'] += 1
            kategorien[e['kategorie']]['dateien'].add(e['datei'])
        for gruppe in ('wahl', 'pruefung'):
            for e in wahl.get(gruppe, []):
                kategorien.setdefault(e['kategorie'], {'kategorie': e['kategorie'], 'pool': 0, 'dateien': set(), 'wahl': 0, 'pruefung': 0})[gruppe] += 1
        zeilen = [dict(z, dateien=len(z['dateien'])) for z in kategorien.values()]
        liste = [dict(e, gruppe='Training') for e in wahl.get('wahl', [])] + [dict(e, gruppe='Prüfung (neu)') for e in wahl.get('pruefung', [])]
        return {'saat': wahl.get('saat'), 'pool': len(pool), 'kategorien': zeilen, 'liste': liste}

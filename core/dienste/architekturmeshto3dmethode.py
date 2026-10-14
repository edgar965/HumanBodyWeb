# -*- coding: utf-8 -*-
"""Architekturmeshto3dmethode — wie die Anpassung rechnet, und ihre Grenzen: Texte des Reiters „MeshTo3D" (Hilfe → Architektur → 2D3D, 11.10.2026).

Jeder Punkt kommt aus dem Quelltext oder aus `.claude/rules/meshfigur.md` mit dem Datum der Messung dort; was die Datei „gemessen" nennt, steht hier mit Datum und Fall
(Damira = Hunyuan-Netz des Reiters „Mesh", Edgar = sein Körpernetz). Nichts hier ist neu gemessen worden außer dort, wo es ausdrücklich steht. Die Optionen der Seite
liest `Architekturmeshto3d` aus `Meshfiguroptionen.KATALOG` (nicht von Hand), die Zeiten aus den fertigen Aufträgen (`Architekturmeshto3dzeiten`).
"""

__all__ = ['Architekturmeshto3dmethode']


class Architekturmeshto3dmethode:
    #: (Überschrift, [Punkte]) — wie die Anpassung rechnet.
    METHODE = [
        ('Das Ziel: ein Abstandsmaß, nicht ein Lernmodell',
         ['Es gibt kein trainiertes Netz für die Anpassung. Die Regler von Genesis 9 und die Haltung sind freie Größen; die Registrierung (`Meshfigurregistrierung`) verkleinert den '
          'Abstand Figur ↔ Netz mit Adam in torch auf der Grafikkarte (`Meshfigurmodell`: Punkte = P0 + Σ Δx · J + Gelenkkorrekturen, die Gelenke wandern mit).',
          'Abstand (`Meshfigurabstand`): Nächste Nachbarn in beiden Richtungen (pytorch3d `knn_points`), Punkt-zu-Ebene, robuste Verlustfunktion nach Geman-McClure; Paare, deren Normalen '
          'gegeneinander zeigen oder über der Grenze liegen, zählen nicht; die Nachbarn werden nur alle 5 Schritte neu gesucht (brute force 25k × 80k Paare war der Hauptkostenpunkt).',
          'Nach jedem Schritt werden die Regler auf die Grenzen von Daz geklemmt; die Dämpfung misst die Wirkung eines Reglers an seiner eigenen Region (Option daempfung 0,01 | 0,02 | 0,05).',
          'Die Kinematik (`Meshfigurkinematik`) posiert Genesis in torch wie Daz und `G9knochenmatrizen`; gegen `G9formung(drehung)` auf 0,0006 mm geprüft (27.09.2026).']),
        ('Zwei Welten wechseln sich ab',
         ['python10 (GPU, torch, pytorch3d, MediaPipe, pyrender) rechnet die Registrierung, ein Schritt je Aufruf von `_run_meshfigur.py`. python14 lebt in Django und kann Genesis 9 '
          'ECHT rechnen — die Formelketten, die Knochenskalierung, die Gelenkkorrekturen (JCMs) der gefundenen Haltung. Darum rechnet python14 zwischen den Runden die Figur nach '
          '(`Meshfigurgenesis`), bevor die nächste Runde auf ihr aufsetzt. Der Zustand (Haltung, Lage) wandert über arbeit/zustand.npz.',
          'Der Auftrag läuft in einem eigenen Prozess (`manage.py meshfigur_fahren <id>`, gestartet von `Meshfigurarbeiter`), damit ein Neustart des Servers ihn nicht mitreißt. Folge: '
          'Code, der nach dem Start geändert wird, gilt erst im nächsten Lauf. Der Blender-Import rechnet den Auftrag dagegen im eigenen Prozess des Imports (`Blendimportfigur.rechnen`).']),
        ('Stufen: Größe zuerst, Feinregler zuletzt',
         ['`Meshfigurregler` teilt jeden Regler einer Stufe zu: 1 Größe und Proportionen (BodyMass, Beine, Arme, Rumpf, Hals, Schultern, Brustkorb, Hände, Füße), 2 Körpertyp '
          '(Charakterkörper, Heavy, Pear, Muscular, Fitness), 3 die übrigen Bereiche; Kopf: 11 Schädel und Charakterköpfe, 12 Züge (Nase, Mund, Lippen, Augen, Brauen, Wangen, Kinn, Kiefer), '
          '13 Ohren und Rest; Stufe 0 wird nie gestellt (z. B. ProportionSmaller/Larger, Mundhöhle, Ears Gone, Mimik, HipGenitalBulge) — Stand 27.09.2026, 158 Körper- und 296 Kopfregler.',
          'Körper, Runde 1: haltung (300 Schritte) → groesse (300) → koerpertyp (300) → bereiche (400); ab Runde 2 eine Stufe mit allen Reglern. Gesicht: kopfhaltung (200) → schaedel (300) → '
          'zuege (400) → fein (300). Frühstopp seit 02.10.2026: alle 25 Schritte; bringt das Beste der letzten 50 weniger als 0,2 % gegenüber dem Besten davor, endet die Stufe (frühestens '
          'nach einem Drittel der Schritte).']),
        ('Wo das Netz zählt: Gewichte der Käfigpunkte',
         ['`G9netzbereiche` gibt jedem Käfigpunkt ein Gewicht: Haut 1, Finger 0, Hand 0,1, Innen 0, Ohr 0,2, Zehen 0,3, Schritt 0,1; Kopfhaut zählt einseitig, wenn die Probe nicht Hautfarbe hat. '
          'Mit Hand 0,3 und Zehen 1 liefen MassHands, MassFeet und FootArchDepth an die Grenze — Faust und Zehenklumpen formten die Figur (27.09.2026).',
          'Gesichtskern: Kopfpunkte bis 3,5 cm über der Augenhöhe und mindestens 2 cm vor dem Ohrknochen — Augen, Nase, Mund, Wangen, Kinn, Brauen; dort zählt das Netz immer beidseitig. Stirn und '
          'Schläfen darüber werden einseitig, sobald Haar darüber liegt (sonst wächst der Kopf ins Haar: 170 statt 167 cm).',
          'Hautton: aus den KAHLEN Stellen (`Meshfigurhautmodell`, 29.09.2026), nicht aus Rumpf und Oberschenkeln; was nicht Haut ist, gilt als bedeckt und zieht nur einseitig (Körper unter Haar oder Stoff).']),
        ('Das Körper-Tor',
         ['Nach dem Körperschritt prüft `Meshfigurrumpfpruefung`, ob die Figur so tief ist wie das Netz und nicht Dutzende Regler am Anschlag stehen (Soll höchstens 8). Ein Regler am Anschlag zählt nicht, wenn '
          'mindestens 50 % seiner Wirkung in Zonen mit Gewicht < 1 liegt — gemessen 08.10.2026 von neun Reglern nur MassHands (99,8 %). „melden" lässt den Lauf weiterlaufen und legt den Befund '
          'in ergebnis.koerper.tor ab — in 2D3D Kleider steuert das die Option koerper.tor (04.10.2026), der Blender-Import setzt lauf.tor = „melden".']),
        ('Rest → Eigenmorph',
         ['Was die Regler nicht erreichen, rechnet der Runner je Käfigpunkt über die Hautmischung in die Ruhelage zurück; python14 mittelt links/rechts, glättet und legt den Rest als Eigenmorph '
          'eigen:<kennung> ab. Einseitige (bedeckte) Punkte sind mit Gewicht 1 verankert und dürfen nur nach innen. Die Augenpartie ist Lücke (`Meshfiguraugenhoehle`): sonst zog der Rest sie in die Augenmulde des Netzes.',
          'Normalensuche (Option rest_kandidaten, Vorgabe 16): bei doppelwandigen Netzen sucht der Eigenmorph unter den nächsten Proben die nächste mit passender Normale — Nase 48 → 91 % der Punkte mit Gewicht; '
          'in der Anpassung selbst (kandidaten, Vorgabe 1) zog dieselbe Suche Lippen und Kinn 6–12 mm vor das Netz (29.09.2026). Ein Eigenmorph wird unter demselben Namen neu abgelegt; der Fingerabdruck der Stellung '
          'trägt seit 27.09.2026 den Dateistand.']),
        ('Textur',
         ['Je Texel der fünf Kacheln die Netzfarbe: KD-Baum über 2 Mio. Proben, Fußpunkt auf der Fläche der nächsten Probe, UV bilinear (bis 27.09.2026 die Farbe AN der Probe — die Kachel war ein Mosaik aus 3–8-px-Zellen). '
          'Am Körper zählt nur Hautfarbe; darunter eine Füllschicht je Käfigpunkt, damit Lücken die Netzfarbe aus der Nähe bekommen. `Meshfigurtexelpruefung` verwirft entsättigt-dunkle Treffer (Spaltschatten) und Ausreißer '
          'gegen ein 96-px-Umfeld und füllt alle Löcher mit dem örtlichen Hautton (daher kamen die braunen Klumpen).',
          'Gebacken wird mit `G9texturbacken` über der auf den Hautton getönten Daz-Haut. Die Iris misst `Meshfiguriris` im Ring 0,35–0,9 Irisradius um die Landmarken 468/473; `Meshfiguraugenbild` färbt die Iris von '
          'G9_Eyes01_D.jpg darauf. Flecken in der Textur zuerst im Netz suchen: Hunyuan füllt ungesehene Stellen mit einfarbigen Zellen, die Figur übernimmt sie treu.']),
        ('Eigenes Kopfnetz',
         ['Optional ein zweites Netz nur für den Kopf (Hunyuan-Gesicht): `Meshfigurkopfnetz` findet den Kopf (bis zu 6 × 8 Ansichten, 478 Punkte aus 15 Nahaufnahmen), `Meshfigurkopfabgleich` legt ihn mit Umeyama '
          '(mit Maßstab) auf die Gesichtspunkte des Körpernetzes; Schnitt quer zur Halsachse Schulter → Ohrenmitte. Angeglichen wird der KÖRPER an den Kopf (`Meshfigurfarbangleich`: Rumpf vorn, 12–45 cm unter der Halsebene, '
          'gegen 15 Hautstellen im Gesicht; Grenzen 0,25 … 4); die untersten 35 mm des Kopfes werden an der Naht in die Körperfarbe überblendet (`Meshfigurnaht`). Scheitert der Kopf, läuft der Lauf mit dem Körpernetz, '
          'der Grund steht in erkennung.kopf.fehler.']),
    ]

    #: (Was, Befund) — Grenzen, die jede Session kennen muss, bevor sie ein Ergebnis für gut oder schlecht erklärt.
    GRENZEN = [
        ('Das Netz ist die Obergrenze', 'Kein Fit holt mehr heraus, als das Netz hat: Hunyuan erfand bei Damira die Rückseite, Rücken und Beinrückseiten waren 1–2 cm zu dick; die echte Damira liegt 8,6 mm vom Netz '
                                       '(posiert, Regler fest, Maßstab frei). Darum misst der Testfall zweierlei: den Abstand zum Netz (das Ziel) und zur Referenz (Obergrenze durch die Netzgüte). Stand 27.09.2026.'),
        ('Landmarken des Netzes erst auf die Fläche prüfen', 'Bei Edgars Körpernetz lagen 126 von 478 Landmarken mehr als 8 mm neben der Fläche, 100 in der Luft vor dem Gesicht; die Anpassung zog Nase, '
                                                             'Lippen und Kinn dorthin. Seit 29.09.2026 legt `Meshfigurlandmarkenflaeche` sie vor der Anpassung auf die Fläche.'),
        ('Finger und Zehen', 'In Bild-zu-3D-Netzen verkleben Finger und Zehen; sie zählen mit Gewicht 0 bzw. schwach. Das Ergebnis ist dort kein Maß für die Figur.'),
        ('Kleidung im Netz', 'Sie zieht die Figur nur schwach (Option kleidung weich, kleidungszug 60 %): ohne Zug wird der Rumpf ein Standardkörper — bei Edgar ein Sixpack statt des Bauchs —, zu viel Zug bläht '
                             'die Figur unter weiten Stellen auf (Zauberer in Robe, 12.10.2026: Oberschenkel 103,5 cm mit weich, 51,4 ohne Zug, Grundfigur 53,8). Die Option nah zieht nur Stoff, der an der GRUNDFIGUR '
                             'höchstens kleidung_reichweite_cm (7) entfernt liegt, und legt die Menge einmal fest (Oberschenkel 72,2 cm); bei enger Kleidung (Edgar) ändert sie nichts (Maße ±0,1 cm).'),
        ('Nase und Mund', 'Offen (29.09.2026): 16 von 41 Nasenreglern stehen an der Grenze; der gespitzte Mund des Netzes bleibt 4,7 mm (p90 11 mm) daneben.'),
        ('Regler am Anschlag', 'Auch die acht Regionen-Regler (Hals, Nacken, Unterarm, Handgelenk, Oberschenkel, Oberschenkel hinten, Unterschenkel, Knöchel) haben die Zahl der Regler am Anschlag nicht gesenkt: '
                               'Runde 2 neun mit und ohne sie (drei Läufe, 08.10.2026, Details in meshfigur.md); die Vorgabe der Option koerper.regionen in 2D3D Kleider bleibt AUS.'),
        ('Median verbirgt Fehler', 'Gesichtsform und Augen nie mit einem Median über die ganze Fläche prüfen: der Median von 0,73 mm verbarg, dass die Figur an den Augen 10 mm vor dem Kopfnetz stand. Schnitte alle 2 cm, '
                                   'waagerecht und senkrecht, mit dem Maximum je Schnitt.'),
        ('Die GPU wird geteilt', 'Der Lauf teilt sich die Grafikkarte mit dem Reiter „Mesh" (TRELLIS/Hunyuan): die Stufen sind dann 2–3 × langsamer (27.09.2026). Läufe starten nur nach Ansage.'),
    ]

# -*- coding: utf-8 -*-
"""Architekturmesh3daikleider — Kleider, Haar und ihre Morphs im Datensatz von Mesh3D-AI, und die Entscheidungen dazu (Hilfe → Architektur → Mesh3DAI, 16.10.2026).

Edgar: „Darunter auch die Kleider Morphs, Entscheidungen welche Kleidertypen oder ob sapiens kleider usw".
Die Stücke und ihre Zahlen sind GEMESSEN am 16.10.2026 (`ProjektTemp/_wegwerf/mesh3dai_probe_zeiten.py` — Teile, Punkte, Dreiecke, Außenfläche in Spagat Bild 47;
`mesh3dai_kleider_eintraege.py` — Garderobe: Art, Regler, Varianten). Die Liste der Stücke liest die Seite aus `Ursula1.json` (`figur.kleidung`) und vergleicht sie mit `STUECKE`:
fehlt ein Stück oder ist eins dazugekommen, steht ein Befund da. `ENTSCHEIDUNGEN` trennt, was gebaut, was Vorschlag und was offen ist (Konzept `Docu/konzepte/2026-10-14_mesh3dai-training-konzept.md`).
"""

import json
from pathlib import Path

__all__ = ['Architekturmesh3daikleider']


class Architekturmesh3daikleider:
    #: (Kennung, Teil im Datensatz, Garderobe: Art · Herkunft, Punkte, Dreiecke, außen in Spagat Bild 47, Regler des Stücks, Wert in Ursula1)
    STUECKE = (
        ('daz_anatomie_frau', 'anatomie', 'Kleidung · eigenes Stück (EIGEN), Variante „Ursula"', 4231, 8320, '2.177 (26 %)', '2 (Passform Länge, Weite)', '—'),
        ('dforce_mk_hime_cut_hair', 'haar', 'Haar · Daz „dForce MK Hime Cut Hair Lite", Strähnen (Stranghaar), Stil Bangs C', 364552, 359968, '292.812 (81 %)', '24 (Adjustment: Länge, Abstand …)', 'Farbe #0b0a0a'),
        ('toon_base_female_panty', 'slip', 'Kleidung · Daz „Toon Base Clothing", Variante gelb (umgefärbt)', 9459, 17248, '313 (1,8 %)', '8 (Loosen, Expand, Crotch …)', 'Farbe #0e0b0a'),
        ('lva_pant', 'hose', 'Kleidung · Daz „dForce Leather Viking Armor", Hose', 4892, 8936, '8.357 (94 %)', '6 (Adj Inflate …, Passform)', 'Adj Inflate All −0,27, Farbe #0d1a54'),
        ('mb_joepal_crude_t_shirt_female', 'hemd', 'Kleidung · MakeHuman-Stück als Genesis-Stück (MB, EIGEN)', 1199, 2068, '1.974 (95 %)', '2 (Passform Länge, Weite)', 'Farbe #1a2a6a'),
    )
    KOERPER = ('koerper', 'Genesis-9-Körper, Stufe 0 (Käfig), mit Ursulas 23 Reglern', 27087, 50312, '34.422 (68 %)')

    #: Wie ein Stück im Datensatz entsteht und sich bewegt — gelesen im Code (`mesh3dai_ursula_teile.py`, `Genesis9/folger.py`, `Genesis9/tanzhaut.py`), 16.10.2026.
    BAU = (
        ('Bau in der A-Pose', 'Jedes Stück wie im Browser angefragt (`G9garderobeapi._kleid` mit `getragen` und `rang`: Lagen gegeneinander, Abstand zur Haut 3 mm), EINMAL für die ganze Reihe; '
         'Teile über `Kleidermodellbau._teile`, Farbe = die Umfärbung des Modells (`figur.kleidung[…].farbe`).'),
        ('Kleider-Morphs (Auto-Follow)', 'Ein Stück folgt den Körperreglern über seine drei nächsten Körperpunkte (Kehrwert des Abstands, `G9folger`) — wie Daz’ Projektion; wo das Stück eigene Morphe '
         'mit demselben Kanalnamen mitbringt, gelten SEINE Deltas. Seit 16.10.2026 abends sieht jedes Outfit viele Körper: die vier Jobs und reihum die 40 Formvarianten (Abschnitt 3).'),
        ('Regler der Stücke', 'Daz-Anpassungen (Loosen, Inflate, Längen beim Haar) und die eigenen Passform-Regler Länge/Weite (`passform:*`, jedes Kleidungsstück). Im Datensatz fest: '
         'nur `Adj Inflate All` −0,27 an der Hose ist gestellt.'),
        ('Gewichte', 'Kleidung: die Gewichte des Körpers darunter (drei Projektionsnachbarn gemischt), auf die 138 Knochen; Haar: Gewichte vom nächsten Körperpunkt.'),
        ('Bewegung', 'Je Pose lineare Hautmischung mit diesen Gewichten (`G9tanzhaut`) — KEINE Gelenkkorrekturen (JCM), KEINE Stoffsimulation (dForce), KEINE Kollision je Pose. '
         'Ob Stoff in einer Pose in die Haut sticht, ist im Datensatz nicht gemessen.'),
        ('Etiketten', 'Jedes Dreieck weiß aus dem Bau, zu welchem Teil es gehört (Körper, Anatomie, Haar, Slip, Hose, Shirt) — die Etiketten sind exakt, nicht geschätzt. '
         'Das Netz bekommt sie NICHT (nur Lage und Farbe); die Seite nutzt sie für die Zeilen „Nur Körper“ und „Kleider“.'),
    )

    #: (Frage, Optionen, Stand, Begründung / Quelle)
    ENTSCHEIDUNGEN = (
        ('Woher kommen die Kleider im Datensatz?', 'Genesis-Garderobe · GarmentCode-Schnitte · aus Fotos/Netzen geschnittene Stücke',
         'GEBAUT: die Outfits der vier Jobs aus der Genesis-Garderobe', 'Die Etiketten sind exakt bekannt, die Stücke haben Rig, Morphe und Passform (14.10.2026).'),
        ('Sapiens im Datensatz?', 'Etiketten aus dem Bau · Sapiens/SAM 3 auf Renderings',
         'GEBAUT: aus dem Bau, kein Sapiens', 'Sapiens erzeugt keine Kleider, nur Etiketten je Fläche — im Datensatz sind sie schon exakt. Sapiens gehört in die BASISLINIE (die heutige Anpassung an echten Netzen).'),
        ('Was gibt das Netz für Kleider aus?', 'a) Katalogwahl je Region (Top-k) + Passform + Farbe · b) Stück aus dem Netz schneiden (Etikett → `Fotostuecke`/`Blendimportstuecke`) · c) GarmentCode-Schnittmaße',
         'NICHT GEBAUT — Vorschlag: a), b) als Rückfall; c) nicht bewertet', 'Konzept 14.10.2026, Abschnitt 5: die Messung (Hülle/Abstand wie bei der Frisurwahl) entscheidet unter den Kandidaten des Netzes. Heute gibt das Netz keine Kleider aus.'),
        ('Eigenes Netz für Kleider?', 'Köpfe am selben Rückgrat (Teile je Punkt, Katalogwahl je Region) · eigenes Netz, das die Form eines Stücks erzeugt (z. B. AIpparel)',
         'VORSCHLAG: Köpfe am Rückgrat', 'Für die Wahl reicht das Merkmal der ganzen Figur, das schon Form und Haltung trägt; die Etiketten je Punkt liegen exakt im Datensatz. Ein erzeugendes Netz ist ein eigenes '
         'Großprojekt: AIpparel (09.10.2026 geprüft) hat 27,2 GB Gewichte, ein anderes Ausgabeformat als `params.json` und ist auf Blackwell ungeprüft (`schnittmuster-aipparel.md`).'),
        ('Welche Kleidertypen?', 'Regionen Oberteil · Hose/Rock · Schuhe · Haar · Zubehör; Garderobe heute 700 Einträge',
         'OFFEN', 'Die vier Jobs tragen: Ursula1 Slip, Hose, Shirt, Haar, Anatomie · Damira0 Haar · Mann1 Haar, T-Shirt, Boxershorts · Matt0 Anatomie. Kleid, Rock, Robe, Mantel, Hut, Schuhe fehlen — '
         'für einen Kleiderkopf braucht es Modelle damit (je Kleidertyp 5–10, Vorschlag 16.10.2026).'),
        ('Kleider-Morphs variieren?', 'feste Stellung · Körpervarianten (Auto-Follow folgt) · Passform zufällig',
         'GEBAUT: Körpervarianten', '40 Formvarianten (Abschnitt 3); die Kleidung wird auf jeder neu gebaut und folgt ihrer Körperform über Auto-Follow (`G9folger`). Passform bleibt 0.'),
        ('Stoff simulieren?', 'gehäutet wie heute · dForce/Stoffschwung je Pose',
         'GEBAUT: gehäutet', 'Im Browser werden enge Stücke ebenfalls nicht simuliert (`G9stoff.entscheiden`, p90 Abstand < 5 cm). Lose Stücke (Rock, Kleid) fehlen im Datensatz.'),
        ('Haar?', 'alles Haar als Außenfläche · Frisur als Katalogwahl ausgeben',
         'GEBAUT: alles Haar (Fassung 3); Ausgabe OFFEN', 'Das Strähnenhaar sind 80,6 % aller Dreiecke (359.968 von 446.852) und 22 % der Punkte. Ausgabe als Frisurwahl wie `Meshfigurfrisur` (Vorschlag).'),
    )

    @classmethod
    def kontext(cls, jobs=()):
        """`jobs` = `Architekturmesh3dairegler.jobs()` (was die vier Trainingsjobs tragen)."""
        from django.conf import settings
        datei = Path(settings.HUMANBODY_MODELS_DIR) / 'Ursula1.json'
        im_modell = list(json.loads(datei.read_text(encoding='utf-8'))['figur'].get('kleidung') or {})
        bekannt = [s[0] for s in cls.STUECKE]
        befund = None
        if sorted(im_modell) != sorted(bekannt):
            befund = 'Ursula1.json trägt %s, die Tabelle nennt %s — die Zahlen beschreiben nicht mehr das heutige Modell.' % (', '.join(im_modell), ', '.join(bekannt))
        stuecke = [{'kennung': k, 'teil': t, 'art': a, 'punkte': p, 'dreiecke': d, 'aussen': au, 'regler': r, 'wert': w}
                   for k, t, a, p, d, au, r, w in cls.STUECKE]
        return {'stuecke': stuecke, 'koerper': cls.KOERPER, 'dreiecke': cls.KOERPER[3] + sum(s['dreiecke'] for s in stuecke),
                'punkte': cls.KOERPER[2] + sum(s['punkte'] for s in stuecke), 'bau': cls.BAU, 'entscheidungen': cls.ENTSCHEIDUNGEN, 'befund': befund, 'jobs': list(jobs)}

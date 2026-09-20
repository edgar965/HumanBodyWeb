# -*- coding: utf-8 -*-
"""Bildmodellzielkatalog — die Felder der Schritte „Zielnetz" und „Textur".

Aus `Bildmodellkatalog` herausgelöst (20.09.2026, die Datei stand bei 295 Zeilen, als
`weg`, `gelenkhoehen`, `kopfmasse` und `textur_nebenbilder` dazukamen). Form wie dort:
je Feld `(feld, name, [(wert, name, erklärung)], vorgabe)`.
"""

__all__ = ['Bildmodellzielkatalog']


class Bildmodellzielkatalog:
    FELDER = [
        (
            'weg',
            'Weg zum Zielnetz',
            [
                ('schaetzer', 'Aus dem 3D-Schätzer', 'SMPL-X-Betas, dann Umriss und Maße'),
                ('silhouette', 'Aus den Silhouetten',
                 'Grundfigur → Umriss → Regler, drei Runden; Kopfform vom Gesichtsschätzer'),
                ('silhouette_rein', 'Nur Silhouetten', 'wie „Silhouetten", Kopf aus der Grundfigur'),
            ],
            'silhouette',
        ),
        (
            'symmetrie',
            'Symmetrie',
            [
                ('an', 'Symmetrisch', 'Links und rechts gemittelt (Daz-Figuren sind symmetrisch)'),
                ('aus', 'Wie geschätzt', ''),
            ],
            'an',
        ),
        (
            'groesse',
            'Körpergröße',
            [
                ('schaetzer', 'Aus dem Schätzer', 'Relativ zum Durchschnitt beider Modelle'),
                ('basis', 'Wie die Grundfigur', '170 cm bleiben'),
                ('cm', 'Angabe in cm', 'Feld „Größe cm"'),
            ],
            'schaetzer',
        ),
        (
            'umriss',
            'Umriss der Fotos',
            [
                ('an', 'Silhouette Zeile für Zeile',
                 'Breiten von vorn/hinten, Vorder- und Rückkante von der Seite formen das Ziel'),
                ('aus', 'Aus', 'Nur Maße und Eingaben'),
            ],
            'an',
        ),
        (
            'fotomasse',
            'Maße aus den Fotos',
            [
                ('an', 'Silhouette formt das Ziel',
                 'Hüfte, Taille, Oberschenkel, Wade (vorn), Brust-, Bauch-, Gesäßtiefe (Seite)'),
                ('aus', 'Nur Eingaben', 'Das Ziel bleibt der Schätzer; das Popup formt'),
            ],
            'an',
        ),
        (
            'gelenkhoehen',
            'Gliedlängen aus dem Rig',
            [
                ('an', 'Schulter, Ellbogen, Handgelenk, Hüfte, Knie, Knöchel',
                 'Höhen aus dem YOLO-Rig der Körperbilder vorn/hinten, geeicht an Ursula (`G9rigmasse`) — '
                 'nur im Weg „Silhouetten"'),
                ('aus', 'Aus', 'Gliedlängen bleiben die der Grundfigur (skaliert)'),
            ],
            'an',
        ),
        (
            'kopfmasse',
            'Kopfmaße aus dem Körperfoto',
            [
                ('an', 'Kopfbreite aus den Ohren, Kopfhöhe aus dem Kinn',
                 'openpifpaf/ViTPose/YOLO im Körperbild vorn, geeicht an Ursula — nur im Weg „Silhouetten"; '
                 'eine Eingabe im Popup geht vor'),
                ('aus', 'Aus', 'Kopf wie Grundfigur bzw. Gesichtsschätzer'),
            ],
            'an',
        ),
    ]

    TEXTUR = [
        (
            'textur',
            'Textur',
            [
                ('foto', 'Fotofarbe in HD (Stufe 2)',
                 'Je Texel aus den Bildern mit Häkchen — Nahaufnahmen über ihr Rig registriert, '
                 'als UDIM 2048² gebacken (python10, ~1–3 min)'),
                ('hautton', 'Hautton (Stufe 1)', 'Daz-Haut auf den Hautton der Fotos getönt'),
                ('aus', 'Daz-Haut', 'Unverändert'),
            ],
            'foto',
        ),
        (
            'textur_nebenbilder',
            'Nebenbilder in der Textur',
            [
                ('an', 'Mit Nebenbildern', 'Nahaufnahmen und Nebenbilder mit Häkchen kommen in die Textur'),
                ('aus', 'Nur Hauptbilder', 'zum Vergleich: was die Nebenbilder bringen (Edgar, 20.09.2026)'),
            ],
            'an',
        ),
    ]

# -*- coding: utf-8 -*-
"""Meshfigurregionenoptionen — die Option `regionen` von „Mesh to 3D" und Mesh-3D (12.10.2026), aus `Meshfiguroptionen` herausgelöst (die Datei stand über 300 Zeilen).

Die Regionen-Regler (`G9koerperregionen`, Eigenmorphe `eigen:region_*`) gab es seit dem 08.10.2026 nur in „2D3D Kleider" (Option `koerper.regionen`). Seit dem 12.10.2026 hat der Reiter „Mesh to 3D" dieselbe Wahl, dazu
vier neue Regler (Oberarm, Schulterpartie, Taille, Hüfte). `Meshfigurkette._regler` liest die Option. Vorgabe aus: am Auftrag „Edgar" (12.10.2026) brachten alle zwölf keinen messbaren Gewinn (`.claude/rules/meshfigur-massterm.md`).
"""

__all__ = ['Meshfigurregionenoptionen']


class Meshfigurregionenoptionen:
    KATALOG = [
        {
            'schluessel': 'regionen',
            'titel': 'Regionen-Regler',
            'art': 'wahl',
            'vorgabe': 'aus',
            'fein': True,
            'werte': [
                ('aus', 'Aus — nur die Daz-Regler (Vorgabe)'),
                ('an', 'An — zwölf Umfangsregler dazu (Hals, Nacken, Oberarm, Unterarm, Handgelenk, Schulterpartie, Taille, Hüfte, Oberschenkel, Unterschenkel, Knöchel)'),
            ],
            'hinweis': 'Regler, die Punkte um die Achse eines Gliedes oder des Rumpfs nach außen oder innen rücken (0,5–1,2 cm je Einheit, −2 … 2). Sie geben der Anpassung mehr Raum, wo ein Daz-Regler am Anschlag steht '
            '(Taille, Hüfte, Oberarm und Schulterpartie haben bei Daz keinen einzelnen Regler). Gemessen: `ProjektTemp/_wegwerf/mesh3d/regionen_neu_pruefen.py`.',
        },
    ]

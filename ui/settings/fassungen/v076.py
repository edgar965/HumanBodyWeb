# -*- coding: utf-8 -*-
"""Fassung 0.76 (14.11.2026) — PyTorch-Migration fertig: numpy und scipy durch torch auf der Karte ersetzt, humanbody_core warm und kalt schneller als die numpy-Fassung."""

FASSUNG = {
    'version': '0.76',
    'date': '2026-11-14',
    'title': 'PyTorch-Migration fertig: Rechnungen in torch auf der Grafikkarte statt numpy/scipy; Figur, Regler und Retarget warm und kalt schneller',
    'author': 'edgar965',
    'body_md': (
        '- **numpy → torch**: humanbody_core, Genesis 9, Mesh-Genesis, Foto-Genesis, KoerperKI und die Ablagen (`.pt` statt `.npz` über '
        '`Npztorch`) rechnen in torch auf der Karte; Hooks sperren neuen numpy-/scipy-Code und Tensoren ohne Gerät.\n'
        '- **humanbody_core als Stapel**: Morphs in einem Zug (`Morphstapel`), Quaternionen als Stapel (`Quatstapel`), Retarget-Bildschleife '
        'und Abstandswahrung als Stapel. Warm gegen numpy: Retarget DEF 1,5–1,8 s → 0,30–0,36 s, Genesis 9 1,7–2,1 s → 0,48–0,58 s, '
        'ein Regler + Rechnen 0,9–1,5 ms → 0,34–0,39 ms; Werte bitgleich bzw. bis 2e-15 (Retarget).\n'
        '- **Kaltstart**: Morph-Pakete erst bei Bedarf auf die Karte, Kerne des Figurpfads im Faden beim Import (`Kernvorlauf`), '
        'YAML über libyaml. Im frischen Prozess Figurbau 300 → 110–156 ms (numpy 160–246 ms), erstes Rechnen mit zwölf Reglern '
        '350–470 → 2–4 ms; der Server wärmt nach dem Start auch Figur und Retarget an (erstes Retarget danach 0,27 s statt 1,6–2,1 s).\n'
        '- **Behoben**: Unterteilung und Hautgewichte der HumanBody-Figur brachen seit dem Einspielen am 14.11. (Flächen uint16 auf der '
        'Karte); `/api/character/skin-weights/` antwortet wieder.\n'
        '- **Mesh-Genesis – Eigen-Kleid**: die Robe des Zauberers als eigenes Stück (Schale + Rock, drapiert, Textur aus PSHuman) in Weg z.\n'
    ),
}

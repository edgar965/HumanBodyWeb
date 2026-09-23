# -*- coding: utf-8 -*-
"""Fassung 0.63 (23.09.2026) — BVH Studio parallel/asynchron, Kopf-Pipelines, Genesis-9-Mimik."""

FASSUNG = {
    'version': '0.63',
    'date': '2026-09-23',
    'title': 'BVH Studio: Retarget asynchron und parallel, Figur sofort sichtbar; '
    'Hilfe → Kopf-Pipelines; Genesis-9-Mimik; Kleidung-ohne-Durchschimmern '
    'wieder abgeschaltet',
    'author': 'edgar965',
    'body_md': (
        'HumanBodyWeb ab `5e5050a`, Wurzel ab `5f0edaf`, VideoToBVH ab '
        '`76ef6e8`, jeweils bis zum Commit „Version 0.63“.\n'
        '\n'
        '- **Retarget-Anfrage asynchron und parallel**: `core/api/retarget.py` auf '
        '`async` + eigenen ThreadPool umgestellt, damit die Rechnung nicht mehr den '
        'geteilten Daphne-Dispatch-Faden blockiert; Retarget-Cache '
        '(`retargetdaten.py`) von `json` auf `ujson` (~3,4× schneller bei großen '
        'Dateien). Derselbe Fund an zwei weiteren Stellen behoben: der Garderobe-'
        'Katalog wurde beim Laden bis zu viermal gleichzeitig angefragt statt '
        'einmal (`genesis9kleidung.js`, fehlende Zusammenfassung gleichzeitiger '
        'Aufrufe), und `/api/bildmodell/<id>/zustand/` (Polling der „Modell aus '
        'Dateien"-Seite alle 1–2 s) lief synchron über denselben einen Faden — '
        'jetzt async.\n'
        '- **BVH Studio, Figur sofort sichtbar**: die Renderschleife startet jetzt '
        'vor dem Laden des Projekts (Kamera, Licht, `OrbitControls` waren zwar '
        'sofort da, aber ohne laufende Schleife blieb der Viewport bis zum Ende '
        'des ganzen Ladevorgangs eingefroren); Effekte-Spur mit eigener '
        'Geschwindigkeitskurve, Standbild-Clip (Taste B).\n'
        '- **Hilfe → Kopf-Pipelines**: FLAME (MICA, PyMAF-X), KeenTools FaceBuilder '
        '(ohne Handarbeit in Blender) und ein Vergleich der Verfahren; eigener '
        'Schritt „Kopf" im Bild-Modell-Ablauf, mehrere Fotos je Kopf.\n'
        '- **Genesis 9, Mimik**: Mimik- und Script-Spur wirken jetzt auch auf '
        'Genesis 9 (bisher nur Lipsync) — 26 Kanäle aus Daz\' `Pose Controls/Head` '
        '(Braue, Auge, Wange, Mund, Nase, Zunge).\n'
        '- **Genesis 9, Schuhe**: die Zehenspitze eines Schuhs hängt jetzt am '
        'starren Sammelknochen `l_toes`/`r_toes` statt an einzelnen, unabhängig '
        'beweglichen Zehengliedern — ein geschlossener Schuh biegt sich nicht '
        'zehenweise.\n'
        '- **Genesis 9, „Kleidung ohne Durchschimmern" (Schicht 2/3) wieder aus**: '
        'die Oberflächenbindung (jeder Stoffpunkt wird auf sein nächstes '
        'Körperdreieck projiziert) hielt Kleidung praktisch vollständig '
        '(„mischung" 0,88–1,0 über fast das ganze Netz) auf die Körperoberfläche '
        'fest — an Stellen mit wechselnder Krümmung (Schulternaht, Schuhsohle) '
        'sprang die Dreieckswahl zwischen Nachbarpunkten und riss die Geometrie '
        'auf. Bis das Verfahren auf wirklich dehnbare, eng anliegende Bereiche '
        'begrenzt ist, bleibt es abgeschaltet — reines Skinning wie vor dem '
        '21.09.2026.\n'
        '- Kleinere Korrektur: „Textur: aus/Hautton" löschte eine schon gebackene '
        'Fotofarbe ersatzlos, statt sie nur nicht neu zu rechnen.'
    ),
}

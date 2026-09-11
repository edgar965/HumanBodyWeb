/**
 * Hilfetexte des BVH-Studios: die Schwebehilfe der Zeitleiste.
 *
 * Reiner Inhalt, kein Code — `zeitleiste_hilfe.js` zeigt den Eintrag, der zur
 * Reihe oder zum Clip unter der Maus gehört. Jeder Text sagt, WAS MAN TUN MUSS
 * (Edgar, 11.09.2026: „hover texte in der Timeline mit hilfe was ich tun muss,
 * z.B. bei Kamera, wie ich die Kamera an der aktuellen Position erzeuge").
 *
 * Schlüssel: die Spurart (`bvh`, `model`, `camera`, `light`, `audio`,
 * `scene_object`, `floor`), `clip_<Cliptyp>` für einen Clip unter der Maus,
 * `lineal` für das Zeitlineal, `gruppe` für die Gruppenköpfe „Licht"/„Szene".
 *
 * Jede Angabe ist gegen den Code geprüft (playback.js Tasten, zeitleiste_*
 * Menüs, lichtsetzen.js Alt+Klick, zeitleiste_modellmenue.js Modellwahl).
 */

export const HILFE_ZEITLEISTE = {
    lineal: {
        titel: 'Zeitlineal',
        text: 'Klick oder Ziehen setzt den Abspielkopf. <b>Leertaste</b> Play/Pause, '
            + '<b>←</b> / <b>→</b> ein Bild vor oder zurück. <b>Alt+Ziehen</b> oder die '
            + 'mittlere Maustaste schiebt die Ansicht, der Regler oben zoomt.',
    },
    gruppe: {
        titel: 'Gruppe',
        text: 'Klick klappt die Gruppe auf oder zu.',
    },
    bvh: {
        titel: 'Animation',
        text: 'Bewegung aus der Bibliothek links per <b>Doppelklick</b> (landet auf der '
            + 'gewählten Spur) oder <b>Ziehen</b> auf den Spurnamen legen — oder '
            + '<b>Rechtsklick</b> hier → Hinzufügen an der Klickstelle. Welche Figur '
            + 'die Bewegung spielt, bestimmt die verknüpfte Modellspur.',
    },
    model: {
        titel: 'Modell',
        text: '<b>Rechtsklick</b> → „Modell wählen" gibt der Spur eine Figur: Gibt es am '
            + 'Abspielkopf schon einen Clip, bekommt der die Figur, sonst entsteht einer '
            + 'über die ganze Länge. Rechtsklick auf den Spurnamen verknüpft die Spur mit '
            + 'einer Animation. <b>Entf</b> löscht die Spur samt Figur.',
    },
    camera: {
        titel: 'Kamera',
        text: 'Spur wählen, Ansicht im Bild einstellen (linke Taste dreht, rechte '
            + 'verschiebt, Rad zoomt), dann <b>K</b>: die Kameraposition liegt am '
            + 'Abspielkopf. Oder <b>Rechtsklick</b> hier → Hinzufügen → Kameraposition an '
            + 'der Klickstelle. Zwischen zwei Positionen fährt die Kamera weich; '
            + '„Aktiv" rechts unter Eigenschaften schaltet die Spur ab.',
    },
    light: {
        titel: 'Licht',
        text: 'Spur wählen, dann <b>Alt+Klick</b> im Bild setzt das Licht dorthin; Farbe, '
            + 'Stärke und Ziel rechts unter Eigenschaften. <b>K</b> oder <b>Rechtsklick</b> → '
            + 'Hinzufügen → Lichteigenschaft hält den Zustand als Keyframe fest — ab zwei '
            + 'Keyframes wird dazwischen überblendet.',
    },
    audio: {
        titel: 'Audio',
        text: '<b>Rechtsklick</b> → Audio-Datei wählen (MP3/WAV/OGG) legt den Clip an der '
            + 'Klickstelle an. Clip ziehen verschiebt den Start; Lautstärke, Ein-/Ausblenden '
            + 'und Offset rechts unter Eigenschaften.',
    },
    scene_object: {
        titel: '3D-Objekt',
        text: '<b>Rechtsklick</b> → 3D-Datei wählen (OBJ/GLB/FBX — MTL und Texturen gleich mit '
            + 'auswählen). Objekt im Bild anklicken und an den Griffen verschieben, oder '
            + '<b>Alt+Klick</b> setzt es an die Stelle. <b>Entf</b> löscht die Spur.',
    },
    floor: {
        titel: 'Boden',
        text: 'Farbe, Textur, Breite und Länge rechts unter Eigenschaften.',
    },
    clip_bvh: {
        titel: 'Bewegungsclip',
        text: 'Ziehen verschiebt, am Rand ziehen kürzt (Trim). <b>S</b> teilt am '
            + 'Abspielkopf, <b>Entf</b> löscht. <b>Rechtsklick</b>: Duplizieren, Smooth, '
            + 'Bodenniveau, als BVH speichern.',
    },
    clip_model: {
        titel: 'Modell-Clip',
        text: 'Ab hier spielt die Animation mit dieser Figur. <b>Rechtsklick</b> → anderes '
            + 'Modell wählen; Ziehen verschiebt, <b>Entf</b> löscht.',
    },
    clip_camera_kf: {
        titel: 'Kameraposition',
        text: 'Klick wählt sie: rechts stehen Position, Rotation, FOV und Interpolation; '
            + '„Aktuelle Ansicht übernehmen" schreibt die jetzige Ansicht hinein. Ziehen '
            + 'verschiebt, <b>Entf</b> löscht.',
    },
    clip_light_kf: {
        titel: 'Licht-Keyframe',
        text: 'Klick wählt ihn — die Werte stehen rechts unter Eigenschaften. Ziehen '
            + 'verschiebt, <b>Entf</b> löscht.',
    },
    clip_audio: {
        titel: 'Audio-Clip',
        text: 'Ziehen verschiebt den Start; Lautstärke, Ein-/Ausblenden und Offset rechts '
            + 'unter Eigenschaften. <b>Entf</b> löscht.',
    },
    clip_object_clip: {
        titel: 'Objekt-Clip',
        text: 'Ab hier ist das Objekt zu sehen. Ziehen verschiebt, <b>Entf</b> löscht.',
    },
};

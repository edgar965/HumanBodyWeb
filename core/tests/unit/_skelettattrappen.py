# -*- coding: utf-8 -*-
u"""JS-Attrappen für die Skelett-Prüfungen — Knochen ohne Three.js.

Führender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass hier
keine Testdatei liegt (wie in `_attrappen.py`).

WARUM ATTRAPPEN UND KEINE SZENE: `Anfangshaltung` ruft nur
`quaternion.set`, `position.set` und `position.copy`. Wer dafür Three.js
lädt, prüft eine fremde Bibliothek mit; wer eine Szene aufbaut, braucht
einen Browser. Beides verdeckt nur, was die Klasse selbst tut.
"""

#: Wert3, Knochen, `spur()` und `pruefe()` — das Vorspiel jedes Skripts.
SKELETT = """
class Wert3 {
    constructor() { this.x = 0; this.y = 0; this.z = 0; this.w = 0; }
    set(x, y, z, w) { this.x = x; this.y = y; this.z = z;
                      if (w !== undefined) this.w = w; return this; }
    copy(a) { this.x = a.x; this.y = a.y; this.z = a.z; return this; }
    als() { return [this.x, this.y, this.z]; }
}
class Knochen {
    constructor(name, eltern) {
        this.name = name; this.parent = eltern || null;
        this.position = new Wert3(); this.quaternion = new Wert3();
    }
}
const spur = (name, werte) => ({ name, values: werte });
const pruefe = (was, ist, soll) => {
    const a = JSON.stringify(ist), b = JSON.stringify(soll);
    if (a !== b) throw new Error(was + ':\\n  ist : ' + a + '\\n  soll: ' + b);
};
"""

#: Die Abschlusszeile, die `Webmodul.laufen` als Ergebnis liest. Fehlt sie,
#: meldet der Helfer „node hat nichts ausgegeben" — was aussieht, als fehle
#: node, und keiner der Vergleiche darüber wäre geprüft worden.
FERTIG = "\nconsole.log(JSON.stringify({fertig: true}));\n"

#: Wurzel, Hüften und ihre Ortsspuren — der Aufbau des Bandai-Falls.
BANDAI_AUFBAU = """
const wurzel = new Knochen('joint_Root');
const hueften = new Knochen('Hips', wurzel);
const wurzelSpur = spur('joint_Root.position', [0, 0, 0, 0, 0, 0]);
const hueftSpur = spur('Hips.position', [1, 2, 3, 4, 5, 6]);
const klip = { tracks: [wurzelSpur, hueftSpur] };
"""

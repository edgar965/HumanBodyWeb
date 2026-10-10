/**
 * Stoffnachfuehrung — der Stoffschwung (dForce) liegt auf der Pose DIESES Bildes, nicht auf der des Bildes, für das der
 * Worker rechnete.
 *
 * WARUM (Edgar, 09.10.2026: „haut scheint durch die Kleider bei der Animation bei Damira", Dance Kurz): Der Worker rechnet
 * mit den Knochenmatrizen des Bildes, in dem der Hauptfaden sie schickte; seine Punkte kommen erst ein paar Bilder später an
 * und standen bis dahin unverändert im Anzeigenetz. Der Körper steht dann schon in einer neueren Pose — der Rock liegt in
 * der alten, mit dem Bein darin. Gemessen 09.10.2026 (Chrome-Tab im Hintergrund, Bilder per Screenshot angestoßen, Damira,
 * Dance Kurz, Zeitmesser um `Genesis9stoffschwung._bild` und `_angekommen`, Abstand der Rockpunkte zum nächsten Hautpunkt):
 * Rundlauf Senden → Antwort 132 bis 917 ms; Rockpunkte mehr als 3 mm im Körper 869 bis 1.932 von rund 7.000 (über 2 cm tief:
 * 300 bis 1.100), die gehäutete SkinnedMesh desselben Stücks im selben Bild in den meisten Bildern 0 (in zweien 308 und 361).
 * Mit dem Versatz unten auf der Häutung von jetzt: 10 und 0 statt 1.530 und 1.932. Im Vordergrund-Tab von Edgar bei 60 Bildern/s
 * nicht gemessen — dort ist der Rundlauf kürzer, die Verzögerung wächst aber mit der Bildzeit des Hauptfadens (Folgerung).
 *
 * Deshalb trägt das Anzeigenetz nicht die Punkte des Workers, sondern deren VERSATZ gegen die Häutung von damals, gelegt auf
 * die Häutung von jetzt:
 *
 *     Punkt = Häutung(Matrizen jetzt) + (Punkt des Workers − Häutung(Matrizen beim Senden))
 *
 * Das Schwingen des Stoffs (Versatz) kommt wie bisher vom Worker und hängt entsprechend nach, der Stoff folgt aber dem Körper
 * ohne Verzug. Die Häutung rechnet wie die GPU (`Stoffhaut.welt` ohne `matrixWorld`), gerechnet 11.000 Punkte je Aufruf, zweimal
 * je Bild. Ohne Versatz (noch keine Antwort) bleibt es bei den Punkten des Workers.
 *
 * Ohne Three — nur Zahlen; `M` ist `Stoffhaut.matrizen(netz)`.
 */
export class Stoffnachfuehrung {

    /** Gehäutete Punkte in der Lage des Netzes (ohne `matrixWorld`), in `ziel` (n · 3) oder neu. */
    static haeutung(netz, M, ziel = null) {
        const a = netz.geometry.attributes;
        const pos = a.position.array, index = a.skinIndex.array, gewicht = a.skinWeight.array;
        const n = a.position.count;
        const aus = ziel && ziel.length === n * 3 ? ziel : new Float32Array(n * 3);
        for (let i = 0; i < n; i++) {
            const x = pos[3 * i], y = pos[3 * i + 1], z = pos[3 * i + 2];
            let sx = 0, sy = 0, sz = 0;
            for (let k = 0; k < 4; k++) {
                const w = gewicht[4 * i + k];
                if (w === 0) continue;
                const o = 16 * index[4 * i + k];
                sx += w * (M[o] * x + M[o + 4] * y + M[o + 8] * z + M[o + 12]);
                sy += w * (M[o + 1] * x + M[o + 5] * y + M[o + 9] * z + M[o + 13]);
                sz += w * (M[o + 2] * x + M[o + 6] * y + M[o + 10] * z + M[o + 14]);
            }
            aus[3 * i] = sx; aus[3 * i + 1] = sy; aus[3 * i + 2] = sz;
        }
        return aus;
    }

    /** Beim Senden: die Häutung, für die der Worker rechnet (`e.haeutSend`). Nur ein Auftrag läuft zur Zeit. */
    static senden(e, M) {
        e.haeutSend = Stoffnachfuehrung.haeutung(e.netz, M, e.haeutSend);
    }

    /** Antwort des Workers (`pos`, Lage des Netzes): der Versatz gegen die Häutung beim Senden. */
    static antwort(e, pos) {
        if (!e.haeutSend || e.haeutSend.length !== pos.length) { e.versatz = null; return; }
        const versatz = e.versatz && e.versatz.length === pos.length ? e.versatz : new Float32Array(pos.length);
        for (let i = 0; i < pos.length; i++) versatz[i] = pos[i] - e.haeutSend[i];
        e.versatz = versatz;
    }

    /** Jedes Bild: die Häutung dieses Bildes plus der Versatz der letzten Antwort ins Anzeigenetz. */
    static anwenden(e, M) {
        if (!e.versatz) return;
        const jetzt = e.haeutJetzt = Stoffnachfuehrung.haeutung(e.netz, M, e.haeutJetzt);
        const attribut = e.anzeige.geometry.attributes.position, aus = attribut.array, versatz = e.versatz;
        if (aus.length !== jetzt.length) return;
        for (let i = 0; i < aus.length; i++) aus[i] = jetzt[i] + versatz[i];
        attribut.needsUpdate = true;
    }

    /** Die Animation steht: der Versatz gilt nicht für die nächste Wiedergabe. */
    static vergessen(e) {
        e.versatz = null;
    }
}

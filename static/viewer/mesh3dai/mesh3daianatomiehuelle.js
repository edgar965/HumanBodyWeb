/**
 * Mesh3daianatomiehuelle — unter einem Kleidungsstück der KI, das das Becken umschließt, wird das Anatomie-Stück der bewegten Figur nicht gezeichnet (31.10.2026).
 *
 * Edgar (Testjob edgar, Standardanimation DanceKurz, mit Bild): „während der Animation [kommt] das Geschlechtsteil aus der hose“. Gemessen im Chrome (Stück grün, 8 Blickrichtungen
 * um das Becken, 400 × 400 px, 1,3 m): in jedem halben Sekundenschritt sichtbar, 207–2.010 Pixel je Bild (eine Richtung bis 784). Es sticht nicht durch den Stoff — `Anatomieverdeckung`
 * fand in keinem Bild einen Punkt „außen“ —, es hängt unter dem Schritt heraus: Die Hose der KI ist aus dem Eingang geschnitten und trägt dessen Form; das Daz-Stück der Genesis-Figur
 * liegt tiefer als ihr Schritt und wird mit anderen Gewichten gehäutet. Die Hautregel der Seite (`Hautmaske`, Stoff bis 25 mm über der Haut) deckt nur 139 der 6.979 Punkte des
 * Stücks und 87 der 482 Randpunkte: die Hose steht am Schritt weiter ab.
 *
 * Regel: Vom Ansatz des Stücks (`Anatomiedurchstich.anker`, Mitte der Randpunkte, Ruhelage) laufen `STRAHLEN` waagrechte Strahlen bis `WEITE_M`. Treffen mindestens `MINDEST` davon Stoff
 * eines sichtbaren Stücks (`Hautverdeckung.stoffe`, ohne Ersatzstücke), umschließt es das Becken — das Stück wird ausgeblendet (`visible`), sonst gezeigt. Gemessen am Testjob edgar:
 * Hose 8 von 8, Uhr 0 von 8. `STRAHLEN`, `WEITE_M` und `MINDEST` sind Setzungen. Ausgeblendet zählt es in der Hautverdeckung nicht mehr (`Hautverdeckung.zaehlt`): die Haut darunter
 * bekommt kein Loch, wer `anwenden` ruft, plant die Hautverdeckung neu, wenn sich etwas geändert hat.
 */
import { Anatomiedurchstich } from '../gemeinsam/anatomiedurchstich.js';
import { Anatomielage } from '../gemeinsam/anatomielage.js';
import { Figurhaut } from '../gemeinsam/figurhaut.js';
import { Hautverdeckung } from '../gemeinsam/hautverdeckung.js';

export class Mesh3daianatomiehuelle {
    static STRAHLEN = 8;
    static WEITE_M = 0.6;
    static MINDEST = 7;

    /** Die Anatomie-Stücke der Figur (starr an die Haut gesetzt, `userData.hautTiefe` — wie `Kleidersichtbarkeit.istKoerperteil`, ohne ersetzende Augen). */
    static stuecke(modell) {
        return Object.values(modell?.clothMeshes || {}).filter(netz => netz?.userData?.hautTiefe > 0 && !(netz.userData.ersetzt?.length > 0));
    }

    /** `anwenden`, dann die Hautverdeckung planen — mit `nurGeaendert` nur, wenn sich eine Sichtbarkeit geändert hat (neue Stufe der Figur). */
    static planen(modell, nurGeaendert = false) {
        if (Mesh3daianatomiehuelle.anwenden(modell) || !nurGeaendert) Hautverdeckung.planen(modell);
    }

    /** Sichtbarkeit der Anatomie-Stücke nach der Regel setzen; → true, wenn sich eine geändert hat (dann die Hautverdeckung neu planen). */
    static anwenden(modell) {
        const stuecke = Mesh3daianatomiehuelle.stuecke(modell);
        if (!stuecke.length) return false;
        const stoffe = Hautverdeckung.stoffe(modell, false, true).filter(s => !s.ersatz);
        // Die Quelle der Figur weiß es selbst (`modell.anatomieUnterHose`, 31.10.2026 nachts: 2d-3d-AI, ein Stück „hose“ aus den Fotos — dessen Punkte liegen über dem Ansatz, kein
        // Strahl trifft sie, und in der Bewegung hing das Stück unter der Unterhose heraus; gesehen im Chrome, EdgarTrip Zeile 2, DanceKurz Bild 618)
        const hose = modell.anatomieUnterHose?.() === true;
        let geaendert = false;
        for (const netz of stuecke) {
            const verdeckt = hose || Mesh3daianatomiehuelle.umschlossen(netz, stoffe);
            const vorher = netz.userData.anatomieHuelle;
            netz.visible = !verdeckt;
            netz.userData.anatomieHuelle = verdeckt;
            if (vorher !== verdeckt) geaendert = true;
        }
        return geaendert;
    }

    /** Umschließt einer der Stoffe (`[{punkte, dreiecke}]`, Ruhelage) den Ansatz des Stücks? */
    static umschlossen(netz, stoffe) {
        const geo = netz.geometry, pos = Anatomielage.lage(geo);
        const anker = pos ? Anatomiedurchstich.anker(pos, Figurhaut.vollerIndex(geo)) : null;
        if (!anker) return false;
        return stoffe.some(s => Mesh3daianatomiehuelle.treffer(s.punkte, s.dreiecke, anker) >= Mesh3daianatomiehuelle.MINDEST);
    }

    /** Wie viele der waagrechten Strahlen vom Anker aus treffen ein Dreieck des Stoffs? Nur Dreiecke, die die Höhe des Ankers überspannen, kommen in Frage. */
    static treffer(P, T, anker) {
        const z = Mesh3daianatomiehuelle, [ax, ay, az] = anker, w2 = z.WEITE_M * z.WEITE_M, kandidaten = [];
        for (let k = 0; k + 2 < T.length; k += 3) {
            const a = 3 * T[k], b = 3 * T[k + 1], c = 3 * T[k + 2];
            if (Math.min(P[a + 1], P[b + 1], P[c + 1]) > ay || Math.max(P[a + 1], P[b + 1], P[c + 1]) < ay) continue;
            if ((P[a] - ax) ** 2 + (P[a + 2] - az) ** 2 > w2) continue;
            kandidaten.push([P[a], P[a + 1], P[a + 2], P[b], P[b + 1], P[b + 2], P[c], P[c + 1], P[c + 2]]);
        }
        let n = 0;
        for (let r = 0; r < z.STRAHLEN; r++) {
            const winkel = 2 * Math.PI * r / z.STRAHLEN, dx = Math.sin(winkel) * z.WEITE_M, dz = Math.cos(winkel) * z.WEITE_M;
            if (kandidaten.some(d => { const t = Anatomiedurchstich._schnitt(ax, ay, az, dx, 0, dz, d); return t > 1e-4 && t <= 1; })) n++;
        }
        return n;
    }
}

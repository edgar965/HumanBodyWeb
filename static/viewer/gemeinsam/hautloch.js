/**
 * Hautloch — die Haut unter VERSCHWEISSTEN Ersatzstücken (Scham aus einer .blend), Three.js-Seite (09.10.2026).
 *
 * Die Stücke bringen ihr Loch fertig mit (`stueckloch.js`: Dreiecke der Haut, Verschiebung der Ringpunkte) und legen ihren Rand
 * selbst auf die Haut, wie sie jetzt ist (`stuecknaht.js`). Hier steht, was das Netz betrifft: `naehen` schreibt die
 * Randverschiebung der Stücke, `nurLoecher` kürzt den Index der Haut, wenn kein anderer Stoff etwas zu rechnen gibt. Die
 * Haut-Rechnung (`hautverdeckung.js`) fragt nur noch nach dem, was bleibt. Aus `hautverdeckung.js` herausgelöst (die Datei war
 * schon 300 Zeilen lang).
 */
import { Hautmaske } from './hautmaske.js';
import { Hauteinzug } from './hauteinzug.js';
import { Figurhaut } from './figurhaut.js';
import { Stueckloch } from './stueckloch.js';
import { Stuecknaht } from './stuecknaht.js';
import { Stucknormalen } from './stucknormalen.js';
import { Hautnaht } from './hautnaht.js';
import { Hautnahtpatch } from './hautnahtpatch.js';
import { Stueckhaut } from './stueckhaut.js';
import { Stueckfeder } from './stueckfeder.js';
import { Protokoll } from './protokoll.js';

export class Hautloch {

    /**
     * Der Rand verschweißter Stücke folgt der Haut, wie sie JETZT ist (`stuecknaht.js`): Verschiebung ins `einzug`-Feld des Stücks.
     * Die Haut im Browser ist nicht die des Imports (gemessen 09.10.2026: Median 2,2 mm, bis 7,8 mm an den Oberschenkeln).
     */
    static naehen(geo, loecher, koerper = null) {
        if (!loecher) {                               // kein verschweißtes Stück (mehr): die Haut bekommt ihr Relief zurück
            if (koerper?.geometry?.getAttribute('nahtf')) Hautnahtpatch.aufheben(koerper);
            return;
        }
        const haut = geo.attributes.position.array;
        if (koerper) Hautloch.reliefNehmen(koerper, geo, loecher);
        for (const { netz, ring } of loecher.ringe) {
            const g = netz.geometry;
            Stueckfeder.zuruecknehmen(netz);          // auf der groben Stufe rechnete die Haut das Stück noch als Ersatzstück
            const r = Stuecknaht.verschiebung(g.attributes.position.array, Figurhaut.vollerIndex(g), ring, haut);
            Hauteinzug.eintragen(netz, { werte: r.werte, gesetzt: r.gefunden, geschnappt: 0, band: 0, weg: null });
            const winkel = Hautloch.normalenAngleichen(netz, geo, ring, r);
            const farbe = koerper ? Stueckhaut.angleichen(netz, koerper, r) : null;
            Protokoll.debug('Stuecknaht', `${netz.name || 'Stück'}: ${r.gefunden} von ${r.ecken} Ringecken (${r.rand} Randpunkte), `
                + `Rand ${r.medianMm} mm (Median), ${r.maxMm} mm (größte) zur Haut gerückt, ${winkel} Normalen an die der Haut angeglichen`
                + (farbe ? `, ${farbe.mitFarbe} Punkte mit der Farbe der Haut überblendet, Durchlicht ${farbe.durchlicht ? 'ja' : 'nein'}` : ''));
        }
    }

    /**
     * Der Haut an der Naht das Relief teilweise nehmen (`hautnaht.js`, `hautnahtpatch.js`): die Normalenkarte der gebackenen Haut trägt
     * Poren und Wellen, der Rand des Stücks nicht. Der Faktor hängt nur an den Ringpunkten — er wird je Geometrie gemerkt.
     */
    static reliefNehmen(koerper, geo, loecher) {
        const punkte = loecher.ringe.flatMap(({ ring }) => Array.from(ring.punkte));
        const schluessel = punkte.join(',');
        if (geo.userData.nahtFaktor?.schluessel !== schluessel) {
            geo.userData.nahtFaktor = { schluessel, faktor: Hautnaht.faktor(geo.attributes.position.array, Figurhaut.vollerIndex(geo), punkte) };
        }
        Hautnahtpatch.eintragen(koerper, geo.userData.nahtFaktor.faktor);
    }

    /**
     * Die Normalen des Stücks am Rand gehen in die der Haut über (`stucknormalen.js`). Der Server liefert die des Stücks allein; sie
     * bleiben als `userData.nahtRuhe` erhalten, jeder Lauf rechnet von dort (keine Mischung aus der Mischung). Die Ruhe der
     * Felder-Normalen (`Genesis9normalen`) bekommt die neuen Werte, sonst setzte ein Regler sie auf die alten zurück.
     * @returns Zahl der geänderten Punkte
     */
    static normalenAngleichen(netz, hautGeo, ring, naht) {
        const g = netz.geometry, normal = g.getAttribute('normal'), hautNormal = hautGeo.getAttribute('normal');
        if (!normal || !hautNormal) return 0;
        g.userData.nahtRuhe = g.userData.nahtRuhe || Float32Array.from(normal.array);
        const n = Stucknormalen.angleichen(g.attributes.position.array, normal.array, g.userData.nahtRuhe, naht, ring.punkte,
                                           hautNormal.array);
        normal.needsUpdate = true;
        if (g.userData.normalen?.ruhe) g.userData.normalen.ruhe.set(normal.array);
        return n;
    }

    /** Nur verschweißte Stücke, sonst nichts zu maskieren: aus der Haut fallen genau ihre Löcher weg, ohne Einzug und Saumband. */
    static nurLoecher(inst, geo, voll, loecher) {
        const t0 = performance.now();
        const neu = Hautmaske.indexOhne(voll.index, voll.gruppen, new Uint8Array(geo.attributes.position.count), loecher.weg);
        Figurhaut.indexSetzen(geo, neu.index, neu.gruppen);
        delete geo.userData.hautVerdeckt;
        if (loecher.verschiebung) {      // nur die Ringpunkte rücken (`stueckloch.js`), sonst gibt es keinen Einzug
            const werte = new Float32Array(3 * geo.attributes.position.count);
            Stueckloch.verschieben(werte, loecher.verschiebung);
            Hauteinzug.eintragen(inst.bodyMesh, { werte, gesetzt: 0, geschnappt: 0, band: 0, weg: null });
        } else {
            Hauteinzug.setzen(inst.bodyMesh, null, null);
        }
        Protokoll.debug('Hautverdeckung', `${neu.entfernt} Dreiecke unter ${loecher.schluessel.join(', ')} ausgeblendet (verschweißt)`);
        return { verdeckt: 0, dreiecke: neu.entfernt, stuecke: 0, verschweisst: loecher.schluessel, ms: Math.round(performance.now() - t0) };
    }
}

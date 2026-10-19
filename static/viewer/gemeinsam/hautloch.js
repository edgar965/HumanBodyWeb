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
import { Anatomiekarten } from './anatomiekarten.js';
import { Anatomielage } from './anatomielage.js';
import { Stueckfeder } from './stueckfeder.js';
import { Protokoll } from './protokoll.js';

export class Hautloch {

    /** Die Löcher je Geometrie der Haut, wie `naehen` sie zuletzt bekam (nicht in `userData`: die Netze darin wären ein Kreis für jeden Exporter). */
    static _loecher = new WeakMap();
    /** Je Geometrie der Haut die Stücke (`uuid`), für die `vorab` zuletzt genäht hat. */
    static _vorab = new WeakMap();

    /**
     * Der Rand verschweißter Stücke folgt der Haut, wie sie JETZT ist (`stuecknaht.js`): Verschiebung ins `einzug`-Feld des Stücks.
     * Die Haut im Browser ist nicht die des Imports (gemessen 09.10.2026: Median 2,2 mm, bis 7,8 mm an den Oberschenkeln).
     */
    static naehen(geo, loecher, koerper = null) {
        if (!loecher) {                               // kein verschweißtes Stück (mehr): die Haut bekommt ihr Relief zurück
            if (koerper?.geometry?.getAttribute('nahtf')) Hautnahtpatch.aufheben(koerper);
            Hautloch._loecher.delete(geo);
            return;
        }
        const haut = geo.attributes.position.array;
        Hautloch._loecher.set(geo, loecher);          // für `randAbgleichen`, wenn die Karten des Stücks später fertig werden
        if (koerper) Hautloch.reliefNehmen(koerper, geo, loecher);
        for (const { netz, ring } of loecher.ringe) {
            const g = netz.geometry;
            Stueckfeder.zuruecknehmen(netz);          // auf der groben Stufe rechnete die Haut das Stück noch als Ersatzstück
            const r = Stuecknaht.verschiebung(g.attributes.position.array, Figurhaut.vollerIndex(g), ring, haut);
            Hauteinzug.eintragen(netz, { werte: r.werte, gesetzt: r.gefunden, geschnappt: 0, band: 0, weg: null });
            Hautloch.anatomieNachziehen(netz);
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
     * Ausgenommen sind Stücke, die die Karten der Haut selbst zeigen (`Anatomiekarten.traegtHaut`): ihr Rand hat dieselben Poren, das Relief
     * wegzunehmen ergäbe ein verschwommenes Band um das Stück (Edgar, 12.10.2026: „diese verschwommene Naht beim Übergang zum restlichen Körper").
     */
    static reliefNehmen(koerper, geo, loecher) {
        const punkte = loecher.ringe.filter(({ netz }) => !Anatomiekarten.traegtHaut(netz)).flatMap(({ ring }) => Array.from(ring.punkte));
        const schluessel = punkte.join(',');
        if (geo.userData.nahtFaktor?.schluessel !== schluessel) {
            geo.userData.nahtFaktor = { schluessel, faktor: Hautnaht.faktor(geo.attributes.position.array, Figurhaut.vollerIndex(geo), punkte) };
        }
        Hautnahtpatch.eintragen(koerper, geo.userData.nahtFaktor.faktor);
    }

    /**
     * Die Karten eines Stücks sind fertig oder weg (`Anatomiehaut`): Relief der Haut und Farbrand des Stücks neu eintragen — mit oder ohne Angleichung,
     * je nachdem, ob das Stück jetzt die Karten der Haut trägt. Rechnet nichts neu, nur die gemerkten Faktoren (`naehen`) werden anders gesetzt.
     * @returns Zahl der Stücke am Ring
     */
    static randAbgleichen(inst) {
        const koerper = inst?.bodyMesh, geo = koerper?.geometry, loecher = geo ? Hautloch._loecher.get(geo) : null;
        if (!loecher) return 0;
        Hautloch.reliefNehmen(koerper, geo, loecher);
        for (const { netz } of loecher.ringe) Stueckhaut.randSetzen(netz);
        return loecher.ringe.length;
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

    /**
     * Ein Anatomie-Stück rechnet seine Karten an der Lage MIT Einzug (`Anatomielage`, 18.10.2026: ohne ihn an DamiraAlt 7,8–37 mm neben der Haut, Nähte und fremdes
     * Muster). Der Einzug kommt hier, oft nach dem ersten Bake: `Anatomiehaut` zieht nach (ein laufender Abgleich zuerst zu Ende; ein unveränderter Einzug tut nichts).
     */
    static anatomieNachziehen(netz) {
        const inst = Anatomielage.figuren.get(netz);
        if (!inst) return;
        Promise.all([import('./anatomiehaut.js'), inst._anatomieWartet || null])
            .then(([{ Anatomiehaut }]) => Anatomiehaut.nachziehen(inst))
            .catch(fehler => Protokoll.warnung('Hautloch', `Anatomie nachziehen: ${fehler.message}`));
        // Was durch die Kleidung sticht, ausblenden (`anatomieverdeckung.js`, 19.10.2026) — die Naht läuft nach jedem An- und Ausziehen.
        import('./anatomieverdeckung.js').then(({ Anatomieverdeckung }) => Anatomieverdeckung.planen(inst))
            .catch(fehler => Protokoll.warnung('Hautloch', `Anatomieverdeckung: ${fehler.message}`));
    }

    /**
     * Während eine Stufe nachlädt, wartet die Maske (`Hautverdeckung._rechnen`) — die Löcher verschweißter Stücke kosten keine Rechnung und kommen
     * sofort (19.10.2026: in `/Charakter/` stand die Scham auf der groben Stufe 5 s lang ohne Loch). Nur auf einer Haut ohne Maske der Kleider
     * (`hautVerdeckt`): eine schon gezeigte Maske bleibt stehen, bis die neue fertig ist. Neu genäht wird, sobald ein Stück neu gebaut ist (die feine
     * Fassung kommt oft vor dem feinen Körper — ohne Naht stand ihr Rand dort neben dem groben Loch). @returns der Stand von `nurLoecher` oder null
     */
    static vorab(inst, stuecke) {
        const koerper = inst?.bodyMesh, geo = koerper?.geometry, voll = geo?.userData?.indexVoll;
        if (!geo?.index || !voll || geo.userData.hautVerdeckt) return null;
        const schluessel = stuecke.map(([, netz]) => netz.uuid).join('|');
        if (Hautloch._vorab.get(geo) === schluessel) return null;
        const loecher = Stueckloch.maske(stuecke, voll.index.length / 3, geo.attributes.position.array);
        if (!loecher) return null;
        Hautloch._vorab.set(geo, schluessel);
        Hautloch.naehen(geo, loecher, koerper);
        return Hautloch.nurLoecher(inst, geo, voll, loecher);
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

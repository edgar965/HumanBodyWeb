import studio from '@theatre/studio';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/**
 * Sequenzspuren — ein Theatre-Objekt in die Zeitleiste bringen.
 *
 * ANLASS (Edgar, 11.09.2026): „das Modell erscheint nicht in der Timeline".
 * `sheet.object()` legt ein Objekt mit STATISCHEN Werten an. Das steht in der
 * Gliederung (Outline) des Studios — der Sequenz-Editor, die Zeitleiste,
 * zeigt aber nur Objekte, von denen mindestens ein Wert SEQUENZIERT ist, also
 * eine Spur hat. Kamera und die drei Lichter haben ihre Spuren aus
 * `theatre-state.json`; alles, was später geladen wird, hatte keine — seit
 * der ersten Theatre-Fassung (08.03.2026), das war nie anders.
 *
 * DER WEG ÜBER DIE INTERNE SCHNITTSTELLE: Theatre.js 0.7 bietet öffentlich
 * kein „sequenziere diesen Wert". Der Knopf im Studio ruft in einer
 * Transaktion des INTERNEN Studios (`window.__TheatreJS_StudioBundle._studio`)
 * `stateEditors.coreByProject.historic.sheetsById.sequence
 *  .setPrimitivePropAsSequenced(adresse)` auf; das öffentliche
 * `studio.transaction` reicht `stateEditors` nicht durch. Theatre.js wird seit
 * 0.7.2 (2024) nicht weiterentwickelt — die Schnittstelle bleibt, wie sie ist.
 * Fehlt sie doch, bleibt das Objekt in der Gliederung, und im Log steht warum.
 *
 * SCHLÜSSELBILDER werden direkt geschrieben (`setKeyframeAtPosition`), NICHT
 * über `set()` bei verschobener `sequence.position`: Der Setter von `position`
 * PAUSIERT die Sequenz — eine Figur mitten im Abspielen zu laden, hielte die
 * Kamerafahrt an.
 */
export class Sequenzspuren {

    /** Geradlinig zwischen zwei Schlüsselbildern (Theatre-Vorgabe ist ease-in-out). */
    static LINEAR = [0.5, 0.5, 0.5, 0.5];

    /**
     * Alle Blattwerte ohne Spur sequenzieren, je ein Schlüsselbild bei 0 s
     * mit dem Ist-Wert. Vorhandene Spuren bleiben unangetastet — beim
     * Rückgängig kommt eine Figur mit ihren alten Schlüsselbildern zurück.
     * @returns die neu angelegten Pfade
     */
    static anlegen(objekt) {
        const intern = Sequenzspuren.intern();
        if (!intern || !objekt) return [];
        const vorhanden = Sequenzspuren.spuren(objekt);
        const neu = Sequenzspuren.pfade(objekt.value)
            .filter(pfad => !vorhanden.has(JSON.stringify(pfad)));
        if (!neu.length) return [];
        Sequenzspuren._sequenzieren(intern, objekt, neu);
        Sequenzspuren._schreiben(intern, objekt, Sequenzspuren.spuren(objekt),
            neu.map(pfad => [pfad, 0, Sequenzspuren.wert(objekt.value, pfad)]));
        return neu;
    }

    /**
     * Schlüsselbilder `[[pfad, zeit, wert, griffe?], …]` setzen; die alten
     * Schlüsselbilder dieser Pfade fallen weg, fehlende Spuren entstehen.
     * @returns false, wenn die interne Schnittstelle fehlt
     */
    static setzen(objekt, bilder) {
        const intern = Sequenzspuren.intern();
        if (!intern || !objekt) return false;
        const pfade = Sequenzspuren._eindeutig(bilder.map(([pfad]) => pfad));
        const vorhanden = Sequenzspuren.spuren(objekt);
        Sequenzspuren._sequenzieren(intern, objekt,
            pfade.filter(pfad => !vorhanden.has(JSON.stringify(pfad))));
        const spuren = Sequenzspuren.spuren(objekt);
        Sequenzspuren._leeren(intern, objekt, spuren, pfade);
        Sequenzspuren._schreiben(intern, objekt, spuren, bilder);
        return true;
    }

    // -- Lesen ----------------------------------------------------------------

    /** Das interne Studio — oder null mit Warnung. */
    static intern() {
        const intern = window.__TheatreJS_StudioBundle?._studio;
        if (typeof intern?.transaction !== 'function') {
            Protokoll.warnung('sequenzspuren',
                'Internes Theatre-Studio nicht erreichbar — Objekt bleibt ohne Spuren');
            return null;
        }
        return intern;
    }

    /**
     * Spuren des Objekts aus dem gespeicherten Stand:
     * Map pfad(JSON) → { trackId, bilder: [keyframeId, …] }.
     */
    static spuren(objekt) {
        const { projectId, sheetId, objectKey } = objekt.address;
        const spuren = new Map();
        const eintrag = studio.createContentOfSaveFile(projectId)
            ?.sheetsById?.[sheetId]?.sequence?.tracksByObject?.[objectKey];
        if (!eintrag) return spuren;
        for (const [pfad, trackId] of Object.entries(eintrag.trackIdByPropPath || {})) {
            const bilder = eintrag.trackData?.[trackId]?.keyframes || [];
            spuren.set(pfad, { trackId, bilder: bilder.map(bild => bild.id) });
        }
        return spuren;
    }

    /** Pfade aller Blattwerte; Farben (`{r,g,b,a}`) sind ein Blatt. */
    static pfade(wert, vorne = []) {
        if (!Sequenzspuren._verbund(wert)) return [vorne];
        return Object.entries(wert)
            .flatMap(([name, unter]) => Sequenzspuren.pfade(unter, [...vorne, name]));
    }

    static wert(werte, pfad) {
        return pfad.reduce((stand, name) => stand?.[name], werte);
    }

    static _verbund(wert) {
        if (typeof wert !== 'object' || wert === null || Array.isArray(wert)) return false;
        const felder = Object.keys(wert);
        return !(felder.length === 4 && ['r', 'g', 'b', 'a'].every(f => f in wert));
    }

    static _eindeutig(pfade) {
        return [...new Set(pfade.map(p => JSON.stringify(p)))].map(p => JSON.parse(p));
    }

    // -- Schreiben (interne Transaktionen) -------------------------------------

    static _sequenzieren(intern, objekt, pfade) {
        if (!pfade.length) return;
        intern.transaction(({ stateEditors }) => {
            const sequenz = stateEditors.coreByProject.historic.sheetsById.sequence;
            for (const pfad of pfade) {
                sequenz.setPrimitivePropAsSequenced({ ...objekt.address, pathToProp: pfad });
            }
        });
    }

    static _leeren(intern, objekt, spuren, pfade) {
        const volle = pfade.map(pfad => spuren.get(JSON.stringify(pfad)))
            .filter(spur => spur?.bilder.length);
        if (!volle.length) return;
        intern.transaction(({ stateEditors }) => {
            const sequenz = stateEditors.coreByProject.historic.sheetsById.sequence;
            for (const spur of volle) {
                sequenz.deleteKeyframes({ ...objekt.address, trackId: spur.trackId,
                                          keyframeIds: spur.bilder });
            }
        });
    }

    static _schreiben(intern, objekt, spuren, bilder) {
        intern.transaction(({ stateEditors }) => {
            const sequenz = stateEditors.coreByProject.historic.sheetsById.sequence;
            for (const [pfad, zeit, wert, griffe] of bilder) {
                const spur = spuren.get(JSON.stringify(pfad));
                if (!spur) continue;
                sequenz.setKeyframeAtPosition({
                    ...objekt.address, pathToProp: pfad, trackId: spur.trackId,
                    position: zeit, value: wert, snappingFunction: p => p,
                    ...(griffe ? { handles: griffe } : {}),
                });
            }
        });
    }
}

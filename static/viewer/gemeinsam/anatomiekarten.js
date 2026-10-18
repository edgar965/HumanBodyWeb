/**
 * Anatomiekarten — das starre Anatomie-Stück zeigt die Karten der gewählten Haut (Farbe, Normalen, Rauheit) statt einer einfachen Farbe (11.10.2026).
 *
 * Edgar (Bild, „cute girl DAZ" auf dunkler Haut): „Skin änderung funktioniert nicht bei der Scham, die neue skin Textur erscheint da nicht, nur die farbe."
 * Bis dahin setzte `Anatomiehaut` bei einer Haut, deren Ton nicht zum Stück passt, nur eine einfache Farbe im Hautton (die Poren der Haut fehlten).
 *
 * ERSTE FASSUNG dieser Klasse (UV des nächsten Hautpunkts je Punkt des Stücks, im Chrome gesehen): Streifen und Zickzack; mit dem nächsten Dreieck stetig,
 * aber 3 % der Dreiecke zogen die Karte über eine Naht der Haut-UV (Streifen in der Mittelfurche) und am Rand zur Leiste (Karte der Beine statt des Rumpfs)
 * waren die Texel gestreckt. Ein UV je Punkt kann eine Naht nicht darstellen.
 *
 * HIER: Das Stück behält seine UV. `Anatomiebacken` rechnet seine Karten im Atlas des Stücks neu, Texel für Texel von der Stelle der Haut darunter. Diese
 * Klasse hält, was dazu gehört: den Schlüssel (wovon die gerechneten Karten abhängen), das Ablegen am Material und das Zurücknehmen. Die gerechneten Karten
 * gehören dem Netz (`userData.anatomieGebacken`); Texturen der Haut selbst werden nie verändert.
 */
import { Anatomielage } from './anatomielage.js';

export class Anatomiekarten {

    /** Die eigenen Karten des Stücks — auch, solange gerade gerechnete auf dem Material liegen. */
    static original(m) {
        const a = m?.userData?.anatomieHaut;
        return {
            karte: a ? a.karte : m.map,
            normalen: a && 'normalen' in a ? a.normalen : (m.normalMap || null),
            rauheit: a && 'rauheit' in a ? a.rauheit : (m.roughnessMap || null),
        };
    }

    /**
     * Wovon die gerechneten Karten abhängen: die Karten der Haut-Gruppen (Rumpf, Beine …) und die Form des Stücks — samt seinem `einzug` (`Anatomielage.kennung`,
     * 18.10.2026): die Naht schreibt ihn erst, wenn die Maske gerechnet ist, oft nach dem ersten Bake; ein neuer Einzug ist ein neuer Schlüssel. Null ohne Farbkarte
     * der Haut — dann bleibt `Anatomiehaut` bei der einfachen Farbe.
     */
    static schluessel(inst, netz, haut) {
        const teile = [];
        for (const m of [inst?.bodyMesh?.material].flat()) {
            if (!haut.includes(m?.userData?.gruppe) || !m.map?.isTexture) continue;
            teile.push([m.map, m.normalMap, m.roughnessMap].map(t => t?.uuid || '-').join('/'));
        }
        const einzug = Anatomielage.kennung(netz?.geometry), form = einzug === '-' ? netz?.geometry?.uuid : `${netz?.geometry?.uuid}~${einzug}`;
        return teile.length && netz?.geometry?.uuid ? `${form}|${teile.join('|')}` : null;
    }

    /** Die gerechneten Karten zu `schluessel` — `{leer: true}` nach einem Fehlschlag, null, solange nichts gerechnet ist. */
    static gebacken(netz, schluessel) {
        const g = netz?.userData?.anatomieGebacken;
        return g && g.schluessel === schluessel ? g : null;
    }

    /**
     * Das Stück zeigt die gerechneten Karten. `ablage` ist `m.userData.anatomieHaut` (vom Aufrufer angelegt: Karte und Farbe des Stücks) und merkt sich
     * hier noch Normalen und Rauheit sowie die gesetzte Karte (`hautKarte`: so erkennt `Anatomiehaut` eine später angekommene EIGENE Karte).
     */
    static setzen(m, gebacken, ablage) {
        if (!('normalen' in ablage)) {
            ablage.normalen = m.normalMap || null;
            ablage.rauheit = m.roughnessMap || null;
        }
        ablage.hautKarte = gebacken.map;
        m.map = gebacken.map;
        m.normalMap = gebacken.normalMap || null;
        m.roughnessMap = gebacken.roughnessMap || null;
        m.color.copy(gebacken.farbe);
        m.needsUpdate = true;
    }

    /**
     * Zeigt das Stück gerade die gerechneten Karten der Haut? Dann braucht seine Naht keine Angleichung mehr (`Hautloch.randAbgleichen`): Farbe und Poren
     * am Rand sind die der Haut selbst, und jede Überblendung (flache Hautfarbe im Stück, Relief weg an der Haut) machte den Übergang erst verschwommen.
     */
    static traegtHaut(netz) {
        return [netz?.material].flat().some(m => m?.userData?.anatomieHaut?.hautKarte && m.map === m.userData.anatomieHaut.hautKarte);
    }

    /** Normalen und Rauheit des Stücks zurück (Karte und Farbe stellt `Anatomiehaut._zurueck` selbst her). */
    static zuruecknehmen(m, ablage) {
        if ('normalen' in ablage) {
            m.normalMap = ablage.normalen;
            m.roughnessMap = ablage.rauheit;
            delete ablage.normalen;
            delete ablage.rauheit;
        }
        delete ablage.hautKarte;
    }
}

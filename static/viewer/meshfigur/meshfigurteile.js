import { Meshfigurhaarobjekt } from './meshfigurhaarobjekt.js';

/**
 * Meshfigurteile — die Bestandteile des Netzes als eigene Objekte auf der Figur (12.10.2026).
 *
 * Der Schritt „vorschau" (`Meshfigurteile`, Python) legt je Bestandteil, den SAM 3 am Netz gefunden hat und der von der Figur absteht, ein Objekt ab
 * (`ergebnis/teil_<begriff>.glb`, schon in der Ruhelage der Figur) und führt sie in `ergebnis.teile`: `{name, gruppe, objekt: {datei, bewegung, kontakt}}`. Diese Klasse kennt
 * KEINEN Gegenstand — sie lädt, was in der Liste steht (Stab, Bart, Tasche, Flügel …), und schaltet es nach der Gruppe, die der Begriffsvorrat nennt:
 *
 *     haar      mit dem Kästchen „Haare" — der Bart steht neben JEDER Frisur, nicht nur in „Haar aus dem Netz"
 *     sonst     mit dem Kästchen „Kleider" (Gegenstände, Anhänge)
 *
 * Sichtbar je NETZ, nicht je Gruppe (`Meshfigurhaarobjekt`): der Export (`Modellexportinhalt.objekte`) fragt `mesh.visible`.
 */
export class Meshfigurteile {

    constructor(seite, melden) {
        this.seite = seite;
        this.melden = melden;
        this.eintraege = new Map();
        this.haare = true;
        this.kleider = true;
        // Einzeln abgeschaltete Bestandteile (Edgar, 14.10.2026: der kleine weiße Flügel der Ballerina „auch löschen"): je Auftragsseite gemerkt; ein ausgeblendetes Netz fehlt auch im Export.
        this.aus = new Set(Meshfigurteile.gemerkt());
    }

    static schluessel() { return `mesh3d.bestandteile.aus.${location.pathname}`; }

    static gemerkt() {
        try { return JSON.parse(localStorage.getItem(Meshfigurteile.schluessel()) || '[]'); } catch { return []; }
    }

    /** Einen Bestandteil ein- oder ausschalten (unabhängig von „Haare" und „Kleider"). */
    schalten(name, an) {
        if (an) this.aus.delete(name); else this.aus.add(name);
        try { localStorage.setItem(Meshfigurteile.schluessel(), JSON.stringify([...this.aus])); } catch { /* ohne Speicher geht es auch */ }
        this.anwenden();
    }

    /** `[{name, gruppe, an}]` — die Bestandteile, die ein Objekt haben. */
    liste() {
        return [...this.eintraege].map(([name, e]) => ({ name, gruppe: e.gruppe, an: !this.aus.has(name) }));
    }

    /** Die Liste lesen, neue Objekte anlegen und laden, verschwundene aus der Figur nehmen; `gruppe` = die Gruppe der Figur (oder null); `haltung`: die Figur steht in der Haltung des Netzes (`Meshfigurhaarobjekt`). */
    zeigen(z, gruppe, haltung = false) {
        const liste = (((z || {}).ergebnis || {}).teile || []).filter(t => t && t.objekt && t.objekt.datei);
        const namen = new Set(liste.map(t => t.name));
        for (const [name, eintrag] of this.eintraege) {
            if (namen.has(name)) continue;
            eintrag.objekt.objekt?.parent?.remove(eintrag.objekt.objekt);
            this.eintraege.delete(name);
        }
        for (const t of liste) {
            if (!this.eintraege.has(t.name)) {
                const objekt = new Meshfigurhaarobjekt(this.seite, this.melden, {
                    name: `Bestandteil ${t.name}`,
                    datei: e => (((e || {}).teile || []).find(x => x.name === t.name) || {}).objekt,
                });
                this.eintraege.set(t.name, { gruppe: t.gruppe, objekt });
            }
            this.eintraege.get(t.name).objekt.zeigen(z, gruppe, haltung);
        }
        this.anwenden();
    }

    /** Nach jedem Neubau der Figur: die Objekte hängen sich in ihre neue Gruppe. */
    anhaengen(modell) {
        for (const { objekt } of this.eintraege.values()) objekt.anhaengen(modell.group, modell.skelett);
        this.anwenden();
    }

    /** Die Kästchen „Haare" und „Kleider" der Schalterreihe. */
    sichtbar(haare, kleider) {
        this.haare = haare;
        this.kleider = kleider;
        this.anwenden();
    }

    get vorhanden() { return this.eintraege.size > 0; }

    anwenden() {
        for (const [name, { gruppe, objekt }] of this.eintraege) objekt.sichtbar((gruppe === 'haar' ? this.haare : this.kleider) && !this.aus.has(name));
    }
}

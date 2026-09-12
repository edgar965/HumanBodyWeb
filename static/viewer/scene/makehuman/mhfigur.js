import * as THREE from 'three';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Netzgeometrie } from '../../gemeinsam/netzgeometrie.js';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Mhkleidstueck } from './mhkleidstueck.js';
import { Knochenbau } from '../../gemeinsam/knochenbau.js';
import { Eigenhaut } from '../../gemeinsam/eigenhaut.js';
import { Figurbasis } from '../figurbasis.js';

/**
 * MhFigur — der MakeHuman-Basiskörper (hm08) als Figur der Szene.
 *
 * WARUM (Edgar, 06.09.2026): „Implementiere auch das Hinzufügen eines
 * MakeHuman Modells … unter anderem gibt es garments für MakeHuman, die
 * sollten dann perfekt funktionieren."
 *
 * Und genau das ist der Punkt: Die 181 Stücke der Kleiderbibliothek sind
 * MakeHuman-Stücke mit einer `.mhclo`-Zuordnung auf DIESEN Körper. Auf der
 * HumanBody-Figur ist ihr Sitz eine Näherung mit sieben Reglern
 * (`mhproxy_anpassen.js`); hier ist er die Rechnung selbst — es gibt keinen
 * Fit-Regler, weil es nichts zu justieren gibt. Zahlen und Herkunft:
 * `MakeHuman/basisnetz.py`.
 *
 * Das Netz kommt in Metern mit Y oben — MakeHumans Achsen sind die von
 * Three.js, es wird nur skaliert. Deshalb `drehen = false`; ein zweites Drehen
 * legte die Figur um 90° gekippt daneben.
 *
 * Dieselben Felder wie `CharacterInstance`, `UmaFigur` und `SmplFigur`, damit
 * Liste, Auswahl, Zählung und Speichern nicht je Quelle unterscheiden müssen.
 * Ein Skelett hat sie nicht.
 *
 * MODELLIERT WIRD MIT MAKEHUMANS EIGENEN REGLERN (06.09.2026, Edgar: „nimm
 * dir den source von makeHuman aus dem web"): 269 Stück, davon neun
 * Makroregler (Geschlecht, Alter, Rasse, Muskeln, Gewicht, Größe,
 * Proportionen, Cup, Festigkeit). Sie stehen in `makro` und `regler` und
 * gehen bei JEDER Netzanfrage mit — deshalb POST statt GET: 269 Werte
 * passen in keine Adresse.
 */
export class MhFigur extends Figurbasis {

    static QUELLE = 'makehuman';
    static ADRESSE = '/api/character/mh-figur/';

    /** Vorgabe-Haut — MakeHumans eigener Grundton ist ein helles Beige. */
    static HAUT = { farbe: '#c8a48a', rauheit: 65, metall: 0, deckkraft: 100 };

    constructor(id, daten = {}) {
        super(id, MhFigur.QUELLE);
        this.modell = daten.modell || 'basis';
        this.presetName = daten.presetName || 'MakeHuman-Basiskörper';
        this.bodyType = 'MakeHuman';
        /** Welche Netzteile sichtbar sind (`koerper`, `helfer`, `gelenke`). */
        this.teile = Array.isArray(daten.teile) && daten.teile.length
            ? [...daten.teile] : ['koerper'];
        /** MakeHumans „Smooth": eine Stufe Catmull-Clark. */
        this.glatt = Boolean(daten.glatt);
        this.haut = { ...MhFigur.HAUT, ...(daten.haut || {}) };
        /** MakeHumans Makroregler, 0..1 (`{gender, age, muscle, …}`). */
        this.makro = { ...(daten.makro || {}) };
        /** Die Detailregler, `{'head/head-age-decr|incr': 0.4}`. */
        this.regler = { ...(daten.regler || {}) };
        /** Getragene Stücke: Kennung -> Aussehen. Das Netz hängt in `clothMeshes`. */
        this.kleidung = { ...(daten.kleidung || {}) };
        this.hoehe = 0;
        this.punktzahl = 0;
    }

    // ------------------------------------------------------------------ Körper

    /**
     * Kleidung zuerst, Körper zuletzt — und das ist keine Geschmacksfrage:
     * Welche Haut ausgeblendet wird, hängt an den getragenen Stücken
     * (`delete_verts`, siehe `MakeHuman/loeschmaske.py`). Andersherum
     * käme der Körper ungemaskt und stünde durch den Stoff.
     */
    async load() {
        for (const kennung of Object.keys({ ...this.kleidung })) {
            await this.anziehen(kennung, this.kleidung[kennung]);
        }
        await this.koerperAufbauen();
        return this;
    }

    /**
     * Den Körper neu holen — nach einer Änderung an Teilen oder Glättung.
     * Die Kleidung bleibt hängen: Sie sitzt auf dem BASISNETZ, nicht auf dem
     * angezeigten, und ändert sich durch die Anzeige nicht.
     */
    async koerperAufbauen() {
        const daten = await Serverabruf.senden(
            `${MhFigur.ADRESSE}${encodeURIComponent(this.modell)}/netz/`, {
                teile: this.teile,
                glaetten: this.glatt,
                // Die Haut unter der Kleidung fällt weg — sonst steht sie an
                // eng anliegenden Stellen durch den Stoff (gemessen: 23,5 %
                // der Punkte des Anzugs liegen innerhalb der Haut).
                verdeckt: this.getragen(),
                ...this.formung(),
            });
        if (daten.fehler) throw new Error(daten.fehler);
        this.geformt = Boolean(daten.geformt);
        this._altenKoerperWeg();
        // `drehen = false`: der Server liefert schon Three-Achsen.
        const geometrie = Netzgeometrie.bauen(daten, THREE, null, false);
        this.bodyMesh = new THREE.Mesh(geometrie, this.hautwerkstoff());
        this.bodyMesh.name = `makehuman_${this.modell}`;
        // ERST das Skelett, DANN das Netz einhängen: Die Bindung braucht die
        // Knochen in ihrer Ruhelage (`Eigenhaut.einhaengen`).
        this._skelettBauen(daten.skelett);
        this._hautBinden(daten.hautgewichte);
        this.hoehe = daten.hoehe || 0;
        this.punktzahl = daten.vertex_count || 0;
        this.bodyType = `MakeHuman · ${this.glatt ? 'geglättet' : 'Basisnetz'}`;
        Protokoll.debug('MhFigur',
            `${this.teile.join('+')}${this.glatt ? ' glatt' : ''}: `
            + `${this.punktzahl} Punkte, ${(this.hoehe * 100).toFixed(1)} cm`);
        return this;
    }

    /**
     * `default.mhskel` aus der Antwort bauen — MakeHumans eigenes Rig.
     *
     * Zuerst abraeumen: `load()` laeuft bei JEDEM Reglerzug erneut (269
     * Modellierregler, dazu Teileauswahl und Glättung). Ohne das hängen nach
     * zehn Zügen zehn Skelette ineinander, und der `SkeletonHelper` zeigt
     * die alten Stellungen mit.
     */
    _skelettBauen(angaben) {
        this.skelett = Knochenbau.abraeumen(this.skelett);
        if (!angaben) return;
        this.skelett = Knochenbau.bauen(angaben, this.group);
    }

    /**
     * Das Netz an MakeHumans eigenes Rig binden — sonst bleibt es beim
     * Abspielen starr, während die Knochen sich bewegen.
     *
     * Die Gewichte stammen aus `default_weights.mhw` und sind durch dieselbe
     * Catmull-Clark-Matrix gelaufen wie die Punkte (`Mhhaut`). Ohne Skelett
     * oder ohne Gewichte hängt hier ein gewöhnliches `Mesh`.
     */
    _hautBinden(hautgewichte) {
        if (this.skelett && hautgewichte) {
            this.bodyMesh = Eigenhaut.binden(this.bodyMesh, this.skelett,
                                             hautgewichte);
        }
        Eigenhaut.einhaengen(this.group, this.bodyMesh, this.skelett);
        this.isSkinned = !!this.bodyMesh.isSkinnedMesh;
        this._kleiderBinden();
    }

    /**
     * Die getragenen Stücke an das FRISCHE Skelett binden.
     *
     * WARUM NACHTRÄGLICH (Edgar, 07.09.2026: „Kleider von MakeHuman
     * animieren immer noch nicht"): `load()` zieht die Kleidung ZUERST an —
     * die Löschmaske des Körpers hängt daran (oben begründet). Zu diesem
     * Zeitpunkt gibt es das Skelett noch nicht, `Mhkleidstueck.anlegen`
     * findet `figur.skelett === null` und lässt ein starres `Mesh` hängen.
     * Im Browser gemessen: `isSkinnedMesh false`, kein `skinIndex` — der
     * Körper lief, der Anzug blieb stehen. Am Server lag es nicht, der
     * schickte die Gewichte mit (163 Knochennamen, keiner davon fehlte im
     * Skelett).
     *
     * Der zweite Grund ist `_skelettBauen`: Es räumt bei JEDEM Aufruf ab
     * und baut neu. Eine Bindung von vorher zeigte danach auf Knochen, die
     * nicht mehr in der Szene hängen — deshalb wird hier IMMER neu
     * gebunden, aus den Rohgewichten am Netz, nicht aus den Attributen der
     * Geometrie: Deren Knochennummern gehören zum alten Skelett.
     */
    _kleiderBinden() {
        if (!this.skelett) return;
        for (const [schluessel, altes] of Object.entries(this.clothMeshes)) {
            const haut = altes?.userData?.hautgewichte;
            if (!haut) continue;
            // NUR aushaengen, nicht entsorgen: `Netzentsorgung.entfernen`
            // gibt Geometrie UND Material frei, und beide werden gleich
            // wiederverwendet.
            this.group.remove(altes);
            const roh = new THREE.Mesh(altes.geometry, altes.material);
            roh.name = altes.name;
            roh.visible = altes.visible;
            roh.userData = altes.userData;
            const neues = Eigenhaut.binden(roh, this.skelett, haut);
            this.clothMeshes[schluessel] = neues;
            Eigenhaut.einhaengen(this.group, neues, this.skelett);
        }
    }

    _altenKoerperWeg() {
        if (!this.bodyMesh) return;
        Netzentsorgung.entfernen(this.group, this.bodyMesh);
        this.bodyMesh = null;
    }

    /** Das Hautmaterial aus `this.haut`. */
    hautwerkstoff() {
        const deckkraft = (this.haut.deckkraft ?? 100) / 100;
        return new THREE.MeshStandardMaterial({
            color: new THREE.Color(this.haut.farbe),
            roughness: (this.haut.rauheit ?? 65) / 100,
            metalness: (this.haut.metall ?? 0) / 100,
            transparent: deckkraft < 1, opacity: deckkraft,
        });
    }

    /** Die Hautwerte ins vorhandene Material übernehmen — ohne Neuladen. */
    hautAngleichen() {
        const werkstoff = this.bodyMesh?.material;
        if (!werkstoff) return;
        werkstoff.color.set(this.haut.farbe);
        werkstoff.roughness = (this.haut.rauheit ?? 65) / 100;
        werkstoff.metalness = (this.haut.metall ?? 0) / 100;
        werkstoff.opacity = (this.haut.deckkraft ?? 100) / 100;
        werkstoff.transparent = werkstoff.opacity < 1;
        werkstoff.needsUpdate = true;
    }

    // ---------------------------------------------------------------- Kleidung

    /** Die Reglerstellung, wie der Server sie erwartet. */
    formung() {
        return { makro: this.makro, regler: this.regler };
    }

    /**
     * Nach einer Reglerbewegung: Körper UND Kleidung neu.
     *
     * Die Kleidung MUSS mit — eine `.mhclo` hängt jeden Stoffpunkt an drei
     * Körperpunkte, und die sind gerade gewandert. Ohne diesen Durchgang
     * steckte die Figur in einem Anzug für ihren früheren Körper.
     */
    async neuFormen() {
        await this.koerperAufbauen();
        for (const kennung of this.getragen()) {
            await this.anziehen(kennung, this.kleidung[kennung]);
        }
        return this;
    }

    /** Ein Stück der MakeHuman-Bibliothek anziehen. */
    async anziehen(kennung, werte = null) {
        const stueck = new Mhkleidstueck(this, kennung, werte);
        await stueck.anlegen();
        return stueck;
    }

    /** Ein Stück ausziehen — Netz weg, Eintrag weg. */
    ausziehen(kennung) {
        Netzentsorgung.ausAblage(this.group, this.clothMeshes,
                                 Mhkleidstueck.schluessel(kennung));
        delete this.kleidung[kennung];
    }

    /** Die Kennungen der getragenen Stücke, in der Reihenfolge des Anziehens. */
    getragen() {
        return Object.keys(this.kleidung);
    }

    // ------------------------------------------------------------------ Größe

    /** Sichtbare Höhe in Metern — Netzhöhe mal Skalierung der Gruppe. */
    sichtbareHoehe() {
        return this.hoehe * (this.group.scale.y || 1);
    }

    /** Auf diese Höhe (Meter) bringen; 0 oder eine fehlende Netzhöhe tut nichts. */
    aufHoehe(meter) {
        if (!(meter > 0) || !(this.hoehe > 0)) return;
        this.group.scale.setScalar(meter / this.hoehe);
        this.group.updateMatrixWorld(true);
    }

    // ------------------------------------------------------------------ Rest

    toJSON() {
        return {
            ...this.grunddaten(),
            modell: this.modell,
            teile: [...this.teile],
            glatt: this.glatt,
            haut: { ...this.haut },
            makro: { ...this.makro },
            regler: { ...this.regler },
            kleidung: { ...this.kleidung },
        };
    }

    static fromJSON(daten) {
        return Figurbasis.ausJSON(MhFigur, daten);
    }
}

import * as THREE from 'three';
import { Serverabruf } from '../../gemeinsam/serverabruf.js';
import { Netzgeometrie } from '../../gemeinsam/netzgeometrie.js';
import { Netzentsorgung } from '../../gemeinsam/netzentsorgung.js';
import { Protokoll } from '../../gemeinsam/protokoll.js';
import { Mhkleidstueck } from './mhkleidstueck.js';

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
 * `core/dienste/mhbasisnetz.py`.
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
export class MhFigur {

    static QUELLE = 'makehuman';
    static ADRESSE = '/api/character/mh-figur/';

    /** Vorgabe-Haut — MakeHumans eigener Grundton ist ein helles Beige. */
    static HAUT = { farbe: '#c8a48a', rauheit: 65, metall: 0, deckkraft: 100 };

    constructor(id, daten = {}) {
        this.id = id;
        this.quelle = MhFigur.QUELLE;
        this.modell = daten.modell || 'basis';
        this.presetName = daten.presetName || 'MakeHuman-Basiskörper';
        this.presetKey = null;
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
        this.group = new THREE.Group();
        this.group.userData.characterId = id;
        this.bodyMesh = null;
        // Felder der HumanBody-Figur, hier leer (siehe Kopf).
        this.clothMeshes = {};
        this.hairMesh = null;
        this.garments = [];
        this.garmentState = {};
        this.morphs = {};
        this.meta = {};
        this.cloth = [];
        this.hairStyle = null;
        this.mhProxies = {};
        this.generatedConfig = null;
        this.selected = false;
        this.isSkinned = false;
        this.rigifySkeleton = null;
    }

    // ------------------------------------------------------------------ Körper

    /**
     * Kleidung zuerst, Körper zuletzt — und das ist keine Geschmacksfrage:
     * Welche Haut ausgeblendet wird, hängt an den getragenen Stücken
     * (`delete_verts`, siehe `core/dienste/mhloeschmaske.py`). Andersherum
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
        this.group.add(this.bodyMesh);
        this.hoehe = daten.hoehe || 0;
        this.punktzahl = daten.vertex_count || 0;
        this.bodyType = `MakeHuman · ${this.glatt ? 'geglättet' : 'Basisnetz'}`;
        Protokoll.debug('MhFigur',
            `${this.teile.join('+')}${this.glatt ? ' glatt' : ''}: `
            + `${this.punktzahl} Punkte, ${(this.hoehe * 100).toFixed(1)} cm`);
        return this;
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

    dispose() {
        Netzentsorgung.baum(this.group);
        if (this.group.parent) this.group.parent.remove(this.group);
    }

    toJSON() {
        return {
            id: this.id,
            quelle: this.quelle,
            presetName: this.presetName,
            presetKey: null,
            bodyType: this.bodyType,
            modell: this.modell,
            teile: [...this.teile],
            glatt: this.glatt,
            haut: { ...this.haut },
            makro: { ...this.makro },
            regler: { ...this.regler },
            kleidung: { ...this.kleidung },
            transform: {
                position: this.group.position.toArray(),
                rotation: [this.group.rotation.x, this.group.rotation.y,
                           this.group.rotation.z],
                scale: this.group.scale.toArray(),
            },
        };
    }

    static async fromJSON(daten) {
        const figur = new MhFigur(daten.id, daten);
        await figur.load();
        const lage = daten.transform;
        if (lage) {
            if (lage.position) figur.group.position.fromArray(lage.position);
            if (lage.rotation) {
                figur.group.rotation.set(lage.rotation[0], lage.rotation[1],
                                         lage.rotation[2]);
            }
            if (lage.scale) figur.group.scale.fromArray(lage.scale);
        }
        return figur;
    }
}

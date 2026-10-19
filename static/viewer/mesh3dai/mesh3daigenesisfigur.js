/**
 * Mesh3daigenesisfigur — Ziel und Ergebnis der Jobseite als Genesis-Figur, gebaut mit dem Code der Charakter-Seite (19.10.2026).
 *
 * Edgar an Damira0Tripo: „Das Modell ist doch okay im Character View … Warum hast du eine andere Implementierung in dieser View?“ — „nutze den gleichen Code, verdammt nochmal!!!“ —
 * „es soll immer der gleiche Code genutzt werden wie der von Charakter“. Bis hierher zeichneten Ziel und Ergebnis ein offline gebautes Anzeigenetz (`Mesh3daiflaechen`) mit eigener Häutung;
 * Loch unter dem Anatomie-Stück, Normalen, Haut unter den Kleidern, Texturen fehlten oder waren nachgebaut. Jetzt: `new Genesis9Modell(…)` + `bauen()` wie `Meshfigurbuehne` (Mesh-3D),
 * Studio und Charakter — Figur und Kleidung, wie sie gespeichert sind (`Mesh3daigenesis` auf dem Server), die Haltung als Daz-Gelenkwinkel (`drehung`, der Server rechnet sie wie ein Posenpreset).
 *
 * Je Feld (Zeile × Ziel/Ergebnis) eine eigene Figur: jedes Feld hat seine eigene Szene (`Mesh3daiansicht`; gezeichnet wird mit einem Renderer für alle, `Mesh3daizeichenflaeche`), ein Objekt hängt nur in einer Szene. Die Wurzel
 * richtet `Mesh3daiausrichtung` über die 138 Gelenke auf das Rig der Probe aus (Ziel: `rig.soll`, Ergebnis: `rig.ausgabe`) — so stehen die Figuren im Rahmen der übrigen Felder.
 * Zeilen: ganzer Körper; nur Körper (nur die Anatomie-Stücke); Kleider (nur Stücke der Art `kleidung`, ohne Körper, Anhänge, Haar, Anatomie); Gesicht (ganze Figur, um den Ausschnitt gerückt).
 * Nicht hier (noch der alte Weg): „Hände und Füße“ (vier Ausschnitte in einem Feld), die Animation (Bilder einer Bewegung), Ergebnisse von Läufen ohne Gelenkwinkel.
 */
import { Genesis9Modell } from '../gemeinsam/genesis9modell.js';
import { Genesis9vorrat } from '../gemeinsam/genesis9vorrat.js';
import { Mesh3daiausrichtung } from './mesh3daiausrichtung.js';
import { Mesh3daiechtmaterial } from './mesh3daiechtmaterial.js';

export class Mesh3daigenesisfigur {
    static ZEILEN = new Set(['koerper', 'koerper_nackt', 'gesicht', 'kleider']);
    static ANATOMIE = /anatomie|genital|penis|vagina|anus/i;
    /** So viele Figuren bleiben im Speicher (je Probe bis zu 8); die ältesten fallen heraus. */
    static GRENZE = 24;
    static _daten = new Map();
    static _figuren = new Map();
    static _nummer = 0;
    /** Die Seite hängt neu ein und zeichnet, wenn eine Figur fertig ist oder eine feinere Stufe ankommt; `nurZeichnen` malt nur ein neues Bild (beide gesetzt von `Mesh3daiseite`). */
    static neuZeichnen = null;
    static nurZeichnen = null;

    /** Alle fertig gebauten Figuren — für Strg+Alt+H (`Genesis9aufbau.stufeSetzen`, wie in Charakter). */
    static modelle() {
        return [...Mesh3daigenesisfigur._figuren.values()].map(e => e.modell).filter(Boolean);
    }

    /**
     * Was nach `bauen()` noch kommt, zeichnet niemand (19.10.2026, gesehen an Damira0Tripo: Scham weiß, Körper grau): Charakter zeichnet in einer Dauerschleife, die Felder hier nur
     * auf Anforderung — Bilder des Vorrats (`Genesis9texturen`), die gebackenen Karten des Anatomie-Stücks (`Anatomiehaut`), Masken und Normalen kommen später und setzen nur
     * `needsUpdate`. Die Wache vergleicht alle `WACHE_MS` die Stände (Versionen von Material, Bild, Index, Attributen) und zeichnet nur bei einer Änderung neu.
     */
    static WACHE_MS = 500;
    static _wache = null;

    static _wacheStarten() {
        const z = Mesh3daigenesisfigur;
        if (z._wache) return;
        z._wache = setInterval(() => {
            if (typeof document !== 'undefined' && document.hidden) return;
            let neu = false, malen = false;
            for (const e of z._figuren.values()) {
                if (!e.modell) continue;
                const stand = z._stand(e.modell);
                if (e.zeichenstand && e.zeichenstand.bau !== stand.bau) neu = true;
                else if (e.zeichenstand && e.zeichenstand.rest !== stand.rest) malen = true;
                e.zeichenstand = stand;
            }
            // Neue Netze brauchen das Einhängen (Ebene, Teile der Zeile); ein spätes Bild, eine Maske, eine Karte nur ein neues Bild — gemessen 19.10.2026 (Mann1, Long Animation
            // Frames): das Neu-Einhängen aller Felder bei jedem Bild kostete den Hauptfaden 1,8 s am Stück, die Texturen warteten dahinter.
            if (neu) z.neuZeichnen?.();
            else if (malen) (z.nurZeichnen || z.neuZeichnen)?.();
        }, z.WACHE_MS);
    }

    /**
     * `bau`: die Netze der Figur (kommt eines dazu, muss das Feld neu einhängen); `rest`: was ein neues Bild braucht (Versionen von Index, Attributen, Bildern, Farbe).
     * `material.version` zählt NICHT: three.js (r170, `renderObject`) setzt bei durchsichtigen doppelseitigen Materialien (Wimpern, Brauen, Scham) in JEDEM Bild zweimal `needsUpdate` — die Wache zeichnete sich selbst an.
     */
    static _stand(modell) {
        const bau = [], teile = [];
        modell.group.traverse(o => {
            if (!o.isMesh) return;
            bau.push(o.uuid.slice(0, 8));
            let summe = o.geometry.index?.version ?? 0;
            for (const a of Object.values(o.geometry.attributes)) summe += a.version;
            teile.push(o.geometry.uuid.slice(0, 8), summe);
            for (const m of [o.material].flat()) {
                if (!m) continue;
                teile.push(m.color?.getHex?.() ?? '', m.opacity, m.visible ? 1 : 0);
                for (const t of [m.map, m.normalMap, m.roughnessMap, m.alphaMap]) teile.push(t ? `${t.uuid.slice(0, 8)}.${t.version}` : '-');
            }
        });
        return { bau: bau.join(','), rest: teile.join(',') };
    }

    /**
     * Die Figur dieses Felds: `undefined` = das Feld zeigt keine Genesis-Figur (alter Weg), sonst `{stand, modell, text}` — `stand` 'baut' | 'fertig' | 'fehler'.
     * @param {object} d der Auftrag der Zeile (`Mesh3daizeile.zeigen`) @param {string} art 'soll' | 'ausgabe'
     */
    static fuer(d, art) {
        const z = Mesh3daigenesisfigur;
        if (!d?.echt || !d.job || !z.ZEILEN.has(d.zeile) || (art !== 'soll' && art !== 'ausgabe') || d.probe?.punktsamen !== undefined || d.probe?.id == null) return undefined;
        const schluessel = [d.job, d.probe.id, art, d.zeile].join('|');
        let e = z._figuren.get(schluessel);
        if (!e) {
            e = { stand: 'baut', modell: null, text: 'Genesis-Figur wird gebaut …' };
            z._figuren.set(schluessel, e);
            z._bauen(e, d, art);
            while (z._figuren.size > z.GRENZE) {
                const [alt, wert] = z._figuren.entries().next().value;
                z._figuren.delete(alt);
                wert.modell?.dispose?.();
            }
        }
        return e.stand === 'ohne' ? undefined : e;
    }

    static _datenHolen(job, nr) {
        const schluessel = `${job}|${nr}`;
        if (!Mesh3daigenesisfigur._daten.has(schluessel)) {
            Mesh3daigenesisfigur._daten.set(schluessel, fetch(`/api/mesh3dai/${encodeURIComponent(job)}/genesis/${nr}/`).then(async antwort => {
                if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
                return antwort.json();
            }));
        }
        return Mesh3daigenesisfigur._daten.get(schluessel);
    }

    static async _bauen(e, d, art) {
        const z = Mesh3daigenesisfigur;
        try {
            const daten = await z._datenHolen(d.job, d.probe.id);
            const haltung = art === 'soll' ? daten.ziel : daten.ergebnis;
            // Ergebnis ohne vorhergesagte Gelenkwinkel (Lauf mit freien Punkten): kein Genesis-Ergebnis — das Feld bleibt beim bisherigen Weg.
            if (art === 'ausgabe' && !haltung) {
                e.stand = 'ohne';
                z.neuZeichnen?.();
                return;
            }
            const figur = { ...daten.figur };
            // Eine Haltung als Winkel ersetzt das Posenpreset (der Server nimmt sonst die Pose). Ohne Haltung (Trainingspaar) steht die Figur in ihrer gespeicherten Pose.
            if (haltung) {
                figur.pose = '';
                figur.drehung = Object.keys(haltung).length ? haltung : null;
            }
            if (d.zeile === 'koerper_nackt') {
                figur.kleidung = Object.fromEntries(Object.entries(figur.kleidung || {}).filter(([k]) => z.ANATOMIE.test(k)));
                figur.garmentcode = [];
            }
            // Eine Kennung je Feld: `Netzstufenstand` führt den Stand je Kennung (die Anzeige „Netz: grob …“ zählt sonst nur eine Figur).
            const modell = new Genesis9Modell(`mesh3dai_${art}_${++z._nummer}`, figur);
            await modell.bauen();
            e.modell = modell;
            e.stand = 'fertig';
            e.text = '';
            z.neuZeichnen?.();
            z._wacheStarten();
            // Die feine Stufe kommt nach (`Genesis9aufbau.progressiv`): danach neu ausrichten und zeichnen.
            modell.fein?.then(() => z.neuZeichnen?.(), () => {});
            // Alle Stufen bis zur Einstellung dauerhaft ablegen lassen, wie in Charakter nach dem Laden (19.10.2026); dieselbe Figur in mehreren Zeilen fragt nur einmal (`Genesis9vorrat._abgelegt`).
            Genesis9vorrat.fuellen(modell).catch(f => console.warn(`Genesis9vorrat: ${f.message}`));
        } catch (fehler) {
            e.stand = 'fehler';
            e.text = `Genesis-Figur nicht gebaut: ${fehler.message}`;
            z.neuZeichnen?.();
        }
    }

    /**
     * Die fertige Figur in das Feld hängen: ausrichten (Gelenke auf das Rig der Probe), Teile der Zeile zeigen, Ansichtsart. Bei jedem Zeichnen — die feine Stufe ersetzt Netze und Skelett.
     * Die Materialien der Figur bleiben unberührt (Code der Charakter-Seite schreibt später selbst hinein, etwa die Karte des Anatomie-Stücks): die einfarbigen Ansichtsarten zeichnet das Feld
     * in einem eigenen Durchgang mit `overrideMaterial` über Ebene 1 (`Mesh3daiansicht.zeichnen`); das Feld gibt die Figur beim Leeren nicht frei (`mesh3daiFremd`).
     */
    static einhaengen(inhalt, e, d, art) {
        const z = Mesh3daigenesisfigur;
        const gruppe = e.modell.group;
        z._ausrichten(gruppe, d.rigBeschreibung?.knochen ?? [], art === 'ausgabe' ? d.probe.rig?.ausgabe : d.probe.rig?.soll, d.teil?.ausschnitte?.[0] ?? null);
        z._teile(e.modell, d.zeile);
        gruppe.traverse(o => { o.frustumCulled = false; o.layers.set(1); });
        gruppe.userData.mesh3daiFremd = true;
        inhalt.userData.genesisErsatz = d.modus === 'textur' ? null : z._ersatz(d.modus);
        inhalt.add(gruppe);
    }

    static _ausrichten(gruppe, knochen, ziel, ausschnitt) {
        if (!ziel?.length) return;
        gruppe.position.set(0, 0, 0);
        gruppe.quaternion.identity();
        gruppe.updateMatrixWorld(true);
        const je = new Map();
        gruppe.traverse(o => { if (o.isBone && !je.has(o.name)) je.set(o.name, o); });
        const a = [], b = [];
        knochen.forEach((k, i) => {
            const bone = je.get(k.name);
            if (!bone || !ziel[i]) return;
            const p = bone.getWorldPosition(bone.position.clone());
            a.push([p.x, p.y, p.z]);
            b.push(ziel[i]);
        });
        if (a.length < 3) return;
        const { quaternion, verschiebung } = Mesh3daiausrichtung.starr(a, b);
        gruppe.quaternion.copy(quaternion);
        gruppe.position.copy(verschiebung);
        if (ausschnitt) gruppe.position.add({ x: ausschnitt.ziel[0] - ausschnitt.mitte[0], y: ausschnitt.ziel[1] - ausschnitt.mitte[1], z: ausschnitt.ziel[2] - ausschnitt.mitte[2] });
        gruppe.updateMatrixWorld(true);
    }

    /** Zeile „Kleider“: nur die Stücke der Art `kleidung` (ohne Anatomie), kein Körper, keine Anhänge, kein Haar. Die anderen Zeilen zeigen alles, was gebaut ist. */
    static _teile(modell, zeile) {
        const kleider = zeile === 'kleider';
        if (modell.bodyMesh) modell.bodyMesh.visible = !kleider;
        for (const netz of Object.values(modell.anhangNetze || {})) if (netz) netz.visible = !kleider;
        for (const [kennung, netz] of Object.entries(modell.clothMeshes || {})) {
            if (!netz) continue;
            netz.visible = !kleider || (netz.userData?.art === 'kleidung' && !Mesh3daigenesisfigur.ANATOMIE.test(kennung));
        }
    }

    /** Ansichtsart wie die übrigen Felder (`Mesh3daiechtmaterial`): „Textur“ = die Materialien der Figur (wie in der Charakter-Seite), sonst EIN Material für alle Netze. */
    static _ersatz(modus) {
        // „Punkte“ und „Oberfläche + Drahtnetz“ gibt es für ein gehäutetes Netz nicht als ein Material — dort die Oberfläche.
        const art = modus === 'punkte' || modus === 'oberflaeche_draht' ? 'oberflaeche' : modus;
        const netz = Mesh3daiechtmaterial.netz(undefined, art);      // `undefined`, nicht `null`: der Mesh-Konstruktor liest die Morphziele der Geometrie
        return netz.material ?? netz.children?.[0]?.material ?? null;
    }
}

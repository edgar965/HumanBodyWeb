/**
 * Meshgenesiskikleiderfeld — die Kleider aus der KI im Feld „Ergebnis“ einer Tripo-Jobseite (20.10.2026 nachts, Server `Meshgenesisergebniskleider`).
 * Die Stücke, die die Testseite wirksam gewählt hat (nur Zeilen aus der KI: k geschnitten, s Schnitt, h Frisur), aus ihrer Ruhelage mit der Haltung der KI gehäutet (`Meshgenesistestnetzbau`, dieselben
 * Matrizen wie die Testseite) und als EINE Gruppe auf das Rig der Probe ausgerichtet (`Meshgenesisausrichtung.starr` von den Gelenken der KI-Figur auf das gezeigte Rig) — wie die Figur daneben.
 */
import * as THREE from 'three';
import { Meshgenesisausrichtung } from './meshgenesisausrichtung.js';
import { Meshgenesisflaechennetz } from './meshgenesisflaechennetz.js';
import { Meshgenesishaeutung } from './meshgenesishaeutung.js';
import { Meshgenesiskartenhaut } from './meshgenesiskartenhaut.js';
import { Meshgenesistestnetzbau } from './meshgenesistestnetzbau.js';
import { Meshfighautstueck } from '../meshfigur/meshfighautstueck.js';
import { Texturweg } from '../gemeinsam/texturweg.js';

export class Meshgenesiskikleiderfeld {
    // z (12.11.2026, „Genesis zuerst“): Stück der Garderobe, Server `Meshgenesistestkikleider`; e (20.11.2026): Methode „Eigen“, an das Netzstück gepasst;
    // p (21.11.2026): Methode „Passend“, das passendste Stück der Kleiderbibliothek aus mehreren Kandidaten
    static WEGE = new Set(['k', 's', 'h', 'f', 'g', 'z', 'e', 'p']);
    /** = `Kleiderverdeckung.TIEFE_KOSTUEM_M` auf dem Server (ProjektTemp/_wegwerf/meshgenesis_kleider_verdeckung.py) */
    static STOFF_TIEFE_M = 0.040;
    // Methoden umbenannt (19.11.2026, Edgar: „Methode: Kleiderbibliothek (ehemals Garderobe) und Drapieren“) — z ist die Kleiderbibliothek, f das Drapieren
    static TEXT = { k: 'aus dem Netz geschnitten', s: 'GarmentCode-Schnitt', f: 'Drapieren', g: 'Schicht aus der KI', h: 'Frisur der Kleiderbibliothek', z: 'Kleiderbibliothek', e: 'Eigen' };

    /** → {gruppe, rig, namen: [Text je Stück], stuecke, liste} oder null (keine KI-Kleider gewählt). `ki.weg(st)`: welcher Weg je Zeile (Vorgabe: der wirksame `st.wahl`;
     *  `Fotogenesistestfigur` nimmt für die Methode „Drapieren“ f, wo es ein Netz hat). `ki.daten`: eine schon geholte Liste (dann kein zweiter Abruf).
     *  `ki.nachzug(ergebnis)`: Stücke, die keine Haut verdecken (Frisur ohne Kostüm, `deckt`), werden nicht abgewartet — sie kommen an ihrer Stelle der Liste in `gruppe`,
     *  `namen` und `stuecke` nach, danach dieser Ruf (Feld neu zeichnen); `ergebnis.nachzug` ist das Versprechen darauf. 23.11.2026 (Edgar: „das soll in 2 s gehen“, „das laden
     *  soll genau so gehen wie bei "Charakter" Seite“ — dort steht die Figur zuerst grob, dann kommt der Rest): an iphone_mit_lidar wartete die Figur 2,5 s auf das Haar (108 MB),
     *  Körper und übrige Stücke lagen schon da. Ohne `nachzug` wie bisher: alle Stücke abwarten. */
    static async laden(ki) {
        let daten = ki.daten;
        if (!daten) {
            const antwort = await fetch(ki.liste);
            if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
            daten = await antwort.json();
        }
        const wegVon = ki.weg ?? (st => st.wahl);
        const matrizen = Meshgenesishaeutung.ausDrehungen(ki.dreh, ki.rig, ki.ruhezentren);
        const gruppe = new THREE.Group();
        const namen = [], stuecke = [];
        // Alle Stücke zugleich holen (08.11.2026, Edgar: „alle modelle sollen innerhalb von max. 5 s angezeigt werden“): vorher wartete jedes Stück auf das vorige — im Log der Seite
        // „Zauberer Alle Textur“ lagen zwischen zwei Stücken 35–75 s, weil nach jeder Textur die Seite neu rechnete (`Fotogenesisseite.nachgeladen`). Gebaut wird weiter in der Reihenfolge der Liste.
        const wahl = (daten.stuecke || []).map(st => ({ st, w: wegVon(st) })).filter(({ st, w }) => st.quelle === 'ki' && Meshgenesiskikleiderfeld.WEGE.has(w) && st[w]?.netz);
        const abrufe = wahl.map(({ st, w }) => Meshgenesisflaechennetz.holen(null, st[w].netz)
            .catch(fehler => { console.warn('Meshgenesiskikleiderfeld: %s nicht geladen (%s)', st.id, fehler.message); return null; }));
        const spaeter = wahl.map(({ st }) => !!ki.nachzug && !Meshgenesiskikleiderfeld.deckt(st));
        const ergebnis = { gruppe, rig: ki.rig, namen, stuecke, kleiderAn: true, liste: daten };
        const platz = [];                                  // Listennummern der eingebauten Stücke, aufsteigend: dort steht ein nachkommendes in gruppe/namen/stuecke
        const einbauen = (i, netz) => {
            const { st, w } = wahl[i];
            if (!netz) return false;
            try {
                // Was keine Haut verdeckt (Frisur, Bart), häutet die Grafikkarte (`Meshgenesiskartenhaut`, 21.11.2026): seine Punkte liest auf der CPU niemand. Die deckenden Stücke bleiben auf
                // der CPU gehäutet — `Fotogenesistestfigur._hautStuecke` rechnet aus ihren gezeigten Punkten die Maske der Haut, Punkt für Punkt wie bisher.
                const mesh = (!Meshgenesiskikleiderfeld.deckt(st) && Meshgenesiskartenhaut.mesh(netz, matrizen)) || Meshgenesistestnetzbau.mesh(netz, matrizen);
                mesh.userData.art = st.art;
                mesh.visible = ergebnis.kleiderAn;          // ein nachkommendes Stück folgt dem Schalter „Kleider“
                const stelle = platz.filter(j => j < i).length;
                platz.splice(stelle, 0, i);
                gruppe.add(mesh);
                gruppe.children.splice(gruppe.children.length - 1, 1);
                gruppe.children.splice(stelle, 0, mesh);
                namen.splice(stelle, 0, `${st.name} (${Meshgenesiskikleiderfeld.TEXT[w]})`);
                const kostuem = Meshgenesiskikleiderfeld.kostuem(st[w]);
                // `netz`: die Animation bindet das Stück an das Skelett der Figur (`Meshgenesisbewegungskleid`); `mesh`: das gezeigte, gehäutete Stück (`Fotogenesistestfigur._hautStuecke`)
                stuecke.splice(stelle, 0, { id: st.id, art: st.art, weg: w, ruhe: netz.ruhe, dreiecke: netz.dreiecke, netz, kostuem, mesh, adresse: st[w].netz });
                return true;
            } catch (fehler) {
                console.warn('Meshgenesiskikleiderfeld: %s nicht geladen (%s)', st.id, fehler.message);
                return false;
            }
        };
        const netze = await Promise.all(abrufe.map((abruf, i) => (spaeter[i] ? null : abruf)));
        // je Stück eine Aufgabe (23.11.2026, Edgar: „löse das“): Oberteil, Hose und Schuhe zusammen hielten ein Bild 40–67 ms an (CPU-Häutung je Stück)
        for (const i of wahl.keys()) if (!spaeter[i] && einbauen(i, netze[i])) await Texturweg.naechsteAufgabe();
        if (spaeter.some(Boolean)) {
            // in einer eigenen Aufgabe: liegt das Stück schon da, baute es sonst im selben Bild wie die Figur (Haar 130 ms + Hülle 81 ms, 23.11.2026)
            ergebnis.nachzug = Promise.all(abrufe.map(async (abruf, i) => {
                if (!spaeter[i]) return;
                const netz = await abruf;
                await Texturweg.naechsteAufgabe();
                if (einbauen(i, netz)) ki.nachzug(ergebnis);
            }));
        } else if (!gruppe.children.length) return null;
        gruppe.userData.meshgenesisFremd = true;          // das Feld gibt die Gruppe beim Leeren nicht frei
        return ergebnis;
    }

    /**
     * Die Stücke in der RUHELAGE der KI-Figur als Stoffe der Hautverdeckung (`inst.hautStuecke`, wie `Meshfigurkleider._hautMelden`, 21.10.2026): die Haut und das Anatomie-Stück der
     * Genesis-Figur im Ergebnis fallen dort weg, wo ein Stück sie verdeckt (`Hautverdeckung`, `Anatomieverdeckung`) — Edgar an Mann1: „aus der Hose kommt Genital heraus“. Die Figur im
     * Ergebnis ist aus denselben Reglern gebaut wie die Figur, auf der die Stücke liegen; ihre Ruhelage ist dieselbe. Haar verdeckt keine Haut (`Hautverdeckung.zaehlt`).
     */
    /**
     * Kostümstück für `hautStuecke` (Eintrag des gewählten Wegs `st[st.wahl]`): Kostüm-Weg A (aus dem Eingang ausgeschnitten, `kostuem` oder Rückhäutung) und die Bausteine-Hüllen
     * (`bausteine/kostuemzeilen.py`). Alle Quellen der Bewegung fragen hier (19.11.2026: Testseite und Foto-Genesis gaben das Feld nicht weiter; im Tanz stand die Haut der
     * Goldprinzessin in Flecken vor der Hülle, weil ihre UV-Nähte unverschweißt als lockere Ränder zählten — gesehen an der Kopie _52 mit und ohne das Feld).
     */
    static kostuem(e) {
        return !!(e?.kostuem || e?.uebertrag?.art === 'rueckhaeutung');
    }

    /**
     * Verdeckt das Stück Haut (`userData.art` 'kleidung')? Haar nur als Kostümstück (die Haarschale aus dem Eingang); eine Frisur oder ein Bart zählt in `Hautverdeckung.zaehlt` nicht —
     * dann braucht `Fotogenesistestfigur._hautStuecke` keine eigene Kopie seiner Lage (21.11.2026: Haar 26 MB, Bart 18 MB am Zauberer).
     */
    static deckt(st) {
        return !(st.art === 'haar' && !st.kostuem);
    }

    static hautStuecke(ki) {
        const aus = {};
        for (const st of ki?.stuecke || []) {
            if (!st.ruhe || !st.dreiecke) continue;
            const index = st.dreiecke instanceof Uint32Array ? st.dreiecke : Uint32Array.from(st.dreiecke);
            // Kostümstücke (23.10.2026, Edgar an OlesiaWalk: Haut in Flecken auf Shirt und Jeans; an Edgar: „das Haar fehlt an der Schädeldecke“): dieselbe Regel wie der Server
            // (`Kleiderverdeckung.masken`, Fassung 2) — UV-Nähte verschweißt (sonst ist jede Naht ein „lockerer Rand“), Stoff bis `STOFF_TIEFE_M` hinter der Haut (der Körper der KI ragt dort
            // Zentimeter durch das Stück), und Haar verdeckt wie Stoff (die Haarschale aus dem Eingang; der KI-Kopf ragt sonst oben hindurch).
            const { punkte, dreiecke } = st.kostuem ? Meshfighautstueck.verschweissen(st.ruhe, index) : { punkte: st.ruhe, dreiecke: index };
            const geo = new THREE.BufferGeometry();
            geo.setAttribute('position', new THREE.BufferAttribute(punkte, 3));
            geo.setIndex(new THREE.BufferAttribute(dreiecke, 1));
            const netz = new THREE.Mesh(geo);
            netz.userData.art = Meshgenesiskikleiderfeld.deckt(st) ? 'kleidung' : 'haar';
            netz.userData.haar = st.art === 'haar';
            if (st.kostuem) netz.userData.stoffTiefe = Meshgenesiskikleiderfeld.STOFF_TIEFE_M;
            aus[`ki_${st.id}`] = netz;
        }
        if (ki) ki.haut = aus;
        return aus;
    }

    /**
     * Schalter „Kleider“ der Jobseite (21.10.2026): alle Stücke ein- oder ausblenden — seit 30.10.2026 auch das Haar (Edgar: „die Haare werden nicht deaktiviert“) —, mit ihnen die Stoffe der
     * Hautverdeckung (`Hautverdeckung.zaehlt` übergeht ausgeblendete). → true, wenn sich etwas geändert hat (dann muss die Hautverdeckung neu planen).
     */
    static kleiderZeigen(ki, an) {
        if (!ki || ki.kleiderAn === an) return false;
        ki.kleiderAn = an;
        for (const kind of ki.gruppe.children) kind.visible = an;
        for (const netz of Object.values(ki.haut || {})) netz.visible = an;
        return true;
    }

    /** Die Gruppe auf das gezeigte Rig legen (gleiche Knochenfolge wie die Beschreibung der Seite) und in das Feld hängen. */
    static einhaengen(inhalt, ki, ziel, ausschnitt) {
        const gruppe = ki.gruppe;
        gruppe.position.set(0, 0, 0);
        gruppe.quaternion.identity();
        if (ziel?.length) {
            const a = [], b = [];
            ziel.forEach((p, i) => { if (p && ki.rig[i]) { a.push(ki.rig[i]); b.push(p); } });
            if (a.length >= 3) {
                const { quaternion, verschiebung } = Meshgenesisausrichtung.starr(a, b);
                gruppe.quaternion.copy(quaternion);
                gruppe.position.copy(verschiebung);
            }
        }
        if (ausschnitt) gruppe.position.add({ x: ausschnitt.ziel[0] - ausschnitt.mitte[0], y: ausschnitt.ziel[1] - ausschnitt.mitte[1], z: ausschnitt.ziel[2] - ausschnitt.mitte[2] });
        gruppe.traverse(o => { o.frustumCulled = false; o.layers.set(1); });
        gruppe.updateMatrixWorld(true);
        inhalt.add(gruppe);
    }
}

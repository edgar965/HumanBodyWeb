/**
 * Mesh3dbuehne — die Karte „3D-Ansicht“ der Jobseite „Mesh-3D“ (11.10.2026).
 *
 * Edgar: „machst du mir noch die 3D-Ansicht wie bei dem anderen Job? mit den Filtern für Mesh, Kleider, Model, der Animation usw.“ — es ist DIESELBE Bühne wie auf den Auftragsseiten von „Mesh to 3D“ und
 * „2D3D Kleider“: `Meshfigurbuehne` (Figur im Browser aus den Reglern des Auftrags, Netz 1,5 m links, Haar, Kleider; Knöpfe Mesh · Haare · Kleider · Nebeneinander · 3DModell über `data-schalter`,
 * `meshfigurschalter.js`) und `Engine2d3dKleideranimation` (die BVH-Bewegung live auf der Figur, Leiste `#animations-leiste`). Gezeigt wird die Figur des Auftrags „Mesh to 3D“, den der Schritt „Figur“
 * des Imports gerechnet hat; dessen Zustand holt diese Klasse von `/api/meshfigur/<id>/zustand/`, die Bühne bekommt ihn wie auf ihrer eigenen Seite.
 *
 * Die Bühne kennt von ihrer Seite nur `dateiAdresse(ordner, name)` — diese Klasse ist ihre „Seite“: Dateien des Auftrags „Mesh to 3D“ kommen von dessen Endpunkt, die Bewegung von
 * `/api/mesh3d/<kennung>/bewegungsdatei/` (`Mesh3dbewegung`). Die Bewegung rechnet erst der Knopf „Animation“ (CPU, einige Sekunden), danach merkt sie sich der Zustand der Seite.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Engine2d3dKleideranimation } from '../engine2d3dkleider/engine2d3dkleideranimation.js';
import { Meshfigurbuehne } from '../meshfigur/meshfigurbuehne.js';
import { Meshfigurgelenke } from '../meshfigur/meshfigurgelenke.js';
import { Mesh3danimationswahlfeld } from './mesh3danimationswahlfeld.js';
import { Mesh3dbuehnengroesse } from './mesh3dbuehnengroesse.js';
import { Mesh3dnetzbuehne } from './mesh3dnetzbuehne.js';

export class Mesh3dbuehne {
    /** Der Name, unter dem die Animationsleiste ihre Bewegungsdatei erfragt (`film.bewegung`) — `dateiAdresse` leitet ihn auf den Endpunkt dieser Seite um. */
    static BEWEGUNG = '__bewegung__';
    static SCHLUESSEL = 'mesh3d.buehne.hoehe';
    static SCHLUESSEL_BREITE = 'mesh3d.buehne.breite';

    constructor(seite) {
        this.seite = seite;
        this.figurId = null;
        /** Die Variante, die statt der Ausgabe des Auftrags gezeigt wird (`Mesh3dvarianten`, Auswahl „Ausgabe“); `null` = die Ausgabe des Auftrags. */
        this.ausgabe = null;
        this.bewegung = null;
        this.netzansicht = null;
        this._angestossen = false;
        this._marke = '';
        this._holt = false;
        this._rechnet = false;
        this.knopf = document.getElementById('buehne-animation');
        this.meldung = document.getElementById('animation-meldung');
        this.netzmeldung = document.getElementById('netzansicht-meldung');
        const diese = this;
        // Die „Seite“ der Bühne: nur, was `Meshfigurnetze`, `Meshfigurhaarobjekt` und die Animation von ihr verlangen.
        this.adapter = {
            get jobId() { return diese.figurId; },
            dateiAdresse(ordner, name) {
                if (name === Mesh3dbuehne.BEWEGUNG) return diese.bewegung?.adresse || '';
                // Das Netz im Eingang kann Millionen Dreiecke haben (Zauberer: 67 MB, Laden 2–7 s, Parsen 1,9 s): die Ansicht nimmt die vereinfachte Kopie, wenn es sie gibt.
                // Ohne Auftrag „Mesh to 3D“ (`figurId` leer, siehe `zeigen`) gibt es nur diese Adresse — auch bei einem kleinen Netz (`unnoetig`).
                if (ordner === 'eingang' && diese.netzansicht?.adresse && (diese.netzansicht.status === 'bereit' || !diese.figurId)) return diese.netzansicht.adresse;
                return `/api/meshfigur/${diese.figurId}/datei/${ordner}/${encodeURIComponent(name)}`;
            },
            /** Solange die Kopie gebaut wird, lädt `Meshfigurnetze` nichts (weder das Original noch sie). */
            netzWartet() { return ['fehlt', 'baut'].includes(diese.netzansicht?.status); },
        };
        this.buehne = new Meshfigurbuehne(this.adapter);
        // Höhe und Breite der Ansicht einstellbar (Regler über ihr, Ziehgriff unten rechts); die Bühne beobachtet ihren Behälter und zieht die Leinwand nach.
        this.groesse = new Mesh3dbuehnengroesse(document.getElementById('buehne'), document.getElementById('buehne-groesse'), document.getElementById('buehne-groesse-wert'), Mesh3dbuehne.SCHLUESSEL,
            { regler: document.getElementById('buehne-breite'), wert: document.getElementById('buehne-breite-wert'), schluessel: Mesh3dbuehne.SCHLUESSEL_BREITE });
        this.animation = new Engine2d3dKleideranimation(this.adapter, this.buehne);
        // Daz' Gelenkkorrekturen (JCM) in der Bewegung, wie in Charakter und Studio: Haut, Augen, Mund und die Objekte aus dem Netz, die anliegen (Edgar, 14.10.2026).
        this.gelenke = new Meshfigurgelenke(this.buehne);
        this.animation.nachBild = () => this.gelenke.takt();
        // Eine Bewegung gehört auf die Figur in Ruhe (A-Pose): der erste Bedienbefehl der Leiste (Knopf ODER Taste) schaltet „Haltung“ aus, die Figur wird in Ruhe neu gebaut (`Meshfigurbuehne.haltungAus`),
        // und der Befehl läuft danach von selbst (`Engine2d3dKleideranimation.bedienen`). Die Leiste steht immer da (Edgar, 13.10.2026: „die Animationsleiste ist wieder weg“).
        this.animation.immerSichtbar = true;
        this.animation.vorBedienung = () => this.buehne.haltungAus();
        // Play, Leertaste und alle anderen Befehle ohne Bewegung rechnen sie zuerst (die Standardanimation des Auftrags) und laufen danach von selbst (Edgar, 13.10.2026: „Play ist ausgegraut, auch Space nicht“).
        this.animation.ohneBewegung = () => {
            if (this._rechnet) return true;
            if (this.knopf.disabled) return false;
            this.rechnen();
            return true;
        };
        // Die Standardanimation dieses Auftrags (13.10.2026, Auswahl unter der Leiste): der Knopf „Animation“ rechnet die gewählte Datei; eine neue Wahl rechnet eine schon vorhandene Bewegung neu.
        this.wahl = new Mesh3danimationswahlfeld(seite, () => this._nachWahl());
        // Die zweite Ansicht darunter (Karte „Mesh-Ansicht“): nur das Netz, dasselbe Licht, mittig — liest dieselbe „Seite“, also dieselbe Netz-Kopie.
        this.netzbuehne = new Mesh3dnetzbuehne(this.adapter, this.seite);
        this.knopf.disabled = true;
        this.knopf.addEventListener('click', () => this.rechnen());
    }

    async zeigen(z) {
        this._bewegung(z);
        this.wahl.zeigen(z.animation);
        const id = this.ausgabe || z.figur?.id;
        if (!id || (!this.ausgabe && z.figur.fehlt)) {
            // Keine Figur: die Mesh-Ansicht zeigt das Netz trotzdem (Edgar, 13.10.2026: „Mesh-Ansicht auch ohne den Auftrag Mesh to 3D“).
            this.knopf.disabled = true;
            this.figurId = null;                                // die Adresse des Netzes kommt jetzt vom Zustand, nicht vom (entfernten) Auftrag „Mesh to 3D“
            this._marke = '';
            this._netzOhneFigur(z);
            if (id) this.netzmeldung.textContent = `Der Auftrag „Mesh to 3D“ ${z.figur.kennung} dieses Imports gibt es nicht mehr (er wurde mit einem anderen Import gelöscht) — „Neu berechnen“ ab „Figur“ rechnet ihn neu.`;
            return;
        }
        this.figurId = id;
        this._netzansicht(z.netzansicht || null);
        const laeuft = z.status === 'laeuft' && z.schritt === 'figur';
        const marke = JSON.stringify([id, z.status, z.schritt, z.figur?.lauf?.schritt, (z.figur?.bilder || []).length, this.netzansicht?.status]);
        if (!laeuft && marke === this._marke) return;
        if (this._holt) return;
        this._holt = true;
        try {
            const m = await Serverabruf.json(`/api/meshfigur/${id}/zustand/`);
            this._marke = marke;
            this.knopf.disabled = z.status === 'laeuft' || !Object.keys(m.stellung || {}).length;
            this.netzbuehne.zeigen(m);
            // Nicht abwarten: der Bau der Figur im Browser dauert Sekunden und hielte sonst die übrigen Karten dieses Takts auf.
            this.buehne.zeigen(m).catch(fehler => this.seite.fehlerband.lesefehler(`3D-Ansicht: ${fehler.message}`));
        } catch (fehler) {
            this.seite.fehlerband.lesefehler(`Figur nicht lesbar: ${fehler.message}`);
        } finally {
            this._holt = false;
        }
    }

    /** Eine Variante statt der Ausgabe des Auftrags zeigen (`id`) oder zu ihr zurück (`null`); der nächste Takt der Seite baut die Bühne neu. */
    ausgabeWaehlen(id) {
        if (this.ausgabe === id) return;
        this.ausgabe = id;
        this._marke = '';
        if (this.seite.zustand) this.zeigen(this.seite.zustand);
    }

    /**
     * Das Netz der Mesh-Ansicht, wenn es keinen Auftrag „Mesh to 3D“ gibt (noch nicht angelegt oder gelöscht): der Zustand der Seite nennt die Datei (`netzansicht.datei`, `.adresse`), die Lage ist die
     * des Imports (`koerper.glb` steht schon in Menschenhöhe) — `Meshfigurnetze` stellt es ohne Lage der Erkennung mittig auf den Boden. Bis das Netz da ist (`keine`) oder gebaut wird, bleibt die Karte leer.
     */
    _netzOhneFigur(z) {
        this._netzansicht(z.netzansicht || null);
        const n = this.netzansicht;
        const bereit = n && ['bereit', 'unnoetig'].includes(n.status) && n.adresse;
        this.netzbuehne.zeigen(bereit ? { eingang: { datei: n.datei || 'netz.glb' }, ergebnis: {} } : null);
    }

    /**
     * Die vereinfachte Netz-Kopie (`Mesh3dnetzansicht`): fehlt sie bei einem großen Netz, stößt die Seite ihren Bau EINMAL an (eigener Prozess auf dem Server, etwa eine Minute); bis dahin steht die Figur
     * ohne Netz da, und die Zeile unter der Bühne sagt es. Danach ändert sich die Marke von `zeigen`, und die Bühne lädt die Kopie.
     */
    _netzansicht(z) {
        this.netzansicht = z;
        const s = z?.status;
        if (s === 'fehlt' && !this._angestossen) {
            this._angestossen = true;
            Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/netzansicht/anstossen/`, {})
                .catch(fehler => this.seite.fehlerband.lesefehler(`Netz-Ansicht nicht angestoßen: ${fehler.message}`));
        }
        this.netzmeldung.textContent = {
            fehlt: 'Das Netz ist sehr groß — für die Ansicht wird einmalig eine leichte Kopie gebaut (etwa eine Minute) …',
            baut: 'Das Netz ist sehr groß — für die Ansicht wird einmalig eine leichte Kopie gebaut (etwa eine Minute) …',
            fehler: `Leichte Kopie nicht gebaut (${z?.fehler || 'Fehler'}) — die Ansicht lädt das ganze Netz.`,
            bereit: `Die Ansicht zeigt das Netz vereinfacht (${z?.mb} MB); das Original bleibt der Eingang von „Mesh to 3D“.`,
        }[s] || '';
    }

    /** Die Bewegung aus dem Zustand der Seite an die Animationsleiste geben (`film.bewegung` — dieselbe Form wie bei „2D3D Kleider“). */
    _bewegung(z) {
        const b = z.bewegung;
        this.bewegung = b ? { adresse: `/api/mesh3d/${this.seite.kennung}/bewegungsdatei/?v=${encodeURIComponent(b.stand)}`, bilder: b.bilder } : null;
        this.animation.zeigen({ ergebnis: { film: this.bewegung ? { bewegung: Mesh3dbuehne.BEWEGUNG } : {} } });
        // Ohne Bewegung sagt die Zeile, was zu tun ist (blass ist die Leiste nicht mehr: „ausgegraut“ las sich als gesperrt); während der Knopf rechnet, bleibt seine Meldung stehen.
        if (b) this.meldung.textContent = `Bewegung: ${String(b.bvh).split(/[\\/]/).pop()}, ${b.bilder} Bilder.`;
        else if (!this._rechnet) this.meldung.textContent = 'Noch keine Bewegung — Play, die Leertaste oder der Knopf „Animation“ rechnen sie (Standardanimation).';
    }

    /** Nach einer neuen Standardanimation: liegt schon eine Bewegung auf der Figur, rechnet sie mit der neuen Datei (sonst spielte die Leiste die alte); ohne Bewegung rechnet erst der Knopf. */
    async _nachWahl() {
        if (this.bewegung && !this.knopf.disabled) await this.rechnen();
        else if (!this.bewegung) this.meldung.textContent = 'Noch keine Bewegung — Play, die Leertaste oder der Knopf „Animation“ rechnen sie mit der gewählten Standardanimation.';
    }

    /** Knopf „Animation“: die Bewegung auf der Figur rechnen (die Standardanimation des Auftrags, Vorgabe DanceKurz), danach erscheint die Leiste. */
    async rechnen() {
        this._rechnet = true;
        this.knopf.disabled = true;
        this.meldung.textContent = 'Bewegung wird gerechnet …';
        try {
            const antwort = await Serverabruf.senden(`/api/mesh3d/${this.seite.kennung}/bewegung/`, {});
            if (antwort.error) throw new Error(antwort.error);
            this.bewegung = { adresse: antwort.adresse, bilder: antwort.bilder };
            this.meldung.textContent = `Bewegung: ${String(antwort.bvh).split(/[\\/]/).pop()}, ${antwort.bilder} Bilder${antwort.neu ? '' : ' (schon gerechnet)'}.`;
            await this.seite.aktualisieren();
        } catch (fehler) {
            this.meldung.textContent = '';
            this.animation.befehlVerwerfen();
            this.seite.fehlerband.meldung(`Animation nicht gerechnet: ${fehler.daten?.error || fehler.message}`);
        } finally {
            this._rechnet = false;
            this.knopf.disabled = false;
        }
    }
}

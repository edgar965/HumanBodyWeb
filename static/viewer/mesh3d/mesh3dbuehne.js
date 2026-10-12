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
        this.bewegung = null;
        this.netzansicht = null;
        this._angestossen = false;
        this._marke = '';
        this._holt = false;
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
                if (ordner === 'eingang' && diese.netzansicht?.status === 'bereit') return diese.netzansicht.adresse;
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
        // Die zweite Ansicht darunter (Karte „Mesh-Ansicht“): nur das Netz, dasselbe Licht, mittig — liest dieselbe „Seite“, also dieselbe Netz-Kopie.
        this.netzbuehne = new Mesh3dnetzbuehne(this.adapter);
        this.knopf.disabled = true;
        this.knopf.addEventListener('click', () => this.rechnen());
    }

    async zeigen(z) {
        this._bewegung(z);
        const id = z.figur?.id;
        if (!id) { this.knopf.disabled = true; this.netzbuehne.zeigen(null); return; }
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
        this.meldung.textContent = b ? `Bewegung: ${String(b.bvh).split(/[\\/]/).pop()}, ${b.bilder} Bilder.` : '';
    }

    /** Knopf „Animation“: die Bewegung auf der Figur rechnen (Vorgabe der Tanz), danach erscheint die Leiste. */
    async rechnen() {
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
            this.seite.fehlerband.meldung(`Animation nicht gerechnet: ${fehler.daten?.error || fehler.message}`);
        } finally {
            this.knopf.disabled = false;
        }
    }
}

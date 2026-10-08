import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Engine2d3dKleiderGesichtsbuehne } from './engine2d3dkleidergesichtsbuehne.js';
import { TabellenSortierung } from '/static/djangobase/js/tabellen_sortierung.js';
import { TabellenBreiten } from '/static/djangobase/js/tabellen_breiten.js';

/**
 * Engine2d3dKleiderGesicht — Reiter „Gesicht" der Auftragsseite „2D3D Kleider" (07.10.2026).
 *
 * Edgar: „ich sehe keine verbesserung mit den neuen Reglern, was hast du denn so lange getan?? … mach mir einen zweiten
 * Tab bei der Modell View … wo du nur das Mesh Gesicht und das 3D Modell hast. Zeichne alle Linien ein die du gemessen
 * hast, mit Bezeichnung von 1 bis x und mach rechts eine Tabelle mit allen Spalten Nummer, Mesh (cm), Modell (cm)."
 *
 * Holt die Mess-Strecken UND die Ebenen-Schnitte von `GET /api/engine2d3dkleider/<id>/gesichtsvergleich/`
 * (`Engine2d3dKleiderGesichtsvergleich`: MediaPipe-Landmark-Strecken, Mesh direkt aus `landmarken.npz`, Modell als
 * nächster Oberflächenpunkt der aktuellen Stellung) und zeigt sie zweimal: links auf dem Netz aus den Fotos, rechts
 * auf dem aktuellen Modell — dieselben Nummern wie die Tabelle rechts.
 *
 * Schnitte (Edgar, 07.10.2026: „mach schnitte alle paar cm horizontal, vertikal und diagonal, mach die alle und
 * zeige sie auf dem Tab"): horizontal cyan, vertikal magenta, diagonal grün (`Engine2d3dKleiderGesichtsbuehne.
 * SCHNITTFARBEN`) — zusätzlich zu den gelben nummerierten Strecken, nicht statt ihnen.
 *
 * EIGENES Modulskript, unabhängig von der Seitenklasse (dieselbe Begründung wie „Bewertung"), UND träge: Baut seine
 * beiden Szenen (GLTFLoader, OrbitControls) erst, wenn der Reiter wirklich geöffnet wird — nicht beim Laden der Seite,
 * damit niemand, der „Gesicht" nie anklickt, zwei zusätzliche GLB lädt.
 */
export class Engine2d3dKleiderGesicht {

    static starten(jobId, leiste) {
        const feld = new Engine2d3dKleiderGesicht(jobId);
        if (!leiste || !feld.meshFeld) return feld;
        const reiterfeld = document.getElementById('reiter-gesicht');
        if (reiterfeld && !reiterfeld.hidden) feld.laden();     // Seite kam schon mit #gesicht in der Adresse
        leiste.addEventListener('reiterwechsel', e => {
            if (e.detail?.name === 'gesicht') feld.laden();
        });
        return feld;
    }

    constructor(jobId) {
        this.jobId = jobId;
        this.status = document.getElementById('gesicht-status');
        this.tabelle = document.querySelector('#gesicht-tabelle tbody');
        this.meshFeld = document.getElementById('gesicht-mesh');
        this.modellFeld = document.getElementById('gesicht-modell');
        this.bildHorizontal = document.getElementById('gesicht-bild-horizontal');
        this.bildVertikal = document.getElementById('gesicht-bild-vertikal');
        this.bildSilhouetten = document.getElementById('gesicht-bild-silhouetten');
        this.werttabelle = document.querySelector('#gesicht-werttabelle tbody');
        this._geladen = false;
    }

    async laden() {
        if (this._geladen || !this.meshFeld) return;
        this._geladen = true;
        this._melden('Wird geladen …');
        try {
            const daten = await Serverabruf.json(`/api/engine2d3dkleider/${this.jobId}/gesichtsvergleich/`);
            await this._zeigen(daten);
        } catch (fehler) {
            this._geladen = false;    // ein erneuter Klick auf den Reiter versucht es wieder
            this._melden(`Nicht geladen: ${fehler.daten?.error || fehler.message}`);
        }
    }

    _melden(text) {
        if (this.status) this.status.textContent = text;
    }

    async _zeigen(daten) {
        this.meshBuehne = new Engine2d3dKleiderGesichtsbuehne(this.meshFeld);
        this.modellBuehne = new Engine2d3dKleiderGesichtsbuehne(this.modellFeld);
        const laeuft = [];
        if (daten.mesh_datei) laeuft.push(this.meshBuehne.laden(daten.mesh_datei.url, daten.mesh_datei.ausrichtung));
        else this._warnung(this.meshFeld, 'Kein Netz (Schritt „Netz“ fehlt)');
        if (daten.modell_datei) laeuft.push(this.modellBuehne.laden(daten.modell_datei.url));
        else this._warnung(this.modellFeld, 'Kein Modell (noch kein Stand gebaut)');
        const geladen = await Promise.allSettled(laeuft);
        const fehler = geladen.filter(r => r.status === 'rejected');
        this.meshBuehne.zeichnen(daten.linien.map(l => ({ nummer: l.nummer, a: l.mesh_a, b: l.mesh_b })));
        this.modellBuehne.zeichnen(daten.linien.map(l => ({ nummer: l.nummer, a: l.modell_a, b: l.modell_b })));
        const schnitte = daten.schnitte || [];
        this.meshBuehne.schnitte(schnitte, 'mesh');
        this.modellBuehne.schnitte(schnitte, 'modell');
        this.meshBuehne.rahmen();
        this.modellBuehne.rahmen();
        this._tabelle(daten.linien);
        this._bilder();
        this._werttabelle();
        const zahlen = this._schnittzahlen(schnitte);
        const haltung = daten.haltung?.drehung_grad !== undefined
            ? ` · Kopfhaltung der Person um ${daten.haltung.drehung_grad}° zurückgedreht (Rest ${daten.haltung.rest_rms_mm} mm)`
            : (daten.haltung?.aus ? ` · Haltung NICHT zurückgedreht: ${daten.haltung.aus}` : '');
        const abw = daten.abweichung
            ? ` · Landmarken Mesh ↔ Modell: Median ${daten.abweichung.alle.median_mm} mm (${Object.entries(daten.abweichung.gruppen).filter(([, z]) => z).map(([name, z]) => `${name} ${z.median_mm}`).join(' · ')})`
            : '';
        this._melden(fehler.length
            ? `${daten.linien.length} Strecken · ${zahlen} · ${fehler.length} GLB nicht geladen`
            : `${daten.linien.length} Strecken · ${zahlen} · Mesh = ${daten.mesh_datei?.art || 'Netz aus den Fotos'} · Modell = letzter Stand${haltung}${abw}`);
    }

    /** Die drei statischen Vergleichsbilder (matplotlib) laden — `?t=` gegen Browser-Cache: dieselbe Adresse
     * zeigt nach der naechsten Regler-Aenderung sonst das alte Bild (keine Fassung in der URL wie bei den GLB). */
    _bilder() {
        const t = Date.now();
        if (this.bildHorizontal) this.bildHorizontal.src = `/api/engine2d3dkleider/${this.jobId}/gesichtsbild/horizontal/?t=${t}`;
        if (this.bildVertikal) this.bildVertikal.src = `/api/engine2d3dkleider/${this.jobId}/gesichtsbild/vertikal/?t=${t}`;
        if (this.bildSilhouetten) this.bildSilhouetten.src = `/api/engine2d3dkleider/${this.jobId}/gesichtsbild/silhouetten/?t=${t}`;
        this._detailbilder();
    }

    /** Die Bilderreihen Augen/Mund/Nase. Das erste Bild eines Stands rendert alle drei in einem eigenen Prozess (rund 25 s); ein Fehler kommt als JSON (409), nicht als Bild — darum `fetch` statt `src`. */
    async _detailbilder() {
        const status = document.getElementById('gesicht-detail-status');
        const bilder = ['augen', 'mund', 'nase'].map(name => [name, document.getElementById(`gesicht-bild-${name}`)]).filter(([, bild]) => bild);
        if (!bilder.length) return;
        if (status) status.textContent = 'Bilderreihen werden gerendert (beim ersten Öffnen eines Stands rund 25 s) …';
        const fehler = [];
        await Promise.all(bilder.map(async ([name, bild]) => {
            try {
                const antwort = await fetch(`/api/engine2d3dkleider/${this.jobId}/gesichtsbild/${name}/`);
                if (!antwort.ok) {
                    const daten = await antwort.json().catch(() => ({}));
                    throw new Error(daten.error || `HTTP ${antwort.status}`);
                }
                bild.src = URL.createObjectURL(await antwort.blob());
            } catch (e) {
                fehler.push(`${name}: ${e.message}`);
            }
        }));
        if (status) status.textContent = fehler.length ? `Nicht geladen — ${fehler.join(' · ')}` : '';
    }

    /** Dieselben Zahlen wie in den Bild-Titeln, als sortierbare djangoBase-Tabelle (Kopf klicken = sortieren,
     * Rand ziehen = Spaltenbreite) — Edgar: „die Tabelle als djangoTabelle: Sortierbar und Spalten veraenderbar". */
    async _werttabelle() {
        if (!this.werttabelle) return;
        try {
            const antwort = await Serverabruf.json(`/api/engine2d3dkleider/${this.jobId}/gesichtswerte/`);
            this.werttabelle.replaceChildren(...antwort.zeilen.map((zeile, i) => {
                const tr = document.createElement('tr');
                const werte = [
                    i + 1, zeile.bezeichnung, zeile.offset_mm,
                    zeile.max_delta_mm === null ? '–' : zeile.max_delta_mm.toFixed(1),
                    zeile.bei_mm === null ? '–' : zeile.bei_mm,
                ];
                werte.forEach(wert => {
                    const td = document.createElement('td');
                    td.textContent = String(wert);
                    tr.appendChild(td);
                });
                return tr;
            }));
            const tabelle = document.getElementById('gesicht-werttabelle');
            TabellenSortierung.binden(tabelle.closest('.card'));
            new TabellenBreiten(tabelle, 'gesicht-werte').binden();
        } catch (fehler) {
            console.warn('[2D3D Kleider] Gesicht: Werttabelle nicht geladen:', fehler.message);
        }
    }

    /** „24 Schnitte (8 horizontal, 7 vertikal, 9 diagonal, alle 2,5 cm)" für die Statuszeile. */
    _schnittzahlen(schnitte) {
        if (!schnitte.length) return '0 Schnitte';
        const je = {};
        for (const s of schnitte) je[s.kategorie] = (je[s.kategorie] || 0) + 1;
        const teile = ['horizontal', 'vertikal', 'diagonal'].filter(k => je[k]).map(k => `${je[k]} ${k}`);
        return `${schnitte.length} Schnitte (${teile.join(', ')}, alle 2,5 cm)`;
    }

    _warnung(feld, text) {
        const hinweis = document.createElement('div');
        hinweis.className = 'mesh-betrachter-hinweis';
        hinweis.textContent = text;
        feld.appendChild(hinweis);
    }

    /** Spalten Nummer, Bezeichnung, Mesh (cm), Modell (cm), Differenz — Differenz über 1 cm rot (die Aussage dieses Reiters). */
    _tabelle(linien) {
        if (!this.tabelle) return;
        this.tabelle.replaceChildren(...linien.map(linie => {
            const diff = linie.modell_cm - linie.mesh_cm;
            const zeile = document.createElement('tr');
            for (const text of [linie.nummer, linie.bezeichnung, linie.mesh_cm.toFixed(2), linie.modell_cm.toFixed(2)]) {
                const zelle = document.createElement('td');
                zelle.textContent = String(text);
                zeile.appendChild(zelle);
            }
            const diffZelle = document.createElement('td');
            diffZelle.textContent = `${diff >= 0 ? '+' : ''}${diff.toFixed(2)}`;
            diffZelle.classList.toggle('gv-diff-gross', Math.abs(diff) > 1);
            zeile.appendChild(diffZelle);
            return zeile;
        }));
    }
}

/**
 * Ai2d3dsteuerung — die Bedienleiste im festen Block der Seite „2d-3d-AI“ (24.10.2026): Perspektive (ein Knopf je Foto), Ansichtsart (dieselben wie Mesh3D-AI, `Mesh3daimaterial.MODI`),
 * Genesis-Modell „Ergebnis“ | „Wahrheit“ (nur Exporte), die Schalter „Kleider“ und „Rig“ (nur Tests), Netz Hunyuan3D-2mv | Tripo3D (nur, wenn es beide gibt). Die Leiste hält den Zustand; Änderungen meldet sie an `geaendert(was)`.
 */
import { Mesh3daimaterial } from '../mesh3dai/mesh3daimaterial.js';

export class Ai2d3dsteuerung {
    /** Arten, die für ein Netz als EIN Material keinen Sinn haben, fehlen hier (Punkte, Oberfläche + Drahtnetz — `Ai2d3dnetz.ersatz` würde sie auf „Oberfläche“ setzen). */
    static MODI = Mesh3daimaterial.MODI.filter(m => m.schluessel !== 'punkte' && m.schluessel !== 'oberflaeche_draht');

    /** @param {HTMLElement} leiste @param {object} daten Seitendaten @param {(was: string) => void} geaendert */
    constructor(leiste, daten, geaendert) {
        this.leiste = leiste;
        this.geaendert = geaendert;
        this.foto = Math.max(0, daten.fotos.findIndex(f => f.winkel === 0));
        this.modus = 'textur';
        this.quelle = 'ausgabe';
        this.kleider = true;
        this.rig = false;
        this.netz = 0;
        this.ausschnitt = 'koerper';
        this._gruppe('Perspektive', daten.fotos.map(f => ({ wert: f.nr, text: f.winkel === null ? `${f.name} (?)` : f.name, titel: f.winkel === null ? 'Winkel unbekannt' : `${f.winkel}°` })), 'foto');
        this._gruppe('Ausschnitt', [{ wert: 'koerper', text: 'Ganzer Körper', titel: 'Netz und Genesis-Modell ganz' },
            { wert: 'kopf', text: 'Kopf', titel: 'Netz und Genesis-Modell: nur der Kopf (gekoppelt, ziehen dreht beide)' }], 'ausschnitt');
        this._gruppe('Ansicht', Ai2d3dsteuerung.MODI.map(m => ({ wert: m.schluessel, text: m.name, titel: m.hinweis, icon: m.icon })), 'modus');
        if (daten.genesis && daten.wahrheit) {
            this._gruppe('Genesis-Modell', [{ wert: 'ausgabe', text: 'Ergebnis', titel: 'Was die KI aus den Eingaben macht (heute: Mesh3D-AI aus dem Tripo-Netz)' },
                { wert: 'soll', text: 'Wahrheit', titel: 'Die Figur, aus der die Fotos gerendert sind — Gegenprobe des Vergleichs' }], 'quelle');
        }
        // Ein Schalter statt „an | aus“ (24.10.2026, Edgar: „mach … einen einzigen Kleider Toggle“): gedrückt = Kleider und Haar zu sehen
        this._schalter('Kleider', 'kleider', 'Kleider und Haar zeigen (aus: nur der Körper)', 'fa-shirt');
        // Rig (24.10.2026, Edgar: „Mach einen toggle button für Rig, das möchte ich auch sehen“) — das Skelett der Testfigur in ihrer Haltung, wie der Knopf „Rig“ der Mesh3D-AI-Testseite
        if (daten.test?.adresse && !daten.genesis) this._schalter('Rig', 'rig', 'Das Skelett der Figur in ihrer Haltung über die Ansicht legen (Knochenpunkte, Farbe nach Gruppe)', 'fa-bone');
        if (daten.netze.length > 1) this._gruppe('Netz', daten.netze.map((n, i) => ({ wert: i, text: n.name, titel: `${n.mb} MB` })), 'netz');
    }

    _gruppe(titel, eintraege, schluessel) {
        const gruppe = this.leiste.appendChild(document.createElement('div'));
        gruppe.className = 'ai2d3d-steuergruppe';
        gruppe.append(Object.assign(document.createElement('span'), { className: 'ai2d3d-steuername', textContent: titel }));
        const reihe = gruppe.appendChild(document.createElement('div'));
        reihe.className = 'schalterleiste';
        reihe.setAttribute('role', 'group');
        reihe.setAttribute('aria-label', titel);
        for (const e of eintraege) {
            const knopf = reihe.appendChild(document.createElement('button'));
            knopf.type = 'button';
            knopf.className = 'schaltknopf';
            knopf.title = e.titel ?? '';
            if (e.icon) knopf.append(Object.assign(document.createElement('i'), { className: `fas ${e.icon}` }));
            knopf.append(document.createTextNode(e.text));
            knopf.addEventListener('click', () => this.setzen(schluessel, e.wert));
            knopf._wert = e.wert;
        }
        reihe.dataset.schluessel = schluessel;
        this._markieren(schluessel);
    }

    /** Ein einzelner Schaltknopf für einen Wahrheitswert (gedrückt = an). */
    _schalter(text, schluessel, titel, icon) {
        const reihe = this.leiste.appendChild(document.createElement('div'));
        reihe.className = 'ai2d3d-steuergruppe schalterleiste';
        const knopf = reihe.appendChild(document.createElement('button'));
        knopf.type = 'button';
        knopf.className = 'schaltknopf';
        knopf.title = titel;
        knopf.append(Object.assign(document.createElement('i'), { className: `fas ${icon}` }), document.createTextNode(text));
        knopf.addEventListener('click', () => this.setzen(schluessel, !this[schluessel]));
        knopf._wert = true;
        reihe.dataset.schluessel = schluessel;
        this._markieren(schluessel);
    }

    _markieren(schluessel) {
        const reihe = this.leiste.querySelector(`[data-schluessel="${schluessel}"]`);
        for (const k of reihe?.children ?? []) {
            const an = k._wert === this[schluessel];
            k.classList.toggle('active', an);
            k.setAttribute('aria-pressed', String(an));
        }
    }

    setzen(schluessel, wert) {
        if (this[schluessel] === wert) return;
        this[schluessel] = wert;
        this._markieren(schluessel);
        this.geaendert(schluessel);
    }
}

/**
 * Ai2d3dpshumaneingabe — die Bildplätze der PSHuman-Eingabe auf der Testseite von 2d-3d-AI (03.11.2026, Edgar: „mach im job ein UI das entweder eines oder mehrere
 * Bilder nimmt, mach vorschlag, wie die sein sollten, z.B. Umriss vom Körper, mit Upload möglichkeit für alle. Wenn ein Bild als Input, dann zeige die erzeugten
 * bilder von pshuman“ — „die erfundenen Bilder in auswählbarer Ansicht (Textur, Normale, Mesh usw)“).
 *
 * Sechs Plätze (`Ai2d3dpshumaneingabe` im Dienst): vorn, vorn-links, linke Seite, hinten, rechte Seite, vorn-rechts. Upload nach der Auswahl „Fotos“ oben (04.11.2026, Edgar: „Auswahl anzahl der
 * fotos (1-6), wenn mehrere fotos dann Hochladen funktion bei den Ansichten“): 1 → nur „vorn“; ab 2 jeder Platz, bis die Anzahl belegt ist. Es zählen „vorn“ und die ersten belegten Plätze in
 * Reihenfolge der Ansichten (`eingehend`, gleich `weitere_fotos` in `pshuman_job_rechnen.py`). Was ein Platz zeigt, wählt die Ansicht im Kopf des Blocks:
 *   textur       das Foto, wenn es eingeht; sonst PSHumans erfundenes Farbbild; ohne beides der Umriss als Vorlage
 *   normale      PSHumans Normalenbild des Winkels (bei „vorn“ aus dem Foto geschätzt, sonst erfunden)
 *   netz, netzfarbe, netznormale   PSHumans Netz aus dem Winkel gerendert (`Ai2d3dpshumannetzbilder`)
 * Alle Bilder gleich skaliert (04.11.2026, Edgar: „alle bilder skaliert in der ersten Zeile“): die Person steht in jedem Platz so hoch wie in PSHumans Ansichten (740 von 768 Pixeln), ein Foto
 * mit Rand wird dafür auf die Person zugeschnitten (`_einpassen`). Platz 3:5 statt 1:2: Barbaras breiteste Ansicht reicht 230 von 384 Pixeln neben die Mitte (`_wegwerf/session3dtools/platz_breiten.py`).
 * Upload `POST /api/2d3dai/<job>/pshuman/eingabe/<winkel>/` (Formular, Feld `datei`), entfernen `…/entfernen/`, Bilder `GET …/pshuman/bild/<winkel>/<art>/`.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Ai2d3dfotomass } from './ai2d3dfotomass.js';
import { Ai2d3dpshumannetzbilder } from './ai2d3dpshumannetzbilder.js';
import { Ai2d3dpshumanumriss } from './ai2d3dpshumanumriss.js';

export class Ai2d3dpshumaneingabe {
    /** Bildhöhe je Personenhöhe in PSHumans Ansichten (`crop_size` 740 im Bild 768). */
    static RAND = 768 / 740;

    static binden(block, form) {
        if (!block || !form) throw new Error('Ai2d3dpshumaneingabe: #ai2d3d-pshumaneingabe oder #ai2d3d-jobwahl fehlt');
        const job = block.dataset.job;
        const netzbilder = block.dataset.netz ? new Ai2d3dpshumannetzbilder(block.dataset.netz) : null;
        const plaetze = [...block.querySelectorAll('.ai2d3d-pshumanplatz')];
        const knoepfe = [...block.querySelectorAll('[data-ansicht]')];
        const wahl = form.querySelector('select[name="anzahl"]');
        let ansicht = 'textur';
        const zeichnen = () => {
            const anzahl = Number(wahl.value), eingehend = Ai2d3dpshumaneingabe.eingehend(plaetze, anzahl);
            const frei = anzahl > 1 && eingehend.size < anzahl;
            const belegt = plaetze.filter(p => p.dataset.quelle && eingehend.has(Number(p.dataset.winkel))).length;
            block.querySelector('[data-modushinweis]').textContent = Ai2d3dpshumaneingabe.hinweis(anzahl, belegt);
            for (const k of knoepfe) k.classList.toggle('active', k.dataset.ansicht === ansicht);
            for (const p of plaetze) Ai2d3dpshumaneingabe._zeichnen(p, job, ansicht, netzbilder, eingehend, frei);
        };
        for (const k of knoepfe) {
            if (Ai2d3dpshumannetzbilder.ARTEN.includes(k.dataset.ansicht) && !netzbilder) {
                k.disabled = true;
                k.title = 'Für diesen Job liegt noch kein PSHuman-Netz vor';
            }
            k.addEventListener('click', () => { ansicht = k.dataset.ansicht; zeichnen(); });
        }
        wahl.addEventListener('change', zeichnen);
        for (const p of plaetze) {
            p.querySelector('input[type="file"]').addEventListener('change', e => Ai2d3dpshumaneingabe._hochladen(p, job, e.target, zeichnen));
            p.querySelector('[data-entfernen]').addEventListener('click', () => Ai2d3dpshumaneingabe._entfernen(p, job, zeichnen));
        }
        zeichnen();
    }

    /** Die Winkel, deren Fotos in PSHuman eingehen: immer „vorn“, dazu die ersten belegten Plätze bis zur Anzahl. */
    static eingehend(plaetze, anzahl) {
        const weitere = plaetze.filter(p => p.dataset.quelle && p.dataset.winkel !== '0').map(p => Number(p.dataset.winkel));
        return new Set([0, ...weitere.slice(0, anzahl - 1)]);
    }

    static hinweis(anzahl, belegt) {
        if (anzahl === 1) return 'Ein Foto: PSHuman bekommt nur „vorn“ und erfindet die übrigen fünf Ansichten.';
        return `${belegt} von ${anzahl} Fotos belegt. Jedes Foto ersetzt die Ansicht, die PSHuman sonst erfindet. Der Rechenweg mit mehreren Fotos ist geschrieben, aber noch nie gelaufen.`;
    }

    static _basis(job) {
        return `/api/2d3dai/${encodeURIComponent(job)}/pshuman`;
    }

    static _zeichnen(p, job, ansicht, netzbilder, eingehend, frei) {
        const winkel = Number(p.dataset.winkel), name = p.dataset.name, quelle = p.dataset.quelle, drin = eingehend.has(winkel);
        const feld = p.querySelector('.ai2d3d-pshumanplatz-bild');
        // PSHumans Ansichten sind quadratisch (768²), die Person steht in der Mitte: im Platz seitlich beschnitten statt verkleinert. Ein Foto hat beliebig viel Rand: auf die Person zuschneiden
        const bild = (src, titel, quadrat = false) => {
            const img = document.createElement('img');
            img.src = src;
            img.alt = img.title = titel;
            if (quadrat) img.className = 'ai2d3d-pshumanplatz-quadrat';
            else img.addEventListener('load', () => Ai2d3dpshumaneingabe._einpassen(img));
            return img;
        };
        const server = (art, stand) => `${Ai2d3dpshumaneingabe._basis(job)}/bild/${winkel}/${art}/?v=${stand}`;
        const leer = text => feld.append(Ai2d3dpshumanumriss.svg(winkel), Ai2d3dpshumaneingabe._text(text));
        const zug = `${ansicht}:${drin}:${frei}:${p.dataset.stand}:${p.dataset.standErzeugt}`;
        p.dataset.zug = zug;
        feld.replaceChildren();
        p.classList.toggle('ai2d3d-pshumanplatz-erfunden', !drin && !frei);
        p.querySelector('.ai2d3d-pshumanplatz-knoepfe').hidden = !(drin || frei);
        p.querySelector('[data-entfernen]').hidden = quelle !== 'upload';
        if (ansicht === 'textur') {
            if (quelle && drin) feld.append(bild(server('eingabe', p.dataset.stand), `${name}: ${quelle === 'upload' ? 'hochgeladenes Foto' : 'Foto des Jobs'}`));
            else if (!drin && !frei && p.dataset.erzeugt) feld.append(bild(server('farbe', p.dataset.standErzeugt), `${name}: von PSHuman erfunden (Farbe)`, true));
            // ohne Rechnung, aber mit Bild des Jobs (z. B. Weg B: gerenderte Ansichten als Fotos): das Bild zeigen statt des Umrisses
            else if (quelle) feld.append(bild(server('eingabe', p.dataset.stand), `${name}: Bild des Jobs (geht bei dieser Fotoanzahl nicht in PSHuman)`));
            else if (!drin && !frei) leer('erfindet PSHuman — noch nicht gerechnet');
            else leer(winkel === 0 ? 'Pflicht: Foto von vorn' : 'Foto wie der Umriss hochladen');
        } else if (ansicht === 'normale') {
            if (p.dataset.erzeugt) feld.append(bild(server('normale', p.dataset.standErzeugt), `${name}: Normale von PSHuman (${winkel === 0 ? 'aus dem Foto geschätzt' : 'erfunden'})`, true));
            else leer('Normale — PSHuman noch nicht gerechnet');
        } else if (!netzbilder) {
            leer('kein PSHuman-Netz');
        } else {
            feld.append(Ai2d3dpshumaneingabe._text('Netz wird gerendert …'));
            netzbilder.bild(winkel, ansicht).then(url => {
                if (p.dataset.zug === zug) feld.replaceChildren(bild(url, `${name}: PSHumans Netz aus ${winkel}° (${ansicht})`, true));
            }, fehler => {
                if (p.dataset.zug === zug) feld.replaceChildren(Ai2d3dpshumaneingabe._text(`Netz nicht gerendert: ${fehler?.message ?? fehler}`));
            });
        }
    }

    /** Das Foto `img` so zuschneiden, dass die Person so hoch steht wie in PSHumans Ansichten; ohne erkennbare Person (Foto ohne Freistellung) bleibt das ganze Bild. */
    static _einpassen(img) {
        const a = Ai2d3dfotomass.anteil(img);
        if (!a) return;
        const b = img.naturalWidth, h = img.naturalHeight, seite = img.parentElement.clientWidth / img.parentElement.clientHeight;
        const hoch = Math.max((a.unten - a.oben) * h, (a.rechts - a.links) * b / seite) * Ai2d3dpshumaneingabe.RAND, breit = hoch * seite;
        const links = (a.links + a.rechts) / 2 * b - breit / 2, oben = (a.oben + a.unten) / 2 * h - hoch / 2;
        img.classList.add('ai2d3d-pshumanplatz-quadrat');
        img.style.objectViewBox = `inset(${oben}px ${b - links - breit}px ${h - oben - hoch}px ${links}px)`;
    }

    static _text(text) {
        const s = document.createElement('span');
        s.className = 'ai2d3d-pshumanplatz-text';
        s.textContent = text;
        return s;
    }

    static _uebernehmen(p, platz) {
        p.dataset.quelle = platz.quelle || '';
        p.dataset.stand = platz.stand;
        p.dataset.erzeugt = platz.erzeugt ? '1' : '';
        p.dataset.standErzeugt = platz.stand_erzeugt;
    }

    static async _hochladen(p, job, eingabe, zeichnen) {
        const datei = eingabe.files?.[0];
        if (!datei) return;
        const meldung = p.querySelector('[data-meldung]');
        meldung.textContent = 'Lädt hoch …';
        const daten = new FormData();
        daten.append('datei', datei);
        try {
            const antwort = await Serverabruf.formular(`${Ai2d3dpshumaneingabe._basis(job)}/eingabe/${p.dataset.winkel}/`, daten);
            Ai2d3dpshumaneingabe._uebernehmen(p, antwort.platz);
            meldung.textContent = `${datei.name} gespeichert — gilt ab dem nächsten PSHuman-Lauf`;
        } catch (fehler) {
            meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
        } finally {
            eingabe.value = '';
            zeichnen();
        }
    }

    static async _entfernen(p, job, zeichnen) {
        const meldung = p.querySelector('[data-meldung]');
        try {
            const antwort = await Serverabruf.senden(`${Ai2d3dpshumaneingabe._basis(job)}/eingabe/${p.dataset.winkel}/entfernen/`, {});
            Ai2d3dpshumaneingabe._uebernehmen(p, antwort.platz);
            meldung.textContent = 'aus der Eingabe genommen (Datei umbenannt aufbewahrt)';
        } catch (fehler) {
            meldung.textContent = `Nicht entfernt: ${fehler.message}`;
        } finally {
            zeichnen();
        }
    }
}

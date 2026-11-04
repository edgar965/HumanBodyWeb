import { fn } from '../gemeinsam/registrierung.js';
import { openDialog } from './utils.js';
import { Modellpruefung } from '../gemeinsam/modellpruefung.js';
import { Eigenkleidbacken } from '../gemeinsam/eigenkleidbacken.js';
import { Eigenkleider } from '../gemeinsam/eigenkleider.js';
import { Sanduhr } from '../gemeinsam/sanduhr.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Modellcheck3d } from './modellcheck3d.js';
import { Modellcheckbefunde } from './modellcheckbefunde.js';
import { Modellchecktabelle } from './modellchecktabelle.js';
import { Dialoggroesse } from '../bildmodell/dialoggroesse.js';

/**
 * Modellcheck — Menü Werkzeuge → „Modell Check…“ der Charakter-Seite (02.11.2026, Edgar: „mach es ins UI … Das soll die Fehler des Modells anzeigen in einem
 * Popup, wo die Fehler rot markiert sind“). Prüft die gewählte Genesis-9-Figur mit `Modellpruefung`: links je Prüfung Bestanden/Fehler mit dem Messwert, die
 * Tabelle aller Befunde (`Modellchecktabelle`; überfahren = nur dieser Befund rot im View) und die Prüfbilder (Figur grau, Befund rot, vergrößert); rechts die Figur
 * in 3D (`Modellcheck3d`). Das Fenster ist in der Größe veränderbar, die Größe gemerkt (`Dialoggroesse`, Edgar: „mach das Fenster Veränderbar in der Größe und
 * merke dir die Größe“). Dialog `_modellcheck_dialog.html`, Aussehen `css/modellcheck.css`.
 */
export class Modellcheck {

    static DIALOG = 'modellcheck-dialog';
    static MERKER = 'hb_modellcheck_groesse';
    static raum = null;
    static tabelle = null;
    static TITEL = { deckung: 'Deckung', fuesse_unten: 'Füße von unten', haare: 'Frisur', hand_links: 'Linke Hand', hand_rechts: 'Rechte Hand' };

    static async oeffnen() {
        const dialog = document.getElementById(Modellcheck.DIALOG);
        if (!dialog) return;
        const inst = fn._selectedInst?.();
        const kopf = dialog.querySelector('[data-modellcheck="figur"]'), liste = dialog.querySelector('[data-modellcheck="liste"]');
        const bilder = dialog.querySelector('[data-modellcheck="bilder"]'), stand = dialog.querySelector('[data-modellcheck="stand"]');
        const raum = Modellcheck._raum(dialog);
        raum.weg();
        Modellcheck.tabelle.leeren();
        kopf.textContent = inst?.presetName || inst?.name || '';
        liste.innerHTML = ''; bilder.innerHTML = '';
        openDialog(dialog);
        if (!inst) { stand.textContent = 'Keine Figur gewählt — erst eine Figur in der Liste anklicken.'; stand.className = 'modellcheck-stand fehler'; return; }
        stand.textContent = 'Prüfe …'; stand.className = 'modellcheck-stand';
        Sanduhr.an('Modell Check …');
        let gebacken = [];
        try {
            await new Promise((r) => setTimeout(r, 50));            // Dialog erst zeichnen lassen
            if (inst.quelle === 'genesis9') gebacken = await Eigenkleidbacken.backen(inst);      // selbst gebacken: die 3D-Ansicht zeigt dieselben Netze wie die Prüfung
            const p = await Modellpruefung.pruefen(inst, { bilder: true, gebacken, marken: true });
            Modellcheck._zeigen(p, liste, bilder, stand);
            const befunde = Modellcheckbefunde.sammeln(inst, p, gebacken);
            raum.zeigen(inst, gebacken, befunde);                  // hält die gebackenen Netze, bis der Dialog schließt
            gebacken = [];
            Modellcheck.tabelle.zeigen(befunde);
        } catch (fehler) {
            stand.textContent = fehler.message || String(fehler); stand.className = 'modellcheck-stand fehler';
            Protokoll.warnung('Modell Check', 'Prüfung gescheitert', fehler);
        } finally {
            Eigenkleidbacken.weg(gebacken);
            Sanduhr.aus();
        }
    }

    /** 3D-Ansicht und Befundtabelle des Dialogs (einmal je Seite); schließt der Dialog, gibt die Ansicht Renderer und Netze frei. */
    static _raum(dialog) {
        if (Modellcheck.raum) return Modellcheck.raum;
        Modellcheck.raum = new Modellcheck3d(dialog.querySelector('[data-modellcheck="raum"]'));
        Modellcheck.tabelle = new Modellchecktabelle(dialog.querySelector('[data-modellcheck="befunde"]'), Modellcheck.raum);
        Dialoggroesse.merken(dialog.querySelector('.modellcheck-modal'), Modellcheck.MERKER);
        new MutationObserver(() => { if (!dialog.classList.contains('visible')) Modellcheck.raum.weg(); }).observe(dialog, { attributes: true, attributeFilter: ['class'] });
        return Modellcheck.raum;
    }

    static _zeigen(p, liste, bilder, stand) {
        const gezaehlt = p.pruefungen.filter((x) => x.ok !== null), bestanden = gezaehlt.filter((x) => x.ok).length;
        stand.textContent = p.ok ? `Keine Fehler gefunden — ${bestanden} von ${gezaehlt.length} Prüfungen bestanden.` : `${p.fehler.length} Fehler — ${bestanden} von ${gezaehlt.length} Prüfungen bestanden.`;
        stand.className = `modellcheck-stand ${p.ok ? 'ok' : 'fehler'}`;
        for (const x of p.pruefungen) {
            const zeile = document.createElement('div');
            zeile.className = `modellcheck-zeile ${x.ok === null ? 'leer' : (x.ok ? 'ok' : 'fehler')}`;
            const zeichen = document.createElement('i');
            zeichen.className = `fas ${x.ok === null ? 'fa-minus' : (x.ok ? 'fa-check' : 'fa-times')}`;
            const titel = document.createElement('b'); titel.textContent = x.titel;
            const text = document.createElement('span'); text.textContent = x.text;
            zeile.append(zeichen, titel, text);
            liste.appendChild(zeile);
        }
        const gefaltet = Object.entries(p.gefaltet || {}).filter(([, v]) => v.flaeche_cm2 > 0);
        if (gefaltet.length) {
            const info = document.createElement('div');
            info.className = 'modellcheck-info';
            info.textContent = `Auskunft: umgeklappte Stofffläche ${gefaltet.map(([art, v]) => `${art} ${v.flaeche_cm2} cm²`).join(', ')} — ein Loch ist sie nur, wo die Deckung rot zeigt.`;
            liste.appendChild(info);
        }
        const fehlerhaft = new Set(p.pruefungen.filter((x) => x.ok === false).map((x) => x.schluessel));
        for (const b of p.bilder || []) {
            const art = b.rolle.startsWith('deckung_') ? 'deckung' : (b.rolle === 'fuesse_unten' ? 'schuhe' : (b.rolle.startsWith('hand_') ? 'handstoff' : 'haare'));
            const rote = art === 'deckung' ? (p.deckung.ansichten.find((a) => `deckung_${a.rolle}` === b.rolle)?.rote_px ?? 0) : null;
            const hand = art === 'handstoff' ? p.handstoff?.[b.rolle === 'hand_links' ? 'l' : 'r'] : null;
            const schlecht = art === 'deckung' ? rote > Modellpruefung.DECKUNG_PX_MAX : (hand ? hand.auf_px > Modellpruefung.HAND_STOFF_PX_MAX : true);
            const kachel = document.createElement('figure');
            kachel.className = `modellcheck-kachel ${fehlerhaft.has(art) && schlecht ? 'fehler' : ''}`;
            const img = document.createElement('img');
            img.alt = b.rolle;
            Modellcheck.markieren(b.url, art === 'haare').then((url) => { img.src = url; });
            const unter = document.createElement('figcaption');
            const name = b.rolle.replace('deckung_', '').replace('_', ' ');
            unter.textContent = art === 'deckung' ? `${name} · ${rote} px rot` : (Modellcheck.TITEL[b.rolle] || name) + (hand ? ` · ${hand.auf_px} px` : '');
            kachel.append(img, unter);
            bilder.appendChild(kachel);
        }
    }

    /** Prüfbild lesbar machen: Grund dunkel, Figur grau, Rot vergrößert (3 px) — oder bei der Frisur die Farben auf hellem Grund. */
    static async markieren(url, farbig) {
        const img = new Image();
        img.src = url;
        await img.decode();
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const ctx = c.getContext('2d', { willReadFrequently: true });
        ctx.drawImage(img, 0, 0);
        const daten = ctx.getImageData(0, 0, c.width, c.height), px = daten.data, w = c.width, h = c.height;
        const rot = new Uint8Array(w * h);
        for (let i = 0, j = 0; i < px.length; i += 4, j++) {
            const r = px[i], g = px[i + 1], b = px[i + 2], grund = b > 200 && r < 40 && g < 40;
            if (farbig) { if (grund) px.set([240, 240, 240], i); continue; }
            rot[j] = r > 128 && g < 60 && b < 60 ? 1 : 0;
            px.set(grund ? [27, 31, 36] : [110, 115, 122], i);
        }
        if (!farbig) {
            for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
                if (!rot[y * w + x]) continue;
                for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) {
                    const xx = x + dx, yy = y + dy;
                    if (xx >= 0 && yy >= 0 && xx < w && yy < h) px.set([255, 40, 40], 4 * (yy * w + xx));
                }
            }
        }
        ctx.putImageData(daten, 0, 0);
        return c.toDataURL('image/png');
    }
}

// Für Bildreihen aus dem MCP-Tab (`ProjektTemp/_wegwerf/tripo_wahrheit/`): dieselben Klassen wie das Menü, keine zweite Modulinstanz (ein eigener `import()` lüde
// die Szenenmodule ein zweites Mal)
window.__modellpruefung = { Modellpruefung, Eigenkleidbacken, Eigenkleider };

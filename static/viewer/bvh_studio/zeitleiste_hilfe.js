import { state, RULER_HEIGHT, HEADER_WIDTH } from './state.js';
import { Reihen } from './zeitleiste_reihen.js';
import { Zeitleistenflaeche } from './zeitleiste_flaeche.js';
import { Zeitleistentreffer } from './zeitleiste_treffer.js';
import { HILFE_ZEITLEISTE } from './hilfetexte_zeitleiste.js';

/**
 * Zeitleistenhilfe — die Schwebehilfe der Zeitleiste.
 *
 * Ruht die Maus auf einer Reihe, einem Clip oder dem Lineal, erscheint nach
 * kurzer Zeit ein Kasten mit dem, was man dort tun kann (Texte in
 * `hilfetexte_zeitleiste.js`). Die Zeitleiste ist eine Leinwand, ein
 * `title`-Attribut hilft dort nicht — darum ein eigener Kasten, der über dem
 * Zeiger steht (die Zeitleiste liegt unten am Fenster).
 *
 * Der Zuhörer hängt am scrollbaren Rahmen und deckt so Kopfspalte und
 * Leinwand zugleich ab: Beide liegen auf denselben Reihen (`Reihen.beiY`).
 * Beim Wechsel der Reihe schaltet der Kasten sofort um; Klick, Rad und
 * Rechtsklick nehmen ihn weg, gedrückte Taste (Ziehen) zeigt ihn nicht.
 *
 * WARUM (11.09.2026, Edgar): „mach hover texte in der Timeline mit hilfe was
 * ich tun muss, z.B. bei Kamera, wie ich die Kamera an der aktuellen Position
 * erzeuge".
 */
export class Zeitleistenhilfe {
    /** So lange muss die Maus ruhen, bis der Kasten erscheint. */
    static VERZOEGERUNG_MS = 600;
    /** Abstand des Kastens zum Zeiger. */
    static ABSTAND_PX = 14;
    /** Abstand zum Fensterrand, unter den der Kasten nicht rutscht. */
    static RAND_PX = 8;
    static KENNUNG = 'zeitleiste-hilfe';

    static element = null;
    static timer = 0;
    static schluessel = null;
    static offen = false;
    static lage = { x: 0, y: 0 };

    static anbinden() {
        const rahmen = Zeitleistenflaeche.rahmen;
        if (!rahmen) return;
        rahmen.addEventListener('mousemove', Zeitleistenhilfe._bewegen);
        rahmen.addEventListener('mouseleave', Zeitleistenhilfe.verbergen);
        for (const art of ['mousedown', 'wheel', 'contextmenu']) {
            rahmen.addEventListener(art, Zeitleistenhilfe.verbergen, { passive: true });
        }
    }

    /** Schlüssel des Hilfetexts für eine Stelle der Leinwand — oder null. */
    static schluesselBei(mx, my) {
        if (my < RULER_HEIGHT) return mx > HEADER_WIDTH ? 'lineal' : null;
        const reihe = Reihen.beiY(my);
        if (!reihe) return null;
        if (reihe.header) return 'gruppe';
        const spur = state.project.tracks[reihe.trackIdx];
        if (!spur) return null;
        if (mx > HEADER_WIDTH) {
            const treffer = Zeitleistentreffer.clipBei(mx, my);
            const clip = treffer && spur.clips[treffer.clipIdx];
            if (clip && HILFE_ZEITLEISTE['clip_' + clip.type]) return 'clip_' + clip.type;
        }
        if (spur.type === 'scene_object' && spur.subtype === 'floor') return 'floor';
        return HILFE_ZEITLEISTE[spur.type] ? spur.type : null;
    }

    static _bewegen(e) {
        const H = Zeitleistenhilfe;
        if (e.buttons) { H.verbergen(); return; }   // Ziehen: keine Hilfe
        const rect = Zeitleistenflaeche.canvas.getBoundingClientRect();
        const schluessel = H.schluesselBei(e.clientX - rect.left, e.clientY - rect.top);
        H.lage = { x: e.clientX, y: e.clientY };
        if (!schluessel) { H.verbergen(); return; }
        if (schluessel !== H.schluessel) {
            H.schluessel = schluessel;
            if (H.offen) { H._zeigen(); return; }   // andere Reihe: sofort umschalten
        }
        if (H.offen) return;                        // steht schon und bleibt stehen
        clearTimeout(H.timer);
        H.timer = setTimeout(H._zeigen, H.VERZOEGERUNG_MS);   // erst wenn die Maus ruht
    }

    static _zeigen() {
        const H = Zeitleistenhilfe;
        const eintrag = HILFE_ZEITLEISTE[H.schluessel];
        if (!eintrag) return;
        const el = H._element();
        el.innerHTML = `<b class="zeitleiste-hilfe-titel">${eintrag.titel}</b>${eintrag.text}`;
        el.hidden = false;
        H.offen = true;
        H._platzieren(el);
    }

    /** Über den Zeiger, notfalls darunter; nie über den rechten Rand hinaus. */
    static _platzieren(el) {
        const H = Zeitleistenhilfe;
        const { x, y } = H.lage;
        let links = x + H.ABSTAND_PX;
        let oben = y - el.offsetHeight - H.ABSTAND_PX;
        if (links + el.offsetWidth > window.innerWidth - H.RAND_PX) {
            links = Math.max(H.RAND_PX, x - el.offsetWidth - H.ABSTAND_PX);
        }
        if (oben < H.RAND_PX) oben = y + H.ABSTAND_PX;
        el.style.left = links + 'px';
        el.style.top = oben + 'px';
    }

    static verbergen() {
        const H = Zeitleistenhilfe;
        clearTimeout(H.timer);
        H.offen = false;
        H.schluessel = null;
        if (H.element) H.element.hidden = true;
    }

    static _element() {
        const H = Zeitleistenhilfe;
        if (!H.element) {
            const el = document.createElement('div');
            el.id = H.KENNUNG;
            el.className = 'zeitleiste-hilfe';
            el.hidden = true;
            document.body.appendChild(el);
            H.element = el;
        }
        return H.element;
    }
}

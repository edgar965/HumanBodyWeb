/**
 * Rechtsklickmenüs des BVH Studios protokollieren — EIN Zuhörer statt 63.
 *
 * BVH Studio hat ein eigenes, älteres Kontextmenü-System (statische HTML-
 * Kästen `#*-context-menu` in `bvh_studio.html`, dazu der Bibliotheksbaum
 * `.lib-ctx-*`) — anders als die Szene, die dafür die geteilte Klasse
 * `gemeinsam/kontextmenue.js` nutzt (dort inzwischen selbst protokolliert).
 * 28 Dateien, 63 einzeln gebundene Klicks, kein gemeinsamer Durchgangspunkt
 * (Edgar, 24.09.2026: „Die Rechtsklickmenüs IM BVH STUDIO an das neue System
 * anpassen bez. Logs"). Statt 63 Stellen einzeln anzufassen: EIN Klick-
 * Zuhörer am `document`, in der CAPTURE-Phase — er läuft vor jeder der 63
 * eigentlichen Aktionen (die das Menü meist sofort schließen/umbauen), sonst
 * wäre der geklickte Text schon weg, bevor diese Zeile ihn läse.
 *
 * `.ctx-item` ist die gemeinsame Klasse aller Einträge der statischen
 * Kästen UND der dynamisch gebauten Untermenüs (`zeitleiste_spurmenue.js`
 * `Spurmenue.eintrag()`); `.lib-ctx-item` die des Bibliotheksbaums
 * (geprüft: 41 `.ctx-item` in `bvh_studio.html`, dazu sechs `.lib-ctx-item`
 * in den beiden Bibliotheksmenüs). Ein Eintrag trägt entweder `data-action`
 * (Bibliothek, ein Teil der Zeitleisten-Einträge) oder eine sprechende `id`
 * (die übrigen) — beides sagt mehr als der reine Anzeigetext.
 */
import { fn } from '../gemeinsam/registrierung.js';

const EINTRAG_AUSWAHL = '.ctx-item, .lib-ctx-item';

document.addEventListener('click', (ereignis) => {
    const eintrag = ereignis.target.closest(EINTRAG_AUSWAHL);
    if (!eintrag) return;
    const bezeichner = eintrag.dataset?.action ? `action=${eintrag.dataset.action}`
        : eintrag.id ? `id=${eintrag.id}`
        : `text="${(eintrag.textContent || '').trim().slice(0, 40)}"`;
    fn.serverLog?.('bvh_kontextmenue_aktion', bezeichner);
}, true);

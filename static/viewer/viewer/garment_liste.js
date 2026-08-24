/**
 * Kleidungsliste und Downloadpakete der Modellseite.
 *
 * Aus garment.js herausgeloest (Umbau 16.08.2026).
 *
 * UMBAU 18.08.2026: 229 Zeilen, davon 60 dreimal dieselbe Reglerliste. Jetzt:
 *
 *     kleiderregler.js   Regler lesen/füllen/vorbelegen (Einheiten an EINER Stelle)
 *     kleiderliste.js    Katalog als aufklappbare Liste + Auswahl
 *     kleiderform.js     Zustand auf das Netz rechnen (Maßstab, Bereiche)
 *     kleiderpakete.js   Downloadpakete anbieten und installieren
 *
 * Hier bleiben die Namen, die `garment.js` und `kleiderbedienung.js` aufrufen.
 */
import { Kleiderregler } from './kleiderregler.js';
import { Kleiderliste } from './kleiderliste.js';
import { Kleiderform } from './kleiderform.js';
import { Kleiderpakete } from './kleiderpakete.js';

export function _renderGarmentList() { Kleiderliste.zeichnen(); }
export function _saveGarmentState(gid) { Kleiderregler.speichern(gid); }
export function _applyGarmentState(gid) { Kleiderform.anwenden(gid); }
export function _loadDownloadPacks() { return Kleiderpakete.listeLaden(); }
export function _downloadPack() { return Kleiderpakete.herunterladen(); }

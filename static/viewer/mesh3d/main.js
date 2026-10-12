/**
 * Einstieg für das Bündel der Jobseite „Mesh-3D“ (12.10.2026, `core/dienste/modulbuendel.py`, Eintrag `mesh3d`).
 *
 * Edgar: „40–50 s Wartezeit im Browser für das Modell ist viel zu lange, ich brauche 5–10 s“. Die Seite lud ihre 232 Module einzeln — nach jeder Änderung an irgendeiner Statikdatei (die Fassung steht im Pfad)
 * kalt, im Messtab 6,5 s bis die Bühne angelegt war (warm 0,4–0,6 s). Gebündelt ist es EINE Anfrage, wie bei Szene und BVH Studio.
 *
 * Die Vorlage importiert ALLES, was sie aus den Modulen braucht, aus dieser einen Adresse: Ein Modul, das einmal im Bündel und einmal einzeln geladen würde, hätte zwei Zustände (`es-module-stumme-fehler.md`).
 */
export { Mesh3dseite } from './mesh3dseite.js';
export { Auftragloeschen } from '../gemeinsam/auftragloeschen.js';
export { Auftragname } from '../gemeinsam/auftragname.js';
export { Seitenreiter } from '../gemeinsam/seitenreiter.js';

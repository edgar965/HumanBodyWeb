import { Figurhaut } from '../gemeinsam/figurhaut.js';

/**
 * Spurhaut — die Haut unter der Kleidung einer Studio-Figur wird nicht
 * gezeichnet, und Stoff unter Stoff auch nicht.
 *
 * ANLASS (Edgar, 11.09.2026): „die haut ist immer noch sichtbar im BVH
 * Studio, spiele die Animation ab." Die Maske vom selben Tag lief nur in
 * der Szene (`scene/hautverdeckung.js`, `scene/lagenverdeckung.js`, am
 * `Stueckereignis`); das Studio baut seine Figur selbst (`Spurfigur`,
 * `Spurzubehoer`) und zeichnete den ganzen Körper — in Bewegung kam die
 * Haut an Bund, Schritt und Knie durch die Leggings wie vorher in der Szene.
 *
 * Die Rechnung steht seit dem 12.09.2026 in `gemeinsam/figurhaut.js`: Die
 * Ergebnisseite baut ihre Figur genauso (Körper plus Gruppe mit Stücken,
 * `Garmentcodebindung`) und brauchte dieselbe Maske. Eine Spur IST so eine
 * Figur (`spur.mesh`, `spur.group`, `spur.name`) — hier bleibt nur der
 * Name, unter dem das Studio sie ruft (`Spurfigur.laden`).
 */
export class Spurhaut extends Figurhaut {}

// Für Messungen aus der Konsole.
window.__spurhaut = Spurhaut;

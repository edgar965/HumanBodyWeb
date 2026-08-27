/**
 * HumanBody Animationen — Einstiegspunkt.
 *
 * Der Aufbau steckt in `Animationsseite` (animation/animationsseite.js). Vorher
 * standen hier 134 Zeilen `init()`, davon 50 für einen Bühnenaufbau, den es im
 * Projekt noch zweimal gab.
 */
import './retarget_hybrid.js';
import './gemeinsam/kodierung.js';
import { Animationsseite } from './animation/animationsseite.js';

new Animationsseite().starten();

/**
 * Figur einer Spur laden — Anmeldung.
 *
 * Der Aufbau steckt in `Spurfigur` (spurfigur.js), und die baut seit dem
 * 13.09.2026 nichts mehr selbst: Sie setzt ein `HumanbodyModell`
 * (`gemeinsam/humanbodymodell.js`) in die Spur. Vorher standen hier zwei
 * Funktionen mit je 113 Zeilen, die beide Netzdaten holten, ein SkinnedMesh
 * bauten und banden.
 *
 * EIN LAUF JE SPUR (22.09.2026, Edgar: „ich brauche auch die Beschleunigung
 * im BVH-Studio"): `Clipanimation._figurSichern` ruft dies für JEDEN Clip
 * einer Animationsspur auf (`spur.mesh` ist bis zum ersten Ergebnis null) —
 * beim Laden/Rückgängig mit `Promise.all(wartend)` starten alle Clips
 * GLEICHZEITIG, sehen alle noch `spur.mesh === null` und lösen je einen
 * VOLLEN Figurbau aus. Bei vier Clips derselben Genesis-9-Figur (Olesia1 +
 * vier Kleidungsstücke, käfig UND fein) wurden das vier komplette Bauten
 * nebeneinander — gemessen: ein einziges Undo mit Kamerabewegung (die Figur
 * gar nicht betraf) brauchte 14,3 s, weil der Server die vier Anfragen nur
 * nacheinander abarbeitet. Jetzt merkt sich die Spur den LAUFENDEN Aufbau;
 * jeder weitere Aufruf, solange er läuft, bekommt dasselbe Versprechen statt
 * einen eigenen zu starten.
 *
 * NUR HUMANBODY WARTET AUF DIE GETEILTEN DATEN (22.09.2026, „optimiere die
 * Ladezeiten"): `Spurfigurarten.BAUER.modell` liest `sharedState.
 * rigifySkeletonData`/`skinWeightData` — UMA, MakeHuman, SMPL, UMA Python und
 * Genesis 9 nicht. Früher wartete der GESAMTE Studiostart pauschal auf diese
 * ~4,7 s, bevor überhaupt ein Clip zu laden begann. Jetzt läuft das Laden
 * nebenher (`Studiostart.starten`), und nur eine `quelle: 'modell'`-Spur
 * wartet hier gezielt darauf.
 */
import { _sanitizeBoneNames } from './spur_clips.js';
import { Spurfigur } from './spurfigur.js';
import { humanbodyDatenLaden } from '../character_core.js';

export async function loadTrackCharacter(track) {
    if (track._figurLadenPromise) return track._figurLadenPromise;
    // Das Versprechen SOFORT (synchron) an der Spur ablegen, auch wenn der
    // erste Schritt selbst noch wartet — sonst sähe ein zweiter, kurz danach
    // eintreffender Aufruf `_figurLadenPromise` noch leer und baute doch
    // ein zweites Mal (dieselbe Race wie ohne die Wartezeit).
    const versprechen = (async () => {
        if ((track.quelle || 'modell') === 'modell') await humanbodyDatenLaden();
        return new Spurfigur(track, { namenSaeubern: _sanitizeBoneNames }).laden();
    })().finally(() => { track._figurLadenPromise = null; });
    track._figurLadenPromise = versprechen;
    return versprechen;
}

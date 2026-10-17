/**
 * Mesh3daianimationsdaten — holt die Standardanimation „Spagat“ der Seite „Mesh3D-AI“ vom Server (14.10.2026).
 * Edgar: „ich brauche noch die Animationsleiste + Funktion. Standardanimation ist … Spagat, bei Taste / Klick auf Play in den einzelnen Zeilen möchte ich die animiert sehen.“
 * Die Antwort (`/api/mesh3dai/<job>/animation/`, rund 4,7 MB) hat für jedes Bild dieselbe Form wie eine Probe — die Zeilen zeigen ein Bild mit demselben Code wie eine Probe.
 * Sie wird erst beim ersten Play oder Ziehen am Regler geholt (der Server rechnet beim allerersten Mal das Retarget, danach liegt es im Speicher) und dann von allen fünf Zeilen geteilt:
 * eine Anfrage je Job, kein Abruf je Zeile. Ein Fehler wird nicht gemerkt, der nächste Klick versucht es noch einmal.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Mesh3daianimationsdaten {
    static _abrufe = new Map();

    /** @returns {Promise<{name: string, quelle: string, fps: number, bildzeit: number, bilder: object[]}>} */
    static laden(job) {
        const abrufe = Mesh3daianimationsdaten._abrufe;
        if (!abrufe.has(job)) {
            const abruf = Serverabruf.json(`/api/mesh3dai/${encodeURIComponent(job)}/animation/`);
            abruf.catch(() => abrufe.delete(job));
            abrufe.set(job, abruf);
        }
        return abrufe.get(job);
    }

    /** Beim Wechsel des Jobs: die Bilder des alten gehören nicht mehr dazu. */
    static verwerfen() {
        Mesh3daianimationsdaten._abrufe.clear();
    }
}

/**
 * Bibliothekskanal — „die BVH-Bibliothek hat sich geändert", über Tabs hinweg.
 *
 * Edgar, 16.09.2026: „nach löschen einer Animation z.B. bei /humanbody/scene/
 * oder BVH-Studio (kontext menü) ist die Animation immer noch im Baum."
 * Jede Seite holt ihren Baum nach einer eigenen Aktion neu — aber die
 * Szene, das Studio und die Animationen-Seite laufen meist zugleich in
 * eigenen Tabs, und ein Tab erfährt nichts von dem, was ein anderer löscht,
 * umbenennt oder speichert. Dort stand der Eintrag weiter im Baum, bis man die
 * Seite neu lud.
 *
 * Ein `BroadcastChannel` erreicht alle Tabs desselben Browsers. Der sendende
 * Tab bekommt seine eigene Meldung nicht (eine Kanalinstanz je Tab) — er hat
 * seinen Baum ohnehin schon neu geholt.
 *
 * Ohne Importe — `test_js_bibliothekskanal` rechnet in Node.
 */
export class Bibliothekskanal {

    static NAME = 'bvh-bibliothek';

    static _kanal = null;

    static kanal() {
        if (!Bibliothekskanal._kanal && typeof BroadcastChannel !== 'undefined') {
            Bibliothekskanal._kanal = new BroadcastChannel(Bibliothekskanal.NAME);
        }
        return Bibliothekskanal._kanal;
    }

    /** Nach einer gelungenen Aktion (`delete`, `rename`, `move`, `save`, …). */
    static melden(aktion, daten = {}) {
        Bibliothekskanal.kanal()?.postMessage({ aktion, ...daten, zeit: Date.now() });
    }

    /**
     * `tun(meldung)` bei jeder Meldung eines ANDEREN Tabs; Rückgabe: Abmelden.
     */
    static hoeren(tun) {
        const kanal = Bibliothekskanal.kanal();
        if (!kanal) return () => {};
        const zuhoerer = (ereignis) => tun(ereignis.data || {});
        kanal.addEventListener('message', zuhoerer);
        return () => kanal.removeEventListener('message', zuhoerer);
    }
}

/**
 * Sanduhr — zeigt, dass eine Änderung noch gerechnet wird.
 *
 * Edgar (18.09.2026): „mach eine Sanduhr wenn ich eine Property ändere,
 * damit ich weiss, wann die Property geändert wird". Ein Reglerzug an einer
 * Genesis-9-Figur läuft über den Server (Käfig 0,3 s, Stufe 2 mit Kleid
 * 2–3 s); solange stand die Figur unverändert da, ohne Hinweis.
 *
 * `an(text)` zählt hoch und zeigt das Abzeichen (fest unten links, neben dem
 * Netzstufen-Abzeichen rechts), `aus()` zählt herunter — verschachtelte Läufe
 * halten es, bis der letzte fertig ist. Dazu bekommt `<html>` die Klasse
 * `hb-sanduhr` (Mauszeiger `progress`, `stilhelfer.css`). `um(text, aufruf)`
 * umschließt ein Versprechen, auch bei Fehler wieder aus.
 */
export class Sanduhr {

    static ID = 'hb-sanduhr';
    static KLASSE = 'hb-sanduhr';
    static _offen = 0;
    static _text = '';
    static _beginn = 0;
    static _zeitgeber = null;

    /**
     * Unten MITTE und groß (16.10.2026, Edgar: „Mach eine Sanduhr bis so ein Regler durch ist"): Die Anzeige stand klein unten LINKS neben dem Menü und wurde
     * übersehen — bei einem Reglerzug mit Kleidung wartet man bis zu 20 s. Dazu die verstrichenen Sekunden, damit man sieht, dass es läuft.
     */
    static an(text = 'Rechnet …') {
        Sanduhr._offen += 1;
        Sanduhr._text = text;
        let feld = document.getElementById(Sanduhr.ID);
        if (!feld) {
            feld = document.createElement('div');
            feld.id = Sanduhr.ID;
            Object.assign(feld.style, {
                position: 'fixed', left: '50%', bottom: '28px', transform: 'translateX(-50%)', zIndex: '9000',
                padding: '9px 18px', borderRadius: '8px', font: '600 15px/1.4 sans-serif',
                background: 'rgba(80, 140, 255, 0.95)', color: '#fff',
                pointerEvents: 'none', boxShadow: '0 3px 12px rgba(0,0,0,.5)',
            });
            document.body.appendChild(feld);
            Sanduhr._beginn = performance.now();
            Sanduhr._zeitgeber = setInterval(Sanduhr._zeigen, 250);
        }
        Sanduhr._zeigen();
        document.documentElement.classList.add(Sanduhr.KLASSE);
        return feld;
    }

    static _zeigen() {
        const feld = document.getElementById(Sanduhr.ID);
        if (feld) feld.textContent = `⏳ ${Sanduhr._text} ${((performance.now() - Sanduhr._beginn) / 1000).toFixed(1)} s`;
    }

    static aus() {
        Sanduhr._offen = Math.max(0, Sanduhr._offen - 1);
        if (Sanduhr._offen) return;
        clearInterval(Sanduhr._zeitgeber);
        Sanduhr._zeitgeber = null;
        document.getElementById(Sanduhr.ID)?.remove();
        document.documentElement.classList.remove(Sanduhr.KLASSE);
    }

    /** Ein Versprechen mit Sanduhr — aus, sobald es erfüllt oder gescheitert ist. */
    static async um(text, aufruf) {
        Sanduhr.an(text);
        try {
            return await aufruf();
        } finally {
            Sanduhr.aus();
        }
    }

    static laeuft() {
        return Sanduhr._offen > 0;
    }
}

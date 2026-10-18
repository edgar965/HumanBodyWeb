/**
 * Ein Kontextmenü — der Kasten, die Einträge, das Schließen.
 *
 * WARUM GETEILT (08.09.2026): Das Menü der Animationen war das erste
 * (`Animationsmenue`), gleich danach kam eines auf der Modellzeile (Edgar:
 * „Auch rechtsklick auf das Modell oberhalb des Tabs, neues Kontextmenü").
 * Beide brauchen dasselbe: EINEN Kasten am `body`, Einträge mit Symbol,
 * Randkorrektur am Fensterrand, und einen Klick daneben zum Schließen.
 *
 * Zwei Fassungen desselben Kastens wären die Fehlerklasse „DIESELBEN LISTEN,
 * ZWEIMAL" — und praktisch stünden irgendwann zwei Menüs gleichzeitig offen,
 * weil jedes nur seinen eigenen schließt.
 */
import { fn } from './registrierung.js';

export class Kontextmenue {

    /** Die eine Kennung: Ein zweites Menü gibt es nicht, es wird ersetzt. */
    static KENNUNG = 'hb-ctx';

    /**
     * Menü an einer Bildschirmstelle zeigen.
     *
     * @param x, y      Mausposition
     * @param eintraege [{symbol, text, tun}] — `null` als Trennlinie; mit `auswahl` eine Combo-Box (`_auswahl`)
     */
    static zeigen(x, y, eintraege) {
        const menue = Kontextmenue._kasten();
        menue.innerHTML = '';
        for (const eintrag of eintraege) {
            menue.appendChild(!eintrag ? Kontextmenue._trenner()
                : eintrag.auswahl ? Kontextmenue._auswahl(eintrag) : Kontextmenue._eintrag(eintrag));
        }
        // Erst messen, dann setzen: Am rechten oder unteren Rand liefe das
        // Menü sonst aus dem Fenster und die Einträge wären nicht erreichbar.
        menue.style.left = '0px';
        menue.style.top = '0px';
        menue.style.display = 'block';
        const breite = menue.offsetWidth;
        const hoehe = menue.offsetHeight;
        menue.style.left = `${Math.min(x, window.innerWidth - breite - 4)}px`;
        menue.style.top = `${Math.min(y, window.innerHeight - hoehe - 4)}px`;
        Kontextmenue._schliessenBeiKlick();
        return menue;
    }

    /** Das Menü an ein Element hängen — Rechtsklick öffnet es. */
    static binden(ziel, eintraegeVon) {
        ziel.addEventListener('contextmenu', (ereignis) => {
            ereignis.preventDefault();
            // Ohne `stopPropagation` öffnete zusätzlich das Menü eines
            // äußeren Bereichs — beide zugleich.
            ereignis.stopPropagation();
            const eintraege = eintraegeVon(ereignis);
            if (eintraege && eintraege.length) {
                Kontextmenue.zeigen(ereignis.clientX, ereignis.clientY,
                                    eintraege);
            }
        });
    }

    static verbergen() {
        const menue = document.getElementById(Kontextmenue.KENNUNG);
        if (menue) menue.style.display = 'none';
    }

    // -- Bausteine ------------------------------------------------------------

    static _kasten() {
        let menue = document.getElementById(Kontextmenue.KENNUNG);
        if (menue) return menue;
        menue = document.createElement('div');
        menue.id = Kontextmenue.KENNUNG;
        menue.className = 'hb-kontextmenue';
        menue.style.display = 'none';
        document.body.appendChild(menue);
        return menue;
    }

    static _eintrag({ symbol, text, tun }) {
        const zeile = document.createElement('div');
        zeile.className = 'hb-menueeintrag';
        zeile.innerHTML = `<i class="fas ${symbol || 'fa-circle'} hb-symbolspalte"></i> `;
        // Der Text kann aus einem Dateinamen kommen — als TEXT setzen.
        zeile.appendChild(document.createTextNode(text));
        zeile.addEventListener('click', () => {
            Kontextmenue.verbergen();
            // Protokoll VOR `tun()`: wirft die Aktion, steht wenigstens fest,
            // WAS geklickt wurde (Edgar, 24.09.2026: „alle rechtsklick und
            // server aufrufe sollen geloggt werden").
            fn.serverLog?.('kontextmenue_aktion', text);
            tun();
        });
        return zeile;
    }

    /**
     * Ein Eintrag mit Combo-Box: `{symbol, text, auswahl: [{wert, text}], wert, waehlen(wert)}` — eine andere Wahl schließt das Menü
     * und ruft `waehlen` (Edgar, 18.10.2026: „verschieben Funktion vereinfachen, mach eine Combo Box mit allen ordnern (anstelle der
     * Auflistung)"). Ein Klick in die Zeile schließt es NICHT: `_schliessenBeiKlick` lauscht am Dokument.
     */
    static _auswahl({ symbol, text, auswahl, wert = '', waehlen }) {
        const zeile = document.createElement('div');
        zeile.className = 'hb-menueeintrag hb-menueauswahl';
        zeile.innerHTML = `<i class="fas ${symbol || 'fa-circle'} hb-symbolspalte"></i> `;
        zeile.appendChild(document.createTextNode(text));
        const feld = document.createElement('select');
        for (const eintrag of auswahl) {
            const option = document.createElement('option');
            option.value = eintrag.wert;
            option.textContent = eintrag.text;      // aus Namen des Nutzers — als TEXT
            option.selected = eintrag.wert === wert;
            feld.appendChild(option);
        }
        zeile.addEventListener('click', ereignis => ereignis.stopPropagation());
        feld.addEventListener('change', () => {
            Kontextmenue.verbergen();
            fn.serverLog?.('kontextmenue_aktion', `${text}: ${feld.value}`);
            waehlen(feld.value);
        });
        zeile.appendChild(feld);
        return zeile;
    }

    static _trenner() {
        const linie = document.createElement('div');
        linie.className = 'hb-trennlinie';
        return linie;
    }

    /**
     * Ein Klick daneben schließt das Menü.
     *
     * `{ once: true }` und ein Aufschub um einen Zyklus: Ohne ihn fängt
     * derselbe Klick, der das Menü öffnet, den Schließer gleich mit ab — das
     * Menü blitzt auf und ist weg.
     */
    static _schliessenBeiKlick() {
        setTimeout(() => {
            document.addEventListener('click', () => Kontextmenue.verbergen(),
                                      { once: true });
        }, 0);
    }
}

/**
 * Blendimportleiste — der Fortschritt eines Blender-Imports ganz oben in der Leiste, neben „HumanBody" (08.10.2026).
 *
 * Edgar (08.10.2026): „wenn ich ein Modell importiere, mach eine Fortschrittsleiste ganz oben, neben "HumanBody"
 * Text." Sie hängt im Titel der Topbar (`.topbar-title`, djangoBase), zeigt Namen, Schritt, Balken und Prozent, solange der
 * Import rechnet, und bleibt auch stehen, wenn der Dialog zu ist. Nach dem Neuladen der Seite fragt `aufnehmen()` den
 * Server, ob noch ein Import rechnet. Ein Klick öffnet den Dialog. Fertig: grün, nach `AUS_MS` weg; gescheitert: rot,
 * bis man sie anklickt. Den Stand liefert `Blendimportzustand` (ein Fragesteller für Leiste und Dialog).
 */
import { Blendimportzustand } from './blendimportzustand.js';
import { escapeHtml } from './utils.js';

export class Blendimportleiste {

    static ID = 'blendimport-leiste';
    static AUS_MS = 20000;
    static STIL = `
#blendimport-leiste { display: inline-flex; align-items: center; gap: 8px; margin-left: 14px; padding: 2px 10px;
    font-size: 0.8rem; font-weight: 400; cursor: pointer; border-radius: 4px; color: var(--text-muted, #c4cbdb);
    background: rgba(255, 255, 255, 0.06); max-width: 46vw; }
#blendimport-leiste:hover { background: rgba(255, 255, 255, 0.12); }
#blendimport-leiste .bil-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
#blendimport-leiste .bil-balken { flex: none; width: 150px; height: 8px; border-radius: 4px; overflow: hidden;
    background: rgba(255, 255, 255, 0.14); }
#blendimport-leiste .bil-balken > span { display: block; height: 100%; width: 0; background: var(--accent, #e94560);
    transition: width .4s; }
#blendimport-leiste .bil-prozent { flex: none; min-width: 3ch; text-align: right; font-variant-numeric: tabular-nums; }
#blendimport-leiste.fertig .bil-balken > span { background: var(--success, #5cb85c); }
#blendimport-leiste.fertig .bil-text { color: var(--success, #5cb85c); }
#blendimport-leiste.fehler .bil-balken > span { background: var(--danger, #e05252); }
#blendimport-leiste.fehler .bil-text { color: var(--danger, #e05252); }`;

    static _abschalten = null;
    static _eingerichtet = false;

    /** Einmal je Seite: den Zuhörer anmelden und das Aussehen laden. */
    static einrichten() {
        if (Blendimportleiste._eingerichtet) return;
        Blendimportleiste._eingerichtet = true;
        const stil = document.createElement('style');
        stil.textContent = Blendimportleiste.STIL;
        document.head.appendChild(stil);
        document.addEventListener(Blendimportzustand.EREIGNIS, ereignis => Blendimportleiste.zeigen(ereignis.detail));
    }

    /** Beim Laden der Seite: rechnet noch ein Import (gestartet vor dem Neuladen), zeigt die Leiste ihn weiter. */
    static async aufnehmen() {
        Blendimportleiste.einrichten();
        const kennung = await Blendimportzustand.laufend();
        if (kennung) await Blendimportzustand.beobachten(kennung);
    }

    static element() {
        let leiste = document.getElementById(Blendimportleiste.ID);
        if (leiste) return leiste;
        const titel = document.querySelector('.topbar-title');
        if (!titel) throw new Error('Blendimportleiste: die Topbar (.topbar-title) fehlt auf dieser Seite');
        leiste = document.createElement('span');
        leiste.id = Blendimportleiste.ID;
        leiste.setAttribute('role', 'status');
        leiste.innerHTML = '<span class="bil-text"></span><span class="bil-balken"><span></span></span>'
            + '<span class="bil-prozent"></span>';
        leiste.addEventListener('click', () => Blendimportleiste.klick(leiste));
        titel.appendChild(leiste);
        return leiste;
    }

    static name(zustand) {
        return (zustand.quelle || {}).name || zustand.kennung;
    }

    static zeigen(zustand) {
        const leiste = Blendimportleiste.element();
        clearTimeout(Blendimportleiste._abschalten);
        const prozent = zustand.status === 'fertig' ? 100 : Blendimportzustand.prozent(zustand);
        const name = Blendimportleiste.name(zustand);
        const schritt = Blendimportzustand.TITEL[zustand.schritt] || zustand.schritt || '';
        let text = `Import „${name}"${schritt ? ` · ${schritt}` : ''}`;
        let hinweis = 'Klick öffnet den Import-Dialog';
        if (zustand.status === 'fertig') text = `Import „${name}" fertig`;
        if (zustand.status === 'gescheitert') {
            text = `Import „${name}" gescheitert: ${zustand.fehler || 'ohne Grund'}`;
            hinweis = `${zustand.fehler || ''} — Klick öffnet den Import-Dialog`;
        }
        if (zustand.status === 'angehalten') text = `Import „${name}" angehalten`;
        if (zustand.status === 'unbekannt') text = zustand.detail || 'Import: Stand nicht lesbar';
        leiste.classList.toggle('fertig', zustand.status === 'fertig');
        leiste.classList.toggle('fehler', zustand.status === 'gescheitert' || zustand.status === 'unbekannt');
        leiste.querySelector('.bil-text').innerHTML = escapeHtml(text);
        leiste.querySelector('.bil-balken > span').style.width = `${prozent}%`;
        leiste.querySelector('.bil-prozent').textContent = `${Math.round(prozent)} %`;
        leiste.title = hinweis;
        if (zustand.status === 'fertig' || zustand.status === 'angehalten') {
            Blendimportleiste._abschalten = setTimeout(() => Blendimportleiste.entfernen(), Blendimportleiste.AUS_MS);
        }
    }

    static entfernen() {
        document.getElementById(Blendimportleiste.ID)?.remove();
    }

    static async klick(leiste) {
        const { Modellimportdialog } = await import('./modellimportdialog.js');
        await Modellimportdialog.oeffnen();
        if (!leiste.classList.contains('fehler') && !leiste.classList.contains('fertig')) return;
        Blendimportleiste.entfernen();       // Fertiges und Gescheitertes ist mit dem Klick zur Kenntnis genommen
    }
}

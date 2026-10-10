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
import { Importpflege } from './importpflege.js';
import { escapeHtml } from './utils.js';

export class Blendimportleiste {

    static ID = 'blendimport-leiste';
    static AUS_MS = 20000;
    static STIL = `
#blendimport-leiste { display: inline-flex; align-items: center; gap: 8px; margin-left: 14px; padding: 2px 10px;
    font-size: 0.8rem; font-weight: 400; cursor: pointer; border-radius: 4px; color: var(--text-muted, #c4cbdb);
    background: rgba(255, 255, 255, 0.06); max-width: 46vw; }
#blendimport-leiste:hover { background: rgba(255, 255, 255, 0.12); }
#blendimport-leiste .bil-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; flex: 1 1 auto; }
#blendimport-leiste .bil-balken { flex: none; width: 150px; height: 8px; border-radius: 4px; overflow: hidden;
    background: rgba(255, 255, 255, 0.14); }
#blendimport-leiste .bil-balken > span { display: block; height: 100%; width: 0; background: var(--accent, #e94560);
    transition: width .4s; }
#blendimport-leiste .bil-prozent { flex: none; min-width: 3ch; text-align: right; font-variant-numeric: tabular-nums; }
#blendimport-leiste.fertig .bil-balken > span { background: var(--success, #5cb85c); }
#blendimport-leiste.fertig .bil-text { color: var(--success, #5cb85c); }
#blendimport-leiste.fehler .bil-balken > span { background: var(--danger, #e05252); }
#blendimport-leiste.fehler .bil-text { color: var(--danger, #e05252); }
#blendimport-leiste.getrennt .bil-text { color: var(--warning, #f39c12); }
/* Fehler: der Text ist markierbar (Edgar, 10.10.2026: „ich kann die Fehlermeldung nicht kopieren") — ein Klick darauf öffnet weder den
   Dialog noch nimmt er die Leiste weg; dazu die Knöpfe „Kopieren" (der ganze Text) und „Löschen". Die Leiste bleibt bei max-width 46vw, der
   TEXT kürzt sich (Auslassungspunkte, Volltext im Tooltip und über „Kopieren"): bei 70vw lag „Löschen" hinter dem Fensterrand (gemessen
   10.10.2026: Leiste 577…1734 px bei 1727 px Fensterbreite — Edgar: „der Löschen-Knopf fehlt neben der Fehlermeldung"). */
#blendimport-leiste.fehler { cursor: default; }
#blendimport-leiste.fehler .bil-text { user-select: text; cursor: text; }
#blendimport-leiste.fehler .bil-balken { width: 60px; }
#blendimport-leiste .bil-kopieren, #blendimport-leiste .bil-abbrechen { flex: none; padding: 1px 8px; font-size: 0.75rem; cursor: pointer;
    border-radius: 3px; color: var(--text, #e8e8e8); background: transparent; border: 1px solid var(--border, #3a4058); }
#blendimport-leiste .bil-kopieren:hover { background: rgba(255, 255, 255, 0.14); }
#blendimport-leiste .bil-abbrechen { flex: none; padding: 1px 8px; font-size: 0.75rem; cursor: pointer; border-radius: 3px;
    color: var(--text, #e8e8e8); background: transparent; border: 1px solid var(--danger, #e05252); }
#blendimport-leiste .bil-abbrechen:hover { background: var(--danger, #e05252); }
#blendimport-leiste .bil-abbrechen:disabled { opacity: 0.5; cursor: wait; }`;

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
        // Der Kurzstand von `laufend` (Name, Schritt), solange der erste Zustand noch aussteht — ein belegter Server braucht dafür über eine Minute.
        document.addEventListener(Blendimportzustand.VORLAEUFIG, ereignis => Blendimportleiste.zeigen(ereignis.detail));
        // Der Import wurde gelöscht (hier oder im Dialog): die Leiste dieses Imports verschwindet, nichts fragt mehr nach seinem Stand.
        document.addEventListener(Importpflege.EREIGNIS, ereignis => {
            if (document.getElementById(Blendimportleiste.ID)?.dataset.kennung === ereignis.detail.kennung) {
                Blendimportzustand.vergessen();
                Blendimportleiste.entfernen();
            }
        });
    }

    /** Beim Laden der Seite: rechnet noch ein Import (gestartet vor dem Neuladen), zeigt die Leiste ihn weiter. */
    static async aufnehmen() {
        Blendimportleiste.einrichten();
        await Blendimportzustand.aufnehmen();
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
            + '<span class="bil-prozent"></span><button type="button" class="bil-kopieren" hidden>Kopieren</button>'
            + '<button type="button" class="bil-abbrechen" hidden>Abbrechen</button>';
        leiste.addEventListener('click', ereignis => {
            // Im Fehlerfall gehört ein Klick auf den Text dem Markieren; und wer gerade Text markiert hat, will nichts öffnen.
            if (leiste.classList.contains('fehler') && ereignis.target.closest('.bil-text')) return;
            if (String(window.getSelection() || '').length) return;
            Blendimportleiste.klick(leiste);
        });
        leiste.querySelector('.bil-abbrechen').addEventListener('click', ereignis => {
            ereignis.stopPropagation();            // ein Klick auf den Knopf öffnet nicht zugleich den Dialog
            Blendimportleiste.abbrechen(leiste);
        });
        leiste.querySelector('.bil-kopieren').addEventListener('click', ereignis => {
            ereignis.stopPropagation();
            Blendimportleiste.kopieren(leiste);
        });
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
        const getrennt = zustand.verbindung === 'getrennt';
        if (getrennt) {         // Der Server antwortet nicht — das ist KEIN Fehler des Imports, er rechnet weiter
            text = `Import „${name}"${schritt ? ` · ${schritt}` : ''} — Server antwortet nicht (${zustand.getrennt_s} s), `
                + 'Import rechnet weiter';
            hinweis = `${zustand.detail} — Klick öffnet den Import-Dialog`;
        }
        leiste.classList.toggle('getrennt', getrennt);
        leiste.classList.toggle('fertig', zustand.status === 'fertig');
        leiste.classList.toggle('fehler', !getrennt && (zustand.status === 'gescheitert' || zustand.status === 'unbekannt'));
        leiste.querySelector('.bil-text').innerHTML = escapeHtml(text);
        leiste.querySelector('.bil-balken > span').style.width = `${prozent}%`;
        // Vorläufig (nur der Kurzstand von `laufend`): noch keine Prozent — „0 %" wäre falsch, der Import kann bei 84 % sein.
        leiste.querySelector('.bil-prozent').textContent = zustand.vorlaeufig ? '…' : `${Math.round(prozent)} %`;
        leiste.title = hinweis;
        // Der ganze Fehlertext zum Kopieren: Name, Schritt, Kennung und die Meldung des Servers (`stand.fehler`).
        const fehlerfall = !getrennt && (zustand.status === 'gescheitert' || zustand.status === 'unbekannt');
        leiste.dataset.fehlertext = fehlerfall
            ? [text, zustand.kennung ? `Import ${zustand.kennung}` : '', zustand.schritt ? `Schritt ${zustand.schritt}` : ''].filter(Boolean).join(' · ')
            : '';
        leiste.querySelector('.bil-kopieren').hidden = !fehlerfall;
        Blendimportleiste.knopf(leiste, zustand);
        if (zustand.status === 'fertig' || zustand.status === 'angehalten') {
            Blendimportleiste._abschalten = setTimeout(() => Blendimportleiste.entfernen(), Blendimportleiste.AUS_MS);
        }
    }

    static entfernen() {
        document.getElementById(Blendimportleiste.ID)?.remove();
    }

    /**
     * Der Knopf neben dem Balken (Edgar, 10.10.2026): „Abbrechen" solange der Import rechnet, „Löschen" für einen gescheiterten oder
     * angehaltenen; ein fertiger hat keinen (sein Modell steht im Dialog „Charakter hinzufügen") — beides löscht die Importdaten.
     */
    static knopf(leiste, zustand) {
        const knopf = leiste.querySelector('.bil-abbrechen');
        const laeuft = Blendimportzustand.laeuft(zustand);
        const loeschbar = laeuft || zustand.status === 'gescheitert' || zustand.status === 'angehalten';
        leiste.dataset.kennung = zustand.kennung || '';
        leiste.dataset.laeuft = laeuft ? '1' : '';
        knopf.hidden = !loeschbar || !zustand.kennung;
        knopf.textContent = laeuft ? 'Abbrechen' : 'Löschen';
        knopf.title = laeuft ? 'Import anhalten und alle Importdaten löschen' : 'Importdaten dieses Imports löschen';
    }

    /** „Kopieren": den ganzen Fehlertext (nicht den gekürzten, der im Balken steht) in die Zwischenablage. */
    static kopieren(leiste) {
        return Importpflege.kopieren(leiste.dataset.fehlertext || leiste.querySelector('.bil-text').textContent,
                                     leiste.querySelector('.bil-kopieren'));
    }

    /** „Abbrechen": Rückfrage mit dem Plan, dann anhalten und löschen; die Leiste hört vorher auf, den Stand zu erfragen. */
    static async abbrechen(leiste) {
        const kennung = leiste.dataset.kennung;
        const knopf = leiste.querySelector('.bil-abbrechen');
        if (!kennung || knopf.disabled) return;
        knopf.disabled = true;
        try {
            const geloescht = await Importpflege.loeschen(kennung, {
                abbrechen: leiste.dataset.laeuft === '1', vorSenden: () => Blendimportzustand.vergessen(),
            });
            if (!geloescht) return;
            Blendimportleiste.entfernen();          // (das Ereignis „blendimport-geloescht" kommt von `Importpflege`)
        } catch (fehler) {
            window.alert(`Nicht gelöscht: ${fehler.message}`);
            Blendimportzustand.beobachten(kennung);      // der Import besteht noch: die Leiste zeigt ihn weiter
        } finally {
            knopf.disabled = false;
        }
    }

    static async klick(leiste) {
        const { Modellimportdialog } = await import('./modellimportdialog.js');
        await Modellimportdialog.oeffnen();
        if (!leiste.classList.contains('fehler') && !leiste.classList.contains('fertig')) return;
        Blendimportleiste.entfernen();       // Fertiges und Gescheitertes ist mit dem Klick zur Kenntnis genommen
    }
}

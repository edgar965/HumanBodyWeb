import { Serverabruf } from '../../viewer/gemeinsam/serverabruf.js';
import { Recherchehuman3dprio } from './recherchehuman3dprio.js';

/**
 * Recherchehuman3d — das Fenster der Seite „Hilfe → Recherche → Human 3D" (04.10.2026).
 *
 * Edgar: „Klick auf Eintrag ToDo: Popup mit mehr Infos, mehr Bildern." Die Daten eines Projekts holt das Fenster beim Klick von
 * `/hilfe/recherche/human-3d/popup/<id>/` (gebaut von `Recherchetabelle.popup`; früher stand alles als JSON-Block in der Seite — bei 1.043 Projekten über 2,5 MB doppelt). Alles, was aus der JSON-Datei kommt, stammt aus fremden READMEs: Texte gehen nur über `textContent`, Adressen nur als https-Link bzw. -Bild
 * (der Server hat sie schon geprüft). Ein Bild, das GitHub nicht mehr liefert, verschwindet still (Tabelle: „–"; Fenster: der Rahmen entfällt).
 */
export class Recherchehuman3d {

    static POPUP = '/hilfe/recherche/human-3d/popup/';

    constructor() {
        this.fenster = document.getElementById('rc-popup');
        this.inhalt = document.getElementById('rc-popup-inhalt');
        this.titel = document.getElementById('rc-popup-titel');
    }

    binden() {
        if (!this.fenster) return;
        const tabelle = document.querySelector('table.rc-tabelle');
        if (tabelle) Recherchehuman3dprio.binden(tabelle);
        document.addEventListener('click', (e) => {
            const ziel = e.target instanceof Element ? e.target : null;
            if (!ziel) return;
            const bild = ziel.closest('td.rc-bildzelle img.rc-bild');
            if (bild) { this.bildOeffnen(bild); return; }
            const zelle = ziel.closest('td.rc-todozelle');
            if (!zelle) return;
            const zeile = zelle.closest('tr[data-id]');
            if (zeile) this.oeffnen(zeile.dataset.id);
        });
        document.getElementById('rc-popup-zu').addEventListener('click', () => this.fenster.close());
        // Klick auf den abgedunkelten Rand schließt (das Ziel ist dann das <dialog> selbst, nicht sein Inhalt).
        this.fenster.addEventListener('click', (e) => { if (e.target === this.fenster) this.fenster.close(); });
        // `error` steigt nicht auf, wird aber in der Fangphase gesehen.
        document.addEventListener('error', (e) => Recherchehuman3d.bildFehlt(e.target), true);
    }

    /** Das Hauptbild der Tabelle groß in einem eigenen Fenster (Edgar, 04.10.2026: „Klick auf Hauptbild öffnet mir das im Popup"). Das Fenster entsteht beim ersten Klick. */
    bildOeffnen(bild) {
        const E = Recherchehuman3d;
        if (!this.bildfenster) {
            const fenster = E.el('dialog', 'rc-bildfenster');
            fenster.id = 'rc-bildfenster';
            const zu = E.el('button', 'rc-bildfenster-zu', '×');
            zu.type = 'button';
            zu.title = 'Schließen';
            zu.addEventListener('click', () => fenster.close());
            this.bildgross = E.el('img', 'rc-bildfenster-bild');
            this.bildtitel = E.el('div', 'rc-bildfenster-titel');
            fenster.append(zu, this.bildgross, this.bildtitel);
            fenster.addEventListener('click', (e) => { if (e.target === fenster) fenster.close(); });
            document.body.appendChild(fenster);
            this.bildfenster = fenster;
        }
        const repo = bild.closest('tr')?.querySelector('a[target="_blank"]')?.textContent.trim();
        this.bildgross.alt = bild.alt;
        this.bildgross.src = bild.currentSrc || bild.src;
        this.bildtitel.textContent = repo ? `${bild.alt} — ${repo}` : bild.alt;
        this.bildfenster.showModal();
    }

    static bildFehlt(ziel) {
        if (!(ziel instanceof HTMLImageElement) || !ziel.classList.contains('rc-bild')) return;
        const rahmen = ziel.closest('.rc-galerie-bild');
        if (rahmen) { rahmen.remove(); return; }
        const platz = document.createElement('span');
        platz.className = 'rc-fehlt';
        platz.textContent = '–';
        platz.title = 'Das Bild konnte nicht geladen werden';
        ziel.replaceWith(platz);
    }

    static el(tag, klasse, text) {
        const e = document.createElement(tag);
        if (klasse) e.className = klasse;
        if (text !== undefined && text !== null) e.textContent = text;
        return e;
    }

    static abschnitt(titel) {
        const a = Recherchehuman3d.el('section', 'rc-abschnitt');
        a.appendChild(Recherchehuman3d.el('h3', '', titel));
        return a;
    }

    static liste(punkte, klasse) {
        const ul = Recherchehuman3d.el('ul', klasse);
        for (const p of punkte || []) ul.appendChild(Recherchehuman3d.el('li', '', p));
        return ul;
    }

    static datum(iso) {
        const teile = String(iso || '').slice(0, 10).split('-');
        return teile.length === 3 ? teile.reverse().join('.') : '–';
    }

    /** Holt die Daten des einen Projekts (statt aller in der Seite) und zeigt das Fenster. */
    async oeffnen(id) {
        let p;
        try {
            p = await Serverabruf.json(`${Recherchehuman3d.POPUP}${encodeURIComponent(id)}/`);
        } catch (fehler) {
            window.alert(`Die Angaben zum Projekt konnten nicht geladen werden: ${fehler.daten?.error || fehler.message}`);
            return;
        }
        if (!p) return;
        const E = Recherchehuman3d;
        this.titel.textContent = p.name;
        this.inhalt.replaceChildren();

        const kopf = E.el('div', 'rc-popup-eckdaten');
        kopf.appendChild(E.el('span', 'rc-chip', p.kategorie));
        const meta = [`★ ${Number(p.sterne || 0).toLocaleString('de-DE')}`, `zuletzt ${E.datum(p.aktualisiert)}`, `angelegt ${E.datum(p.angelegt)}`, p.sprache, p.lizenz].filter(Boolean);
        kopf.appendChild(E.el('span', 'rc-popup-meta', meta.join(' · ')));
        if (p.url) {
            const a = E.el('a', 'rc-popup-link', p.repo);
            a.href = p.url;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            kopf.appendChild(a);
        }
        this.inhalt.appendChild(kopf);
        if (p.fork_von) {
            const fork = E.el('p', 'rc-popup-fork');
            fork.append(E.el('b', '', 'Fork von '), p.fork_von, p.fork_grund ? ` — ${p.fork_grund}` : '');
            this.inhalt.appendChild(fork);
        }
        this.inhalt.appendChild(E.el('p', 'rc-popup-kurz', p.kurz));

        const todo = E.abschnitt('Was uns fehlt (ToDo)');
        todo.appendChild(E.liste(p.todo, 'rc-todo-liste'));
        this.inhalt.appendChild(todo);

        // `quellen` läuft parallel zu [Hauptbild, …Galerie] (ohne leere Plätze): die Vorschau liegt lokal, ein Klick öffnet das Original beim Projekt, falls bekannt.
        const bilder = [p.bild, ...(p.bilder || [])].filter(Boolean);
        if (bilder.length) {
            const galerie = E.abschnitt('Bilder aus dem Projekt');
            const reihe = E.el('div', 'rc-galerie');
            for (const [nr, adresse] of bilder.entries()) {
                const rahmen = E.el('a', 'rc-galerie-bild');
                const quelle = (p.quellen || [])[nr];
                rahmen.href = quelle || adresse;
                rahmen.title = quelle ? 'Original beim Projekt öffnen' : 'Bild öffnen';
                rahmen.target = '_blank';
                rahmen.rel = 'noopener noreferrer';
                const bild = E.el('img', 'rc-bild');
                bild.loading = 'lazy';
                bild.referrerPolicy = 'no-referrer';
                bild.alt = p.name;
                bild.src = adresse;
                rahmen.appendChild(bild);
                reihe.appendChild(rahmen);
            }
            galerie.appendChild(reihe);
            this.inhalt.appendChild(galerie);
        }

        if ((p.hf || []).length) {
            const hf = E.abschnitt('Bei Hugging Face');
            const liste = E.el('ul', 'rc-hf-popup');
            for (const h of p.hf) {
                const li = E.el('li');
                const a = E.el('a', `rc-hf rc-hf-${h.typ}`, h.label);
                a.href = h.url;
                a.target = '_blank';
                a.rel = 'noopener noreferrer';
                li.append(a, ` ${h.id} — ♥ ${Number(h.likes || 0).toLocaleString('de-DE')}`);
                liste.appendChild(li);
            }
            hf.appendChild(liste);
            this.inhalt.appendChild(hf);
        }

        const was = E.abschnitt('Beschreibung');
        was.appendChild(E.el('p', '', p.beschreibung));
        this.inhalt.appendChild(was);

        const details = E.abschnitt('Details');
        details.appendChild(E.liste(p.details, 'rc-detail-liste'));
        this.inhalt.appendChild(details);

        this.fenster.showModal();
        this.inhalt.scrollTop = 0;
    }
}

new Recherchehuman3d().binden();

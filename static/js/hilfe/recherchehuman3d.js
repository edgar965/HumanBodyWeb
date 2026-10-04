/**
 * Recherchehuman3d — das Fenster der Seite „Hilfe → Recherche → Human 3D" (04.10.2026).
 *
 * Edgar: „Klick auf Eintrag ToDo: Popup mit mehr Infos, mehr Bildern." Die Daten stehen als JSON-Block `#rc-daten` in der Seite (je Projekt unter seiner `id`, gebaut von
 * `Recherchetabelle.popup`). Alles, was aus der JSON-Datei kommt, stammt aus fremden READMEs: Texte gehen nur über `textContent`, Adressen nur als https-Link bzw. -Bild
 * (der Server hat sie schon geprüft). Ein Bild, das GitHub nicht mehr liefert, verschwindet still (Tabelle: „–"; Fenster: der Rahmen entfällt).
 */
export class Recherchehuman3d {

    constructor() {
        this.fenster = document.getElementById('rc-popup');
        const block = document.getElementById('rc-daten');
        this.daten = block ? JSON.parse(block.textContent) : {};
        this.inhalt = document.getElementById('rc-popup-inhalt');
        this.titel = document.getElementById('rc-popup-titel');
    }

    binden() {
        if (!this.fenster) return;
        document.addEventListener('click', (e) => {
            const zelle = e.target instanceof Element ? e.target.closest('td.rc-todozelle') : null;
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

    static bildFehlt(ziel) {
        if (!(ziel instanceof HTMLImageElement) || !ziel.classList.contains('rc-bild')) return;
        const rahmen = ziel.closest('.rc-galerie-bild');
        if (rahmen) { rahmen.remove(); return; }
        const platz = document.createElement('span');
        platz.className = 'rc-fehlt';
        platz.textContent = '–';
        platz.title = 'Das Bild ist bei GitHub nicht mehr erreichbar';
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
        const d = new Date(`${String(iso).slice(0, 10)}T00:00:00`);
        return Number.isNaN(d.getTime()) ? String(iso || '–') : d.toLocaleDateString('de-DE');
    }

    oeffnen(id) {
        const p = this.daten[id];
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
        this.inhalt.appendChild(E.el('p', 'rc-popup-kurz', p.kurz));

        const todo = E.abschnitt('Was uns fehlt (ToDo)');
        todo.appendChild(E.liste(p.todo, 'rc-todo-liste'));
        this.inhalt.appendChild(todo);

        const bilder = [p.bild, ...(p.bilder || [])].filter((b, i, alle) => b && alle.indexOf(b) === i);
        if (bilder.length) {
            const galerie = E.abschnitt('Bilder aus dem Projekt');
            const reihe = E.el('div', 'rc-galerie');
            for (const adresse of bilder) {
                const rahmen = E.el('a', 'rc-galerie-bild');
                rahmen.href = adresse;
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

/**
 * Meshfigurteileleiste — je Bestandteil des Netzes ein Schaltknopf unter den Knöpfen der 3D-Ansicht (14.10.2026).
 *
 * Edgar: „dieser kleine weiße Flügel am Arm ist nicht als extra Objekt erkannt, das möchte ich auch löschen." Seit der Flügel ein Bestandteil ist (SAM 3, `angel wing`), steht er als eigenes Objekt in der Bühne; dieser Knopf blendet
 * ihn aus — ohne das Netz anzufassen (das Entfernen aus dem Netz ließ Löcher an den Fingern, weil der Flügel dort die Hand des Netzes überdeckt). Ein ausgeblendetes Netz fehlt auch im Export (`Modellexportinhalt.objekte` fragt
 * `mesh.visible`). Die Klasse kennt keinen Gegenstand: sie zeigt, was `Meshfigurteile.liste()` nennt. Ohne Bestandteile bleibt die Leiste versteckt.
 */
export class Meshfigurteileleiste {

    constructor(behaelter, teile) {
        this.behaelter = behaelter;
        this.teile = teile;
        this._stand = null;
    }

    /** Die Leiste zum jetzigen Stand der Liste bauen (neu, wenn sich die Namen geändert haben). */
    zeigen() {
        if (!this.behaelter) return;
        const liste = this.teile.liste();
        const stand = JSON.stringify(liste.map(t => t.name));
        if (stand !== this._stand) {
            this._stand = stand;
            this.behaelter.replaceChildren();
            for (const t of liste) this.behaelter.append(this._knopf(t));
        }
        for (const knopf of this.behaelter.querySelectorAll('button[data-teil]')) {
            const t = liste.find(x => x.name === knopf.dataset.teil);
            knopf.classList.toggle('active', Boolean(t && t.an));
        }
        this.behaelter.classList.toggle('hb-versteckt', liste.length === 0);
    }

    _knopf(t) {
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'schaltknopf active';
        knopf.dataset.teil = t.name;
        knopf.title = `Bestandteil „${t.name}“ ein- oder ausblenden — ausgeblendet fehlt er auch im Export; das Netz bleibt unverändert`;
        const symbol = document.createElement('i');
        symbol.className = 'fas fa-cube';
        knopf.append(symbol, ` ${t.name}`);
        knopf.addEventListener('click', () => {
            this.teile.schalten(t.name, !knopf.classList.contains('active'));
            this.zeigen();
        });
        return knopf;
    }
}

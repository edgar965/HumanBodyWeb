import { escapeHtml } from '../utils.js';
import { Genesis9umrissfenster } from './genesis9umrissfenster.js';
import { Genesis9hautteilregler } from './genesis9hautteilregler.js';

/**
 * Genesis9eigenregler — der Abschnitt „Eigen" direkt unter Genesis 9 (`Genesis9/eigenregler.py`; 25.10.2026, Edgar: „Mach einen neuen Abschnitt bei den Genesis-Reglern: Eigen,
 * darin Unterkategorien wie Kopf, Rumpf usw.", dann „verschiebe den Eigen-Bereich direkt als Hauptkategorie unter Genesis 9").
 *
 * Der Bereich kommt mit dem Reglerplan (`schluessel` eigen_regler) und wird hier herausgenommen (`teilen`, wie `Genesis9genitalien`). Je Gruppe (Kopf, Hals, Rumpf …) ein
 * aufklappbarer Kasten, leere Gruppen mit „Noch keine Regler"; je Regler Schieber + Knopf „Formen …" (`Genesis9umrissfenster`).
 */
export class Genesis9eigenregler {

    static SCHLUESSEL = 'eigen_regler';

    /** → [Plan ohne den Bereich, Bereich] */
    static teilen(plan) {
        const bereiche = plan?.bereiche || [];
        const block = bereiche.find(b => b.schluessel === Genesis9eigenregler.SCHLUESSEL) || { schluessel: Genesis9eigenregler.SCHLUESSEL, regler: [], gruppen: [] };
        return [{ ...plan, bereiche: bereiche.filter(b => b !== block) }, block];
    }

    static fuellen(behaelter, block, inst, zeileBauen) {
        if (!behaelter) return;
        behaelter.innerHTML = '';
        const gruppen = [...(block.gruppen || []), ...new Set(block.regler.map(r => r.gruppe).filter(g => !(block.gruppen || []).includes(g)))];
        if (!gruppen.length) behaelter.innerHTML = '<div class="gedaempft">Keine Eigenregler vom Server.</div>';
        for (const name of gruppen) {
            const regler = block.regler.filter(r => r.gruppe === name);
            const textur = Genesis9hautteilregler.zeilen(inst, name);
            const kasten = document.createElement('details');
            kasten.className = 'uma-gruppe g9-untergruppe';
            kasten.dataset.gruppe = name;
            kasten.innerHTML = `<summary>${escapeHtml(name)} <span class="gedaempft">(${regler.length + textur.length})</span></summary>`;
            if (!regler.length && !textur.length) kasten.insertAdjacentHTML('beforeend', '<div class="gedaempft g9-eigenregler-leer">Noch keine Regler</div>');
            if (regler.length) kasten.insertAdjacentHTML('beforeend', '<div class="gedaempft g9-eigenregler-unter">Form</div>');
            for (const r of regler) kasten.appendChild(Genesis9eigenregler._zeile(r, inst, zeileBauen));
            // Texturregler je Körperteil (Hautfarbe, Tattoo — `Genesis9hautteilregler`, Shader-Zusatz der Hautebenen, wirken ohne Neubau)
            if (textur.length) kasten.insertAdjacentHTML('beforeend', '<div class="gedaempft g9-eigenregler-unter">Textur</div>');
            for (const z of textur) kasten.appendChild(z);
            behaelter.appendChild(kasten);
        }
        // „Kleider“ und „Haare“ standen hier bis zur Stufe K2a (25.10.2026); seither in Assets → Eigen (`Genesis9eigengarderobe`, Edgar: „Die neuen Kleider-Regler sollen
        // in den Tab Assets → Eigen“). Hier bleiben die Körper-Eigenregler und die Hauttextur.
    }

    static _zeile(regler, inst, zeileBauen) {
        const zeile = zeileBauen(regler);
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'btn-toggle g9-eigenregler-knopf';
        knopf.textContent = 'Formen …';
        knopf.title = `${regler.anzeige} von Hand formen`;
        knopf.addEventListener('click', () => Genesis9umrissfenster.oeffnen({ inst, regler, zeile }));
        zeile.appendChild(knopf);
        return zeile;
    }
}

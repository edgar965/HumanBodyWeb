import { Exportleistefigur } from '../exportleiste/exportleistefigur.js';

/**
 * Engine2d3dKleiderexportquelle — die Figur der Seite „2D3D Kleider" für die Exportleiste (31.10.2026, Edgar „mach beides").
 *
 * GLB, Blender und Render nimmt der Server vom Auftrag (`core/dienste/engine2d3dkleiderexportquelle.py`, `zustand.eigenes_modell`: das Stand-Modell mit Stoff und Strähnen).
 * Aus der Seite kommt nur die OBJ: die Genesis-Figur der Bühne (`Meshfigurbuehne.modell`, „3DModell"), wie bis zur Umstellung über „Modell speichern" → OBJ (`Meshfigurspeicher`).
 */
export class Engine2d3dKleiderexportquelle {

    constructor(seite) {
        this.seite = seite;
    }

    async modell() {
        const inst = this.seite.buehne?.modell;
        if (!inst) throw new Error('Die Bühne zeigt keine Genesis-Figur — „3DModell“ einschalten (OBJ schreibt die Seite aus dieser Figur)');
        await Exportleistefigur.vollBauen(inst);
        return { inst };
    }
}

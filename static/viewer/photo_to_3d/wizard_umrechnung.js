/**
 * Umrechnung zwischen Foto- und Leinwandkoordinaten im Ausricht-Assistenten.
 *
 * Umbau 16.08.2026: `transformPtGlobal` gab es zweimal — hier und als innere
 * `transformPt` in `renderWizardCanvas()`, Zeile für Zeile gleich. Jetzt steht
 * sie an einer Stelle, zusammen mit ihrer Umkehrung.
 *
 * Zwei Fälle: Bei einer unbewegten Figur wird um die Mitte des Netzrahmens
 * skaliert, bei einer posierten um die Mitte des Umrisses selbst.
 */

/** Fotopunkt → Leinwandpunkt. */
export function transformPtGlobal(px, py, verschiebung, netzX, netzY, posiert,
                                  mitteX, mitteY, maszstab) {
    if (posiert) {
        return [((px - mitteX) * verschiebung.scale + mitteX
                 + verschiebung.center_x) * maszstab,
                ((py - mitteY) * verschiebung.scale + mitteY
                 + verschiebung.center_y) * maszstab];
    }
    return [((px - netzX) * verschiebung.scale + verschiebung.center_x) * maszstab,
            ((py - netzY) * verschiebung.scale + verschiebung.center_y) * maszstab];
}

/** Leinwandpunkt → Fotopunkt. */
export function inverseTransformPt(x, y, verschiebung, netzX, netzY, posiert,
                                   mitteX, mitteY, maszstab) {
    const px = x / maszstab;
    const py = y / maszstab;
    if (posiert) {
        return [(px - mitteX - verschiebung.center_x) / verschiebung.scale + mitteX,
                (py - mitteY - verschiebung.center_y) / verschiebung.scale + mitteY];
    }
    return [(px - verschiebung.center_x) / verschiebung.scale + netzX,
            (py - verschiebung.center_y) / verschiebung.scale + netzY];
}

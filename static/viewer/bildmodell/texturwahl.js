/**
 * Texturwahl — je Kachel ein Farbfeld (Hautton des Bildes) und ein Häkchen
 * „für die Textur"; oben die Zusammenfassung „Hautton aus n Bildern".
 *
 * Edgar (19.09.2026): „welches Bild für die Textur genutzt werden könnte und
 * welches nicht, und wie sich dann interaktiv die Textur / das Modell
 * verändert, wenn ich eine Textur anwähle / abwähle." Die Sichtung misst je
 * Ausschnitt `textur` (`hauttonprobe.py`: Hautton, Anteil, Maskenhöhe,
 * tauglich, grund); das Häkchen schreibt `textur_an` an den Eintrag, der
 * Server mischt sofort neu und die 3D-Ansicht tönt die Haut (`Ansicht3d.
 * hauttonAnwenden`). Untaugliche Bilder zeigen den Grund und sind abgewählt.
 */
export class Texturwahl {

    /** Das Feld für die Kachel — oder null, wenn die Sichtung nichts gemessen hat. */
    static feld(b, stellen) {
        const t = b.textur;
        if (!t) return null;
        const zeile = document.createElement('label');
        zeile.className = 'bildmodell-textur';
        const an = 'textur_an' in b ? !!b.textur_an : !!t.tauglich;
        if (t.hautton) {
            const farbe = document.createElement('span');
            farbe.className = 'bildmodell-hautton';
            farbe.style.background = `rgb(${t.hautton.join(',')})`;
            farbe.title = `Hautton ${t.hautton.join(', ')} · Haut ${Math.round((t.anteil || 0) * 100)} % der Maske · ${t.maske_px} px`;
            zeile.appendChild(farbe);
        }
        const kasten = document.createElement('input');
        kasten.type = 'checkbox';
        kasten.checked = an && !!t.hautton;
        kasten.disabled = !t.hautton;
        kasten.title = t.tauglich ? 'für die Textur (Hautton) verwenden' : `nicht tauglich: ${t.grund || ''}`;
        kasten.addEventListener('change', () => stellen(b.datei, { textur_an: kasten.checked }));
        zeile.appendChild(kasten);
        const text = document.createElement('span');
        text.className = 'hb-hinweis';
        text.textContent = t.tauglich ? 'Textur' : (t.grund || 'nicht tauglich');
        zeile.appendChild(text);
        return zeile;
    }

    /** Die Zusammenfassung in der Kopfzeile der Bilderkarte. */
    static zusammenfassung(zustand) {
        const feld = document.getElementById('textur-stand');
        if (!feld) return;
        const t = zustand.textur || {};
        feld.innerHTML = '';
        if (!t.hautton) {
            feld.textContent = t.tauglich ? 'Hautton: kein Bild gewählt' : 'Hautton: noch nicht gemessen';
            return;
        }
        const farbe = document.createElement('span');
        farbe.className = 'bildmodell-hautton';
        farbe.style.background = `rgb(${t.hautton.join(',')})`;
        feld.append(farbe, ` Hautton aus ${t.bilder} von ${t.tauglich} tauglichen Bildern — wirkt sofort auf das Modell oben`);
    }
}

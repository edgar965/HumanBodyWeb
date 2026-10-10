/**
 * Modellimportstil — das CSS des Dialogs „Modell importieren" (`Modellimportdialog`).
 *
 * Eigene Klasse, damit der Rahmen des Dialogs unter 300 Zeilen bleibt (struktur.md). Der Modalrahmen selbst
 * (`.scene-modal-overlay`, Kopf, Fuß) kommt aus `figurwahldialog.css`; hier stehen nur die Felder, der Lauf und seit
 * 10.10.2026 die Reiter (JSON · Blender · OBJ · FBX).
 */
export class Modellimportstil {

    static CSS = `
#modellimport-dialog .scene-modal { width: min(760px, 96vw); }
#modellimport-dialog .mi-reiter { display: flex; gap: 2px; margin: -4px 0 10px; border-bottom: 1px solid var(--border, #3a4058); }
#modellimport-dialog .mi-reiter button { padding: 6px 16px; color: var(--text-muted, #9aa3b5); background: transparent;
    border: 1px solid transparent; border-bottom: 0; border-radius: 4px 4px 0 0; cursor: pointer; font-weight: 600; }
#modellimport-dialog .mi-reiter button:hover { color: var(--text, #e8e8e8); }
#modellimport-dialog .mi-reiter button.aktiv { color: var(--text, #e8e8e8); background: var(--bg-input, #1d2233);
    border-color: var(--border, #3a4058); box-shadow: 0 2px 0 var(--accent, #e94560) inset; }
#modellimport-dialog .mi-tafel[hidden] { display: none; }
#modellimport-dialog .mi-zeile { display: grid; grid-template-columns: 210px 1fr; gap: 6px 12px; align-items: center;
    margin: 6px 0; }
#modellimport-dialog input, #modellimport-dialog select { width: 100%; padding: 5px 7px; color: var(--text, #e8e8e8);
    background: var(--bg-input, #1d2233); border: 1px solid var(--border, #3a4058); border-radius: 4px;
    color-scheme: dark; }
#modellimport-dialog .scene-modal-body button { padding: 5px 12px; color: var(--text, #e8e8e8);
    background: var(--bg-input, #1d2233); border: 1px solid var(--border, #3a4058); border-radius: 4px; cursor: pointer; }
#modellimport-dialog .scene-modal-body .mi-reiter button { padding: 6px 16px; background: transparent; border-color: transparent; }
#modellimport-dialog .scene-modal-body .mi-reiter button.aktiv { background: var(--bg-input, #1d2233);
    border-color: var(--border, #3a4058); }
#modellimport-dialog .mi-hinweis { grid-column: 2; font-size: 0.75rem; color: var(--text-muted, #9aa3b5); }
#modellimport-dialog .mi-abschnitt { margin: 14px 0 6px; font-weight: 600; }
#modellimport-dialog .mi-abschnitt:first-child { margin-top: 0; }
#modellimport-dialog .mi-quelle { min-height: 1.4em; font-size: 0.8rem; }
#modellimport-dialog .mi-haut { margin: 4px 0 0 222px; font-size: 0.78rem; color: var(--text-muted, #9aa3b5); }
#modellimport-dialog .mi-zeile.inaktiv { opacity: 0.45; }
#modellimport-dialog .scene-modal-footer button:disabled { opacity: 0.5; cursor: not-allowed; }
#modellimport-dialog .scene-modal-footer button[hidden] { display: none; }
#modellimport-dialog .mi-balken { height: 10px; background: var(--bg-input, #1d2233); border-radius: 5px;
    overflow: hidden; margin: 8px 0; }
#modellimport-dialog .mi-balken > div { height: 100%; width: 0; background: var(--accent, #e94560);
    transition: width .4s; }
#modellimport-dialog .mi-schritte { display: flex; flex-wrap: wrap; gap: 4px 10px; font-size: 0.78rem; }
#modellimport-dialog .mi-schritte .fertig { color: var(--success, #5cb85c); }
#modellimport-dialog .mi-schritte .aktiv { color: var(--accent, #e94560); font-weight: 600; }`;
}

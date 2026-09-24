import { defineConfig } from 'vite';
import path from 'path';

/**
 * Eigenstaendiger Bau NUR von @theatre/core + @theatre/studio als lokale
 * ESM-Dateien — fuer BVH Studio (`static/vendor/theatre/`), das wie three.js
 * ohne CDN/Netz auskommen muss (`templates/bvh_studio.html`,
 * Import-Map-Kommentar dort). `vite.config.js` (Theatre-App selbst) bleibt
 * unveraendert; dieser Bau laeuft separat:
 *
 *     npm run build:vendor-theatre
 */
export default defineConfig({
    build: {
        outDir: path.resolve(__dirname, '../static/vendor/theatre'),
        emptyOutDir: false,
        lib: {
            entry: {
                core: path.resolve(__dirname, 'src/vendor/theatre-core-entry.js'),
                studio: path.resolve(__dirname, 'src/vendor/theatre-studio-entry.js'),
            },
            formats: ['es'],
            fileName: (_format, name) => `${name}.esm.js`,
        },
        minify: 'esbuild',
        sourcemap: false,
    },
    define: {
        'import.meta.env.DEV': 'true',
        // Vites App-Baumodus (vite.config.js) ersetzt process.env.NODE_ENV
        // automatisch — der Bibliotheksmodus hier nicht. Ohne das: `Uncaught
        // ReferenceError: process is not defined` beim ersten `getProject()`
        // (Theatre.js prueft `process.env.NODE_ENV` fuer Warnungen).
        'process.env.NODE_ENV': JSON.stringify('production'),
    },
});

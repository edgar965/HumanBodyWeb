import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
    resolve: {
        // Allow model_generator.js (outside TheatreJS/) to resolve 'three'
        dedupe: ['three'],
        alias: {
            // Die Module unter static/viewer/gemeinsam/ leiten auf djangoBase
            // weiter — mit einer ABSOLUTEN URL (`/static/djangobase/js/...`),
            // wie der Browser sie braucht. Beim Bauen gibt es keinen Server,
            // der sie ausliefert, also zeigt dieser Alias auf das Paket auf der
            // Platte. Ohne ihn scheitert der Build mit „Could not resolve"
            // (17.08.2026, beim Umstellen von console.* auf Protokoll).
            '/static/djangobase/js': path.resolve(
                __dirname, '../../../shared/djangoBase/djangobase/static/djangobase/js'),
        },
    },
    build: {
        outDir: path.resolve(__dirname, '../static/theatre'),
        emptyOutDir: true,
        rollupOptions: {
            input: path.resolve(__dirname, 'src/main.js'),
            output: {
                entryFileNames: 'theatre-app.js',
                // Keep everything in one file
                inlineDynamicImports: true,
            },
        },
        minify: 'esbuild',
        sourcemap: false,
    },
    // Force DEV-like behaviour so Theatre Studio is not tree-shaken away
    define: {
        'import.meta.env.DEV': 'true',
    },
});

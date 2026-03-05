import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
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

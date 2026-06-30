# Configuración del Frontend — Explicación Didáctica

## 1. `vite.config.js` — Configuración de Vite

Archivo mínimo de configuración para Vite, el bundler/build tool:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

- **`@vitejs/plugin-react`**: plugin oficial que añade soporte para React (JSX transform, React Refresh para hot reload).
- Sin configuración adicional: Vite usa valores por defecto sensatos. El servidor de desarrollo corre en `http://localhost:5173` y el build output va a `dist/`.

**¿Por qué Vite?** Es significativamente más rápido que Webpack/CRA porque usa ES modules nativos en desarrollo y un bundler optimizado (Rollup) en producción.

---

## 2. `index.html` — Punto de entrada

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>client</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

Puntos clave:
- **`lang="en"`**: está en inglés. Para una app en español, debería ser `lang="es"`.
- **`<div id="root">`**: el contenedor donde React monta la aplicación.
- **`<script type="module">`**: Vite aprovecha los ES modules nativos. No hay bundling en desarrollo.
- **Favicon**: usa `/favicon.svg` (SVG, escalable).

---

## 3. `eslint.config.js` — ESLint con flat config

Usa el nuevo sistema de **flat config** de ESLint v9+:

```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default defineConfig([
  globalIgnores(['dist']),           // Ignorar carpeta de build
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,                // Reglas base de JS
      reactHooks.configs.flat.recommended,   // Reglas de React Hooks
      reactRefresh.configs.vite,             // Reglas de React Refresh
    ],
    languageOptions: {
      globals: globals.browser,              // Variables globales del navegador
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
])
```

### Reglas incluidas:
- **`@eslint/js` recommended**: reglas básicas de JavaScript (variables no usadas, comparaciones, etc.)
- **`react-hooks`**: verifica que los hooks se usen correctamente (reglas de hooks: no llamar hooks dentro de condicionales, dependencias correctas).
- **`react-refresh`**: asegura que los componentes exportados sean compatibles con Hot Module Replacement de Vite.

### Nota sobre `globals`
```javascript
globals: globals.browser
```
Define `window`, `document`, `console`, `fetch`, etc. como globales para que ESLint no las marque como indefinidas.

---

## Resumen

| Archivo | Propósito | Tecnología |
|---|---|---|
| `vite.config.js` | Configuración del bundler | Vite + React plugin |
| `index.html` | Punto de entrada HTML | HTML5 + ES modules |
| `eslint.config.js` | Linting y calidad de código | ESLint flat config |

Esta configuración es la **base mínima** para un proyecto React moderno con Vite: rápida, con linting y hot reload. No incluye configuración de proxy, variables de entorno, CSS preprocessors ni testing (todo eso se puede añadir según necesidades).

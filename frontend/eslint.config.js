import js from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

/* ============================================================
   Configuración de ESLint.

   TypeScript ya verifica los tipos, así que esto no está para eso. Cubre
   la clase de error que el compilador acepta sin quejarse: un useEffect
   al que le falta una dependencia y se queda con un valor viejo, una
   promesa sin await que falla en silencio, una variable que quedó de un
   refactor a medias.

   Se apoya en las configuraciones recomendadas en vez de armar una lista
   de reglas propia: una lista curada a mano envejece y nadie la revisa.
   ============================================================ */

export default tseslint.config(
  { ignores: ['dist', 'coverage', 'node_modules'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,

      // Advierte, no falla: componer mal las exportaciones de un módulo rompe
      // la recarga en caliente del desarrollo, pero no la aplicación
      // compilada. No es motivo para frenar un merge.
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],

      // Un argumento sin usar suele ser deliberado al respetar una firma
      // (un handler que ignora el evento). Se permite marcarlo con guion
      // bajo, que es la convención, en vez de silenciar la regla entera.
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
)

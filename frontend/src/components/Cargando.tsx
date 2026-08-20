/* ============================================================
   Espera.

   Dos formas de la misma pieza:

   - BloqueCarga: el bloque en sí — anillo, título y texto. Es solo la
     presentación: no declara rol ni región viva, porque quién anuncia la
     espera depende de dónde se lo use. Se usa suelto cuando no hay nada
     detrás que velar, como en P-02 mientras se busca un análisis por su
     id; ahí la página lo envuelve en un `status`, que informa sin
     interrumpir.

   - Cargando: el mismo bloque bajo un velo, que es el patrón del diseño
     para P-01. El formulario sigue visible y completo detrás, y eso es
     deliberado — comunica que los datos no se perdieron. Ahí sí hay una
     interrupción sobre contenido existente, así que el velo es un
     `alertdialog`. El bloque no agrega un rol propio: dos regiones vivas
     anidadas harían que la espera se anuncie dos veces.

   El texto de espera de P-01 es el del diseño, con una corrección: decía
   que «los cambios quedan guardados», lo que se contradecía con el resto
   del producto. Ahora que los análisis se persisten, la frase es cierta,
   pero se refiere al envío, no al análisis, así que se precisa.
   ============================================================ */

interface PropsBloque {
  titulo: string
  texto: string
}

export function BloqueCarga({ titulo, texto }: PropsBloque) {
  return (
    <div className="bloque-carga">
      <span className="anillo" aria-hidden="true" />
      <p className="bloque-carga__titulo">{titulo}</p>
      <p className="bloque-carga__texto">{texto}</p>
    </div>
  )
}

interface Props {
  titulo?: string
  texto?: string
}

export function Cargando({
  titulo = 'Analizando...',
  texto = 'Si se supera el tiempo de espera, tus datos siguen cargados y el envío se vuelve a intentar.',
}: Props) {
  return (
    <div className="velo" role="alertdialog" aria-busy="true" aria-live="assertive" aria-label={titulo}>
      <BloqueCarga titulo={titulo} texto={texto} />
    </div>
  )
}

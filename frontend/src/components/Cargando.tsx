/* ============================================================
   Velo de carga.

   El patrón del diseño: el formulario sigue visible y completo detrás, y
   encima cae un velo semitransparente con el bloque de carga centrado.
   Que se siga viendo lo que se cargó es deliberado — comunica que los
   datos no se perdieron.

   El texto de espera es el del diseño, con una corrección: decía que
   «los cambios quedan guardados», lo que se contradecía con el resto del
   producto. Ahora que los análisis se persisten, la frase es cierta, pero
   se refiere al envío, no al análisis, así que se precisa.
   ============================================================ */

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
      <div className="bloque-carga">
        <span className="anillo" aria-hidden="true" />
        <p className="bloque-carga__titulo">{titulo}</p>
        <p className="bloque-carga__texto">{texto}</p>
      </div>
    </div>
  )
}

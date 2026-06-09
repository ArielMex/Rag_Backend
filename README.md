## Flujo de Trabajo y Estrategia de Branching

**Flujo de trabajo configurado:** Feature Branch Workflow

**Estrategia seleccionada:** GitHub Flow

**Justificación:** Para el control de versiones del proyecto decidimos implementar esta configuración. Al trabajar en distintos módulos simultáneamente (como el backend o las vistas), esto nos permite una forma de coordinar el desarrollo en paralelo lo que nos ayuda a no generar conflictos graves de integración y evita que alguno de los miembros del equipo sobreescriba el progreso de otro por accidente después de subir cambios.

Al utilizar esta estrategia, el flujo de trabajo configurado garantiza lo siguiente:

* **Aislamiento del código:** Cada nuevo componente, corrección o ajuste del sistema lo desarrollamos en una rama completamente independiente que nace de la principal. Para no perder el orden en el repositorio, por ejemplo, en el backend usamos **feat/configuracion-bd** para preparar la conexión a nuestra base de datos o **feat/pipeline-rag** para integrar la lógica de los PDFs. Y para el frontend usamos **feat/ui-dashboard** para el panel de control y **feat/ui-chat** para la interacción con la IA. De esta manera cada integrante puede probar sus cambios sin afectar a los demás.

* **Estabilidad del proyecto:** Nos aseguramos de que la rama **main** sea intocable de forma directa. La mantenemos protegida para que siempre contenga una versión estable, limpia y funcional. En pocas palabras, si alguien sube cambios a la rama principal, significa que ya fue probado y no existirán errores en el proyecto.

* **Revisión de pares:** Este flujo exige el uso de solicitudes de integración (Pull Requests) para unir los cambios. Esto es clave ya que nos permite revisar el código de forma colaborativa antes de cualquier fusión, detectando errores a tiempo y para asegurarnos de que todos respeten los estándares que definimos.

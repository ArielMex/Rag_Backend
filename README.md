## Flujo de Trabajo y Estrategia de Branching

**Flujo de trabajo configurado:** Feature Branch Workflow

**Estrategia seleccionada:** GitHub Flow

**Justificación:**
Para el control de versiones del proyecto decidimos implementar esta configuración. Al trabajar en distintos módulos al mismo tiempo, nos permite coordinar el desarrollo en paralelo sin generar conflictos en el código base ni sobreescribir el progreso de los demás.

Al utilizar esta estrategia, el flujo de trabajo configurado garantiza lo siguiente:
*   **Aislamiento:** Cada nuevo componente del sistema lo desarrollamos en una rama aislada (ej. `feat/conexion-bd` o `feat/ui-login`) a partir de la principal.
*   **Estabilidad:** Nos aseguramos de que la rama `main` se mantenga siempre protegida, en un estado limpio y funcional.
*   **Revisión de pares:** Este flujo exige el uso de solicitudes de integración (Pull Requests) para unir los cambios. Esto permite realizar revisiones de código de forma colaborativa antes de cualquier fusión, detectando errores a tiempo y respetando los estándares que definimos para el proyecto.

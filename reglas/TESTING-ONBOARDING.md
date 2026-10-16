# Reglas de testing: onboarding Java + Quarkus.

## Propósito y fuentes de verdad

Este documento define las reglas para probar el backend de onboarding de la
wallet desde el rol de testing. Aplica a pruebas automatizadas y manuales del
flujo de onboarding y de sus métricas internas.

- El contrato vigente de endpoints, estados, errores y datos es
  [`ENDPOINTS.md`](../docs/ENDPOINTS.md). No se deben inventar comportamientos para
  hacer pasar una prueba.
- Las reglas generales de tecnología y calidad están en
  [`../REGLAS.md`](../REGLAS.md). La cobertura mínima es 90% para el código
  modificado; esta meta no reemplaza las pruebas de comportamiento.
- Los requisitos funcionales están en
  [`../HU/user-stories/user-onboarding-mvp-completion.sp.md`](../HU/user-stories/user-onboarding-mvp-completion.sp.md).
- Los campos y reglas KYC concretos son una decisión pendiente de
  producto/compliance. Hasta que se aprueben, usar fixtures de prueba
  explícitos y no afirmar que cubren reglas KYC productivas.

## Herramientas y estructura

- Java y Quarkus según las versiones aprobadas y compatibles registradas en
  `REGLAS.md`; ejecutar siempre con Maven Wrapper (`mvnw.cmd` en Windows).
- JUnit 5 y `quarkus-junit5` para las pruebas del backend.
- REST Assured para verificar los endpoints HTTP y su contrato observable.
- Testcontainers para las pruebas de integración con PostgreSQL y otros
  servicios reales que formen parte del alcance.
- JaCoCo para medir cobertura; no excluir lógica de negocio ni alterar umbrales
  para ocultar código no probado.
- Mantener las pruebas en `src/test/java`, junto al paquete correspondiente,
  siguiendo el patrón de nombres y perfiles que adopte el proyecto Quarkus.

Cuando exista el proyecto Maven, los comandos de referencia son
`mvnw.cmd test` para las pruebas y `mvnw.cmd verify` para ejecutar las fases de
verificación configuradas. Si el `pom.xml` define perfiles requeridos, usar el
perfil del proyecto en ambos comandos.

## Reglas obligatorias

1. Probar comportamiento observable y requisitos del contrato; evitar acoplar
   las pruebas a métodos privados, orden incidental o detalles internos.
2. Para cada endpoint, cubrir el camino exitoso, límites relevantes y cada
   código de error documentado en la matriz de este archivo.
3. En errores HTTP, comprobar el código, `Content-Type:
   application/problem+json`, `status` y el `code` estable cuando esté definido.
   En errores de validación, comprobar los campos corregibles y que el flujo no
   avance. No exigir textos variables que el contrato no fija.
   Si una precondición del contrato no define su respuesta HTTP, registrar el
   vacío como pendiente de contrato y no inventar un código de estado para la
   prueba.
4. Usar datos sintéticos y aislados por prueba. No registrar tokens, secretos,
   documentos KYC ni respuestas completas del onboarding en salidas de prueba.
5. Evitar dependencia del orden, hora local, red externa y datos compartidos.
   Fijar reloj y zona horaria cuando se prueben timestamps o agregaciones
   mensuales; el contrato usa UTC para timestamps y `America/Lima` para meses.
6. Usar PostgreSQL real en pruebas de integración mediante Testcontainers para
   validar migraciones, consultas, transacciones, restricciones e idempotencia.
   Las pruebas unitarias pueden sustituir dependencias externas, pero no son
   sustituto de la integración con la base de datos.
7. Probar autenticación y autorización en servidor, incluida la separación del
   permiso analítico respecto del usuario de onboarding. Verificar aislamiento
   entre usuarios y no asumir que el cliente puede elegir el `userId`.
8. Verificar consistencia: un error de validación no persiste respuestas ni
   avanza el paso; completar el último paso activa la wallet y registra la
   finalización sin duplicar eventos; cerrar no activa una wallet.
9. Para `Idempotency-Key`, probar clave obligatoria, repetición de la misma
   solicitud, repetición con cuerpo diferente, aislamiento entre usuarios y
   operaciones, y reintentos concurrentes. La repetición idéntica no debe
   duplicar cambios ni eventos; el cuerpo diferente debe producir el conflicto
   que define el contrato.
10. No adaptar una prueba para aceptar un bug. Registrar el defecto y mantener
    la expectativa derivada del contrato hasta que se corrija.
11. Validar cobertura de al menos 90% del código modificado con JaCoCo y revisar
    también ramas críticas. La cobertura por sí sola no demuestra que los
    criterios de aceptación estén probados.
12. No hacer llamadas a proveedores de identidad, analítica o adquisición
    productivos. Usar dobles de prueba o servicios locales controlados; verificar
    que no se filtren respuestas KYC ni datos personales en las métricas.

## Niveles de prueba

| Nivel | Qué verificar | Herramientas / entorno |
|---|---|---|
| Unitario | Reglas de transición, validación de dominio, cálculo de métricas e idempotencia aislada | JUnit 5; dependencias reemplazadas cuando corresponda |
| Integración | CDI, límites transaccionales, repositorios, migraciones, persistencia y eventos | `@QuarkusTest`, PostgreSQL con Testcontainers |
| API / contrato | Métodos, rutas, headers, códigos, esquemas y errores documentados | `@QuarkusTest`, REST Assured y contrato OpenAPI |
| Seguridad | Token ausente/inválido, acceso entre usuarios y rol analítico | Configuración OIDC de prueba y tokens no productivos |
| Regresión | Criterios de aceptación y defectos corregidos | Suite automatizada en CI; evidencia vinculada al cambio |

## Matriz mínima por endpoint

Cada fila de error representa una respuesta documentada que debe tener al menos
una prueba. Agregar casos adicionales para variantes significativas sin duplicar
pruebas equivalentes.

| Endpoint | Caso | Tipo | Resultado esperado |
|---|---|---|---|
| `POST /api/v1/onboardings` | Iniciar con `countryCode: PE`, token válido y clave de idempotencia válida | Camino feliz | `201`; flujo `in_progress`, wallet `pending`, pasos definidos por servidor y evento de inicio registrado |
| `POST /api/v1/onboardings` | Repetir la misma solicitud con la misma clave | Idempotencia / borde | Resultado original; no se crean flujos ni eventos duplicados |
| `POST /api/v1/onboardings` | Repetir una clave con un cuerpo diferente | Error `409` / idempotencia | Conflicto; no se crea un segundo flujo ni se altera el resultado original |
| `POST /api/v1/onboardings` | Clave de idempotencia ausente o fuera de longitud permitida | Borde / validación | La solicitud no crea un flujo; si el código HTTP no está definido por el contrato, registrar esa brecha en lugar de asumirlo |
| `POST /api/v1/onboardings` | Solicitud mal formada | Error `400` | `application/problem+json`; ningún flujo creado |
| `POST /api/v1/onboardings` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; acceso denegado |
| `POST /api/v1/onboardings` | Ya existe un onboarding en curso | Error `409` | Código `ONBOARDING_ALREADY_IN_PROGRESS` e identificador del flujo reanudable |
| `POST /api/v1/onboardings` | País o solicitud no cumple las reglas del dominio | Error `422` | `application/problem+json`; onboarding no creado |
| `GET /api/v1/onboardings/current` | Consultar el flujo del usuario autenticado | Camino feliz | `200`; muestra pasos, paso actual y estado de wallet del principal autenticado |
| `GET /api/v1/onboardings/current` | El usuario no ha iniciado onboarding | Error `404` | `application/problem+json`; no se devuelven datos de otro usuario |
| `GET /api/v1/onboardings/current` | El flujo existente no es reanudable | Error `409` | `application/problem+json`; estado no cambia |
| `GET /api/v1/onboardings/current` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; acceso denegado |
| `PUT /api/v1/onboardings/current/steps/{stepId}` | Enviar respuestas válidas para el paso actual | Camino feliz | `200`; paso completado y avance coherente; si es el último, onboarding `completed`, wallet `active` y `completedAt` informado |
| `PUT /api/v1/onboardings/current/steps/{stepId}` | Repetir la misma solicitud con la misma clave | Idempotencia / borde | Respuesta equivalente; no duplica finalización ni eventos |
| `PUT /api/v1/onboardings/current/steps/{stepId}` | Reutilizar la clave con otro cuerpo, enviar paso fuera de orden o con flujo cerrado | Error `409` / borde | Conflicto conforme al contrato; estado y eventos sin cambios indebidos |
| `PUT /api/v1/onboardings/current/steps/{stepId}` | Solicitud mal formada | Error `400` | `application/problem+json`; el paso no avanza |
| `PUT /api/v1/onboardings/current/steps/{stepId}` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; acceso denegado |
| `PUT /api/v1/onboardings/current/steps/{stepId}` | No hay onboarding activo o el paso no pertenece al flujo | Error `404` | `application/problem+json`; no se modifica el flujo |
| `PUT /api/v1/onboardings/current/steps/{stepId}` | Falta información obligatoria o las respuestas son inválidas | Error `422` | Incluye errores por campo; no persiste el paso ni cambia el paso actual |
| `POST /api/v1/onboardings/current/close` | Cerrar voluntariamente un flujo en curso | Camino feliz | `200`; estado `closed`, cierre registrado y wallet permanece `pending` |
| `POST /api/v1/onboardings/current/close` | No existe onboarding actual | Error `404` | `application/problem+json`; no se crea un cierre |
| `POST /api/v1/onboardings/current/close` | El flujo ya está completado o cerrado | Error `409` | `application/problem+json`; no se altera la activación ni se duplica el cierre |
| `POST /api/v1/onboardings/current/close` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; acceso denegado |
| `GET /api/v1/internal/analytics/onboarding/monthly` | Consultar un rango mensual válido con rol autorizado | Camino feliz | `200`; meses inclusivos, `America/Lima`, moneda `PEN` y agregados conforme al esquema |
| `GET /api/v1/internal/analytics/onboarding/monthly` | Mes inválido, parámetros ausentes o rango inválido | Error `400` | `application/problem+json`; no se ejecuta una consulta fuera del rango válido |
| `GET /api/v1/internal/analytics/onboarding/monthly` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; acceso denegado |
| `GET /api/v1/internal/analytics/onboarding/monthly` | Principal autenticado sin permiso analítico | Error `403` | `application/problem+json`; no se exponen datos analíticos |
| Métricas mensuales | Mes sin completados o sin nuevos usuarios activos | Borde | Conteos no negativos; `medianCompletionSeconds` nulo si no hay completados y `cacPerNewUser` nulo si `newActiveUsers` es cero |
| Métricas mensuales | Revisar atribución y contenido de respuesta | Privacidad / contrato | Agregados únicamente; nunca respuestas KYC, identificadores personales ni costos declarados por el cliente |

## Criterios de salida

Una entrega de testing está lista cuando:

- Todos los endpoints y códigos de respuesta de [`ENDPOINTS.md`](../docs/ENDPOINTS.md)
  están cubiertos, o los casos bloqueados por decisiones pendientes están
  reportados con su dependencia explícita.
- Las pruebas automatizadas relevantes pasan con Maven Wrapper y no dependen de
  servicios ni credenciales productivas.
- Las migraciones y pruebas de integración se ejecutan sobre PostgreSQL de
  prueba, no sobre una base compartida o de producción.
- JaCoCo confirma al menos 90% de cobertura del código modificado y las ramas
  de transición, autorización e idempotencia tienen aserciones de
  comportamiento.
- Los resultados, defectos y decisiones pendientes quedan vinculados a la
  historia o al cambio. No se reporta como validada una métrica —por ejemplo,
  MAU basado en actividad de pagos— hasta que su fuente e integración estén
  definidas.

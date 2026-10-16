# Estrategia de pruebas del onboarding

## Estado

Este documento especifica pruebas derivadas de `docs/ENDPOINTS.md`. No se encontraron fuentes Java/TypeScript, `pom.xml`, `package.json` ni suites de prueba en `wallet_team7/`; por ello no es posible integrar código ejecutable, correrlo en verde ni medir cobertura. No se simulan respuestas para presentar pruebas como aprobadas. La matriz debe convertirse en pruebas de integración Quarkus con JUnit 5 y REST Assured y pruebas Angular con el runner soportado por el proyecto, conforme a `REGLAS.md`, cuando el código esté disponible.

Base URL de los endpoints: `/api/v1`.

## Matriz de casos

| endpoint | caso | tipo | resultado esperado |
| --- | --- | --- | --- |
| `POST /onboardings` | Token válido, `countryCode: PE`, clave idempotente válida y sin flujo activo | Camino feliz | `201`; flujo `in_progress`, wallet `pending`, país `PE`, pasos iniciales, `startedAt` y evento de inicio registrados. |
| `POST /onboardings` | Repetir la misma solicitud con la misma `Idempotency-Key` | Caso borde | Se devuelve el resultado original y no se crea otro flujo ni se duplica el evento de inicio. |
| `POST /onboardings` | JSON mal formado | Error `400` | `application/problem+json`; no se crea onboarding. |
| `POST /onboardings` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; no se crea onboarding. |
| `POST /onboardings` | Ya existe onboarding en curso para el usuario | Error `409` | `code: ONBOARDING_ALREADY_IN_PROGRESS` y `onboardingId`; no se crea otro flujo. |
| `POST /onboardings` | Solicitud que no cumple una regla de dominio aprobada | Error `422` | `application/problem+json`; no se crea onboarding. La regla y fixture deben ser aprobados por producto/compliance, pues el contrato no especifica cuál usar. |
| `GET /onboardings/current` | Usuario autenticado con onboarding en curso | Camino feliz | `200`; devuelve estado, pasos ordenados, `currentStepId` y timestamps coherentes. |
| `GET /onboardings/current` | El onboarding está cerrado y no es reanudable | Caso borde / Error `409` | `application/problem+json`; no se presenta un flujo cerrado como activo. |
| `GET /onboardings/current` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; no se exponen datos de otro usuario. |
| `GET /onboardings/current` | Usuario sin onboarding iniciado | Error `404` | `application/problem+json`. |
| `PUT /onboardings/current/steps/{stepId}` | Enviar respuestas válidas para el paso actual con clave idempotente | Camino feliz | `200`; paso completado y progreso actualizado. En el último paso, estado `completed`, wallet `active` y `completedAt` definido. |
| `PUT /onboardings/current/steps/{stepId}` | Repetir idéntica solicitud con la misma `Idempotency-Key` | Caso borde | Mismo resultado original; no duplica la finalización ni el evento del paso. |
| `PUT /onboardings/current/steps/{stepId}` | JSON mal formado | Error `400` | `application/problem+json`; el flujo no avanza. |
| `PUT /onboardings/current/steps/{stepId}` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; no se altera el flujo. |
| `PUT /onboardings/current/steps/{stepId}` | No hay onboarding activo o `stepId` no pertenece al flujo | Error `404` | `application/problem+json`; no se altera el flujo. |
| `PUT /onboardings/current/steps/{stepId}` | El paso no es el actual o el flujo está cerrado | Error `409` | `application/problem+json`; no se altera el flujo. |
| `PUT /onboardings/current/steps/{stepId}` | Reutilizar una clave idempotente con un cuerpo diferente | Error `409` | La clave/cuerpo conflictivos se rechazan; el primer resultado y el estado del onboarding permanecen intactos. |
| `PUT /onboardings/current/steps/{stepId}` | Falta un dato requerido o una respuesta no satisface una regla aprobada | Error `422` | `ValidationProblem` con `errors`; el paso no se completa y no se emite evento de finalización. Los campos/reglas deben definirse por producto/compliance. |
| `POST /onboardings/current/close` | Usuario autenticado con onboarding en curso | Camino feliz | `200`; estado `closed`, wallet no activa, `closedAt` definido y evento de cierre registrado. |
| `POST /onboardings/current/close` | Cerrar un flujo ya cerrado o completado | Caso borde / Error `409` | `application/problem+json`; no cambia el estado terminal ni duplica el evento de cierre. |
| `POST /onboardings/current/close` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; no se altera el flujo. |
| `POST /onboardings/current/close` | No existe onboarding actual | Error `404` | `application/problem+json`. |
| `GET /internal/analytics/onboarding/monthly` | Rol de analítica autorizado y rango válido con datos | Camino feliz | `200`; meses inclusivos, `America/Lima`, moneda `PEN`, campos y fórmulas conformes al esquema; sin datos personales. |
| `GET /internal/analytics/onboarding/monthly` | `from` y `to` son el mismo mes válido | Caso borde | `200`; un único mes calendario. Validar límites inclusivos y agregación en `America/Lima`. |
| `GET /internal/analytics/onboarding/monthly` | Mes válido sin activaciones, con fixtures de fuentes vacías | Caso borde | `200`; conteos no negativos, `cacPerNewUser: null` si `newActiveUsers` es cero y `medianCompletionSeconds: null` si no hubo finalizaciones. |
| `GET /internal/analytics/onboarding/monthly` | Mes ausente o con formato inválido | Error `400` | `application/problem+json`; no se consulta un rango inválido. |
| `GET /internal/analytics/onboarding/monthly` | Token ausente, inválido o vencido | Error `401` | `application/problem+json`; no se devuelven métricas. |
| `GET /internal/analytics/onboarding/monthly` | Principal autenticado sin permiso de analítica | Error `403` | `application/problem+json`; no se devuelven métricas. |

## Pruebas ejecutables

**Bloqueadas por ausencia de implementación.** No se añade código de prueba no compilable o acoplado a clases, paquetes, configuración de identidad o fixtures que no existen en el workspace. `REGLAS.md` prescribe JUnit 5, `quarkus-junit5`, REST Assured, Testcontainers y Playwright; no prescribe paquetes, helpers de autenticación, estrategia de token de prueba ni comandos de ejecución. Cuando estén disponibles backend y frontend, implementar la matriz como pruebas en las suites existentes y ejecutar el build y los tests antes de declarar resultados.

## Cobertura

La meta establecida en `REGLAS.md` es al menos 90% del código modificado con JaCoCo. No es medible mientras no haya código fuente ni configuración de build. La cobertura debe acompañarse de las pruebas de contrato anteriores y no sustituye pruebas de comportamiento.

## Documentos consultados

- `docs/ENDPOINTS.md`
- `REGLAS.md`
- `PLAN.md`

# Plan de implementación: Onboarding MVP

## Objetivo

Implementar el flujo de registro y activación de la wallet para la cohorte MVP de Perú, con guía de progreso, validación accionable, activación al completar el último paso y registro de eventos para seguimiento. La implementación debe conservar íntegramente el contrato de `docs/ENDPOINTS.md` y respetar `REGLAS.md`.

## Fuentes y trazabilidad

- Épica: `HU/epic/peru-wallet-mvp.sp.md`.
- Historia: `HU/user-stories/user-onboarding-mvp-completion.sp.md`.
- Contrato API: `docs/ENDPOINTS.md` (OpenAPI 3.0.3).
- Convenciones técnicas y calidad: `REGLAS.md`.

La historia priorizada es onboarding y activación. Los pagos de bajo monto, pagos QR y conciliación pertenecen al alcance más amplio de la épica, pero no se implementan en este plan salvo la integración mínima necesaria para enlazar la wallet activa al punto de entrada de pagos.

## Alcance

### Incluido

- API Quarkus para iniciar, consultar, avanzar y cerrar el onboarding.
- Persistencia transaccional de onboarding y pasos, idempotencia y eventos requeridos.
- Interfaz Angular del flujo guiado y sus estados de carga, validación, error, reanudación y finalización.
- Endpoint interno de métricas mensuales con fuentes autorizadas para actividad y gasto de adquisición.
- Pruebas, controles de seguridad y validaciones de CI establecidas en `REGLAS.md`.

### Excluido

- Cambiar rutas, métodos, campos, respuestas o códigos de `docs/ENDPOINTS.md`.
- Definir por cuenta propia campos o requisitos regulatorios KYC.
- Implementar procesamiento de pagos, QR, interoperabilidad o disputas de la épica.
- Aceptar desde el navegador eventos analíticos, costos de adquisición o decisiones de activación como autoridad.
- Agregar dependencias sin necesidad demostrable y justificación técnica.

## Decisiones y dependencias previas

Resolver y registrar estas decisiones antes de cerrar los contratos internos de dominio y formularios. No implican modificar el OpenAPI existente.

1. **KYC y pasos:** producto/compliance debe aprobar los `stepId`, campos, tipos, obligatoriedad, validaciones, mensajes, tratamiento y retención de datos. El contrato solo expone `id`, `title`, `order` y `status` para pasos y un objeto `answers`; por sí solo no define formularios dinámicos. La interfaz asociará los pasos aprobados a formularios tipados sin inferir requisitos regulatorios.
2. **Autenticación:** identificar proveedor aprobado, flujo de sesión, claims y roles. La API exige Bearer y la consulta de métricas requiere permiso analítico; la regla de autenticación OIDC del backend está comentada en `REGLAS.md`, así que no se debe seleccionar proveedor ni mecanismo sin aprobación. La decisión Angular debe ajustarse al punto 43 de `REGLAS.md` (OIDC con PKCE o BFF, según arquitectura).
3. **Duración:** validar con producto la métrica propuesta en `docs/ENDPOINTS.md`: desde el primer `startedAt` persistido hasta `completedAt`, incluyendo la política para sesiones reanudadas. La mediana objetivo es 3 minutos frente a la línea base de 8 minutos.
4. **Abandono y retención:** aprobar expiración de onboarding, registro de cierre por expiración y retención de respuestas KYC, claves idempotentes y eventos.
5. **MAU y adquisición:** identificar la fuente autorizada de actividad de pagos, su ventana de actividad y la fuente/regla de atribución del gasto. Confirmar con Product Owner si el CAC se calcula como gasto atribuido dividido entre nuevos usuarios activados, tal como propone el contrato. Sin estas fuentes, no se puede certificar MAU ni CAC.
6. **Diseño del cliente:** confirmar sistema de diseño, textos y flujo de autenticación antes de implementar vistas finales. Los pasos deben mostrarse en el orden recibido del servidor.
7. **Reintentos:** acordar la ventana de retención de `Idempotency-Key`, respetando la política descrita en el contrato y el rechazo por reutilización con un cuerpo distinto.

## Propuesta de implementación

### Fase 1: Preparación y diseño

- Revisar el proyecto existente dentro de `wallet_team7/` y documentar cómo se integran las convenciones Quarkus, Angular, construcción y CI; no reemplazar configuración existente sin necesidad.
- Resolver o registrar los bloqueos de la sección anterior. Definir modelos de dominio y límites de persistencia/API usando las tecnologías ya especificadas en `REGLAS.md`.
- Establecer ejemplos de escenarios y datos de prueba aislados, sin datos personales reales.
- Mantener `docs/ENDPOINTS.md` sin cambios; validar cualquier implementación contra sus rutas y esquemas.

### Fase 2: Backend de onboarding

- Implementar las operaciones existentes: `POST /api/v1/onboardings`, `GET /api/v1/onboardings/current`, `PUT /api/v1/onboardings/current/steps/{stepId}` y `POST /api/v1/onboardings/current/close`.
- Derivar identidad y permisos del principal autenticado; no aceptar `userId` del cliente. Aplicar autorización por usuario y separar el permiso de analítica.
- Persistir el estado y la configuración aprobada de pasos en PostgreSQL mediante Hibernate ORM/Panache y migraciones Flyway, conforme a `REGLAS.md`.
- Hacer atómicas las transiciones de estado, el registro de idempotencia y la activación. Repetir una operación idéntica debe devolver su resultado sin duplicar finalizaciones ni eventos; una clave reutilizada con cuerpo distinto debe producir el conflicto previsto.
- Responder `422` ante validaciones fallidas sin avanzar el flujo; devolver `Problem`/`ValidationProblem` con códigos estables y mensajes seguros. Implementar los casos `401`, `404` y `409` según cada operación del contrato.
- Al completar el último paso, transicionar una sola vez a `completed`, activar la wallet y establecer `completedAt`. El cierre no debe activar la wallet.

### Fase 3: Eventos y analítica

- Registrar en servidor inicio, finalización de cada paso, activación y cierre/expiración, incluyendo usuario, onboarding, timestamp y atribución disponible, sin incluir respuestas sensibles en eventos analíticos.
- Usar transacción y mecanismo durable/outbox si es necesario para evitar pérdida o duplicación de eventos; elegirlo solo según el requisito de consistencia, como indica `REGLAS.md`.
- Implementar `GET /api/v1/internal/analytics/onboarding/monthly` con los campos definidos, agregados mensuales en `America/Lima` y montos en PEN. No exponer respuestas KYC ni identificadores personales.
- Calcular duración desde el primer inicio persistido hasta la finalización, CAC como gasto atribuido por nuevos usuarios activos y MAU desde la fuente de actividad aprobada. No sustituir fuentes faltantes con datos simulados en producción.

### Fase 4: Frontend Angular

- Construir el flujo como aplicación Angular siguiendo standalone components, TypeScript estricto, Router, Reactive Forms tipados, Signals/RxJS y demás reglas aplicables de `REGLAS.md`; reutilizar el sistema de diseño aprobado.
- Al entrar, consultar el onboarding actual. Si no existe (`404`), iniciar con `POST`; si el inicio reporta un flujo ya existente (`409`), recuperar el flujo mediante `GET /current` cuando la sesión permita hacerlo.
- Mostrar pasos y progreso usando `steps`, `currentStepId` y el estado del servidor. Asociar formularios a los identificadores de paso definidos y aprobados, sin construir campos KYC por inferencia.
- Enviar respuestas con `PUT` y `Idempotency-Key`; mantener la misma clave para reintentar la misma operación. Traducir `ValidationIssue` a errores accesibles y conservar los datos editables ante errores recuperables sin persistir información sensible de forma insegura.
- Permitir cierre voluntario con `POST /close`. Al completarse, mostrar wallet activa y el punto de entrada a pagos de bajo monto solo cuando el servidor devuelva `completed` y `walletStatus: active`.
- Manejar `401`, `404`, `409`, `422`, problemas de red, expiración de sesión y estados de carga con acciones claras. No usar guards de frontend como sustituto de autorización backend.
- No consumir el endpoint de métricas desde el cliente de onboarding; es interno para operaciones/analítica.

### Fase 5: Verificación y salida

- Ejecutar pruebas automatizadas, análisis estático, escaneo de dependencias y build reproducible en CI; mantener CodeQL, Dependency Review y JaCoCo habilitados.
- Verificar accesibilidad WCAG 2.2 AA, navegación por teclado y lector de pantalla, responsividad móvil y revisión manual además de pruebas automáticas.
- Validar configuración, permisos, políticas de retención y fuentes de analítica antes de habilitar la cohorte MVP.
- Desplegar de forma controlada según la estrategia ya existente en el proyecto; observar fallas del funnel y estados de onboarding sin registrar datos KYC.

## Criterios de aceptación y pruebas

| Criterio | Verificación propuesta |
| --- | --- |
| Se muestra la secuencia requerida y el paso actual | Prueba de componente Angular con varias secuencias, y prueba de integración contra `GET /current`; verificar orden del servidor y `currentStepId`. |
| Datos inválidos bloquean el avance con una corrección accionable | Prueba backend `422` sin transición ni evento de finalización; prueba frontend que asocia errores a controles y permite corregirlos. |
| La finalización activa la wallet y habilita el acceso al pago | Prueba transaccional del último paso y prueba UI que solo habilita el punto de entrada ante `completed` y `active`. |
| Se registran inicio, pasos y cierre | Pruebas de persistencia/eventos, incluyendo reintentos idempotentes, cierre y expiración aprobada sin duplicados. |
| La mediana de onboarding se reduce de 8 a 3 minutos | Instrumentar timestamps y entregar medición por cohorte; evaluar la mediana tras el periodo acordado. Es un objetivo de producto, no se demuestra solo con pruebas unitarias. |
| La salida mensual incluye nuevos activos, MAU y gasto/CAC | Pruebas del endpoint analítico con fuentes controladas, zona horaria y límites de mes; validar permisos y ausencia de datos personales. |
| Se conserva el contrato de API | No editar `docs/ENDPOINTS.md`; ejecutar pruebas de contrato para paths, métodos, schemas, códigos y formatos de error. |
| Clean Code y cobertura | Revisar responsabilidades por método, ausencia de duplicación y anidamiento profundo, uso de constantes con nombre; cumplir cobertura mínima de 90% del código modificado con JaCoCo. |

## Riesgos y mitigaciones

- **KYC no definido:** puede bloquear la construcción de formularios y validaciones finales. Mitigar aprobando un catálogo de pasos/campos antes de la fase Angular completa.
- **Autenticación pendiente:** sin proveedor, claims y roles no pueden cerrarse la protección de rutas ni el endpoint analítico. Mantener la integración detrás de la decisión aprobada; no simular seguridad en producción.
- **Dependencias analíticas externas:** sin datos de actividad y gasto no se puede demostrar MAU/CAC. Definir responsables y disponibilidad de esas fuentes antes de comprometer el reporte productivo.
- **Reintentos y duplicidad:** proteger transiciones y eventos mediante idempotencia atómica y pruebas concurrentes.
- **Frontera temporal y reanudación:** fijar formalmente cómo contar tiempo y sesiones reanudadas antes de reportar la mediana.

## Resultado esperado

Una experiencia de onboarding reanudable y accesible, una wallet que solo se activa tras completar el flujo en servidor, eventos de funnel consistentes y métricas internas protegidas. La liberación funcional queda condicionada a la aprobación de KYC/autenticación; la verificación completa de MAU y CAC queda condicionada además a sus fuentes de datos autorizadas.

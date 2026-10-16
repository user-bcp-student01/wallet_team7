# Diseño técnico: onboarding MVP de wallet

## Fuente y estado

- Especificación: [finalización del onboarding de wallet](./specs/spec.md).
- Evidencia consultada: [README del proyecto](../../../README.md),
  [código de la aplicación](../../../src/README.md),
  [demo](../../../demo/index.html),
  [contratos de API](../../../docs/ENDPOINTS.md) y marcador de
  [pruebas](../../../tests/README.md).
- Estado: propuesta arquitectónica pendiente de aprobación humana. No habilita
  implementación ni cambios de contrato por sí sola.

## Contexto técnico actual

El proyecto no muestra una implementación de wallet: `src/` y `tests/` contienen
marcadores, la demo es una página estática servida por Nginx y `docker-compose`
solo levanta ese servidor. No se encontró servicio de onboarding, persistencia,
autenticación ni integración analítica existente en los artefactos examinados.

`docs/ENDPOINTS.md` contiene un contrato OpenAPI descrito como propuesto. Incluye
rutas de onboarding y analítica, autenticación Bearer, eventos e idempotencia,
pero esas decisiones no se desprenden de la spec aprobada ni tienen una
implementación visible. Este diseño no las considera contratos aprobados.

## Impacto

La capacidad requiere introducir, cuando se apruebe, una implementación
incremental de onboarding en las capas de presentación, aplicación/dominio,
persistencia y captura analítica. No se recomienda reescribir la demo ni
incorporar los flujos de pago.

El cambio funcional central es mantener una única transición autoritativa:
`in_progress` a `completed` solo cuando todos los pasos aprobados pasan su
validación; la activación de wallet debe ocurrir como parte de esa finalización.
Un flujo cerrado o incompleto no puede activar la wallet.

## Componentes afectados

Los siguientes son límites lógicos propuestos, no módulos o tecnologías ya
existentes:

- **Presentación del onboarding:** muestra la secuencia aprobada, el paso actual
  y errores accionables. No decide si la wallet queda activa.
- **Servicio de aplicación de onboarding:** inicia o reanuda el flujo, obtiene
  el progreso y coordina la validación, finalización de pasos, cierre y
  activación.
- **Reglas de dominio/configuración de pasos:** aplica el orden y las reglas
  obligatorias aprobadas por Producto y Cumplimiento. No se deben inventar pasos
  ni requisitos KYC mientras estén pendientes.
- **Persistencia del flujo y estado de wallet:** conserva el progreso y aplica
  las transiciones de forma consistente. La activación debe derivarse de una
  finalización válida, no de un indicador enviado por el cliente.
- **Captura y consulta analítica:** registra inicio, finalización por paso y
  cierre; genera la salida para duración, usuarios activos y adquisición solo
  después de que Producto apruebe las definiciones y fuentes pertinentes.
- **Integración con el punto de entrada de pagos:** hace visible el acceso
  existente al completar y activar. La implementación de pagos queda fuera de
  alcance.

## Contratos protegidos

- No cambiar los contratos HTTP existentes de ReqFlow: `POST /auth/login`,
  `GET/POST /api/tasks`, `GET /api/summary` y `POST /api/requirements`.
- La spec del onboarding no define rutas, cuerpos, respuestas ni códigos HTTP.
  Antes de implementar una API para esta capacidad, se debe resolver si el
  borrador de [docs/ENDPOINTS.md](../../../docs/ENDPOINTS.md) se aprueba, se
  revisa o se descarta, y registrar explícitamente el impacto sobre cualquier
  contrato existente.
- La activación debe seguir siendo invisible para el flujo de pagos hasta que
  se complete correctamente el onboarding. No se rediseña ni se modifica el
  contrato del flujo de pagos en esta historia.
- El cliente no debe poder declarar por sí mismo un paso completado, activar la
  wallet ni establecer el costo de adquisición que alimenta las métricas.

## Estrategia incremental

1. **Cerrar decisiones de producto y cumplimiento.** Aprobar lista y orden de
   pasos, requisitos de validación, reglas KYC/documentales, significado de
   cierre y disponibilidad esperada del punto de entrada a pagos.
2. **Aprobar contratos y dependencias.** Determinar si se implementará una API
   nueva y resolver el estado del borrador en `docs/ENDPOINTS.md`; identificar
   autenticación, autorización, persistencia, fuente de adquisición e
   integración existente de activación antes de seleccionarlas.
3. **Proteger las invariantes con pruebas.** Definir pruebas de dominio y de
   integración para validación, orden, progreso y activación antes de agregar
   persistencia o interfaz. Mantener pruebas de contrato separadas si se
   aprueba una API.
4. **Implementar el recorrido mínimo.** Añadir el flujo guiado y la validación
   autoritativa del servidor sobre los pasos aprobados. Hacer que el avance y la
   finalización sean seguros frente a reintentos conforme a una política de
   idempotencia acordada.
5. **Integrar activación y eventos.** Persistir el cambio de estado y registrar
   los eventos requeridos sin permitir activaciones parciales o eventos
   duplicados. Elegir transacción local u otro mecanismo después de conocer la
   tecnología de persistencia y los destinos de eventos.
6. **Habilitar reportes con definiciones aprobadas.** Incorporar métricas de
   duración, MAU y CAC únicamente cuando estén fijados población, ventanas
   temporales, tratamiento de abandonos, definición de usuario activo y regla
   de atribución.

Los pasos 1 y 2 son prerrequisitos para fijar el alcance implementable. Cada
incremento posterior debe poder revisarse sin introducir cambios en los
contratos protegidos.

## Pruebas necesarias

Antes de modificar el producto, proteger al menos estos comportamientos:

- El progreso muestra los pasos requeridos y señala el actual.
- La información obligatoria faltante o inválida bloquea el avance y permite
  identificar qué corregir; el estado del flujo permanece sin completar.
- Un paso solo se completa después de validar sus datos y respetar el orden
  aprobado.
- Completar correctamente el último paso activa la wallet y habilita el punto
  de entrada a pagos; iniciar, abandonar, cerrar o fallar validación no la activa.
- Los eventos cubren inicio, cada paso completado y cierre; los reintentos no
  generan estados ni registros duplicados según la política que se apruebe.
- La salida analítica marca las métricas como no verificables mientras falten
  sus definiciones y, una vez aprobadas, permite cotejar resultados contra las
  metas especificadas.
- Si se aprueba una API, pruebas de contrato verifican compatibilidad de los
  contratos autorizados y no alteración de los contratos ReqFlow protegidos.

El repositorio examinado no contiene aún una suite funcional de wallet, por lo
que las pruebas deben añadirse junto con el primer incremento implementable;
no hay pruebas actuales que puedan tomarse como cobertura de regresión de esta
capacidad.

## Riesgos y trade-offs

- **Pasos y KYC no definidos:** diseñar formularios o validaciones ahora puede
  fijar requisitos regulatorios incorrectos. Mantenerlos configurables no
  sustituye su aprobación.
- **Contrato API no aprobado:** implementar el borrador de endpoints crearía
  compromisos de compatibilidad antes de confirmar el alcance. Separar la
  decisión de API de las reglas de dominio reduce ese riesgo.
- **Consistencia de activación y eventos:** guardar la finalización, activar la
  wallet y registrar eventos en almacenes distintos puede producir estados
  parciales. La estrategia concreta depende de la infraestructura que aún no
  está definida.
- **Ambigüedad analítica:** instrumentar antes de fijar semántica puede producir
  datos que no permitan evaluar duración, MAU o CAC. Demorar los reportes
  verificables tiene menor riesgo que presentar una métrica engañosa.
- **Dependencia del punto de entrada de pagos:** la historia exige habilitarlo,
  pero no identifica la interfaz o servicio existente. Debe localizarse y
  acordarse el punto de integración antes de implementar la activación.
- **Alcance de esta entrega:** el diseño no elige stack, modelo de datos,
  proveedor analítico ni mecanismo de autenticación porque la evidencia
  disponible no confirma esas decisiones.

## Decisiones abiertas

1. ¿Está aprobada la lista y el orden de pasos, incluidas las reglas KYC y
   documentales para Perú?
2. ¿Qué significa cerrar el flujo y qué ocurre con el progreso si la persona
   reanuda más tarde?
3. ¿Se aprueba el borrador de `docs/ENDPOINTS.md` como contrato, requiere
   cambios o debe reemplazarse? ¿Quiénes son sus consumidores?
4. ¿Qué autenticación, almacenamiento y servicio existente determinan el estado
   de la wallet y habilitan el acceso a pagos?
5. ¿Cuáles son los nombres, atributos, semántica de cierre y política de
   deduplicación de los eventos?
6. ¿Qué timestamps, población, tratamiento de recorridos incompletos y método
   de cálculo definen la duración?
7. ¿Cómo se definen usuario activo, denominador/fuente de CAC, atribución y
   permisos de acceso a los reportes?

## Decisión arquitectónica y gate

Se propone mantener las reglas y transiciones del onboarding detrás de un
servicio autoritativo, separado de la presentación y del reporte analítico; no
se propone tecnología, esquema ni contrato de API hasta resolver las preguntas
abiertas. Esta separación es reversible y permite implementar primero el
recorrido validado sin acoplarlo a pagos o a una plataforma analítica concreta.

No se registra ADR: con la evidencia actual no hay una decisión tecnológica o
de contrato suficientemente confirmada que justifique fijarla como decisión
arquitectónica permanente.

**Gate:** detenerse aquí para revisión humana y aprobación de alcance, impacto,
contratos, riesgos y estrategia de pruebas. No iniciar implementación hasta
resolver los prerrequisitos de producto/cumplimiento y contratos indicados
arriba.

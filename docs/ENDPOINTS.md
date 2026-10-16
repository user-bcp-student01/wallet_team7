# Contratos de API: onboarding MVP de wallet

Este documento define los endpoints necesarios para el onboarding y su seguimiento analítico, de acuerdo con la épica `HU/epic/peru-wallet-mvp.sp.md` y la historia `HU/user-stories/user-onboarding-mvp-completion.sp.md`.

## Alcance y convenciones

- Especificación base: OpenAPI 3.0.3; los ejemplos de abajo son contratos propuestos para el MVP.
- Base URL: `/api/v1`. El endpoint analítico es interno y requiere autorización de operaciones/analítica.
- Autenticación: `Bearer` token. Los endpoints de onboarding operan sobre la identidad del token; el cliente no envía un `userId`.
- País y moneda: Perú (`PE`), `PEN`. Los importes analíticos se expresan en soles, como números decimales.
- Fechas: RFC 3339 en UTC para timestamps; agregaciones mensuales según `America/Lima`.
- Una wallet solo se considera activa al completar correctamente el último paso. El servidor registra los eventos de inicio, pasos completados, activación y cierre; el cliente no puede declarar un onboarding completo ni emitir esos eventos analíticos.
- `answers` permite transportar datos de pasos configurados por producto/compliance. Los campos y reglas KYC concretos son intencionalmente configurables y deben acordarse antes de implementar sus esquemas definitivos.
- Los errores usan `application/problem+json` (RFC 9457), con `code` estable para manejo de la aplicación.

## OpenAPI 3.0.3

```yaml
openapi: 3.0.3
info:
  title: Peru Wallet Onboarding API
  version: 1.0.0
  description: API de onboarding de usuarios y consulta interna de métricas mensuales.
servers:
  - url: /api/v1
security:
  - bearerAuth: []
tags:
  - name: Onboarding
  - name: Analytics
paths:
  /onboardings:
    post:
      tags: [Onboarding]
      operationId: startOnboarding
      summary: Iniciar el onboarding del usuario autenticado
      description: Crea un flujo de onboarding para Perú. Si ya existe uno en curso, responde con conflicto e identifica el flujo que debe reanudarse.
      parameters:
        - $ref: '#/components/parameters/IdempotencyKey'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/StartOnboardingRequest'
            example:
              countryCode: PE
              attributionToken: camp_opaque_7f4a
      responses:
        '201':
          description: Flujo creado; el evento de inicio quedó registrado.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Onboarding'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '409':
          description: Ya existe un onboarding en curso para el usuario.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
              example:
                type: about:blank
                title: Onboarding en curso
                status: 409
                code: ONBOARDING_ALREADY_IN_PROGRESS
                detail: Reanuda el flujo existente.
                onboardingId: onb_01JABC
        '422':
          $ref: '#/components/responses/UnprocessableEntity'
  /onboardings/current:
    get:
      tags: [Onboarding]
      operationId: getCurrentOnboarding
      summary: Consultar el progreso del usuario autenticado
      description: Devuelve los pasos requeridos, el paso actual y el estado de la wallet para mostrar el siguiente paso del flujo.
      responses:
        '200':
          description: Estado actual del onboarding.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Onboarding'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          description: El usuario no tiene un onboarding iniciado.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
        '409':
          description: No existe un flujo reanudable (por ejemplo, fue cerrado).
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
  /onboardings/current/steps/{stepId}:
    put:
      tags: [Onboarding]
      operationId: submitOnboardingStep
      summary: Validar y completar un paso
      description: Valida las respuestas del paso y, solo si son válidas, lo marca como completado y avanza el flujo. Repetir la misma solicitud no debe duplicar la finalización ni sus eventos.
      parameters:
        - name: stepId
          in: path
          required: true
          description: Identificador estable del paso del flujo, obtenido en la respuesta de onboarding.
          schema:
            type: string
            minLength: 1
        - $ref: '#/components/parameters/IdempotencyKey'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SubmitStepRequest'
            example:
              answers:
                configuredField: value
      responses:
        '200':
          description: Paso válido y guardado. Si era el último, el onboarding queda completado y la wallet activa.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Onboarding'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          description: No existe onboarding activo o el paso no pertenece al flujo.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
        '409':
          description: El paso no es el paso actual o el flujo ya fue cerrado.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
        '422':
          description: Datos inválidos o información obligatoria faltante. El flujo no avanza.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/ValidationProblem'
              example:
                type: about:blank
                title: Datos no válidos
                status: 422
                code: VALIDATION_FAILED
                detail: Corrige los campos indicados para continuar.
                errors:
                  - field: configuredField
                    code: REQUIRED
                    message: Este dato es obligatorio.
  /onboardings/current/close:
    post:
      tags: [Onboarding]
      operationId: closeOnboarding
      summary: Cerrar voluntariamente el onboarding
      description: Registra el cierre sin activar la wallet. Los cierres por expiración deben registrarse también en el servidor. No se admite el cierre de un flujo completado.
      responses:
        '200':
          description: Flujo cerrado y evento de cierre registrado.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Onboarding'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '404':
          description: No existe onboarding actual.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
        '409':
          description: El flujo ya está completado o cerrado.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
  /internal/analytics/onboarding/monthly:
    get:
      tags: [Analytics]
      operationId: getMonthlyOnboardingMetrics
      summary: Consultar métricas mensuales de onboarding y adquisición
      description: Endpoint interno para operaciones/analítica. Los costos deben provenir de una fuente de adquisición autorizada, no de valores declarados por el cliente.
      security:
        - bearerAuth: []
      parameters:
        - name: from
          in: query
          required: true
          description: Primer mes incluido, formato YYYY-MM en la zona America/Lima.
          schema:
            type: string
            pattern: '^\d{4}-(0[1-9]|1[0-2])$'
          example: '2026-01'
        - name: to
          in: query
          required: true
          description: Último mes incluido, formato YYYY-MM en la zona America/Lima.
          schema:
            type: string
            pattern: '^\d{4}-(0[1-9]|1[0-2])$'
          example: '2026-03'
      responses:
        '200':
          description: Métricas por mes calendario, inclusive.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MonthlyOnboardingMetrics'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '403':
          description: El principal no tiene permisos de analítica.
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/Problem'
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  parameters:
    IdempotencyKey:
      name: Idempotency-Key
      in: header
      required: true
      description: Clave única por operación y usuario. Repetirla con la misma solicitud devuelve el resultado original.
      schema:
        type: string
        minLength: 16
        maxLength: 128
  responses:
    BadRequest:
      description: Solicitud mal formada.
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/Problem'
    Unauthorized:
      description: Token ausente, inválido o vencido.
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/Problem'
    UnprocessableEntity:
      description: La solicitud no cumple las reglas del dominio.
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/Problem'
  schemas:
    StartOnboardingRequest:
      type: object
      additionalProperties: false
      required: [countryCode]
      properties:
        countryCode:
          type: string
          enum: [PE]
          description: País MVP. La identidad del usuario se obtiene del token.
        attributionToken:
          type: string
          maxLength: 512
          nullable: true
          description: Token opaco opcional para asociar adquisición; nunca representa un costo confiable.
    SubmitStepRequest:
      type: object
      additionalProperties: false
      required: [answers]
      properties:
        answers:
          type: object
          description: Respuestas definidas por la configuración del paso y las reglas aprobadas por producto/compliance.
          additionalProperties: true
    Onboarding:
      type: object
      required: [id, status, walletStatus, countryCode, steps, currentStepId, startedAt, updatedAt]
      properties:
        id:
          type: string
          example: onb_01JABC
        status:
          type: string
          enum: [in_progress, completed, closed]
        walletStatus:
          type: string
          enum: [pending, active]
        countryCode:
          type: string
          enum: [PE]
        steps:
          type: array
          items:
            $ref: '#/components/schemas/OnboardingStep'
        currentStepId:
          type: string
          nullable: true
          description: Nulo cuando el onboarding ya no tiene un paso pendiente.
        startedAt:
          type: string
          format: date-time
        completedAt:
          type: string
          format: date-time
          nullable: true
        closedAt:
          type: string
          format: date-time
          nullable: true
        updatedAt:
          type: string
          format: date-time
    OnboardingStep:
      type: object
      required: [id, title, order, status]
      properties:
        id:
          type: string
          example: identity
        title:
          type: string
          description: Etiqueta para presentación; no sustituye las reglas de validación del servidor.
        order:
          type: integer
          minimum: 1
        status:
          type: string
          enum: [pending, current, completed]
        completedAt:
          type: string
          format: date-time
          nullable: true
    ValidationIssue:
      type: object
      required: [code, message]
      properties:
        field:
          type: string
          description: Ruta del campo dentro de answers, cuando corresponda.
        code:
          type: string
          example: REQUIRED
        message:
          type: string
          description: Mensaje accionable y seguro para mostrar al usuario.
    Problem:
      type: object
      required: [title, status]
      properties:
        type:
          type: string
          format: uri-reference
          default: about:blank
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
          format: uri-reference
        code:
          type: string
          description: Código estable para lógica del cliente.
        onboardingId:
          type: string
          description: Identificador existente cuando code es ONBOARDING_ALREADY_IN_PROGRESS.
    ValidationProblem:
      allOf:
        - $ref: '#/components/schemas/Problem'
        - type: object
          required: [errors]
          properties:
            errors:
              type: array
              items:
                $ref: '#/components/schemas/ValidationIssue'
    MonthlyOnboardingMetrics:
      type: object
      required: [timezone, currency, months]
      properties:
        timezone:
          type: string
          enum: [America/Lima]
        currency:
          type: string
          enum: [PEN]
        months:
          type: array
          items:
            type: object
            required: [month, startedUsers, completedUsers, newActiveUsers, monthlyActiveUsers, medianCompletionSeconds, acquisitionSpend, cacPerNewUser]
            properties:
              month:
                type: string
                pattern: '^\d{4}-(0[1-9]|1[0-2])$'
              startedUsers:
                type: integer
                minimum: 0
              completedUsers:
                type: integer
                minimum: 0
              newActiveUsers:
                type: integer
                minimum: 0
                description: Usuarios únicos cuya wallet pasó a activa por primera vez durante el mes.
              monthlyActiveUsers:
                type: integer
                minimum: 0
                description: Usuarios únicos con actividad de pago durante el mes; requiere integración con la fuente de actividad de pagos.
              medianCompletionSeconds:
                type: integer
                minimum: 0
                nullable: true
                description: Mediana entre startedAt y completedAt de los onboardings completados en el mes.
              acquisitionSpend:
                type: number
                format: double
                minimum: 0
                description: Gasto de adquisición en PEN atribuido a la cohorte de nuevos usuarios activos.
              cacPerNewUser:
                type: number
                format: double
                minimum: 0
                nullable: true
                description: acquisitionSpend / newActiveUsers; null si no hay nuevos usuarios activos.
```

## Reglas del contrato

- El orden y el conjunto de pasos los define el servidor y se devuelven en `steps`; `currentStepId` permite al cliente mostrar el progreso y el siguiente paso sin inferirlo.
- Una validación fallida devuelve `422`, enumera los campos corregibles y no avanza el paso. Los mensajes no deben revelar reglas internas sensibles.
- El último paso válido transiciona el onboarding a `completed`, activa la wallet y establece `completedAt`; el mismo evento no debe duplicarse en reintentos.
- Inicio, finalización de cada paso, activación y cierre/expiración se registran en servidor con identificador de usuario, onboarding, timestamp y atribución disponible. No se expone un endpoint público para falsificar eventos.
- Los endpoints de onboarding solo permiten acceder al flujo asociado al principal autenticado. El endpoint analítico exige un rol/permisos explícitos y debe retornar agregados, no respuestas KYC ni datos personales.
- `Idempotency-Key` es obligatorio en creación y envío de pasos. El mismo valor con un cuerpo diferente debe rechazarse como conflicto; la retención de claves debe cubrir la ventana de reintentos definida por la plataforma.
- Aplicar límites de tamaño de payload, rate limiting y política de retención de datos acorde con seguridad y privacidad.

## Definiciones analíticas y decisiones pendientes

- La propuesta mide duración desde el primer `startedAt` persistido hasta `completedAt`, ambos en UTC. La historia señala que la frontera oficial de inicio/fin está abierta; producto debe aprobar esta definición, en particular para sesiones reanudadas.
- `newActiveUsers` cuenta activaciones únicas, no inicios ni usuarios que solo completaron pasos. El CAC mensual se calcula como gasto atribuido dividido entre esos nuevos usuarios activos; si el Product Owner define otra cohorte de CAC, se debe ajustar la fórmula antes de implementar.
- `monthlyActiveUsers` requiere una fuente de actividad de pagos definida por la épica; onboarding por sí solo no permite calcular MAU. La fuente, la ventana de actividad y su integración deben acordarse.
- El gasto de adquisición y su atribución deben integrarse desde una fuente confiable de marketing/finanzas, con reglas de atribución y moneda acordadas. No se aceptan importes desde el cliente.
- Producto y compliance deben aprobar los campos, obligatoriedad, validaciones, evidencias y tratamiento de datos de cada paso KYC. Este contrato no prescribe documentos ni requisitos regulatorios.
- Definir el plazo y regla de expiración de flujos abandonados, además de la retención de eventos y métricas.

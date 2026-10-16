# Endpoints y pantallas del onboarding: guía de implementación

Este documento relaciona las pantallas del [prototipo](./prototipo-onboarding-celular.html) con los endpoints definidos en [ENDPOINTS.md](./ENDPOINTS.md). Sirve como base para codificar el cliente móvil.

## Fuentes y leyenda

- Contrato de API: [ENDPOINTS.md](./ENDPOINTS.md) (OpenAPI 3.0.3, base `/api/v1`).
- Pantallas: [prototipo-onboarding-celular.html](./prototipo-onboarding-celular.html).
- Historia y épica: `HU/user-stories/user-onboarding-mvp-completion.sp.md` y `HU/epic/peru-wallet-mvp.sp.md`.

Cada elemento lleva una etiqueta:

- **[C] Contrato**: definido en ENDPOINTS.md. Implementar tal cual.
- **[P] Propuesta**: lo define el prototipo o este documento, pero producto y compliance deben aprobarlo antes de implementarlo como definitivo.
- **[G] Brecha**: el prototipo necesita algo que el contrato no define. Requiere decisión o un cambio al contrato antes de codificar.

## Flujo general

| # | Pantalla | Acción del usuario | Endpoint | Resultado esperado |
|---|---|---|---|---|
| 1 | Bienvenida | Crear mi wallet | `POST /onboardings` [C] | 201: ir a pantalla 2. 409: reanudar el flujo existente. |
| 1 | Bienvenida | Ya tengo cuenta | Sin endpoint [G] | Flujo de acceso fuera del contrato. |
| 2 | Número de celular y términos | Continuar | `PUT /onboardings/current/steps/{stepId}` [C] con paso de celular [P] | 200: ir al siguiente paso. 422: marcar campos. |
| 3 | Código SMS | Completar 6 dígitos | `PUT /onboardings/current/steps/{stepId}` [C] con paso de código [P] | 200: ir a pantalla 4. 422: mostrar error del servidor. |
| 3 | Código SMS | Reenviar código | Sin endpoint [G] | No definido. |
| 3 | Código SMS | Cambiar número | Sin endpoint [G] | No definido. |
| 4 | Crear PIN | Activar wallet | `PUT /onboardings/current/steps/{stepId}` [C] con paso de PIN [P] | 200 con `status: completed` y `walletStatus: active`: ir a pantalla 5. |
| 5 | Cuenta lista | Hacer mi primer pago | Fuera del onboarding [G] | Navegar a la pantalla de inicio de la wallet. |
| 5 | Cuenta lista | Banner de DNI y límite PEN 300 | Sin endpoint [G] | El valor del límite y el banner no vienen del servidor. |

El cliente no debe asumir cuántos pasos hay ni sus identificadores. Los pasos los define el servidor en `steps`, y el paso actual viene en `currentStepId` [C]. Los identificadores de ejemplo de este documento (celular, código, PIN) son propuestas [P].

## Reglas generales para el cliente

Todas las reglas de esta sección vienen del contrato [C].

- **Identidad**: cada solicitud lleva `Authorization: Bearer <token>`. El cliente no envía `userId`; la identidad sale del token.
- **Idempotency-Key**: obligatoria en `POST /onboardings` y en `PUT .../steps/{stepId}`. Debe tener entre 16 y 128 caracteres.
  - Generar una clave por acción del usuario. Reutilizarla en reintentos con el mismo cuerpo.
  - Si el cuerpo cambia, generar una clave nueva. El contrato rechaza la misma clave con un cuerpo distinto.
- **Errores**: llegan como `application/problem+json`. Usar `code` para la lógica y mostrar solo `message` (seguro para el usuario).
- **Errores de validación (422)**: `errors[].field` es la ruta dentro de `answers`. Usarla para marcar el campo correspondiente. El paso no avanza.
- **Estado al reanudar**: antes de mostrar una pantalla de paso, usar `GET /onboardings/current` para conocer `currentStepId`.
- **Datos sensibles**: no registrar `answers` en logs, analítica ni crash reports. Esto incluye el celular, el código y el PIN.
- **Analítica**: la app no llama a `/internal/analytics/...` ni envía eventos, importes ni métricas. Los eventos los registra el servidor.

### Respuestas por endpoint

| Endpoint | Código | Significado | Acción en la app |
|---|---|---|---|
| `POST /onboardings` | 201 | Flujo creado. | Mostrar el paso indicado en `currentStepId`. |
| `POST /onboardings` | 409 `ONBOARDING_ALREADY_IN_PROGRESS` | Ya existe un flujo. Trae `onboardingId`. | Llamar a `GET /onboardings/current` y reanudar. |
| `POST /onboardings` | 400 / 422 | Solicitud o dominio inválido. | Mostrar error genérico y registrar el fallo sin datos personales. |
| `GET /onboardings/current` | 200 | Estado actual. | Renderizar según `steps` y `currentStepId`. |
| `GET /onboardings/current` | 404 | Sin onboarding. | Ir a pantalla 1. |
| `GET /onboardings/current` | 409 | Flujo cerrado o no reanudable. | Ir a pantalla 1 y crear un flujo nuevo. |
| `PUT .../steps/{stepId}` | 200 | Paso válido. | Si `status` es `completed` y `walletStatus` es `active`, ir a pantalla 5. Si no, ir al `currentStepId`. |
| `PUT .../steps/{stepId}` | 422 `VALIDATION_FAILED` | Datos inválidos o faltantes. | Marcar los campos de `errors[]` y mostrar su `message`. No avanzar. |
| `PUT .../steps/{stepId}` | 409 | Paso no actual o flujo cerrado. | Recargar con `GET /onboardings/current`. |
| `PUT .../steps/{stepId}` | 404 | Sin onboarding activo o paso ajeno. | Recargar con `GET /onboardings/current`. |
| `POST .../close` | 200 | Flujo cerrado. | Salir del onboarding. |
| `POST .../close` | 409 | Ya completado o cerrado. | Recargar el estado. |
| Cualquiera | 401 | Token ausente, inválido o vencido. | Reautenticar [G]. |

## Detalle por pantalla

### Pantalla 1: Bienvenida

- **Campos**: ninguno.
- **Acción principal**: `POST /onboardings` [C].
  - Cuerpo: `{ "countryCode": "PE" }`. Opcionalmente, `attributionToken`.
  - `countryCode` es obligatorio y su único valor válido es `PE` [C].
  - `attributionToken` es opcional, opaco, de hasta 512 caracteres y nullable [C]. El contrato no define su origen. Puede venir de un enlace de campaña [P]. Nunca representa un costo confiable [C].
  - Headers: `Authorization` e `Idempotency-Key` [C].
- **Acción secundaria**: "Ya tengo cuenta" no tiene endpoint [G].

### Pantalla 2: Número de celular y términos

- **Campo 1: número de celular** [P]
  - Prefijo fijo `+51`. El país ya viene en `countryCode` del inicio, así que no se envía por separado.
  - 9 dígitos numéricos. Formato supuesto para celulares peruanos: inicia con `9` [P, confirmar].
  - Teclado numérico (`inputmode="numeric"`) y autocompletado de teléfono.
- **Campo 2: aceptación de términos y política de datos** [P]
  - Casilla obligatoria antes de continuar.
  - Los enlaces a términos y política de datos no tienen URL definida [G].
- **Botón "Continuar"**: habilitado solo con 9 dígitos y la casilla marcada [P]. Es una ayuda de interfaz. El servidor valida igual y responde 422 si algo falla [C].
- **Llamada**: `PUT /onboardings/current/steps/{stepId}` [C].
  - `stepId`: identificador del paso de celular, tomado de `steps` [C]. El valor no está definido [G].
  - Cuerpo: `{ "answers": { "<campo celular>": "<9 dígitos>", "<campo términos>": true } }` [P para los nombres de campo].
- **Errores**: 422 marca el campo de `errors[].field` con su `message`.
- **Brecha**: no hay un endpoint para enviar el SMS. No se sabe si el envío ocurre al completar este paso [G].

### Pantalla 3: Código SMS

- **Campo**: código de 6 dígitos [P].
  - Seis cajas numéricas con `autocomplete="one-time-code"`.
  - Al escribir un dígito, el foco pasa a la siguiente caja. Con Backspace en una caja vacía, el foco retrocede.
- **Envío del código**: el prototipo no tiene botón de envío [G].
  - Propuesta [P]: enviar automáticamente al completar los 6 dígitos.
- **Llamada**: `PUT /onboardings/current/steps/{stepId}` con el paso de código [C]. Cuerpo: `{ "answers": { "<campo código>": "<6 dígitos>" } }` [P para el nombre del campo].
- **Error de código incorrecto**: el mensaje debe venir del servidor en `errors[].message` [C].
  - El prototipo muestra "Te quedan 2 intentos". El contrato no tiene contador de intentos [G]. No codificar ese texto fijo.
- **Reenvío con temporizador de 30 segundos**: no hay endpoint de reenvío [G]. El temporizador es solo visual.
- **"Cambiar número"**: no hay endpoint para volver al paso de celular [G].

### Pantalla 4: Crear PIN

- **Campo 1: PIN de 6 dígitos** [P].
- **Campo 2: confirmación del PIN** [P].
  - Ambos valores deben coincidir. La coincidencia se valida en la app y el servidor la repite.
  - Teclado numérico. Enmascarado (`type="password"`).
  - Cada campo tiene 6 casillas de un dígito con avance y retroceso automático, como el código SMS [P].
- **Validación en la app** [P], en este orden:
  1. Mensaje "Elige un PIN menos predecible." si los 6 dígitos son iguales (`111111`) o forman una secuencia ascendente o descendente (`123456`, `987654`).
  2. Mensaje "Los PIN no coinciden." si la confirmación es distinta del PIN.
  - El botón "Activar wallet" queda deshabilitado mientras no se cumplan ambas reglas.
  - La lista de patrones prohibidos es una propuesta del prototipo y no está definida en la épica ni en el contrato [G]. El servidor debe validarla de forma independiente y su mensaje debe venir de `errors[].message`.
- **Botón "Activar wallet"**: habilitado solo con los dos PIN válidos y coincidentes [P].
- **Llamada**: `PUT /onboardings/current/steps/{stepId}` con el paso de PIN [C].
  - Cuerpo: `{ "answers": { "<campo pin>": "<6 dígitos>", "<campo confirmación>": "<6 dígitos>" } }` [P].
  - Si este es el último paso, el 200 trae `status: completed` y `walletStatus: active` [C].
- **Brecha**: no está definido cómo viaja el PIN ni cómo se almacena [G]. Debe revisarlo seguridad antes de codificar. El cliente no debe persistirlo ni registrarlo.

### Pantalla 5: Cuenta lista

- **Entrada**: se muestra solo cuando la respuesta final tiene `status: completed` y `walletStatus: active` [C].
- **Límite diario "PEN 300"**: el contrato no devuelve límites [G]. El valor del prototipo es un ejemplo y compliance debe confirmarlo. No codificar fijo.
- **Banner "Verifica tu DNI"**: no hay endpoint ni paso de DNI en el contrato [G]. Confirmar si es parte del MVP y cómo se realiza.
- **Botón "Hacer mi primer pago"**: navega fuera del onboarding [G]. El destino no está definido.

## Brechas que requieren decisión antes de codificar

1. **Envío y reenvío de OTP**. El contrato no define cuándo se envía el SMS, cómo reenviarlo ni cómo cambiar el número. Propuesta: un paso de envío y un paso de reenvío configurados por el servidor.
2. **Campos por paso**. El cliente no sabe qué campos pide cada `stepId` antes de enviarlo. Propuesta: que `OnboardingStep` incluya la lista de campos (`name`, `type`, `required`, `pattern`), para que la app renderice las pantallas sin codificar reglas.
3. **Nombres de campos en `answers`**. El contrato solo tiene el ejemplo `configuredField`. Los nombres de este documento son propuestas [P]. El contrato define `answers` como objeto libre, pero la regla §4.2 de [reglas-security.md](../reglas/reglas-security.md) exige rechazar campos no esperados. El servidor debe validar cada campo contra una lista explícita por paso [G].
4. **Envío del código**. El prototipo no tiene botón. Decidir entre envío automático con 6 dígitos o un botón explícito.
5. **Intentos restantes**. El contrato no los expone. Decidir si el servidor los devuelve en `errors[].message`, con un código nuevo, o no se muestran.
6. **Límite PEN 300 y banner de DNI**. Base: [reglas-security.md](../reglas/reglas-security.md).
   - **Límite**: el servidor debe devolverlo y aplicarlo. La app solo lo muestra (§3.5: nunca confiar en el frontend) [P].
   - **DNI**: es dato personal regulado (§7.2). Se propone que sea un paso del mismo onboarding y no un banner posterior a la activación. Así aplican idempotencia, auditoría con `correlation-id` y MFA para el alta de cuenta y los cambios KYC (§3.4, §4.7, §9.2) [P].
   - **Minimización y retención**: guardar solo lo necesario, cifrado en reposo, enmascarado en logs y con política de retención definida (§6.6, §7.1, §7.3, §7.4) [G].
   - **Decisiones pendientes**: valor del límite, si el DNI es obligatorio para activar la wallet y si el SMS cuenta como segundo factor para el alta (§3.4) [G]. Las decide producto con compliance y seguridad.
7. **Acceso con cuenta existente** ("Ya tengo cuenta") y manejo de 401. Fuera del contrato.
8. **Retroceso y salida**. Las flechas "←" no tienen operación en el contrato. Solo existe `POST .../close`. Decidir si "←" regresa de paso (no soportado) o si se usa el cierre con confirmación.
9. **Transmisión y almacenamiento del PIN**. Definir con seguridad si viaja en `answers` y cómo se protege.
10. **Términos y política de datos**. Falta la URL y el texto aprobado por compliance.
11. **Formato del celular**. Confirmar los 9 dígitos y el inicio con `9`.
12. **Flujos abandonados**. El contrato ya indica que falta definir la expiración y retención [C, pendiente].

## Fuera de alcance de este documento

- Endpoints de analítica (`/internal/analytics/onboarding/monthly`). Son para backoffice y no los consume la app.
- Diseño visual y textos finales. El prototipo es referencia de flujo, no de diseño de producción.

# Spec: finalización del onboarding de wallet

## Propósito

Definir el comportamiento verificable del onboarding MVP de wallet en Perú, su
relación con la activación y el acceso a pagos de bajo monto, y la información
analítica necesaria para evaluar los objetivos de la historia.

## Fuente

- Historia [user-onboarding-mvp-completion](../../../../user-stories/user-onboarding-mvp-completion.sp.md).
- [Épica MVP de wallet en Perú](../../../../epic/peru-wallet-mvp.sp.md).
- Issue o hallazgo fuente: no se identifica uno en los artefactos consultados.

## Contexto actual

La historia define un onboarding guiado con validación, activación posterior a
su finalización e instrumentación analítica. La épica fija una meta de reducir
la mediana de finalización de 8 a 3 minutos dentro de un trimestre posterior al
lanzamiento, y establece objetivos de MAU y CAC para los primeros tres meses.

Los artefactos fuente no describen el comportamiento actualmente implementado
ni definen los timestamps, la población analítica, la definición de usuario
activo o la regla de atribución de gasto. Esta especificación no presupone esos
detalles.

## Problema confirmado

La historia requiere que el usuario pueda entender su progreso y corregir datos
antes de avanzar, completar el onboarding antes de que su wallet se presente
como activa y contar con medición para evaluar las metas del MVP.

## Comportamiento a preservar

- La wallet solo se activa como resultado de completar correctamente todos los
  pasos requeridos del onboarding.
- El acceso habilitado por esta historia es el punto de entrada a pagos de bajo
  monto; esta especificación no define el comportamiento de los pagos.
- La instrumentación debe cubrir el inicio, la finalización de cada paso y el
  cierre del flujo.
- Las metas de tiempo, MAU y CAC no se declaran alcanzadas cuando las
  definiciones necesarias para medirlas no han sido aprobadas.
- No se autoriza cambiar contratos HTTP existentes mediante esta
  especificación.

## Alcance

- Mostrar la secuencia requerida y el paso actual durante el onboarding.
- Validar información obligatoria y datos ingresados antes de permitir avanzar,
  indicando qué corregir.
- Activar la wallet al completar correctamente el flujo y habilitar el punto de
  entrada a pagos de bajo monto.
- Registrar eventos de inicio, finalización de pasos y cierre del onboarding.
- Producir información analítica que permita evaluar la duración, la activación
  y la adquisición conforme a las definiciones aprobadas por Producto.

## Fuera de alcance

- Definir requisitos de KYC, documentación o cumplimiento; la historia indica
  que deben acordarse con Producto y Cumplimiento antes de implementar.
- Definir o implementar los flujos de pago, transferencias o cobros con QR.
- Fijar la definición de usuario activo, los timestamps de duración, la
  población de medición o la regla de atribución del gasto sin aprobación de
  Producto.
- Cambiar endpoints, cuerpos, estados o respuestas HTTP existentes.

## Requisitos añadidos

### Requirement: Progreso guiado del onboarding

El flujo MUST mostrar la secuencia de pasos requeridos y el paso actual durante
todo el onboarding.

#### Scenario: La persona inicia o continúa el onboarding

- **WHEN** la persona inicia o continúa el onboarding
- **THEN** el flujo muestra la secuencia requerida y señala el paso actual

### Requirement: Validación antes de avanzar

El flujo MUST bloquear el avance si falta información obligatoria o hay datos
inválidos, y MUST mostrar un mensaje accionable para corregirlos.

#### Scenario: Falta información obligatoria

- **WHEN** la persona intenta avanzar sin completar información obligatoria
- **THEN** el flujo no avanza y muestra qué debe corregir

#### Scenario: Los datos ingresados son inválidos

- **WHEN** la persona intenta avanzar con datos inválidos
- **THEN** el flujo no avanza y muestra una acción para corregirlos

### Requirement: Activación posterior a completar el onboarding

El sistema MUST cambiar el estado de la wallet a activo únicamente cuando el
onboarding finalice correctamente. Al completarse, MUST permitir que la persona
acceda al punto de entrada de pagos de bajo monto.

#### Scenario: Onboarding finaliza correctamente

- **WHEN** la persona completa correctamente todos los pasos requeridos
- **THEN** la wallet cambia a activa y queda disponible el punto de entrada de
  pagos de bajo monto

#### Scenario: Onboarding no ha finalizado correctamente

- **WHEN** todavía falta completar correctamente el onboarding
- **THEN** la wallet no se presenta como activa por efecto de este flujo

### Requirement: Eventos analíticos del onboarding

El sistema MUST registrar eventos de inicio del onboarding, finalización de cada
paso y cierre del flujo para analítica del MVP.

#### Scenario: Inicio y pasos completados

- **WHEN** la persona inicia el onboarding y completa uno o más pasos
- **THEN** se registran el inicio y la finalización de cada paso completado

#### Scenario: Cierre del flujo

- **WHEN** el flujo se cierra
- **THEN** se registra el evento de cierre para analítica

### Requirement: Medición de duración

La medición de la cohorte MVP en Perú MUST permitir evaluar una reducción de la
mediana de finalización de 8 a 3 minutos dentro del trimestre posterior al
lanzamiento. Producto MUST aprobar y documentar la población, los límites
temporales y el método de cálculo antes de reportar el resultado.

#### Scenario: Reporte de duración con definición aprobada

- **GIVEN** que Producto aprobó y documentó la población, la frontera temporal y
  el método de cálculo
- **WHEN** se produce el reporte de la cohorte MVP en Perú para el periodo
  definido
- **THEN** el reporte permite verificar la mediana frente a la línea base de 8
  minutos y la meta de 3 minutos

#### Scenario: Definición de duración pendiente

- **GIVEN** que no se han acordado los timestamps o el método de cálculo
- **WHEN** se revisan resultados de duración
- **THEN** el resultado se marca como no verificable y no se declara alcanzada la
  meta de 3 minutos

### Requirement: Salida analítica de activación y adquisición

La salida analítica MUST incluir conteos mensuales de nuevos usuarios activos y
la atribución de gasto de adquisición necesaria para evaluar MAU de 1,000–2,000
y CAC de PEN 10 por usuario nuevo durante los primeros tres meses posteriores al
lanzamiento. Producto MUST aprobar las definiciones de usuario activo y de
atribución antes de declarar estos objetivos verificables.

#### Scenario: Reporte mensual con definiciones aprobadas

- **GIVEN** que Producto aprobó la definición de usuario activo y la fuente y
  regla de atribución de gasto
- **WHEN** se produce la salida analítica mensual durante los primeros tres meses
  posteriores al lanzamiento
- **THEN** incluye los conteos mensuales y la atribución necesaria para evaluar
  MAU y CAC frente a los objetivos de la historia

#### Scenario: Definición de MAU o CAC pendiente

- **GIVEN** que la definición de usuario activo o la regla de atribución de gasto
  no ha sido aprobada
- **WHEN** se revisa la salida analítica
- **THEN** se identifican las métricas afectadas como no verificables y no se
  afirma que se alcanzaron sus objetivos

## Contratos afectados/protegidos

La historia no identifica endpoints ni contratos técnicos propios del
onboarding. Por tanto, esta especificación no define cambios de request,
response, estados HTTP ni campos de ningún endpoint.

Se preservan los contratos protegidos de ReqFlow: `POST /auth/login`,
`GET/POST /api/tasks`, `GET /api/summary` y `POST /api/requirements`. Cualquier
cambio a esos contratos requiere una decisión explícita y una actualización de
la especificación que corresponda.

## Riesgos, supuestos y preguntas abiertas

- **Supuesto de la historia:** los requisitos de KYC y documentación se
  definirán con Producto y Cumplimiento antes de implementar.
- **Supuesto de negocio:** el rango de MAU (1,000–2,000) y el objetivo de CAC
  (PEN 10) fueron definidos por el Product Owner.
- **Riesgo de medición:** sin acordar los timestamps y el método de cálculo, la
  duración no es verificable.
- **Riesgo de medición:** sin aprobar la definición de usuario activo y la regla
  de atribución de gasto, MAU y CAC no son verificables.
- **Pregunta abierta:** ¿qué eventos o timestamps definen oficialmente el
  inicio y el fin de la duración del onboarding?
- **Pregunta abierta:** ¿qué definición de usuario activo, población y regla de
  atribución se usarán para reportar MAU y CAC?

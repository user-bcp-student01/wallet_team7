# Proposal: completar el onboarding MVP de wallet

## Why

La historia de onboarding indica que las personas usuarias deben poder completar
un recorrido guiado y entender el siguiente paso para comenzar a pagar sin
abandonar el proceso. También establece como objetivo reducir de 8 a 3 minutos
la mediana de finalización, y solicita instrumentación para evaluar activación,
MAU y CAC del MVP en Perú.

Esta propuesta convierte esa necesidad y sus criterios existentes en una
especificación trazable. La fuente no documenta el comportamiento actual de una
implementación, por lo que no se presupone que el flujo ya exista ni que sus
métricas actuales hayan sido medidas.

## Fuentes

- Historia: [user-onboarding-mvp-completion](../../user-stories/user-onboarding-mvp-completion.sp.md).
- Épica: [MVP de wallet en Perú](../../epic/peru-wallet-mvp.sp.md).
- Reglas de producto: [REGLAS_PO.md](../../rules/REGLAS_PO.md).

## What Changes

- **Dentro del alcance:** especificar un onboarding guiado con pasos y progreso
  visibles; impedir el avance ante información obligatoria ausente o inválida y
  mostrar cómo corregirla; activar la wallet al completar el flujo y permitir
  el acceso al punto de entrada de pagos de bajo monto; registrar inicio,
  finalización de pasos y cierre para analítica; y producir información que
  permita evaluar las métricas de negocio declaradas.
- **Fuera del alcance:** lanzamiento multipaís, programas avanzados de lealtad,
  paridad completa con todos los proveedores desde el primer día, diseño de
  arquitectura o selección de tecnologías, y definición de requisitos KYC o
  documentos que aún no hayan sido aprobados por Producto y Cumplimiento.
- **Comportamiento a preservar:** no presentar la wallet como activa antes de
  finalizar correctamente el onboarding; no ampliar los pasos, límites ni datos
  solicitados más allá de requisitos aprobados; respetar los comportamientos
  existentes de pagos de bajo monto y los contratos funcionales existentes.

## Capabilities

### New Capabilities

- `wallet-onboarding-completion`: recorrido guiado, validación de avance,
  activación de wallet e instrumentación analítica del onboarding MVP.

### Modified Capabilities

Ninguna identificada en las fuentes disponibles. No se proporcionó un catálogo
de capacidades de wallet ya aprobado contra el cual declarar modificaciones.

## Impact

- Producto: pasos del onboarding, mensajes de validación, estado de activación y
  acceso al punto de entrada de pagos de bajo monto.
- Analítica: eventos de inicio, finalización de pasos y cierre; conteos mensuales
  de nuevos usuarios activos y atribución de gasto de adquisición.
- Las fuentes no identifican endpoints, esquemas de datos ni contratos técnicos.
  Cualquier impacto sobre ellos requiere análisis y aprobación en una etapa
  posterior.

## Decisiones pendientes

- Requisitos de KYC y documentación para el MVP en Perú.
- Eventos y timestamps que delimitan la duración del onboarding.
- Definición de usuario activo, fuente de gasto y regla de atribución para
  verificar MAU y CAC.
- Secuencia definitiva de pasos obligatorios y definición de un cierre del flujo
  para fines analíticos.

La propuesta queda sujeta a revisión humana; no representa aprobación de las
decisiones pendientes.

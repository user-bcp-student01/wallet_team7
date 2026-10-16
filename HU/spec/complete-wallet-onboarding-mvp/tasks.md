# Tasks: onboarding MVP de wallet

Las tareas están pendientes y describen trabajo de producto y validación a alto
nivel. No seleccionan tecnologías ni sustituyen el diseño técnico. Las tareas
que dependen de definiciones de Producto y Cumplimiento no deben considerarse
listas para implementación hasta que esas decisiones estén aprobadas.

## 1. Cerrar definiciones de producto

- [ ] 1.1 Acordar con Producto y Cumplimiento los requisitos KYC y de
  documentación aplicables al MVP en Perú.
- [ ] 1.2 Aprobar la lista y secuencia de pasos obligatorios del onboarding.
- [ ] 1.3 Aprobar los timestamps que delimitan el inicio y fin de onboarding, la
  población de medición y el método de cálculo de la mediana.
- [ ] 1.4 Acordar la definición de usuario activo, el origen de datos de gasto y
  la regla de atribución necesaria para evaluar MAU y CAC.
- [ ] 1.5 Definir qué evento representa el cierre del flujo y qué significa el
  punto de entrada de pagos de bajo monto en la experiencia del producto.

## 2. Especificar y revisar el comportamiento

- [ ] 2.1 Trazar cada criterio de aceptación de la historia a un requisito y a
  evidencia que permita comprobarlo.
- [ ] 2.2 Revisar que los mensajes de error orienten a corregir los datos sin
  cambiar los requisitos obligatorios aprobados.
- [ ] 2.3 Confirmar que la wallet solo se presenta como activa al completar
  correctamente el flujo y que el acceso a pagos está disponible entonces.
- [ ] 2.4 Revisar los contratos funcionales existentes y documentar cualquier
  impacto propuesto para aprobación explícita.
- [ ] 2.5 Obtener revisión y aprobación humana de esta especificación antes del
  handoff a Arquitectura.

## 3. Implementar según decisiones aprobadas

- [ ] 3.1 Implementar la experiencia guiada conforme a la lista de pasos y
  decisiones de producto aprobadas.
- [ ] 3.2 Implementar bloqueo de avance y mensajes accionables para información
  ausente o inválida.
- [ ] 3.3 Implementar la transición de activación y el acceso a pagos de bajo
  monto de acuerdo con el comportamiento aprobado.
- [ ] 3.4 Implementar la instrumentación acordada para inicio, pasos completados
  y cierre, junto con la salida analítica mensual requerida.

## 4. Validar criterios y métricas

- [ ] 4.1 Verificar los estados de progreso, validación, finalización, activación
  y acceso a pagos con pruebas funcionales y evidencia revisable.
- [ ] 4.2 Verificar la presencia de eventos de inicio, finalización de cada paso
  y cierre; adjuntar una muestra de la salida obtenida.
- [ ] 4.3 Verificar que la salida analítica soporte el cálculo de duración
  mediana con la definición aprobada, sin declarar resultados no medidos.
- [ ] 4.4 Verificar que los reportes mensuales permitan evaluar MAU y CAC con las
  definiciones aprobadas durante los primeros tres meses posteriores al
  lanzamiento.
- [ ] 4.5 Adjuntar resultados reales de pruebas, evidencia del flujo y un
  ejemplo de reporte analítico; dejar explícitas las métricas aún no evaluables.

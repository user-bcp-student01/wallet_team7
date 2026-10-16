# Reglas de producto — Onboarding MVP

Estas reglas guían la definición, implementación y aceptación de la historia
[user-onboarding-mvp-completion](../user-stories/user-onboarding-mvp-completion.sp.md)
y mantienen su alineación con la [épica MVP de wallet en Perú](../epic/peru-wallet-mvp.sp.md).
Son reglas de producto; no prescriben una solución técnica.

## 1. Resumen

El onboarding debe permitir que usuarios de smartphone que realizan transferencias
diarias de bajo monto completen un flujo guiado, entiendan el siguiente paso y
puedan empezar a pagar al activarse su wallet. El resultado se mide por la
finalización del flujo y por la instrumentación necesaria para evaluar activación,
MAU y CAC del MVP en Perú.

## 2. Alcance

- **Dentro:** recorrido guiado de onboarding para la cohorte MVP en Perú; estado
  visible del paso; validación de avance; activación de la wallet al completar el
  flujo; acceso al punto de entrada de pagos de bajo monto; y eventos analíticos
  de inicio, finalización de pasos y cierre.
- **Fuera:** despliegue multipaís, programas avanzados de lealtad y paridad
  funcional completa con todos los proveedores desde el primer día, conforme a
  la épica. No ampliar el alcance a pagos o cobros distintos de los necesarios
  para esta historia sin aprobación de producto.

## 3. Supuestos

- Los requisitos de KYC y documentación deben ser definidos por Producto y
  Cumplimiento antes de cerrar el alcance implementable; esta historia no los
  especifica.
- Los objetivos de MAU de 1,000–2,000 y CAC de PEN 10 por usuario nuevo son
  objetivos de negocio para los primeros tres meses posteriores al lanzamiento,
  no resultados que el flujo por sí solo garantice.
- La duración objetivo de onboarding es reducir la mediana de 8 a 3 minutos
  dentro del trimestre posterior al lanzamiento.

## 4. Decisiones de producto

- **Resuelto:** la cohorte de esta historia es el MVP en Perú y el usuario
  objetivo son personas de smartphone que realizan transferencias diarias de
  bajo monto.
- **Resuelto:** la wallet solo se considera activada cuando el onboarding finaliza
  correctamente; entonces debe estar disponible el punto de entrada de pagos de
  bajo monto.
- **Pendiente:** acordar el evento y los timestamps que marcan el inicio y el fin
  usados para medir la duración. No reportar la métrica de 3 minutos como
  verificable hasta fijar esta definición.
- **Pendiente:** acordar con Cumplimiento y Producto los requisitos de KYC y
  documentación antes de aprobar el alcance final del flujo.
- No introducir criterios, pasos, límites o recopilación de datos que no estén
  definidos en la historia o aprobados explícitamente por Producto y
  Cumplimiento.

## 5. Riesgos y mitigaciones

- **KYC/documentación sin definición:** puede cambiar pasos obligatorios y bloquear
  la aceptación. **Mitigación:** obtener decisión documentada de Producto y
  Cumplimiento antes de cerrar alcance y criterios.
- **Frontera analítica ambigua:** inicio o fin inconsistentes impiden comparar la
  línea base de 8 minutos con la meta de 3. **Mitigación:** acordar y documentar
  eventos, timestamps y regla de cálculo antes de instrumentar y evaluar.
- **Métricas de adquisición incompletas:** sin conteo mensual de nuevos usuarios
  activos y atribución de gasto no se puede verificar MAU/CAC. **Mitigación:**
  validar que la salida analítica permita segmentar por mes y vincular la
  atribución necesaria, sin asumir un modelo de atribución no aprobado.

## 6. Criterios de aceptación (medibles)

1. Durante todo el flujo se muestran la secuencia de pasos requeridos y el paso
   actual.
2. Ante información obligatoria ausente o inválida, el avance queda bloqueado y
   se presenta un mensaje accionable para corregirla.
3. Al completar correctamente el último paso, la wallet queda activa y el usuario
   puede acceder al punto de entrada de pagos de bajo monto; si el flujo no
   finaliza correctamente, no se presenta como activada.
4. Se registran los eventos de inicio, finalización de cada paso y cierre del
   flujo para analítica del MVP.
5. La mediana del tiempo de finalización para la cohorte MVP en Perú se reduce de
   8 a 3 minutos dentro del trimestre posterior al lanzamiento, usando una
   definición de inicio/fin aprobada y documentada.
6. La salida analítica presenta conteos mensuales de nuevos usuarios activos y
   atribución de gasto de adquisición suficiente para evaluar MAU de 1,000–2,000
   y CAC de PEN 10 por usuario nuevo durante los primeros tres meses posteriores
   al lanzamiento.

## 7. Plan de validación

- **Pruebas unitarias:** comprobar reglas de avance, validación de datos y
  transición a estado activo solo al completar correctamente el flujo.
- **Pruebas funcionales:** recorrer éxito, datos obligatorios ausentes o inválidos
  y cierre del flujo; comprobar pasos visibles, mensajes accionables y acceso a
  pagos tras la activación.
- **Seguridad y cumplimiento:** revisar con Cumplimiento los requisitos KYC
  acordados y verificar que el flujo no solicite datos adicionales no aprobados.
  Confirmar controles de acceso a la salida analítica según las políticas
  aprobadas, sin inventar una política en esta historia.
- **Evidencia requerida:** resultados de pruebas; capturas o registro de los
  estados y mensajes del flujo; muestra de eventos por inicio, paso y cierre; y
  reporte mensual que permita verificar la duración mediana, MAU y CAC con la
  definición de medición aprobada.

## 8. Tareas sugeridas por rol

- **Chapter/PO:** resolver la frontera temporal de medición; confirmar los
  objetivos y la regla de cálculo de MAU/CAC; obtener aprobación de KYC y
  documentación con Cumplimiento.
- **Tech Lead:** (1) confirmar cobertura de criterios en la solución propuesta;
  (2) revisar verificabilidad de activación y eventos sin ampliar alcance;
  (3) registrar dependencias que afecten la aceptación.
- **Backend:** (1) implementar y probar validaciones y transición de activación;
  (2) emitir los eventos acordados; (3) entregar datos del reporte mensual.
- **Frontend:** (1) mostrar secuencia y paso actual; (2) bloquear avance inválido
  con mensajes accionables; (3) mostrar acceso a pagos solo tras activación.
- **QA:** (1) diseñar casos de éxito, validación y cierre; (2) verificar eventos y
  datos de salida; (3) adjuntar resultados y evidencia de los criterios.
- **Cyber/Cumplimiento:** (1) validar requisitos KYC aprobados; (2) revisar el
  manejo de datos; (3) revisar el acceso analítico según políticas aplicables.

## 9. Preguntas abiertas

- ¿Qué eventos o timestamps oficiales marcan el inicio y fin de onboarding para
  calcular su duración?
- ¿Qué requisitos de KYC y documentación son obligatorios para el MVP en Perú?
- ¿Qué fuente y regla de atribución de gasto se usarán para calcular CAC, y qué
  definición de usuario activo aplicará al conteo mensual?

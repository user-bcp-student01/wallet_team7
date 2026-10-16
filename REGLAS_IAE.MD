# Contrato para ingeniería de IA

1. Antes de integrar un modelo, define el problema, la métrica de éxito y el criterio para decidir que la IA no es la solución adecuada.
2. Ninguna funcionalidad con IA se despliega sin un conjunto de evaluación versionado y con resultados reproducibles.
3. Toda salida generada por un modelo se trata como no confiable: valídala antes de usarla en reglas de negocio, persistencia o respuestas al usuario.
4. Las decisiones con impacto financiero, de identidad o de cumplimiento (aprobación de onboarding, KYC, límites, bloqueos) requieren revisión humana o reglas deterministas; el modelo solo puede recomendar.
5. No envíes a un proveedor externo datos personales, documentos KYC, tokens ni secretos sin minimización, enmascaramiento y aprobación de privacidad y cumplimiento.
6. No agregues claves de API, endpoints ni nombres de modelo en el código; usa variables de entorno o el gestor de secretos de la plataforma.
7. Meta de cobertura del código modificado: 90% o superior, incluyendo la lógica de construcción de prompts, parseo de respuestas y manejo de errores.
8. Separa en capas revisables: cliente del proveedor, construcción de prompts, parseo y validación de salidas, políticas (guardrails) y lógica de negocio.

## Prompts y configuración

9. Versiona los prompts como código o como recursos inmutables con identificador; un cambio de prompt se trata como un cambio de comportamiento y pasa por evaluación.
10. No concatenes entradas del usuario directamente en instrucciones del sistema; delimita el contenido no confiable y declara explícitamente que no son instrucciones.
11. Fija la versión del modelo, la temperatura y los parámetros de generación en configuración centralizada, no dispersos en el código.
12. Usa constantes con nombre para límites (número máximo de tokens, reintentos, tiempo de espera) en lugar de valores mágicos.

## Salidas estructuradas y validación

13. Solicita salidas en un formato estructurado (JSON con esquema) y valídalas con Jakarta Bean Validation antes de usarlas.
14. Si la salida no cumple el esquema, reintenta un número acotado de veces y después aplica un camino de fallback determinista o escala a revisión humana. Nunca propagues una salida inválida.
15. No registres en logs prompts completos, respuestas completas ni datos personales; registra identificadores de correlación, versión de prompt, versión de modelo, latencia y tokens consumidos.

## Costos, latencia y disponibilidad

16. Define presupuesto de tokens y costo por operación; alerta cuando se superen los umbrales.
17. Aplica tiempos de espera explícitos, reintentos con backoff y limitación de tasa hacia el proveedor.
18. Toda funcionalidad con IA debe tener un comportamiento degradado definido cuando el proveedor no esté disponible.
19. Cachea respuestas solo cuando la entrada y el contexto sean idénticos y no contengan datos sensibles; no agregues Redis ni otra caché distribuida sin requisito medible.

## Evaluación y calidad

20. Mantén un conjunto de casos de prueba dorados con entradas anonimizadas y resultados esperados; ejecútalo en CI antes de cualquier cambio de prompt, modelo o parámetros.
21. Define métricas por tarea (precisión, tasa de alucinación, tasa de escalamiento humano, tasa de fallo de esquema) y umbrales mínimos para aprobar un cambio.
22. Incluye pruebas de regresión para entradas adversarias: inyección de prompts, intentos de exfiltrar datos y solicitudes fuera de dominio.
23. Las pruebas unitarias del código que rodea al modelo deben usar un doble del proveedor; las pruebas de integración contra un proveedor real se ejecutan de forma controlada y no bloquean el pipeline sin justificación.

## Seguridad y cumplimiento

24. Aplica filtros de entrada y salida para detectar datos personales y contenido prohibido antes y después de la llamada al modelo.
25. Documenta el uso de IA en cada funcionalidad: finalidad, datos procesados, proveedor, retención y responsable.
26. Mantén trazabilidad de decisiones asistidas por IA para auditoría, sin exponer datos personales en el registro.
27. Revisa periódicamente sesgos y desempeño por segmento de usuarios cuando la salida afecte a personas.

## Agentes y herramientas

28. Un agente solo puede invocar las herramientas listadas explícitamente en su configuración, con permisos mínimos.
29. Las acciones de escritura o de alto impacto (transferencias, cambios de estado, envíos externos) requieren confirmación explícita y no pueden ser decididas solo por el modelo.
30. Limita el número de pasos y el tiempo total de ejecución de un agente, y registra cada llamada a herramienta.

## Línea base tecnológica

31. Integrar los modelos dentro del servicio Java/Quarkus definido en `REGLAS.md`, siguiendo las mismas reglas de capas, seguridad y CI.
32. Usar el cliente HTTP o SDK aprobado por el equipo de plataforma; las versiones deben verificarse al iniciar el proyecto y gestionarse en un único lugar.
33. Las dependencias de IA pasan por el mismo escaneo de vulnerabilidades y revisión de Dependency Review que el resto del proyecto.

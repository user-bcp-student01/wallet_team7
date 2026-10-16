# Contrato para agentes

1. Analiza el flujo completo antes de cambiar autenticación.
2. Conserva el contrato del Onboarding.
3. Crea pruebas de caracterización antes de refactorizar persistencia.
4. No silencies CodeQL, Dependency Review ni JaCoCo.
5. No agregues secretos reales; usa variables de entorno y valores de prueba aislados.
6. Separa API, servicio, repositorio y seguridad en cambios revisables.
7. Meta de cobertura del código modificado: 90% o superior.

## Clean code

8. Cada método hace una sola cosa; si un método valida, accede a datos y arma
   la respuesta a la vez, sepáralo en capas.
9. Aplicar los principios SOLID.
10. Sin duplicación: un bloque de código repetido en dos lugares se extrae a
    un método reutilizable.
11. Evitar anidamiento profundo (`if` dentro de `if` dentro de `if`); usar
    guard clauses / retorno anticipado en su lugar.
12. Sin números o strings "mágicos" sueltos en el código para la expiración del token); usar constantes con nombre.

## Línea base tecnológica: Java y Quarkus

Estas especificaciones son la propuesta para implementar la API de onboarding descrita en `docs/ENDPOINTS.md`. Las versiones finales deben verificarse contra la matriz oficial de compatibilidad de Quarkus, el proveedor de Java y las dependencias aprobadas al iniciar el proyecto.

### Plataforma

13. Usar Java 21 LTS como versión objetivo para un servicio nuevo, siempre que Quarkus, el runtime de despliegue y todas las dependencias necesarias estén certificados para esa versión.
14. Usar Quarkus 3.x en una versión estable con mantenimiento vigente. Gestionar las versiones de Quarkus y sus extensiones mediante el BOM oficial de Quarkus; no fijar versiones individuales de extensiones administradas por ese BOM.
15. Usar Maven con Maven Wrapper (`./mvnw` o `mvnw.cmd`) para que CI y desarrollo local ejecuten la misma versión. Mantener las versiones del plugin y del BOM en una ubicación centralizada.
16. Desarrollar y desplegar inicialmente en modo JVM dentro de una imagen de contenedor no privilegiada. Considerar compilación nativa únicamente si pruebas representativas demuestran una mejora necesaria en tiempo de arranque o consumo de memoria y se cubren las limitaciones de compatibilidad y depuración.

### API y arquitectura

17. Implementar HTTP/JSON con Quarkus REST (`quarkus-rest-jackson`) y documentar contratos mediante SmallRye OpenAPI (`quarkus-smallrye-openapi`), manteniendo compatibilidad con OpenAPI 3.0.3 y el contrato de `docs/ENDPOINTS.md`.
18. Mantener recursos REST delgados y separar API, servicio de aplicación, dominio, persistencia y seguridad. Usar inyección CDI de Quarkus y límites transaccionales explícitos; no colocar reglas de negocio ni acceso a datos en los recursos HTTP.
19. Validar entradas con Jakarta Bean Validation (`quarkus-hibernate-validator`) y transformar errores al formato `application/problem+json` definido por el contrato. No exponer trazas, reglas internas sensibles ni datos personales en errores.
<!-- 20. Implementar autenticación y autorización con OIDC/JWT (`quarkus-oidc`) integrado a un proveedor de identidad aprobado. Validar permisos en servidor, separar el rol de analítica y no implementar criptografía, emisión de tokens o validación JWT propia. -->
21. Aplicar idempotencia del lado servidor para creación y envío de pasos de onboarding, conforme al encabezado `Idempotency-Key` del contrato. El registro de clave, usuario, operación y resultado debe ser atómico con la operación de negocio para evitar efectos financieros o eventos duplicados.

### Persistencia e integraciones

22. Usar PostgreSQL como base relacional para usuarios, estado de onboarding y eventos transaccionales. Seleccionar una versión soportada por el proveedor de despliegue y por las extensiones de Quarkus aprobadas; no depender de características exclusivas de una versión sin justificarlo.
23. Usar Hibernate ORM con Panache (`quarkus-hibernate-orm-panache`) solo como conveniencia de persistencia, sin acoplar entidades directamente a los DTO o al contrato HTTP. Usar el driver JDBC de PostgreSQL administrado por el BOM.
24. Gestionar cambios de esquema con Flyway (`quarkus-flyway`) y migraciones versionadas, revisables e inmutables una vez desplegadas. No usar actualización automática del esquema en producción.
25. Ejecutar pasos de onboarding y sus cambios de estado dentro de transacciones consistentes. Publicar eventos analíticos mediante un mecanismo durable o una tabla outbox cuando la pérdida o duplicación del evento afecte las métricas; no depender de una llamada remota no transaccional dentro de la actualización de estado.
<!-- 26. No agregar Redis, Kafka ni otro componente distribuido por anticipado. Incorporarlo solo cuando exista un requisito medible de caché, coordinación distribuida o mensajería y se hayan definido operación, tolerancia a fallas y consistencia. -->

### Pruebas, seguridad y operación

27. Usar JUnit 5 con `quarkus-junit5`, pruebas HTTP con REST Assured (`rest-assured`) y Testcontainers para validar PostgreSQL y dependencias reales en integración. Las pruebas de contrato deben comprobar códigos HTTP, esquemas, errores de validación, autorización e idempotencia.
28. Mantener la meta de cobertura de al menos 90% para el código modificado con JaCoCo; complementar la cobertura con pruebas de comportamiento y no excluir lógica de negocio para alcanzar artificialmente el porcentaje.
29. Exponer probes de disponibilidad con SmallRye Health (`quarkus-smallrye-health`) y métricas/trazas con Micrometer y OpenTelemetry usando estándares compatibles con la plataforma de observabilidad. Usar logs estructurados con identificadores de correlación; nunca registrar tokens, documentos KYC, respuestas completas de onboarding ni secretos.
30. Obtener secretos y configuración sensible desde el gestor de secretos de la plataforma o variables de entorno inyectadas en runtime. No incluir secretos reales en código, imágenes, archivos de configuración versionados ni registros.
31. Ejecutar en CI compilación, pruebas, análisis estático, escaneo de dependencias y construcción de imagen reproducible. Mantener CodeQL y Dependency Review habilitados; revisar actualizaciones del BOM y dependencias con una política de actualización y escaneo de vulnerabilidades.
32. Aplicar controles de acceso a métricas analíticas. Los datos personales y KYC deben minimizarse, protegerse y retenerse según las políticas aprobadas de privacidad y cumplimiento.

## Línea base tecnológica: Frontend Angular

Esta línea base aplica al cliente web del onboarding. Usar versiones estables con soporte vigente y confirmar la matriz oficial de compatibilidad de Angular, Node.js y TypeScript al iniciar el proyecto; no adoptar versiones preliminares en producción.

### Plataforma y arquitectura

33. Usar Angular en su versión estable con soporte vigente, Angular CLI y TypeScript en modo estricto. Mantener versiones reproducibles mediante el lockfile del gestor de paquetes y usar `npm ci` en CI cuando el proyecto utilice npm.
34. Usar componentes standalone y configuración por providers para código nuevo. Organizar la aplicación por dominios funcionales y mantener componentes de presentación separados de servicios de API, estado de sesión y lógica de negocio.
35. Usar Angular Router para navegación y carga diferida de rutas funcionales. Los guards pueden mejorar la experiencia de navegación, pero no sustituyen la autenticación ni la autorización que debe aplicar el backend.
36. Usar Signals para estado local y derivado cuando simplifiquen el flujo; usar RxJS para flujos asíncronos, eventos y composición de llamadas HTTP. Incorporar una librería global de estado solo si la complejidad y el estado compartido lo justifican.
37. Mantener los contratos alineados con `docs/ENDPOINTS.md`. Generar tipos y clientes desde OpenAPI cuando sea viable y verificar su actualización en CI; evitar duplicar manualmente los modelos del API.

### Onboarding, interfaz y accesibilidad

38. Implementar formularios con Reactive Forms tipados y validaciones del lado cliente para retroalimentación inmediata; el servidor sigue siendo la autoridad de validación. Mapear `application/problem+json` y `ValidationIssue` a errores asociados al campo y mensajes accionables.
39. Tratar el estado devuelto por el servidor como fuente de verdad para el paso actual, pasos completados y activación de la wallet. Manejar explícitamente inicio, reanudación, carga, envío, validación fallida, expiración de sesión, cierre y finalización.
40. Mantener accesibilidad conforme a WCAG 2.2 nivel AA: HTML semántico, navegación completa por teclado, foco visible, nombres y etiquetas accesibles, contraste suficiente y anuncios programáticos de errores y cambios de estado.
41. Diseñar primero para móvil y conservar contenido y funcionalidad al ampliar texto o aplicar zoom. Respetar `prefers-reduced-motion` y no comunicar estados únicamente mediante color o animación.
42. Usar el sistema de diseño aprobado por el producto. Centralizar tokens de diseño y mantener componentes reutilizables, responsivos y accesibles; evitar estilos globales que interfieran con la encapsulación de componentes.

### Seguridad e integración

43. Usar OIDC Authorization Code con PKCE para una SPA cuando corresponda, o preferir un Backend for Frontend (BFF) con cookies `HttpOnly`, `Secure` y `SameSite` si la arquitectura lo permite. No guardar tokens de acceso o refresh en `localStorage` o `sessionStorage`.
44. Aplicar interceptores HTTP solo para preocupaciones transversales, como correlación y manejo común de errores; evitar reintentos automáticos de operaciones mutables. Para inicio y envío de pasos, respetar `Idempotency-Key` y conservar la misma clave durante los reintentos de una operación.
45. Usar el escape y la sanitización por defecto de Angular. No usar `bypassSecurityTrust...` ni insertar HTML no confiable; si se usan cookies para autenticación, implementar protección CSRF y configurar una Content Security Policy compatible con la aplicación.
46. No incluir secretos en el bundle, archivos `environment` del cliente, URLs, logs ni telemetría. No registrar tokens, datos KYC ni respuestas completas; transmitir únicamente eventos analíticos aprobados y minimizados.

### Calidad y rendimiento

47. Mantener lint, formato, compilación de producción y verificación de tipos en CI. Probar lógica y componentes con el runner de pruebas soportado por la versión de Angular adoptada y `TestBed`; probar recorridos críticos de onboarding con Playwright. Mantener la meta de cobertura de código modificado establecida en estas reglas.
48. Probar validaciones, errores de red, reintentos, idempotencia, permisos, expiración de sesión, navegación por teclado y visualización en móvil. Las pruebas automatizadas de accesibilidad complementan, pero no reemplazan, la revisión manual con teclado y lector de pantalla.
<!-- 49. Usar carga diferida y presupuestos de bundle del Angular CLI para limitar el código inicial. Medir Core Web Vitals en condiciones representativas y apuntar en el percentil 75 a LCP ≤ 2.5 s, INP ≤ 200 ms y CLS ≤ 0.1; optimizar según mediciones. -->
50. Revisar dependencias directas y transitivas con escaneo de vulnerabilidades y actualizaciones controladas. No ignorar alertas de seguridad sin evaluación y justificación documentadas.

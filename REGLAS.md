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
12. Sin números o strings "mágicos" sueltos en el código (por ejemplo `3600`
    para la expiración del token); usar constantes con nombre.

## Línea base tecnológica: Java y Quarkus

Estas especificaciones son la propuesta para implementar la API de onboarding descrita en `docs/ENDPOINTS.md`. Las versiones finales deben verificarse contra la matriz oficial de compatibilidad de Quarkus, el proveedor de Java y las dependencias aprobadas al iniciar el proyecto.

### Plataforma

13. Usar Java 25 LTS como versión objetivo para un servicio nuevo, siempre que Quarkus, el runtime de despliegue y todas las dependencias necesarias estén certificados para esa versión. Si existe una incompatibilidad, usar Java 21 LTS y registrar la razón y el criterio para reevaluar la actualización.
14. Usar Quarkus 3.x en una versión estable con mantenimiento vigente. Gestionar las versiones de Quarkus y sus extensiones mediante el BOM oficial de Quarkus; no fijar versiones individuales de extensiones administradas por ese BOM.
15. Usar Maven con Maven Wrapper (`./mvnw` o `mvnw.cmd`) para que CI y desarrollo local ejecuten la misma versión. Mantener las versiones del plugin y del BOM en una ubicación centralizada.
16. Desarrollar y desplegar inicialmente en modo JVM dentro de una imagen de contenedor no privilegiada. Considerar compilación nativa únicamente si pruebas representativas demuestran una mejora necesaria en tiempo de arranque o consumo de memoria y se cubren las limitaciones de compatibilidad y depuración.

### API y arquitectura

17. Implementar HTTP/JSON con Quarkus REST (`quarkus-rest-jackson`) y documentar contratos mediante SmallRye OpenAPI (`quarkus-smallrye-openapi`), manteniendo compatibilidad con OpenAPI 3.0.3 y el contrato de `docs/ENDPOINTS.md`.
18. Mantener recursos REST delgados y separar API, servicio de aplicación, dominio, persistencia y seguridad. Usar inyección CDI de Quarkus y límites transaccionales explícitos; no colocar reglas de negocio ni acceso a datos en los recursos HTTP.
19. Validar entradas con Jakarta Bean Validation (`quarkus-hibernate-validator`) y transformar errores al formato `application/problem+json` definido por el contrato. No exponer trazas, reglas internas sensibles ni datos personales en errores.
20. Implementar autenticación y autorización con OIDC/JWT (`quarkus-oidc`) integrado a un proveedor de identidad aprobado. Validar permisos en servidor, separar el rol de analítica y no implementar criptografía, emisión de tokens o validación JWT propia.
21. Aplicar idempotencia del lado servidor para creación y envío de pasos de onboarding, conforme al encabezado `Idempotency-Key` del contrato. El registro de clave, usuario, operación y resultado debe ser atómico con la operación de negocio para evitar efectos financieros o eventos duplicados.

### Persistencia e integraciones

22. Usar PostgreSQL como base relacional para usuarios, estado de onboarding y eventos transaccionales. Seleccionar una versión soportada por el proveedor de despliegue y por las extensiones de Quarkus aprobadas; no depender de características exclusivas de una versión sin justificarlo.
23. Usar Hibernate ORM con Panache (`quarkus-hibernate-orm-panache`) solo como conveniencia de persistencia, sin acoplar entidades directamente a los DTO o al contrato HTTP. Usar el driver JDBC de PostgreSQL administrado por el BOM.
24. Gestionar cambios de esquema con Flyway (`quarkus-flyway`) y migraciones versionadas, revisables e inmutables una vez desplegadas. No usar actualización automática del esquema en producción.
25. Ejecutar pasos de onboarding y sus cambios de estado dentro de transacciones consistentes. Publicar eventos analíticos mediante un mecanismo durable o una tabla outbox cuando la pérdida o duplicación del evento afecte las métricas; no depender de una llamada remota no transaccional dentro de la actualización de estado.
26. No agregar Redis, Kafka ni otro componente distribuido por anticipado. Incorporarlo solo cuando exista un requisito medible de caché, coordinación distribuida o mensajería y se hayan definido operación, tolerancia a fallas y consistencia.

### Pruebas, seguridad y operación

27. Usar JUnit 5 con `quarkus-junit5`, pruebas HTTP con REST Assured (`rest-assured`) y Testcontainers para validar PostgreSQL y dependencias reales en integración. Las pruebas de contrato deben comprobar códigos HTTP, esquemas, errores de validación, autorización e idempotencia.
28. Mantener la meta de cobertura de al menos 90% para el código modificado con JaCoCo; complementar la cobertura con pruebas de comportamiento y no excluir lógica de negocio para alcanzar artificialmente el porcentaje.
29. Exponer probes de disponibilidad con SmallRye Health (`quarkus-smallrye-health`) y métricas/trazas con Micrometer y OpenTelemetry usando estándares compatibles con la plataforma de observabilidad. Usar logs estructurados con identificadores de correlación; nunca registrar tokens, documentos KYC, respuestas completas de onboarding ni secretos.
30. Obtener secretos y configuración sensible desde el gestor de secretos de la plataforma o variables de entorno inyectadas en runtime. No incluir secretos reales en código, imágenes, archivos de configuración versionados ni registros.
31. Ejecutar en CI compilación, pruebas, análisis estático, escaneo de dependencias y construcción de imagen reproducible. Mantener CodeQL y Dependency Review habilitados; revisar actualizaciones del BOM y dependencias con una política de actualización y escaneo de vulnerabilidades.
32. Limitar permisos del contenedor y del servicio a los necesarios, habilitar TLS en los límites de red y aplicar controles de acceso a métricas analíticas. Los datos personales y KYC deben minimizarse, protegerse y retenerse según las políticas aprobadas de privacidad y cumplimiento.


## Tecnologías

13. 
# Reglas de Seguridad — Onboarding Wallet (Java + Quarkus)

## 1) Propósito y alcance

Estas reglas definen la línea base de seguridad para la aplicación de onboarding wallet implementada con Java + Quarkus.

Objetivo: reducir riesgo de fraude, fuga de datos, suplantación, abuso de APIs y fallas de configuración.

> Nota: no existe mitigación absoluta de “cualquier” ataque. Estas reglas reducen de forma sustancial la superficie de ataque y mejoran detección/respuesta.

---

## 2) Principios obligatorios

1. **Secure by default**: toda funcionalidad nueva nace cerrada, autenticada y validada.
2. **Least privilege**: usuarios, servicios, tokens y cuentas técnicas con permisos mínimos.
3. **Defense in depth**: controles en API, aplicación, datos, red y operación.
4. **Fail securely**: ante error, no exponer datos internos ni degradar controles.
5. **Traceability**: toda operación sensible debe ser auditable con correlación.

---

## 3) Reglas de autenticación y autorización

1. Usar OIDC/JWT de proveedor confiable; **no** implementar firma/validación JWT propia.
2. Validar `iss`, `aud`, `exp`, `nbf`, `iat`, `sub` y tolerancia de reloj acotada.
3. Token de acceso de corta vida; refresh token rotatorio y revocable.
4. Requerir MFA para acciones críticas (alta de cuenta, cambio de datos KYC, operaciones sensibles).
5. Aplicar control de acceso por permisos/roles en backend (nunca confiar en frontend).
6. Bloquear elevación de privilegios por manipulación de claims o parámetros.
7. Cerrar sesión y revocar sesiones ante eventos de riesgo (password reset, compromiso, fraude).

---

## 4) Reglas de entrada/salida y contrato API

1. Toda entrada se valida con Bean Validation y reglas de negocio explícitas.
2. Rechazar payloads inesperados, campos extra y formatos inválidos (`400`/`422`).
3. Limitar tamaño de request/response y número de intentos por ventana de tiempo.
4. Sanitizar y normalizar entradas antes de persistir o procesar.
5. No reflejar entrada del usuario en mensajes de error.
6. Errores en formato controlado (`problem+json`) sin stacktrace, clase Java ni SQL.
7. Implementar idempotencia (`Idempotency-Key`) en operaciones críticas para evitar duplicados.

---

## 5) Reglas de protección contra ataques comunes (OWASP)

1. **Injection (SQL/NoSQL/Command):** usar consultas parametrizadas y evitar concatenación dinámica.
2. **Broken Access Control:** validar propiedad de recurso (tenant/usuario) en cada operación.
3. **Cryptographic Failures:** cifrado fuerte en tránsito y reposo; gestión segura de claves.
4. **Security Misconfiguration:** hardening de Quarkus, headers HTTP y perfiles por entorno.
5. **Vulnerable Components:** escaneo SCA continuo y actualización de dependencias con SLA.
6. **Identification & Authentication Failures:** anti brute-force, lockout progresivo y monitoreo de intentos.
7. **Software & Data Integrity:** dependencias firmadas/confiables y pipeline con verificaciones.
8. **Logging & Monitoring Failures:** alertas de seguridad accionables y retención auditada.
9. **SSRF/CSRF/CORS:** listas permitidas de destinos salientes, CORS restrictivo y tokens CSRF si aplica.

---

## 6) Reglas de secretos y criptografía

1. Secretos solo en gestor seguro o variables de entorno protegidas.
2. Prohibido hardcodear secretos en código, pruebas, imágenes o repositorio.
3. Rotación periódica de secretos y llaves; plan de rotación de emergencia.
4. Hash de contraseñas con algoritmo resistente (Argon2id o bcrypt con costo adecuado).
5. Nunca almacenar contraseñas, PIN o documentos sensibles en texto plano.
6. Cifrar datos sensibles en reposo (KYC/PII) con claves separadas por entorno.

---

## 7) Reglas de datos personales y KYC

1. Minimización: almacenar solo datos estrictamente necesarios para onboarding.
2. Clasificación de datos: público, interno, sensible, regulado.
3. Enmascarar PII en logs, trazas, métricas y herramientas de soporte.
4. Definir políticas de retención y borrado seguro de datos KYC.
5. Restringir acceso a PII por necesidad operativa y perfil aprobado.

---

## 8) Reglas de infraestructura y despliegue

1. TLS obligatorio extremo a extremo; deshabilitar protocolos/cifrados débiles.
2. Contenedores no privilegiados, filesystem de solo lectura cuando sea viable.
3. Imágenes mínimas y actualizadas; escaneo de vulnerabilidades en CI/CD.
4. Separar ambientes (dev/qa/prod) con secretos y credenciales distintas.
5. Bloquear puertos y rutas no necesarios; acceso administrativo con MFA.
6. Política de backups cifrados y pruebas periódicas de restauración.

---

## 9) Reglas de observabilidad, detección y respuesta

1. Registrar eventos de seguridad: login, fallo auth, cambio de rol, rechazo KYC, bloqueo.
2. Incluir `correlation-id` en toda transacción de onboarding.
3. Alertar por patrones de abuso: brute force, picos de errores, decisiones KYC anómalas.
4. Definir runbooks de incidentes: contención, erradicación, recuperación y postmortem.
5. Conservar evidencia técnica con cadena de custodia para auditoría.

---

## 10) Reglas de pruebas de seguridad (mínimo por release)

1. SAST y SCA obligatorios en CI con umbrales de severidad definidos.
2. DAST básico sobre endpoints críticos de onboarding.
3. Pruebas de autorización horizontal/vertical.
4. Pruebas de rate limiting, lockout e idempotencia.
5. Pruebas de no exposición de secretos/PII en respuestas y logs.
6. Revisión manual de amenazas para cambios de arquitectura.

---

## 11) Reglas de gobierno y excepciones

1. Toda excepción de seguridad requiere:
   - riesgo documentado,
   - compensating controls,
   - responsable y fecha de vencimiento.
2. Hallazgos `HIGH/CRITICAL` no pueden pasar a producción sin aprobación formal.
3. Revisar estas reglas al menos trimestralmente o ante cambios regulatorios/arquitectónicos.

---

## 12) Checklist operativo rápido (antes de liberar)

- [ ] Endpoints críticos autenticados y autorizados en backend.
- [ ] Validación de inputs y límites de tamaño activos.
- [ ] CORS y headers de seguridad configurados de forma restrictiva.
- [ ] Secretos fuera del código y rotación vigente.
- [ ] Dependencias sin vulnerabilidades críticas abiertas.
- [ ] Logs sin PII/secretos y con correlación habilitada.
- [ ] Evidencia de pruebas de seguridad adjunta al release.


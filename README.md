# wallet_team7

Estructura inicial para el proyecto de wallet del hackathon.

## Estructura

- `src/`: codigo de la aplicacion.
- `agents/`: agentes del proyecto.
- `skills/`: habilidades o instrucciones reutilizables.
- `infra/`: infraestructura y configuracion de despliegue.
- `tests/`: pruebas automatizadas.
- `docs/`: documentacion del proyecto.
- `demo/`: demostracion web inicial.
- `evidence.md`: registro de evidencias y validaciones.
- `.env.example`: plantilla de variables de entorno.
- `requirements.txt`: dependencias Python.
- `docker-compose.yml`: ejecucion local de la demo.

## Ejecutar la demo

Requiere Docker Compose. Desde la raiz del repositorio, ejecuta:

```sh
docker compose up
```

Abre <http://localhost:8080> para ver la pagina inicial. Esta demo es solo un punto de partida; no implementa operaciones financieras.

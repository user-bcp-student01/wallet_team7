"""Agente Product Owner para definir requisitos de producto verificables."""

from pathlib import Path

from crewai import Agent, Task
from crew.llm_config import llm

KEY = "po"
LABEL = "Product Owner"
SPEC_FILE = str(Path(__file__).resolve().parent.parent / "product_spec.md")
EXTRACT_CODE = False

INSTRUCTIONS = """Actúa como Product Owner de wallet_team7. Define qué valor debe entregar el
producto y cómo se verificará. Revisa la necesidad y el contexto proporcionados; distingue
requisitos confirmados, restricciones, supuestos, decisiones pendientes y preguntas abiertas.

Guarda la especificación de producto como product_spec.md directamente en la raíz del
proyecto wallet_team7, no dentro de agents/ ni fuera de esa carpeta. Si se solicita
materializarla mediante OpenSpec, usa la ruta openspec/changes/<CHANGE_NAME>/specs/ dentro
de esa misma raíz.

Redacta historias centradas en el usuario y criterios de aceptación observables, comprobables y
trazables. Define las métricas con población, periodo, unidad y cálculo solo cuando la fuente
proporcione esos datos; si faltan, decláralos como pendientes. Mantén explícitos el alcance,
dependencias y riesgos de producto.

No inventes necesidades, reglas de negocio, requisitos regulatorios, métricas, datos, integraciones
ni resultados de validación. No diseñes arquitectura, elijas tecnologías ni implementes código.
Preserva los contratos y decisiones aprobados; cualquier cambio propuesto requiere decisión humana.
No conviertas hipótesis en requisitos aprobados ni presentes una recomendación como aprobación.
Señala las preguntas que bloqueen la especificación y requiere revisión humana antes del handoff
a Arquitectura.

Entrega una especificación con resumen y valor para el usuario; alcance incluido y excluido;
historia o requisitos funcionales; criterios de aceptación; restricciones y supuestos; decisiones
pendientes y preguntas abiertas; riesgos, dependencias y plan de validación; y fuentes revisadas
y estado de aprobación humana."""

agent = Agent(
    role="Product Owner",
    goal="Convertir necesidades confirmadas en requisitos de producto claros, trazables y verificables.",
    backstory=(
        "Eres el Product Owner de wallet_team7. Proteges el valor para el usuario y el alcance "
        "aprobado, haces explícita la incertidumbre y no sustituyes las decisiones ni aprobaciones "
        "humanas."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
)


def build_task(feature: dict) -> Task:
    return Task(
        description=(
            INSTRUCTIONS
            + "\n\nNecesidad o feature: "
            + str(feature.get("title", ""))
            + "\nDescripción:\n"
            + str(feature.get("description", ""))
            + "\nCriterios de aceptación existentes:\n"
            + str(feature.get("acceptance_criteria", []))
        ),
        expected_output=(
            "Una especificación de producto en español que contenga resumen y valor; alcance "
            "incluido y excluido; historia o requisitos; criterios de aceptación verificables; "
            "restricciones y supuestos; decisiones pendientes y preguntas abiertas; riesgos, "
            "dependencias y plan de validación; fuentes revisadas y estado de aprobación humana. "
            "No afirmes que hubo aprobación humana si no se proporcionó evidencia."
        ),
        agent=agent,
    )

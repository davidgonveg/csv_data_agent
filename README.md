# CSV Data Agent

Sistema de análisis de datos conversacional que permite hacer preguntas en lenguaje natural sobre archivos CSV y obtener respuestas mediante generación y ejecución automática de código Pandas.

---

## 🚀 Estado del Proyecto: v1.0.0 (Funcional)

El proyecto se encuentra en una versión **estable y funcional**.

### ✅ Implementado (Ready)
*   **Lectura Inteligente**: Carga de CSVs con detección automática de encoding y separadores.
*   **Análisis de Esquema**: Extracción automática de metadatos para "entender" los datos antes de consultarlos.
*   **Motor LLM**: Integración con **Groq (Llama 3.3 70B)** para generación rápida de código.
*   **Ejecución Segura**: Sandbox local que ejecuta Pandas/Numpy/Plotly bloqueando acceso al sistema (os, sys).
*   **Interfaz Gráfica**: App completa en **Streamlit** con chat, historial y carga de archivos.
*   **Visualización**: Generación de gráficos interactivos con **Plotly**.
*   **Documentación**: Guías técnicas y de uso completas en `/docs`.

### 🚧 Pendiente / Mejoras Futuras
*   Soporte para múltiples archivos simultáneos.
*   Modo "auto-corrección" si el código generado falla a la primera.
*   Exportación de reportes a PDF/HTML.

---

## Objetivo

Construir un agente que:

1. Cargue cualquier archivo CSV
2. Entienda su estructura (columnas, tipos, datos)
3. Reciba preguntas en lenguaje natural del usuario
4. Genere código Pandas para responder la pregunta
5. Ejecute el código de forma segura
6. Devuelva el resultado (número, tabla, gráfico)
7. Mantenga contexto conversacional para análisis iterativo

**Caso de uso principal:** Análisis de datos de sistemas antidron (timestamps, señales RF, detecciones) sin necesidad de escribir código manualmente.

---

## Stack tecnológico

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| Lenguaje | Python 3.10+ | Ecosistema de datos maduro |
| Datos | Pandas | Estándar para manipulación tabular |
| LLM | Groq API (Llama 3.3 70B) | Gratis, rápido, buena generación de código |
| Interfaz | Streamlit | Prototipado rápido, visual, sin frontend |
| Gráficos | Matplotlib/Plotly | Integración nativa con Streamlit |
| Entorno | venv | Sin dependencias externas complejas |

---

## Documentación
- [Guía de Uso (Walkthrough)](docs/walkthrough.md)
- [Arquitectura Técnica](docs/architecture.md)
- [Referencia API](docs/api_reference.md)
- [Estrategia de Prompts](docs/prompts.md)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Upload CSV  │  │ Chat Input  │  │ Results Display     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CORE ENGINE                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ CSV Loader  │  │ Schema      │  │ Conversation        │  │
│  │             │──▶ Analyzer    │──▶ Manager             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      LLM LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Prompt      │  │ Claude API  │  │ Response Parser     │  │
│  │ Builder     │──▶ Client      │──▶                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTION LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Code        │  │ Safe        │  │ Result Formatter    │  │
│  │ Extractor   │──▶ Executor    │──▶                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Estructura de archivos

```
csv-agent/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── csv_loader.py        # Carga y validación de CSV
│   ├── schema_analyzer.py   # Análisis de estructura del DataFrame
│   ├── prompt_builder.py    # Construcción de prompts para el LLM
│   ├── llm_client.py        # Cliente de Claude API
│   ├── code_executor.py     # Ejecución segura de código
│   ├── result_formatter.py  # Formateo de resultados
│   └── conversation.py      # Gestión del historial
├── app.py                   # Aplicación Streamlit
├── tests/
│   ├── __init__.py
│   ├── test_core_logic.py   # Tests de lógica interna
│   └── sample_data/
│       └── test_antidron.csv
└── docs/
    ├── walkthrough.md       # Guía de uso
    ├── architecture.md      # Arquitectura técnica
    ├── prompts.md           # Estrategia de prompting
    └── api_reference.md     # Documentación de módulos
```

---

## Guía de uso rápida

1.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configurar API Key**:
    Copia `.env.example` a `.env` y añade tu `GROQ_API_KEY`.

3.  **Ejecutar**:
    ```bash
    python -m streamlit run app.py
    ```

---

## Licencia

MIT

---

## Autor

David González
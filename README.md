# CSV Data Agent

Sistema de análisis de datos conversacional que permite hacer preguntas en lenguaje natural sobre archivos CSV y obtener respuestas mediante generación y ejecución automática de código Pandas.

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
| LLM | Groq API (Llama 3.1 70B) | Gratis, rápido, buena generación de código |
| Interfaz | Streamlit | Prototipado rápido, visual, sin frontend |
| Gráficos | Matplotlib/Plotly | Integración nativa con Streamlit |
| Entorno | venv | Sin dependencias externas complejas |

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
│   ├── test_csv_loader.py
│   ├── test_schema_analyzer.py
│   ├── test_code_executor.py
│   └── sample_data/
│       └── test_antidron.csv
└── docs/
    └── prompts.md           # Documentación de prompts usados
```

---

## Fases del proyecto

### Fase 1: Setup y estructura base
Preparar el entorno de desarrollo y la estructura del proyecto.

### Fase 2: Carga y análisis de CSV
Implementar la carga de archivos y extracción de metadatos.

### Fase 3: Integración con LLM
Conectar con Claude API y diseñar los prompts.

### Fase 4: Ejecución de código
Implementar la ejecución segura del código generado.

### Fase 5: Interfaz de usuario
Crear la aplicación Streamlit.

### Fase 6: Mejoras y robustez
Añadir funcionalidades avanzadas y pulir el sistema.

---

## Tareas detalladas

### Fase 1: Setup y estructura base

#### Tarea 1.1: Crear estructura de directorios
```bash
mkdir -p csv-agent/{src,tests/sample_data,docs}
touch csv-agent/src/__init__.py
touch csv-agent/tests/__init__.py
```
**Criterio de completitud:** Estructura de carpetas creada.

#### Tarea 1.2: Crear entorno virtual
```bash
cd csv-agent
python -m venv venv
source venv/bin/activate  # Linux/Mac
```
**Criterio de completitud:** Entorno activado, `which python` apunta al venv.

#### Tarea 1.3: Crear requirements.txt
```
pandas==2.1.4
groq==0.5.0
streamlit==1.31.0
python-dotenv==1.0.0
matplotlib==3.8.2
plotly==5.18.0
```
**Criterio de completitud:** `pip install -r requirements.txt` ejecuta sin errores.

#### Tarea 1.4: Crear .env.example
```
GROQ_API_KEY=tu_api_key_aqui
```
**Criterio de completitud:** Archivo creado con placeholder.

#### Tarea 1.5: Crear .gitignore
```
venv/
__pycache__/
.env
*.pyc
.DS_Store
```
**Criterio de completitud:** Archivo creado.

#### Tarea 1.6: Crear CSV de prueba
Crear `tests/sample_data/test_antidron.csv` con datos simulados:
```csv
timestamp,frequency_mhz,rssi_dbm,protocol,drone_id,latitude,longitude
2024-01-15 10:30:00,2437.5,-65,WiFi,DJI_001,40.4168,-3.7038
2024-01-15 10:30:05,2437.5,-68,WiFi,DJI_001,40.4169,-3.7039
...
```
Incluir al menos 100 filas con variación en todos los campos.
**Criterio de completitud:** CSV creado con datos realistas y variados.

---

### Fase 2: Carga y análisis de CSV

#### Tarea 2.1: Implementar csv_loader.py

**Archivo:** `src/csv_loader.py`

**Funcionalidad:**
- Función `load_csv(file_path: str | BytesIO) -> pd.DataFrame`
- Detectar encoding automáticamente (utf-8, latin-1, cp1252)
- Detectar separador automáticamente (coma, punto y coma, tab)
- Parsear columnas de fecha automáticamente
- Manejar errores de carga con mensajes claros

**Interfaz:**
```python
def load_csv(file) -> pd.DataFrame:
    """
    Carga un CSV desde path o BytesIO.
    
    Args:
        file: Path al archivo o BytesIO desde upload
        
    Returns:
        DataFrame con datos cargados
        
    Raises:
        ValueError: Si el archivo no es válido
    """
    pass
```

**Criterio de completitud:** 
- Carga correctamente el CSV de prueba
- Detecta automáticamente el formato de fecha
- Test unitario pasa

#### Tarea 2.2: Implementar schema_analyzer.py

**Archivo:** `src/schema_analyzer.py`

**Funcionalidad:**
- Función `analyze_schema(df: pd.DataFrame) -> dict`
- Extraer: nombre columnas, tipos, valores únicos (si < 20), min/max, nulls
- Función `get_sample_rows(df: pd.DataFrame, n: int = 5) -> str`
- Función `generate_schema_description(df: pd.DataFrame) -> str` que genera texto legible

**Interfaz:**
```python
def analyze_schema(df: pd.DataFrame) -> dict:
    """
    Analiza la estructura del DataFrame.
    
    Returns:
        {
            "columns": [
                {
                    "name": "timestamp",
                    "dtype": "datetime64[ns]",
                    "null_count": 0,
                    "unique_count": 1000,
                    "sample_values": ["2024-01-15 10:30:00", ...],
                    "min": "2024-01-15 10:30:00",
                    "max": "2024-01-16 18:45:00"
                },
                ...
            ],
            "row_count": 1000,
            "memory_usage_mb": 0.5
        }
    """
    pass

def generate_schema_description(df: pd.DataFrame) -> str:
    """
    Genera descripción en texto del esquema para el LLM.
    
    Returns:
        String formateado describiendo el DataFrame
    """
    pass
```

**Criterio de completitud:**
- Genera esquema correcto del CSV de prueba
- La descripción es clara y concisa
- Test unitario pasa

---

### Fase 3: Integración con LLM

#### Tarea 3.1: Implementar llm_client.py

**Archivo:** `src/llm_client.py`

**Funcionalidad:**
- Clase `LLMClient` que encapsula la API de Groq
- Método `query(prompt: str, system: str = None) -> str`
- Modelo: `llama-3.1-70b-versatile`
- Manejo de rate limits con retry exponencial
- Logging de tokens usados

**Interfaz:**
```python
class LLMClient:
    def __init__(self, api_key: str = None, model: str = "llama-3.1-70b-versatile"):
        """Inicializa cliente. Si no hay key, lee de .env"""
        pass
    
    def query(self, prompt: str, system: str = None) -> str:
        """
        Envía query a Groq y devuelve respuesta.
        
        Args:
            prompt: Mensaje del usuario
            system: System prompt opcional
            
        Returns:
            Respuesta del modelo como string
        """
        pass
```

**Criterio de completitud:**
- Conecta con API de Groq correctamente
- Maneja errores de API gracefully
- Test manual con query simple funciona

#### Tarea 3.2: Implementar prompt_builder.py

**Archivo:** `src/prompt_builder.py`

**Funcionalidad:**
- Función `build_system_prompt(schema_description: str) -> str`
- Función `build_user_prompt(question: str, conversation_history: list = None) -> str`
- El system prompt debe instruir al LLM a:
  - Generar SOLO código Pandas válido
  - Usar la variable `df` que ya existe
  - Guardar resultado en variable `result`
  - No usar print(), solo asignar a `result`
  - Manejar fechas con pd.to_datetime si es necesario

**System prompt base:**
```python
SYSTEM_PROMPT_TEMPLATE = """
Eres un analista de datos experto. Tu tarea es generar código Pandas para responder preguntas sobre un DataFrame.

REGLAS ESTRICTAS:
1. Genera ÚNICAMENTE código Python válido
2. El DataFrame ya existe en la variable `df`
3. Guarda el resultado final en la variable `result`
4. NO uses print(), solo asigna a `result`
5. Para fechas, la columna timestamp ya es datetime
6. Si necesitas mostrar un gráfico, usa matplotlib y guarda la figura en `result_fig`
7. Responde SOLO con código, sin explicaciones

ESQUEMA DEL DATAFRAME:
{schema_description}

EJEMPLOS DE CÓDIGO VÁLIDO:

Pregunta: ¿Cuántas filas tiene el dataset?
Código:
result = len(df)

Pregunta: ¿Cuál es la media de rssi_dbm?
Código:
result = df['rssi_dbm'].mean()

Pregunta: ¿Cuántas detecciones hubo entre 10:00 y 12:00 del 15 de enero?
Código:
mask = (df['timestamp'] >= '2024-01-15 10:00:00') & (df['timestamp'] <= '2024-01-15 12:00:00')
result = df[mask].shape[0]
"""
```

**Interfaz:**
```python
def build_system_prompt(schema_description: str) -> str:
    """Construye system prompt con el esquema del DataFrame."""
    pass

def build_user_prompt(question: str, conversation_history: list = None) -> str:
    """Construye prompt del usuario, opcionalmente con historial."""
    pass
```

**Criterio de completitud:**
- System prompt incluye esquema correctamente
- Prompts generados son claros y concisos
- Test con preguntas de ejemplo genera código válido

#### Tarea 3.3: Crear docs/prompts.md
Documentar todos los prompts usados, su propósito, y ejemplos de entrada/salida.

**Criterio de completitud:** Documento completo y claro.

---

### Fase 4: Ejecución de código

#### Tarea 4.1: Implementar code_executor.py

**Archivo:** `src/code_executor.py`

**Funcionalidad:**
- Función `extract_code(llm_response: str) -> str` que extrae código de la respuesta
- Función `execute_code(code: str, df: pd.DataFrame) -> ExecutionResult`
- Ejecución en namespace aislado
- Timeout de ejecución (máximo 30 segundos)
- Captura de errores con traceback limpio

**Interfaz:**
```python
@dataclass
class ExecutionResult:
    success: bool
    result: any  # El valor de `result` después de ejecutar
    result_fig: any  # Figura matplotlib si existe
    error: str = None  # Mensaje de error si falló
    execution_time: float = 0.0

def extract_code(llm_response: str) -> str:
    """
    Extrae código Python de la respuesta del LLM.
    Maneja respuestas con o sin bloques ```python```.
    """
    pass

def execute_code(code: str, df: pd.DataFrame, timeout: int = 30) -> ExecutionResult:
    """
    Ejecuta código Pandas de forma segura.
    
    Args:
        code: Código Python a ejecutar
        df: DataFrame sobre el que operar
        timeout: Segundos máximos de ejecución
        
    Returns:
        ExecutionResult con el resultado o error
    """
    pass
```

**Consideraciones de seguridad:**
- NO permitir imports arbitrarios (solo pandas, numpy, matplotlib)
- NO permitir acceso a filesystem (open, os, sys)
- NO permitir ejecución de comandos (subprocess, os.system)
- Implementar lista blanca de funciones permitidas

**Criterio de completitud:**
- Ejecuta código válido correctamente
- Captura errores sin crashear
- Bloquea código malicioso
- Test unitario con casos válidos e inválidos pasa

#### Tarea 4.2: Implementar result_formatter.py

**Archivo:** `src/result_formatter.py`

**Funcionalidad:**
- Función `format_result(result: ExecutionResult) -> dict`
- Detectar tipo de resultado (número, string, DataFrame, figura)
- Formatear para display apropiado
- Truncar DataFrames grandes (max 100 filas en display)

**Interfaz:**
```python
def format_result(execution_result: ExecutionResult) -> dict:
    """
    Formatea resultado para mostrar en UI.
    
    Returns:
        {
            "type": "number" | "string" | "dataframe" | "figure" | "error",
            "value": <valor formateado>,
            "raw": <valor original>,
            "display_html": <HTML para renderizar si aplica>
        }
    """
    pass
```

**Criterio de completitud:**
- Formatea correctamente todos los tipos de resultado
- DataFrames grandes se truncan con mensaje indicando total
- Test unitario pasa

---

### Fase 5: Interfaz de usuario

#### Tarea 5.1: Implementar conversation.py

**Archivo:** `src/conversation.py`

**Funcionalidad:**
- Clase `ConversationManager` que mantiene historial
- Almacenar pares (pregunta, código, resultado)
- Método para generar contexto para el LLM
- Método para limpiar conversación

**Interfaz:**
```python
@dataclass
class ConversationTurn:
    question: str
    code: str
    result_summary: str
    timestamp: datetime

class ConversationManager:
    def __init__(self, max_history: int = 10):
        """Inicializa con historial máximo."""
        pass
    
    def add_turn(self, question: str, code: str, result_summary: str):
        """Añade un turno a la conversación."""
        pass
    
    def get_context_for_llm(self) -> str:
        """Genera resumen del historial para incluir en prompt."""
        pass
    
    def clear(self):
        """Limpia el historial."""
        pass
```

**Criterio de completitud:**
- Mantiene historial correctamente
- Genera contexto útil para el LLM
- Limita historial al máximo configurado

#### Tarea 5.2: Implementar app.py (estructura base)

**Archivo:** `app.py`

**Funcionalidad inicial:**
- Layout de Streamlit con sidebar y área principal
- Sidebar: upload de CSV, botón de limpiar
- Área principal: zona de chat
- Estado de sesión para df, conversación, resultados

**Estructura:**
```python
import streamlit as st

st.set_page_config(
    page_title="CSV Data Agent",
    page_icon="📊",
    layout="wide"
)

# Inicializar estado de sesión
if "df" not in st.session_state:
    st.session_state.df = None
if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationManager()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📁 Cargar datos")
    uploaded_file = st.file_uploader("Sube un CSV", type="csv")
    # ... resto de sidebar

# Área principal
st.title("📊 CSV Data Agent")

if st.session_state.df is None:
    st.info("👈 Sube un CSV para empezar")
else:
    # Mostrar chat
    # ...
```

**Criterio de completitud:**
- App arranca sin errores
- Se puede subir CSV
- Layout es claro y funcional

#### Tarea 5.3: Implementar flujo completo en app.py

**Funcionalidad:**
- Al subir CSV: cargar, analizar, mostrar preview
- Input de chat para preguntas
- Al enviar pregunta:
  1. Mostrar pregunta en chat
  2. Construir prompt con esquema y contexto
  3. Llamar a LLM
  4. Extraer y ejecutar código
  5. Mostrar resultado
  6. Guardar en historial
- Mostrar código generado (colapsable)
- Mostrar errores de forma clara

**Criterio de completitud:**
- Flujo completo funciona end-to-end
- Se pueden hacer múltiples preguntas seguidas
- Errores se muestran sin crashear la app

#### Tarea 5.4: Añadir visualización de esquema

**Funcionalidad:**
- En sidebar, mostrar resumen del CSV cargado:
  - Número de filas y columnas
  - Lista de columnas con tipos
  - Preview de primeras 5 filas
- Colapsable para no ocupar mucho espacio

**Criterio de completitud:**
- Información de esquema visible y clara
- No interfiere con el flujo principal

---

### Fase 6: Mejoras y robustez

#### Tarea 6.1: Añadir manejo de errores mejorado

**Funcionalidad:**
- Si el código falla, pedir al LLM que lo corrija
- Máximo 2 reintentos automáticos
- Mostrar al usuario qué se intentó

**Criterio de completitud:**
- Errores simples se auto-corrigen
- Usuario ve el proceso de corrección

#### Tarea 6.2: Añadir generación de gráficos

**Funcionalidad:**
- Detectar cuando la pregunta pide visualización
- Instrucciones en prompt para generar gráficos
- Renderizar figura en Streamlit

**Ejemplo de pregunta:** "Muéstrame un gráfico de la señal rssi a lo largo del tiempo"

**Criterio de completitud:**
- Gráficos se generan y muestran correctamente
- Al menos soporta: líneas, barras, histogramas

#### Tarea 6.3: Añadir sugerencias de análisis

**Funcionalidad:**
- Al cargar CSV, generar 3-5 preguntas sugeridas
- Basadas en el esquema detectado
- Clickeables para ejecutar directamente

**Criterio de completitud:**
- Sugerencias son relevantes al dataset
- Click ejecuta la pregunta

#### Tarea 6.4: Añadir export de resultados

**Funcionalidad:**
- Botón para exportar resultado actual como CSV
- Botón para exportar historial de conversación

**Criterio de completitud:**
- Exports funcionan correctamente
- Archivos son válidos

#### Tarea 6.5: Testing final

**Funcionalidad:**
- Probar con al menos 3 CSVs diferentes
- Documentar casos que funcionan y casos límite
- Escribir tests unitarios para componentes críticos

**Criterio de completitud:**
- Cobertura de tests > 70% en módulos core
- Documentación de limitaciones conocidas

---

## Guía de uso

### Instalación

```bash
# Clonar o crear directorio
cd csv-agent

# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env y añadir tu GROQ_API_KEY (conseguir en https://console.groq.com)
```

### Ejecución

```bash
streamlit run app.py
```

Abre http://localhost:8501 en el navegador.

### Ejemplo de uso

1. Sube tu archivo CSV
2. Revisa el esquema detectado en el sidebar
3. Haz preguntas en lenguaje natural:
   - "¿Cuántas detecciones hay en total?"
   - "¿Cuál es la media de rssi entre las 10:00 y las 12:00?"
   - "¿Qué protocolos aparecen y cuántas veces cada uno?"
   - "Muéstrame un gráfico de detecciones por hora"

---

## Limitaciones conocidas

- **Tamaño de CSV:** Datasets muy grandes (>1M filas) pueden ser lentos
- **Complejidad de queries:** Preguntas muy complejas pueden generar código incorrecto
- **Tipos de datos:** Algunos tipos exóticos pueden no parsearse bien
- **Gráficos:** Limitado a tipos básicos de matplotlib

---

## Posibles mejoras futuras

- [ ] Soporte para múltiples CSVs simultáneos
- [ ] Joins entre tablas
- [ ] Caché de queries frecuentes
- [ ] Modo offline con Ollama (Llama 3.1 8B local)
- [ ] Exportar análisis como notebook Jupyter
- [ ] Integración con bases de datos SQL

---

## Licencia

MIT

---

## Autor

David González

---

## Changelog

### v0.1.0 (en desarrollo)
- Setup inicial
- Carga de CSV con detección automática
- Integración con Claude API
- Ejecución segura de código
- Interfaz Streamlit básica
import streamlit as st
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Import our modules
from src.csv_loader import load_csv
from src.schema_analyzer import analyze_schema, generate_schema_description
from src.llm_client import LLMClient
from src.prompt_builder import build_system_prompt, build_user_prompt, build_correction_prompt
from src.code_executor import execute_code
from src.result_formatter import format_result
from src.conversation import ConversationManager
from src.report_generator import generate_html_report

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="CSV Data Agent",
    page_icon="🤖",
    layout="wide"
)

# --- Session State Initialization ---
if "df" not in st.session_state:
    st.session_state.df = None
if "schema_desc" not in st.session_state:
    st.session_state.schema_desc = None
if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationManager()
if "messages" not in st.session_state:
    st.session_state.messages = [] # For UI display
if "api_key" not in st.session_state:
    # Try validation from env first
    env_key = os.getenv("GROQ_API_KEY")
    st.session_state.api_key = env_key if env_key else None

# --- Sidebar ---
with st.sidebar:
    st.title("🤖 Configuración")
    
    # API Key Handling
    if not st.session_state.api_key:
        api_input = st.text_input("Groq API Key", type="password")
        if api_input:
            st.session_state.api_key = api_input
            st.rerun()
    else:
        st.success("API Key cargada")
        if st.button("Cambiar Key"):
            st.session_state.api_key = None
            st.rerun()

    st.divider()

    # File Upload
    st.header("1. Cargar Datos")
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv", "txt"])
    
    if uploaded_file is not None:
        try:
            # Only reload if it's a new file or df is not set
            # Simple check: assuming if user re-uploads, they want to reload
            if st.session_state.df is None or getattr(uploaded_file, 'name', '') != st.session_state.get('last_filename', ''):
                with st.spinner("Cargando y analizando..."):
                    df = load_csv(uploaded_file)
                    st.session_state.df = df
                    st.session_state.last_filename = uploaded_file.name
                    
                    # Generate Schema
                    st.session_state.schema_desc = generate_schema_description(df)
                    st.session_state.schema_dict = analyze_schema(df)
                    
                    # Reset conversation on new file
                    st.session_state.conversation.clear()
                    st.session_state.messages = []
                    
                st.success(f"Cargado: {len(df)} filas")

        except Exception as e:
            st.error(f"Error cargando archivo: {e}")

    # Schema Preview
    if st.session_state.df is not None:
        with st.expander("📊 Ver Estructura"):
            st.json(st.session_state.schema_dict)

    st.divider()
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpiar"):
            st.session_state.conversation.clear()
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.session_state.messages:
            report_html = generate_html_report(st.session_state.messages)
            st.download_button(
                label="📥 Reporte",
                data=report_html,
                file_name="analisis.html",
                mime="text/html"
            )

# --- Main Interface ---
st.title("CSV Data Agent 🕵️‍♀️")
st.caption("Pregunta lo que quieras sobre tus datos.")

if st.session_state.df is None:
    st.info("👈 Por favor, sube un archivo CSV en el menú lateral para comenzar.")
    
    # Show example if no file loaded
    st.markdown("""
    ### ¿Qué puedo hacer?
    1. Subir archivos CSV complejos.
    2. Preguntar en lenguaje natural.
    3. Obtener **respuestas directas** y **gráficos interactivos**.
    """)
else:
    # Check API Key before proceeding
    if not st.session_state.api_key:
        st.warning("⚠️ Por favor configura tu API Key de Groq en el sidebar.")
        st.stop()

    # Initialize LLM
    try:
        llm = LLMClient(api_key=st.session_state.api_key)
    except Exception as e:
        st.error(f"Error inicializando LLM: {e}")
        st.stop()

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.plotly_chart(msg["image"], use_container_width=True)
            if "dataframe" in msg:
                st.dataframe(msg["dataframe"])
            if "code" in msg:
                with st.expander("Ver código"):
                    st.code(msg["code"], language="python")

    # User Input
    if prompt := st.chat_input("Escribe tu pregunta sobre los datos..."):
        # 1. Show user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. Process
        with st.chat_message("assistant"):
            with st.spinner("Analizando y generando código..."):
                try:
                    # A. Build Prompt
                    system_msg = build_system_prompt(st.session_state.schema_desc)
                    
                    # --- RETRY LOOP START ---
                    max_retries = 2
                    current_try = 0
                    result_obj = None
                    final_code = ""
                    last_error = ""

                    while current_try <= max_retries:
                        if current_try == 0:
                            # First attempt
                            prompt_to_send = prompt
                        else:
                            # Correction attempt
                            st.warning(f"⚠️ Intento {current_try}: Hubo un error, reintentando...")
                            prompt_to_send = build_correction_prompt(prompt, last_error, final_code)
                        
                        # B. Get Code from LLM
                        code_response = llm.query(prompt_to_send, system=system_msg)
                        
                        # Clean code (remove markdown backticks if present)
                        code = code_response.replace("```python", "").replace("```", "").strip()
                        final_code = code # Store for potential correction prompt
                        
                        # C. Execute Code
                        result_obj = execute_code(code, st.session_state.df)
                        
                        if result_obj.success:
                            break # Success!
                        else:
                            last_error = result_obj.error
                            current_try += 1
                    
                    # --- RETRY LOOP END ---
                    
                    # D. Format Output
                    formatted = format_result(result_obj)
                    
                    # E. Display output
                    if formatted["type"] == "error":
                        st.error("Error en la ejecución (incluso tras reintentos):")
                        st.error(formatted["value"])
                        content_to_save = f"Error: {formatted['value']}"
                    
                    elif formatted["type"] == "plot":
                        st.plotly_chart(formatted["value"], use_container_width=True)
                        content_to_save = "Gráfico generado."
                        # Add to history with specific marker
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "Aquí tienes el gráfico:", 
                            "image": formatted["value"],
                            "code": final_code
                        })
                        # Avoid double appending
                        st.rerun() 
                        
                    elif formatted["type"] == "dataframe":
                        st.dataframe(formatted["value"])
                        content_to_save = formatted["summary"]
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "Aquí están los datos:", 
                            "dataframe": formatted["value"],
                            "code": final_code
                        })
                        st.rerun()

                    else:
                        st.markdown(formatted["value"])
                        content_to_save = str(formatted["value"])
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": formatted["value"],
                            "code": final_code
                        })
                        st.rerun()

                    # Add to context history
                    st.session_state.conversation.add_turn(prompt, final_code, content_to_save)

                except Exception as e:
                    st.error(f"Ocurrió un error inesperado: {e}")

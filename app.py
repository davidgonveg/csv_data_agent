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
from src.ssh_manager import SSHManager

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

    # File Selection Mode
    st.header("1. Cargar Datos")
    data_source = st.radio("Fuente de datos:", ["Subir Archivo", "Archivo Local", "Servidor Remoto"])

    uploaded_file = None
    local_file_path = None
    remote_file_path = None
    ssh_manager = None

    if data_source == "Subir Archivo":
        uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv", "txt"])
        
    elif data_source == "Archivo Local":
        local_file_path = st.text_input("Ruta absoluta del archivo (ej: C:/datos/data.csv)")
        
    elif data_source == "Servidor Remoto":
        try:
            ssh_manager = SSHManager()
            # Hardcoded remote path as requested
            remote_base_dir = "/home/innovacion/Documents/inteligencia_rf/datos"
            
            with st.spinner("Conectando al servidor..."):
                files = ssh_manager.list_files(remote_base_dir)
                
            if files:
                selected_filename = st.selectbox("Selecciona un archivo:", files)
                if selected_filename:
                    # Force forward slashes for Linux remote
                    remote_file_path = f"{remote_base_dir}/{selected_filename}"
                    print(f"DEBUG: Remote file selected: {remote_file_path}")
            else:
                st.warning("No se encontraron archivos CSV en el directorio remoto.")
                print("DEBUG: No CSV files found in remote directory.")
                
        except Exception as e:
            st.error(f"Error SSH: {e}")
            print(f"DEBUG: SSH Error: {e}")
            st.info("Verifica tus credenciales en el archivo .env")

        
    # Live Mode Configuration
    st.divider()
    live_mode = st.toggle("🔴 Modo LIVE", value=False)
    refresh_interval = 5
    if live_mode:
        refresh_interval = st.slider("Intervalo de actualización (seg)", 2, 60, 5)
        st.caption(f"Actualizando cada {refresh_interval}s si hay cambios.")
    
    # Store settings in session state
    st.session_state.live_mode = live_mode
    st.session_state.refresh_interval = refresh_interval
    
    # Logic to load data
    file_to_load = None
    current_mtime = None

    if data_source == "Subir Archivo" and uploaded_file is not None:
        file_to_load = uploaded_file
        # Pseudo mtime for uploaded file
        current_mtime = getattr(uploaded_file, 'size', 0) 
    
    elif data_source == "Archivo Local" and local_file_path:
        if os.path.exists(local_file_path):
            file_to_load = local_file_path
            current_mtime = os.path.getmtime(local_file_path)
        else:
            st.sidebar.error("El archivo no existe.")
            
    elif data_source == "Servidor Remoto" and remote_file_path and ssh_manager:
        # For remote, we load the file object
        # We delay validation to the loading block
        file_to_load = "REMOTE_placeholder" 

    if file_to_load:
        try:
             # Check if we need to reload
            should_reload = False
            
            # Identify source signature
            if data_source == "Servidor Remoto":
                 current_source_sig = f"ssh:{remote_file_path}"
                 # Check mtime via SSH if in live mode or if check logic needed
                 if live_mode:
                     try:
                         current_mtime = ssh_manager.get_mtime(remote_file_path)
                     except:
                         current_mtime = 0
                 else:
                     # If not live, maybe just trust it or force reload if different file
                     # Use 0 or current timestamp if we want to force load only on change
                     current_mtime = 0 
            else:
                current_source_sig = str(file_to_load.name) if hasattr(file_to_load, 'name') else str(file_to_load)
            
            last_source = st.session_state.get('last_source', '')
            last_mtime = st.session_state.get('last_mtime', 0)
            
            if st.session_state.df is None:
                should_reload = True
            elif current_source_sig != last_source:
                should_reload = True
            elif live_mode and current_mtime != last_mtime:
                should_reload = True
            
            if should_reload:
                print(f"DEBUG: Reloading data from {current_source_sig}")
                with st.spinner("Cargando y analizando..."):
                    
                    # Actual loading logic
                    if data_source == "Servidor Remoto":
                         # Download file object
                         print(f"DEBUG: Downloading remote file: {remote_file_path}")
                         file_obj = ssh_manager.get_file(remote_file_path)
                         df = load_csv(file_obj)
                         if ssh_manager: ssh_manager.close()
                    else:
                        print(f"DEBUG: Loading local file: {file_to_load}")
                        df = load_csv(file_to_load)
                        
                    st.session_state.df = df
                    st.session_state.last_source = current_source_sig
                    st.session_state.last_mtime = current_mtime
                    
                    # Generate Schema
                    st.session_state.schema_desc = generate_schema_description(df)
                    st.session_state.schema_dict = analyze_schema(df)
                    
                    # Clear conversation ONLY if source changed entirely, potentially? 
                    # If it's just an update (live mode), we might want to KEEP history but update last charts.
                    # But for now, let's keep the existing logic: Reset if new file, strict update if just refresh.
                    
                    if current_source_sig != last_source:
                        # Full reset for new file
                        st.session_state.conversation.clear()
                        st.session_state.messages = []
                    
                    elif live_mode:
                         # LIVE UPDATE LOGIC: Re-run assistant code blocks
                        st.toast("Datos actualizados. Refrescando gráficos...", icon="🔄")
                        
                        # Iterate backwards to find last assistant message with code? 
                        # Or update ALL charts? The user requested: "los gráficos que se han hecho y tal se actualicen"
                        # We should re-run all assistant messages that have code.
                        
                        updated_messages = []
                        for msg in st.session_state.messages:
                            if msg["role"] == "assistant" and "code" in msg and msg["code"]:
                                try:
                                    # Re-execute
                                    res_obj = execute_code(msg["code"], df)
                                    if res_obj.success:
                                        # Format again
                                        formatted = format_result(res_obj)
                                        # Update msg content
                                        if formatted["type"] == "plot":
                                            msg["image"] = formatted["value"]
                                            msg["content"] = "Gráfico actualizado:" # Update text too?
                                        elif formatted["type"] == "dataframe":
                                            msg["dataframe"] = formatted["value"]
                                            msg["content"] = f"Datos actualizados ({len(formatted['value'])} filas):"
                                        else:
                                            msg["content"] = str(formatted["value"])
                                except Exception as e:
                                    msg["content"] += f"\n(Error actualizando: {e})"
                            
                            updated_messages.append(msg)
                        st.session_state.messages = updated_messages

                if current_source_sig != last_source:
                    st.success(f"Cargado: {len(df)} filas")
                else:
                    st.toast(f"Reloaded: {len(df)} rows")

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

# --- Auto-Refresh ---
if st.session_state.get('live_mode', False):
    time.sleep(st.session_state.get('refresh_interval', 5))
    st.rerun()

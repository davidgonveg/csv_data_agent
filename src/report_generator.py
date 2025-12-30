import pandas as pd
import plotly.graph_objects as go
import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Reporte de Análisis - CSV Data Agent</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 900px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .timestamp {{ color: #888; font-size: 0.9em; margin-bottom: 30px; }}
        .message {{ margin-bottom: 25px; padding: 15px; border-radius: 6px; }}
        .user {{ background-color: #e3f2fd; border-left: 4px solid #2196f3; }}
        .assistant {{ background-color: #f1f8e9; border-left: 4px solid #8bc34a; }}
        .role-label {{ font-weight: bold; margin-bottom: 5px; color: #555; }}
        pre {{ background-color: #272822; color: #f8f8f2; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .plot-container {{ margin: 15px 0; border: 1px solid #ddd; padding: 10px; background: white; }}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Reporte de Análisis</h1>
        <div class="timestamp">Generado el: {date}</div>
        
        <div class="chat-history">
            {content}
        </div>
    </div>
</body>
</html>
"""

def generate_html_report(messages: list) -> str:
    """
    Generates a standalone HTML string from the conversation history.
    
    Args:
        messages: List of message dictionaries from st.session_state.messages
    """
    content_html = ""
    
    for msg in messages:
        role = msg["role"]
        role_label = "Usuario" if role == "user" else "Asistente"
        css_class = role
        
        message_body = ""
        
        # 1. Text Content
        if "content" in msg:
            # Simple newline to break conversion
            text = msg["content"].replace("\n", "<br>")
            message_body += f"<div class='text'>{text}</div>"
        
        # 2. Code Block
        if "code" in msg and msg["code"]:
            message_body += f"<pre><code>{msg['code']}</code></pre>"
            
        # 3. DataFrames
        if "dataframe" in msg and isinstance(msg["dataframe"], pd.DataFrame):
            df_html = msg["dataframe"].to_html(classes='table', border=0)
            message_body += f"<div class='dataframe-container'>{df_html}</div>"
            
        # 4. Plots
        if "image" in msg:
            fig = msg["image"]
            # Convert Plotly figure to HTML div
            # include_plotlyjs='cdn' ensures it's interactive but loads lib from CDN (smaller file)
            # full_html=False gives us just the div
            if isinstance(fig, (go.Figure)):
                plot_html = fig.to_html(full_html=False, include_plotlyjs=False) 
                message_body += f"<div class='plot-container'>{plot_html}</div>"
        
        content_html += f"""
        <div class="message {css_class}">
            <div class="role-label">{role_label}</div>
            {message_body}
        </div>
        """
        
    return HTML_TEMPLATE.format(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        content=content_html
    )

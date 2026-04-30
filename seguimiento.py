import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Configuración de la página
st.set_page_config(page_title="Seguimiento de Obra", layout="centered")

# 1. Incorporar imagen del logo
if os.path.exists("logo.png"):
    st.image("logo.png", width=200)
else:
    st.info("Logo de la empresa")

st.title("🏗️ Control de Avance de Obra")

# Inicializar el estado de la aplicación para guardar registros temporalmente
if 'df_seguimiento' not in st.session_state:
    st.session_state.df_seguimiento = pd.DataFrame(columns=[
        "Fecha", "Trabajador", "Tarea", "Estado"
    ])

# --- FORMULARIO DE ENTRADA ---
with st.form("formulario_obra"):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_trabajador = st.text_input("Nombre del trabajador")
    with col2:
        fecha_envio = st.date_input("Fecha de envío", date.today())

    # Desplegable de tareas
    tareas = [
        "Trazado y marcado de cajas, tubos y cuadros",
        "Ejecución rozas en paredes y techos",
        "Montaje de soportes",
        "Colocación tubos y conductos",
        "Tendido de cables",
        "Identificación y etiquetado",
        "Conexionado de cables en bornes o regletas",
        "Instalación y conexionado de mecanismos",
        "Fijación de carril DIN y mecanismos en cuadro eléctrico",
        "Cableado interno del cuadro eléctrico",
        "Configuración de equipos domóticos y/o automáticos",
        "Conexionado de sensores/actuadores",
        "Pruebas de continuidad",
        "Pruebas de aislamiento",
        "Verificación de tierras",
        "Programación del automatismo",
        "Pruebas de funcionamiento"
    ]
    tarea_seleccionada = st.selectbox("Seleccione la tarea:", tareas)

    # Desplegable de estado
    estados = [
        "Avance de la tarea en torno al 25% aprox.",
        "Avance de la tarea en torno al 50% aprox.",
        "Avance de la tarea en torno al 75% aprox.",
        "OK, finalizado sin errores",
        "Finalizado, pero con errores pendientes de corregir",
        "Finalizado y corregidos los errores"
    ]
    estado_seleccionado = st.selectbox("Estado de la tarea:", estados)

    submit_button = st.form_submit_button("Añadir Registro")

if submit_button:
    if nombre_trabajador:
        nuevo_registro = {
            "Fecha": fecha_envio,
            "Trabajador": nombre_trabajador,
            "Tarea": tarea_seleccionada,
            "Estado": estado_seleccionado
        }
        st.session_state.df_seguimiento = pd.concat([
            st.session_state.df_seguimiento, 
            pd.DataFrame([nuevo_registro])
        ], ignore_index=True)
        st.success("Registro añadido correctamente.")
    else:
        st.error("Por favor, introduce el nombre del trabajador.")

# --- GESTIÓN DE DATOS Y EXPORTACIÓN ---
st.subheader("Registros actuales")
st.dataframe(st.session_state.df_seguimiento)

# Generar Excel
excel_file = "seguimiento_obra.xlsx"
st.session_state.df_seguimiento.to_excel(excel_file, index=False)

# Botón de descarga
with open(excel_file, "rb") as f:
    st.download_button(
        label="📥 Descargar Excel",
        data=f,
        file_name=excel_file,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- ENVÍO POR CORREO ---
st.divider()
st.subheader("Enviar reporte por Email")

def enviar_correo(archivo):
    # Obtener credenciales desde Streamlit Secrets
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASS"]
        destinatario = st.secrets["EMAIL_DESTINATION"]

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Reporte de Obra - {date.today()}"

        cuerpo = "Se adjunta el reporte de seguimiento de obra generado desde la app."
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Adjuntar archivo
        attachment = open(archivo, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {archivo}")
        msg.attach(part)

        # Configuración del servidor (Ejemplo para Gmail)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar: {e}")
        return False

if st.button("📧 Enviar Excel por Correo"):
    if not st.session_state.df_seguimiento.empty:
        if enviar_correo(excel_file):
            st.success(f"Correo enviado con éxito a la empresa/profesora.")
    else:
        st.warning("No hay datos para enviar."

from flask import Flask, request, jsonify, render_template
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Configurações do Google Drive
SERVICE_ACCOUNT_FILE = 'teste-de-integracao-edna-0f300bc2a370.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1yn-xz1Ub0uFc0CjkSWu1DZ3U7Rpq6wCS'

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def upload_file_to_drive(file_path):
    drive_service = get_drive_service()
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(file_path, resumable=True)
    result = drive_service.files().create(
        body=file_metadata, media_body=media, fields='id'
    ).execute()
    return result

def generate_shareable_link(file_id):
    drive_service = get_drive_service()
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    drive_service.permissions().create(fileId=file_id, body=permission).execute()
    file = drive_service.files().get(fileId=file_id, fields='webViewLink').execute()
    return file.get('webViewLink')

@app.route("/")
def index():
    # Se não utilizar templates, pode retornar um texto simples:
    return "Hello from Python Flask on Vercel"

@app.route("/upload", methods=["POST"])
def upload_handler():
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({"error": f"Erro ao ler JSON: {str(e)}"}), 400

    file_path = data.get("file_path")
    # Em ambiente serverless, o sistema de arquivos é somente leitura e contém apenas os arquivos do deploy.
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Caminho do arquivo inválido ou arquivo não encontrado."}), 400

    try:
        uploaded = upload_file_to_drive(file_path)
        file_id = uploaded.get("id")
        link = generate_shareable_link(file_id)
        return jsonify({"download_link": link}), 200
    except Exception as e:
        return jsonify({"error": f"Erro durante o upload: {str(e)}"}), 500

if __name__ == "__main__":
    # Para testes locais
    app.run(debug=True)

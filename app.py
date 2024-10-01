from flask import Flask, request, jsonify
from pypdf import PdfReader
import docx2txt
import os
import openai
import requests

# Inicialize o Flask
app = Flask(__name__)

# Defina sua chave API OpenAI (certifique-se de ter a variável de ambiente configurada ou insira diretamente)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Função para extrair texto de PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para extrair texto de DOCX
def extract_text_from_docx(file_path):
    return docx2txt.process(file_path)

# Função para resumir o texto utilizando a API do ChatGPT
def summarize_text(text):
    response = openai.chat.completions.create(
        model = "gpt-4o",
        messages= [
            {"role": "system", "content": "Você é um resumidor de conteúdo de documento"},
            {"role": "user", "content": f"Resuma o seguinte texto:\n\n{text}"}
        ],
        max_tokens=150,
        temperature=0.5,
    )
    summary = response.choices[0].message.content.strip()
    return summary

# Função para fazer o download do arquivo a partir de uma URL
def download_file(url):
    local_filename = url.split('/')[-1]
    file_path = os.path.join("/tmp", local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_path

# Endpoint para upload do documento
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Nome de arquivo inválido"}), 400

    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)

    try:
        # Identifique o tipo de arquivo (PDF ou DOCX)
        if file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            return jsonify({"error": "Formato de arquivo não suportado"}), 400

        # Resuma o texto utilizando o ChatGPT
        summary = summarize_text(text)
        
        # Retorne o resumo
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Apague o arquivo temporário após o processamento
        os.remove(file_path)

# Novo endpoint para receber a URL de um arquivo
@app.route('/summarize-url', methods=['POST'])
def summarize_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "Nenhuma URL fornecida"}), 400
    
    url = data['url']
    file_path = ""
    try:
        # Faça o download do arquivo a partir da URL
        file_path = download_file(url)
        file_name = file_path.split('/')[-1]

        # Identifique o tipo de arquivo (PDF ou DOCX)
        if file_name.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_name.endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            return jsonify({"error": "Formato de arquivo não suportado"}), 400

        # Resuma o texto utilizando o ChatGPT
        summary = summarize_text(text)
        
        # Retorne o resumo
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Apague o arquivo temporário após o processamento
        if os.path.exists(file_path):
            os.remove(file_path)

# Endpoint para upload do documento
@app.route('/health-check', methods=['GET'])
def health_check():
    return jsonify({"health_check": True})

# Execute o app Flask
if __name__ == '__main__':
    app.run(debug=True)

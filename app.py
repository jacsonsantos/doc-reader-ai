from flask import Flask, request, jsonify
from pypdf import PdfReader
import docx2txt
import os
import openai

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
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Resuma o seguinte texto:\n\n{text}",
        max_tokens=150,
        temperature=0.5,
    )
    summary = response.choices[0].text.strip()
    return summary

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

# Execute o app Flask
if __name__ == '__main__':
    app.run(debug=True)

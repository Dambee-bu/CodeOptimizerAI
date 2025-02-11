# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import os
import openai

app = Flask(__name__)

# Directory to store uploaded files
UPLOAD_FOLDER = './uploads'
PROCESSED_FOLDER = './processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ensure upload and processed folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Uploads a file, processes it, and rewrites the code using AI if it's a code file.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded file
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(upload_path)

    # Read the uploaded file
    content = read_file(upload_path)
    if content is None:
        return jsonify({'error': 'Error reading the uploaded file'}), 500

    # Rewrite the code with AI
    rewritten_code = rewrite_code_with_ai(content)
    if rewritten_code is None:
        return jsonify({'error': 'Error rewriting the code with AI'}), 500

    # Save the rewritten code to a new file
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], f"rewritten_{file.filename}")
    write_file(processed_path, rewritten_code)

    return jsonify({
        'message': 'File successfully uploaded and processed',
        'processed_file': processed_path,
        'rewritten_code': rewritten_code
    })


def read_file(file_path):
    """
    Reads the content of a file, trying multiple encodings for compatibility.
    """
    encodings = ['utf-8', 'utf-16', 'latin1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
    print(f"Error: Could not decode the file '{file_path}' with supported encodings.")
    return None


def write_file(file_path, content):
    """
    Writes content to a file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def rewrite_code_with_ai(code):
    """
    Uses the OpenAI API to rewrite the given code for better efficiency.
    """
    prompt = (
        "Rewrite the following Python code to make it more efficient and maintainable, while preserving its functionality. "
        "Add comments to explain any major changes you make.\n\n"
        f"Code:\n{code}\n\nEfficient Code:"
    )

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Choose the appropriate GPT model
            prompt=prompt,
            max_tokens=1500,
            temperature=0
        )
        rewritten_code = response.choices[0].text.strip()
        return rewritten_code
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=False)

import os
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, jsonify, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from litellm import completion
from pypdf import PdfReader

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# Setup safe storage paths
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Connection (NoSQL - MongoDB)
client = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27017"))
db = client["rag_production"]
users_col = db["users"]
chats_col = db["chat_history"]

# --- Global Template Context ---
@app.context_processor
def inject_global_variables():
    return {
        "app_name": os.getenv("APP_NAME", "Default AI App")
    }

# --- Utility Cryptography & Extraction Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def extract_pdf_text(filepath):
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text[:5000]  # Caps context token payload windows to 5k chars
    except Exception as e:
        print(f"Error parsing PDF layout architecture: {e}")
        return ""

# --- Authentication Endpoints ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if users_col.find_one({"email": data['email']}):
        return jsonify({"error": "User profile already matches an account."}), 400
    
    user_doc = {
        "username": data['username'],
        "email": data['email'],
        "password": hash_password(data['password']),
        "created_at": datetime.utcnow()
    }
    users_col.insert_one(user_doc)
    return jsonify({"success": "Profile verified and committed to storage"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users_col.find_one({"email": data['email']})
    if user and user['password'] == hash_password(data['password']):
        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        return jsonify({"success": "Session instantiated"})
    return jsonify({"error": "Invalid login credentials."}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- Application View Logic ---
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('chat.html', username=session['username'])

@app.route('/login_page')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

# --- Asynchronous Data Endpoints ---
@app.route('/history', methods=['GET'])
def get_history():
    if 'user_id' not in session: 
        return jsonify([]), 401
    history = list(chats_col.find({"user_id": session['user_id']}).sort("timestamp", 1))
    for h in history: 
        h['_id'] = str(h['_id']) 
    return jsonify(history)

@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if 'file' not in request.files:
        return jsonify({"status": "error", "error": "Empty network attachment header payload"}), 400
        
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({"status": "error", "error": "Invalid document metadata extension formatting."}), 400

    try:
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        
        extracted_context = extract_pdf_text(save_path)
        if not extracted_context.strip():
            return jsonify({"status": "error", "error": "Document yields an empty string. Might be flat graphic image arrays (needs OCR)."}), 400
            
        session['context'] = extracted_context
        return jsonify({"status": "success", "filename": file.filename})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session: 
        return jsonify({"error": "Session mapping lookup failed."}), 401
    
    user_msg = request.json.get('message')
    context = session.get('context', "No background target reference file context currently ingested.")
    
    try:
        response = completion(
            model=os.getenv("LLM_MODEL"),
            messages=[
                {"role": "system", "content": f"Answer concisely based on this context:\n{context}"},
                {"role": "user", "content": user_msg}
            ],
            api_base=os.getenv("OLLAMA_API_BASE")  # Evaluates dynamically if using a remote server
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"AI Inference engine execution runtime breakdown: {str(e)}"

    chats_col.insert_one({
        "user_id": session['user_id'],
        "query": user_msg,
        "answer": answer,
        "timestamp": datetime.utcnow()
    })
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
#!/bin/python3
import os
import sqlite3
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from os import listdir, makedirs
from linkpreview import link_preview

app = Flask(__name__)

# Ensure asset directories exist
makedirs("assets/images", exist_ok=True)
makedirs("assets/audio", exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('bulletin.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Ensure notes table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Auto-migrate: Add new columns if they don't exist
    columns = [row[1] for row in cursor.execute('PRAGMA table_info(notes)').fetchall()]
    
    if 'color' not in columns:
        cursor.execute('ALTER TABLE notes ADD COLUMN color TEXT DEFAULT "#fff9c4"')
    if 'pos_x' not in columns:
        cursor.execute('ALTER TABLE notes ADD COLUMN pos_x INTEGER DEFAULT 0')
    if 'pos_y' not in columns:
        cursor.execute('ALTER TABLE notes ADD COLUMN pos_y INTEGER DEFAULT 0')
        
    conn.commit()
    conn.close()

# Run schema check on startup
init_db_schema()

@app.route("/")
def index():
    conn = get_db_connection()
    notes_rows = conn.execute('SELECT * FROM notes ORDER BY created_at DESC').fetchall()
    conn.close()
    
    notes = []
    for row in notes_rows:
        note = dict(row)
        if note['metadata']:
            try:
                note['metadata'] = json.loads(note['metadata'])
            except:
                note['metadata'] = {}
        notes.append(note)
        
    return render_template("bulletin.html", notes=notes)

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)

@app.route("/upload-media", methods=["POST"])
def upload_media():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = file.filename
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        save_path = os.path.join("assets/images", filename)
        file.save(save_path)
        
        # Create a note for the image
        conn = get_db_connection()
        conn.execute('INSERT INTO notes (type, content, metadata, color) VALUES (?, ?, ?, ?)',
                     ('image', filename, json.dumps({"url": f"/assets/images/{filename}"}), "#ffffff"))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "type": "image", "url": f"/assets/images/{filename}"})
    
    if filename.lower().endswith(('.mp3', '.wav', '.ogg')):
        save_path = os.path.join("assets/audio", filename)
        file.save(save_path)
        
        # Also create a note for the audio
        conn = get_db_connection()
        conn.execute('INSERT INTO notes (type, content, metadata, color) VALUES (?, ?, ?, ?)',
                     ('audio', filename, json.dumps({"url": f"/assets/audio/{filename}"}), "#fff3e0"))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "type": "audio", "url": f"/assets/audio/{filename}"})
    
    return jsonify({"error": "Unsupported file type"}), 400

@app.route("/add-note", methods=["POST"])
def add_note():
    data = request.json
    content = data.get('content', '').strip()
    note_type = data.get('type', 'message')
    color = data.get('color', '#fff9c4')
    pos_x = data.get('pos_x', 0)
    pos_y = data.get('pos_y', 0)
    
    if not content:
        return jsonify({"error": "Content is empty"}), 400
    
    metadata = None
    
    # Check if it's a URL
    if content.startswith(('http://', 'https://')):
        try:
            preview = link_preview(content)
            note_type = 'link'
            metadata = json.dumps({
                "title": preview.title,
                "description": preview.description,
                "image": preview.absolute_image,
                "url": content
            })
            if 'color' not in data: # default green for links if not specified
                color = "#e8f5e9" 
        except Exception as e:
            print(f"Error fetching preview: {e}")
            note_type = 'link'
            metadata = json.dumps({"url": content})
            if 'color' not in data:
                color = "#e8f5e9"

    conn = get_db_connection()
    conn.execute('INSERT INTO notes (type, content, metadata, color, pos_x, pos_y) VALUES (?, ?, ?, ?, ?, ?)',
                 (note_type, content, metadata, color, pos_x, pos_y))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route("/update-note/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.json
    
    conn = get_db_connection()
    # Build dynamic update query based on what was provided
    fields = []
    values = []
    
    if 'content' in data:
        fields.append("content = ?")
        values.append(data['content'])
    if 'color' in data:
        fields.append("color = ?")
        values.append(data['color'])
    if 'pos_x' in data:
        fields.append("pos_x = ?")
        values.append(data['pos_x'])
    if 'pos_y' in data:
        fields.append("pos_y = ?")
        values.append(data['pos_y'])
        
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
        
    values.append(note_id)
    
    query = f"UPDATE notes SET {', '.join(fields)} WHERE id = ?"
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route("/delete-note/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

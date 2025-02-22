from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import os
from waitress import serve

app = Flask(__name__)

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "mysql")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "jenkins")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "jenkinspass")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DATABASE", "jenkins_builds")
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

def init_db():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS builds (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_name VARCHAR(255) NOT NULL,
                branch_name VARCHAR(255),
                commit_hash VARCHAR(64),
                start_time BIGINT NOT NULL,
                end_time BIGINT NOT NULL,
                build_duration INT GENERATED ALWAYS AS (end_time - start_time) STORED,
                build_result ENUM('SUCCESS', 'FAILURE', 'ABORTED', 'UNSTABLE') NOT NULL,
                job_url TEXT NOT NULL,
                node_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        mysql.connection.commit()
        cursor.close()

@app.route("/build", methods=["POST"])
def receive_build():
    data = request.json

    required_fields = {"job_name", "start_time", "end_time", "build_result", "job_url"}
    if not required_fields.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO builds (job_name, branch_name, commit_hash, start_time, end_time, build_result, job_url, node_name) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["job_name"], 
            data.get("branch_name"), 
            data.get("commit_hash"), 
            data["start_time"], 
            data["end_time"], 
            data["build_result"], 
            data["job_url"], 
            data.get("node_name")
        ))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Build data stored"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return "Build router to MySQL"

if __name__ == "__main__":
    init_db()
    print("Server running on port 5000...")
    serve(app, host="0.0.0.0", port=5000)

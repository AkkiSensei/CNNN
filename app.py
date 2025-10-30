from flask import Flask, render_template_string, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# -------------------------------
# Database Model
# -------------------------------
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_name = db.Column(db.String(100))
    candidate = db.Column(db.String(100))

# -------------------------------
# File Paths (use raw strings to avoid escape issues)
# -------------------------------
INDEX_HTML = "./index.html"
VOTE_HTML = "./vote.html"
RESULTS_HTML = "./results.html"

# Function to read HTML files safely
def load_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# -------------------------------
# Routes
# -------------------------------

# Home Page
@app.route('/')
def index():
    return render_template_string(load_html(INDEX_HTML))

# Voting Page
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        name = request.form['name']
        candidate = request.form['candidate']
        new_vote = Vote(voter_name=name, candidate=candidate)
        db.session.add(new_vote)
        db.session.commit()
        return redirect('/results')
    return render_template_string(load_html(VOTE_HTML))

# Results Page
@app.route('/results')
def results():
    votes = Vote.query.all()
    candidates = {}
    for v in votes:
        candidates[v.candidate] = candidates.get(v.candidate, 0) + 1

    html = load_html(RESULTS_HTML)
    # Replace {{results_table}} with actual vote data
    table_rows = ""
    for c, count in candidates.items():
        table_rows += f"<tr><td>{c}</td><td>{count}</td></tr>"
    html = html.replace("{{results_table}}", table_rows)

    return render_template_string(html)

# Reset votes route
@app.route('/reset', methods=['POST'])
def reset_votes():
    db.session.query(Vote).delete()
    db.session.commit()
    return "✅ All votes have been deleted successfully!"

# -------------------------------
# Run Server (Fixed Context Issue)
# -------------------------------
if __name__ == '__main__':
    with app.app_context():       # ✅ FIX: create database within app context
        db.create_all()

    app.run(host='0.0.0.0', port=5000, debug=True)

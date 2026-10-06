"""Calorie calculator API and SQLite-backed food diary."""
import os, secrets, sqlite3
from datetime import date
from pathlib import Path
from flask import Flask, g, jsonify, render_template, request, session

ACTIVITY = {"sedentary":1.2,"light":1.375,"moderate":1.55,"active":1.725,"very_active":1.9}
FOODS = [{"name":"Oats, dry","serving":"40 g","calories":152,"protein":5.3},{"name":"Banana","serving":"1 medium","calories":105,"protein":1.3},{"name":"Egg, boiled","serving":"1 large","calories":78,"protein":6.3},{"name":"Chicken breast, cooked","serving":"100 g","calories":165,"protein":31.0},{"name":"Brown rice, cooked","serving":"1 cup","calories":216,"protein":5.0},{"name":"Greek yogurt, plain","serving":"170 g","calories":100,"protein":17.0},{"name":"Apple","serving":"1 medium","calories":95,"protein":0.5},{"name":"Almonds","serving":"28 g","calories":164,"protein":6.0},{"name":"Whole wheat bread","serving":"1 slice","calories":81,"protein":4.0},{"name":"Milk, 2%","serving":"1 cup","calories":122,"protein":8.1}]

def create_app(config=None):
    app=Flask(__name__); app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),DATABASE=os.environ.get('DATABASE_PATH','data/calories.db'))
    if config: app.config.update(config)
    def db():
        if 'db' not in g:
            g.db=sqlite3.connect(app.config['DATABASE'],timeout=30); g.db.row_factory=sqlite3.Row
        return g.db
    @app.teardown_appcontext
    def close_db(error):
        if 'db' in g: g.pop('db').close()
    Path(app.config['DATABASE']).parent.mkdir(parents=True,exist_ok=True)
    with app.app_context():
        db().executescript('''CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY,day TEXT NOT NULL,food TEXT NOT NULL,serving TEXT NOT NULL,calories INTEGER NOT NULL,protein REAL NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS goals(day TEXT PRIMARY KEY,target INTEGER NOT NULL CHECK(target BETWEEN 500 AND 10000));''')
    @app.before_request
    def csrf_check():
        if request.method in ('POST','DELETE') and session.get('csrf') and request.headers.get('X-CSRF-Token')!=session['csrf']: return jsonify(error='Refresh the page and try again'),403
    @app.after_request
    def headers(r):
        r.headers['X-Content-Type-Options']='nosniff'; r.headers['X-Frame-Options']='DENY'; r.headers['Content-Security-Policy']="default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        if request.path.startswith('/api/'): r.headers['Cache-Control']='no-store'
        return r
    @app.get('/')
    def home(): session.setdefault('csrf',secrets.token_hex(32)); return render_template('index.html')
    @app.get('/health')
    def health(): db().execute('SELECT 1'); return jsonify(status='healthy')
    @app.get('/api/session')
    def get_session(): session.setdefault('csrf',secrets.token_hex(32)); return jsonify(csrf=session['csrf'])
    @app.post('/api/calculate')
    def calculate():
        d=request.get_json(silent=True) or {}
        try: age,height,weight=int(d['age']),float(d['height_cm']),float(d['weight_kg']); sex,activity=d['sex'],d['activity']
        except (KeyError,TypeError,ValueError): return jsonify(error='Enter age, height, weight and activity level.'),400
        if not 19<=age<=78 or not 100<=height<=250 or not 25<=weight<=350 or sex not in ('female','male') or activity not in ACTIVITY: return jsonify(error='Check the values and try again. This calculator covers adults ages 19–78.'),400
        bmr=10*weight+6.25*height-5*age+(5 if sex=='male' else -161); maintenance=round(bmr*ACTIVITY[activity])
        return jsonify(bmr=round(bmr),maintenance=maintenance,target=maintenance,method='Mifflin-St Jeor')
    @app.get('/api/foods')
    def foods(): return jsonify(FOODS)
    @app.route('/api/entries',methods=['GET','POST'])
    def entries():
        today=date.today().isoformat()
        if request.method=='POST':
            d=request.get_json(silent=True) or {}
            try: food,serving,calories=str(d['food']).strip(),str(d['serving']).strip(),int(d['calories']); protein=float(d.get('protein',0))
            except (KeyError,TypeError,ValueError): return jsonify(error='Enter a food, serving and calorie amount.'),400
            if not food or len(food)>120 or not serving or len(serving)>80 or not 0<=calories<=10000 or not 0<=protein<=1000: return jsonify(error='Check the food details and try again.'),400
            cur=db().execute('INSERT INTO entries(day,food,serving,calories,protein) VALUES(?,?,?,?,?)',(today,food,serving,calories,protein)); db().commit(); return jsonify(id=cur.lastrowid),201
        rows=[dict(r) for r in db().execute('SELECT id,food,serving,calories,protein,created_at FROM entries WHERE day=? ORDER BY id DESC',(today,))]; goal=db().execute('SELECT target FROM goals WHERE day=?',(today,)).fetchone()
        return jsonify(day=today,entries=rows,total=sum(r['calories'] for r in rows),protein=round(sum(r['protein'] for r in rows),1),goal=goal['target'] if goal else None)
    @app.delete('/api/entries/<int:entry_id>')
    def delete_entry(entry_id):
        cur=db().execute('DELETE FROM entries WHERE id=? AND day=?',(entry_id,date.today().isoformat())); db().commit()
        if not cur.rowcount: return jsonify(error='Entry not found'),404
        return jsonify(ok=True)
    @app.post('/api/goal')
    def set_goal():
        try: target=int((request.get_json(silent=True) or {})['target'])
        except (KeyError,TypeError,ValueError): return jsonify(error='Enter a daily calorie goal.'),400
        if not 500<=target<=10000: return jsonify(error='Goal must be between 500 and 10,000 calories.'),400
        db().execute('INSERT INTO goals(day,target) VALUES(?,?) ON CONFLICT(day) DO UPDATE SET target=excluded.target',(date.today().isoformat(),target)); db().commit(); return jsonify(target=target)
    return app

app=create_app()
if __name__ == "__main__":
    app.run(debug=True)

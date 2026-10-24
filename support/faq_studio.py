"""Admin-curated FAQ knowledge. Publishing requires a separate explicit action."""
from datetime import datetime, timezone
import re
import sqlite3
from support.intelligence import _connect, sanitize

def _init(db):
    db.execute("""CREATE TABLE IF NOT EXISTS faq_articles(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      app TEXT NOT NULL, question TEXT NOT NULL, answer TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'draft',
      updated_at TEXT NOT NULL
    )""")

def list_articles(db_path, app=None, published_only=False):
    with _connect(db_path) as db:
        _init(db)
        sql="SELECT id,app,question,answer,status,updated_at FROM faq_articles"
        conditions=[];args=[]
        if app:
            conditions.append("app=?");args.append(app)
        if published_only:
            conditions.append("status='published'")
        if conditions:
            sql+=" WHERE "+" AND ".join(conditions)
        sql+=" ORDER BY id DESC LIMIT 100"
        rows=db.execute(sql,args).fetchall()
        return [dict(zip(("id","app","question","answer","status","updated_at"),r)) for r in rows]

def save_draft(db_path, app, question, answer):
    if not isinstance(app,str) or not re.fullmatch(r"[a-z][a-z0-9_-]{1,31}",app):
        raise ValueError("Invalid application")
    if not isinstance(question,str) or not isinstance(answer,str):
        raise ValueError("Invalid content")
    if not 8<=len(question.strip())<=300 or not 8<=len(answer.strip())<=3000:
        raise ValueError("Invalid length")
    # No HTML rendering; textContent only. Sanitize common secrets/PII.
    question=sanitize(question)
    answer="\n".join(sanitize(line) for line in answer.splitlines())[:3000]
    now=datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as db:
        _init(db)
        return db.execute("INSERT INTO faq_articles(app,question,answer,status,updated_at) VALUES(?,?,?,?,?)",
                          (app,question,answer,"draft",now)).lastrowid

def set_publication(db_path, article_id, publish):
    if type(article_id) is not int or article_id<1 or type(publish) is not bool:
        raise ValueError("Invalid publication request")
    with _connect(db_path) as db:
        _init(db)
        result=db.execute("UPDATE faq_articles SET status=?,updated_at=? WHERE id=?",
                          ("published" if publish else "draft",datetime.now(timezone.utc).isoformat(),article_id))
        return result.rowcount==1

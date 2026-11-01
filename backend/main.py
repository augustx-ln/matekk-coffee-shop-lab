from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3, secrets, html
from datetime import datetime, timezone
BASE=Path(__file__).resolve().parent.parent
DATA=BASE/"data"; Q=DATA/"uploads"; DB=DATA/"matekk.db"; DIST=BASE/"dist"; PUBLIC=BASE/"public"
DATA.mkdir(exist_ok=True); Q.mkdir(exist_ok=True)
app=FastAPI(title="Matekk Coffee Shop Lab", version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1","http://localhost"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.middleware("http")
async def lab_fingerprint(request, call_next):
 response=await call_next(request)
 response.headers["X-Powered-By"]="Matekk-Lab/1.0 (FastAPI; Starlette)"
 response.headers["X-Matekk-Stack"]="React; Vite; FastAPI; Starlette; SQLite"
 return response
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def now(): return datetime.now(timezone.utc).isoformat()
with db() as c:
 c.executescript("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password TEXT,role TEXT,created_at TEXT); CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,user_id INTEGER,username TEXT,rating INTEGER,comment TEXT,photo_name TEXT,photo_id TEXT,status TEXT DEFAULT 'published',created_at TEXT); CREATE TABLE IF NOT EXISTS customer_private_records(id INTEGER PRIMARY KEY,customer_id INTEGER UNIQUE,full_name TEXT,email TEXT,phone TEXT,internal_note TEXT);")
 for name,pw,role in [("Sally","admin1234","admin"),("Jhon","iloveyou","customer")]:
  if not c.execute("SELECT id FROM users WHERE username=?",(name,)).fetchone(): c.execute("INSERT INTO users(username,password,role,created_at) VALUES(?,?,?,?)",(name,pw,role,now()))
 if not c.execute("SELECT id FROM reviews LIMIT 1").fetchone():
  c.execute("INSERT INTO reviews(user_id,username,rating,comment,created_at) VALUES(1,'Sally',5,'The oat latte is silky, balanced, and beautifully made.',?)",(now(),))
  c.execute("INSERT INTO reviews(user_id,username,rating,comment,created_at) VALUES(2,'Jhon',4,'A calm corner for a slow morning. The cold brew is a favourite.',?)",(now(),))
 records=[(1001,"Amara Reyes","amara@example.test","+63-000-000-0001","Fictional VIP training record"),(1002,"Noah Santos","noah@example.test","+63-000-000-0002","Fictional refund training record"),(1003,"Mika Flores","mika@example.test","+63-000-000-0003","Fictional loyalty training record")]
 for row in records:
  if not c.execute("SELECT id FROM customer_private_records WHERE customer_id=?",(row[0],)).fetchone(): c.execute("INSERT INTO customer_private_records(customer_id,full_name,email,phone,internal_note) VALUES(?,?,?,?,?)",row)
sessions={}
def current(authorization:str|None=Header(default=None)):
 u=sessions.get((authorization or "").replace("Bearer ","",1))
 if not u: raise HTTPException(401,"Please sign in")
 return u
def admin(u=Depends(current)):
 if u["role"]!="admin": raise HTTPException(403,"Administrator access required")
 return u
@app.get("/api/health")
def health(): return {"ok":True,"app":"Matekk Coffee Shop","lab":True}
@app.get("/lab/fingerprint")
def fingerprint():
 import fastapi, starlette
 try:
  import multipart
  multipart_version=getattr(multipart,"__version__","unknown")
 except Exception: multipart_version="unknown"
 return {"application":"Matekk Coffee Shop Lab","framework":"FastAPI","fastapi_version":fastapi.__version__,"starlette_version":starlette.__version__,"multipart_version":multipart_version,"frontend":"React + Vite","database":"SQLite","notice":"Intentionally vulnerable localhost training target; version disclosure is deliberate."}
@app.post("/api/login")
def login(p:dict):
 with db() as c: r=c.execute("SELECT id,username,password,role FROM users WHERE username=?",(str(p.get("username",""))[:80],)).fetchone()
 if not r or r["password"]!=str(p.get("password","")): raise HTTPException(401,"Incorrect username or password")
 t=secrets.token_hex(12); u={"id":r["id"],"username":r["username"],"role":r["role"]}; sessions[t]=u
 return {"token":t,"user":u}
@app.post("/api/logout")
def logout(u=Depends(current),authorization:str|None=Header(default=None)):
 sessions.pop((authorization or "").replace("Bearer ","",1),None); return {"ok":True}
@app.get("/api/me")
def me(u=Depends(current)): return u
@app.get("/api/reviews")
def reviews():
 with db() as c: return [dict(r) for r in c.execute("SELECT id,username,rating,comment,photo_name,status,created_at FROM reviews WHERE status='published' ORDER BY id DESC")]
@app.post("/api/reviews")
def create_review(rating:int=Form(...),comment:str=Form(...),guest_name:str=Form(default=""),photo:UploadFile|None=File(default=None),authorization:str|None=Header(default=None)):
 if rating<1 or rating>5: raise HTTPException(400,"Rating must be from 1 to 5")
 comment=comment.strip()[:1200]
 if not comment: raise HTTPException(400,"Please add a short review")
 pid=None; name=None
 if photo and photo.filename:
  # Intentional lab flaw: trust client-supplied MIME metadata; bytes stay inert in quarantine.
  allowed_types={"image/jpeg","image/png","image/webp","image/gif","text/plain","application/x-msdownload","application/vnd.microsoft.portable-executable","application/octet-stream","application/pdf","application/msword","application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
  if photo.content_type not in allowed_types: raise HTTPException(400,"Choose JPG, PNG, WEBP, GIF, TXT, EXE, PDF, DOC, or DOCX")
  raw=photo.file.read(5*1024*1024+1)
  if len(raw)>5*1024*1024: raise HTTPException(413,"File must be 5 MB or smaller")
  pid=secrets.token_hex(12); name=Path(photo.filename).name.replace("\\","_").replace("/","_")[:120]; (Q/(pid+".bin")).write_bytes(raw)
 u=sessions.get((authorization or "").replace("Bearer ","",1))
 display_name=(u["username"] if u else (guest_name.strip()[:60] or "Walk-in customer")); user_id=u["id"] if u else None
 with db() as c: c.execute("INSERT INTO reviews(user_id,username,rating,comment,photo_name,photo_id,created_at) VALUES(?,?,?,?,?,?,?)",(user_id,display_name,rating,comment,name,pid,now()))
 return {"ok":True}
@app.get("/api/customers/{customer_id}/private-records")
def customer_private_records(customer_id:int,u=Depends(current)):
 # Intentional IDOR exercise: authentication is required, but record ownership is not checked.
 with db() as c: rows=c.execute("SELECT customer_id,full_name,email,phone,internal_note FROM customer_private_records WHERE customer_id=?",(customer_id,)).fetchall()
 if not rows: raise HTTPException(404,"Customer record not found")
 return [dict(x) for x in rows]
@app.get("/api/admin/summary")
def summary(u=Depends(admin)):
 with db() as c:
  users=c.execute("SELECT COUNT(*) n FROM users").fetchone()["n"]; count=c.execute("SELECT COUNT(*) n FROM reviews").fetchone()["n"]; avg=c.execute("SELECT AVG(rating) n FROM reviews WHERE status='published'").fetchone()["n"] or 0
  return {"users":users,"reviews":count,"average":round(avg,1),"latest":[dict(x) for x in c.execute("SELECT id,username,rating,comment,status,created_at FROM reviews ORDER BY id DESC LIMIT 8")]}
@app.get("/api/admin/users")
def users(u=Depends(admin)):
 with db() as c: return [dict(x) for x in c.execute("SELECT id,username,role,created_at FROM users ORDER BY id")]
@app.get("/api/admin/reviews")
def all_reviews(u=Depends(admin)):
 with db() as c: return [dict(x) for x in c.execute("SELECT id,username,rating,comment,photo_name,photo_id,status,created_at FROM reviews ORDER BY id DESC")]
@app.patch("/api/admin/reviews/{rid}")
def moderate(rid:int,p:dict,u=Depends(admin)):
 s=p.get("status")
 if s not in ("published","pending","hidden"): raise HTTPException(400,"Invalid status")
 with db() as c:
  cur=c.execute("UPDATE reviews SET status=? WHERE id=?",(s,rid))
  if not cur.rowcount: raise HTTPException(404,"Review not found")
 return {"ok":True}
@app.get("/api/admin/quarantine")
def quarantine(u=Depends(admin)):
 with db() as c: rows=c.execute("SELECT id,username,photo_name,photo_id,created_at FROM reviews WHERE photo_id IS NOT NULL ORDER BY id DESC").fetchall()
 return [{"review_id":r["id"],"username":r["username"],"filename":r["photo_name"],"quarantine_id":r["photo_id"],"created_at":r["created_at"],"scan_status":"NOT SCANNED - LAB DEMO"} for r in rows]
def listing(folder:Path,title:str):
 links=[]
 for item in sorted(folder.iterdir()):
  if item.is_file(): links.append(f'<li><a href="{html.escape(item.name)}">{html.escape(item.name)}</a> <small>{item.stat().st_size} bytes</small></li>')
 return HTMLResponse('<!doctype html><html><head><title>'+title+'</title></head><body><h1>Index of '+title+'</h1><ul>'+''.join(links)+'</ul><p>Matekk local training lab.</p></body></html>')
@app.get("/documents/",response_class=HTMLResponse)
def documents_index(): return listing(PUBLIC/"documents","/documents/")
@app.get("/documents/{filename}")
def document_file(filename:str):
 target=(PUBLIC/"documents"/filename).resolve()
 if target.parent!=(PUBLIC/"documents").resolve() or not target.is_file(): raise HTTPException(404,"Document not found")
 return FileResponse(target,filename=target.name)
@app.get("/backup/",response_class=HTMLResponse)
def backup_index(): return listing(PUBLIC/"backup","/backup/")
@app.get("/backup/{filename}")
def backup_file(filename:str):
 target=(PUBLIC/"backup"/filename).resolve()
 if target.parent!=(PUBLIC/"backup").resolve() or not target.is_file(): raise HTTPException(404,"Backup not found")
 return FileResponse(target,filename=target.name)
@app.get("/internal/",response_class=HTMLResponse)
def internal_index(): return listing(PUBLIC/"internal","/internal/")
@app.get("/internal/{filename}")
def internal_file(filename:str):
 target=(PUBLIC/"internal"/filename).resolve()
 if target.parent!=(PUBLIC/"internal").resolve() or not target.is_file(): raise HTTPException(404,"Internal file not found")
 return FileResponse(target,filename=target.name)
@app.get("/staff/archive")
def legacy_staff_archive(): return FileResponse(PUBLIC/"backup"/"old_site_backup.txt",filename="staff-archive.txt")
if PUBLIC.exists(): app.mount("/static-lab",StaticFiles(directory=PUBLIC),name="static-lab")
if DIST.exists():
 app.mount("/assets",StaticFiles(directory=DIST/"assets"),name="assets")
 @app.get("/{path:path}")
 def frontend(path:str):
  target=DIST/path
  if target.is_file() and DIST in target.resolve().parents: return FileResponse(target)
  return FileResponse(DIST/"index.html")
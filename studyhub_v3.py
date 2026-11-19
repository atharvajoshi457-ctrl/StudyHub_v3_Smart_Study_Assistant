
import json, os, re, shutil, subprocess, sys, csv, tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import date, timedelta
from exam_tracker import TOPICS, EXAMS

ROOT=Path(__file__).resolve().parent
NOTES=ROOT/"Study_Notes"
STATE=ROOT/"studyhub_v3_data.json"
BG="#0b1020"; PANEL="#131b2e"; PANEL2="#1b2740"; FG="#eef2ff"; MUTED="#9aa8c7"; PURPLE="#8b5cf6"; GREEN="#34d399"
COLORS={"PS":"#60a5fa","CNM":"#a78bfa","IAM":"#34d399","ICS":"#fbbf24","AIMLT":"#f472b6","DAA":"#fb923c","SEPM":"#22d3ee"}
EXTS={".pdf",".docx",".txt",".md",".rtf",".py",".c",".cpp",".java",".html",".csv"}
EVENTS=[
("2026-10-26","PBL III external practical","2:15–4:15 PM"),
("2026-10-27","FSDL internal practical (may take all day)","2:15–4:15 PM"),
("2026-10-28","PS theory exam","As scheduled"),
("2026-10-29","AIMLT oral exam","2:15–4:15 PM"),
("2026-10-30","ICS oral exam","2:15–4:15 PM"),
("2026-10-31","IAM oral exam","2:15–4:15 PM"),
("2026-11-23","IAM theory exam","As scheduled"),
("2026-11-25","ICS theory exam","As scheduled"),
("2026-11-27","AIMLT theory exam","As scheduled"),
("2026-12-01","DAA theory exam","As scheduled"),
("2026-12-02","CNM theory exam","As scheduled"),
("2026-12-22","SEPM theory exam","As scheduled")]
DELAYS=[1,3,7,14]

def fresh():
    return {"topics":{s:[{"unit":u,"name":n,"status":"Not started","confidence":0,"notes":"","last":"","next_review":"","stage":0} for u,ns in units.items() for n in ns] for s,units in TOPICS.items()},"log":[],"cards":[],"settings":{"reminders":True}}
def save(d): STATE.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
def load():
    if STATE.exists():
        try:
            d=json.loads(STATE.read_text(encoding="utf-8")); base=fresh()
            for s,items in base["topics"].items():
                d.setdefault("topics",{}).setdefault(s,[])
                names={x["name"] for x in d["topics"][s]}
                d["topics"][s].extend(x for x in items if x["name"] not in names)
                for t in d["topics"][s]:
                    for k,v in {"next_review":"","stage":0,"confidence":0,"notes":"","last":""}.items(): t.setdefault(k,v)
            d.setdefault("log",[]); d.setdefault("cards",[]); d.setdefault("settings",{"reminders":True})
            return d
        except Exception: pass
    d=fresh(); save(d); return d
def extract(p):
    try:
        if p.suffix.lower() in {".txt",".md",".rtf",".py",".c",".cpp",".java",".html",".csv"}: return p.read_text(encoding="utf-8",errors="replace")
        if p.suffix.lower()==".pdf":
            from pypdf import PdfReader
            return "\n\n".join(pg.extract_text() or "" for pg in PdfReader(str(p)).pages)
        if p.suffix.lower()==".docx":
            from docx import Document
            doc=Document(str(p)); return "\n".join(x.text for x in doc.paragraphs)
    except ImportError: return "[Install optional readers: python -m pip install pypdf python-docx]"
    except Exception as e: return "[Preview error: "+str(e)+"]"
    return ""
def subj(p):
    for s in ["aimlt","sepm","cnm","iam","ics","daa","ps"]:
        if re.search(r"(^|[^a-z])"+s+r"([^a-z]|$)",str(p).lower()): return s.upper()
    return "General"

class App:
 def __init__(self,r):
    self.r=r; r.title("StudyHub v3 | Smart Study Assistant"); r.geometry("1280x800"); r.minsize(1000,650); r.configure(bg=BG)
    self.d=load(); self.notes=[]; self.current_note=None; self.subject="PS"; self.scan(); self.style(); self.shell(); self.dashboard()
    due=self.due()
    if due and self.d["settings"].get("reminders",True): r.after(500,lambda:messagebox.showinfo("Revision due",f"{len(due)} topic(s) are due for spaced revision. Open Syllabus to review them."))
    upcoming=[f"{n} — {ds} ({tm})" for ds,n,tm in EVENTS if 0 <= (date.fromisoformat(ds)-date.today()).days <= 1]
    if upcoming and self.d["settings"].get("reminders",True): r.after(900,lambda:messagebox.showinfo("Upcoming exam/practical","\n".join(upcoming)))
 def style(self):
    s=ttk.Style(); s.theme_use("clam"); s.configure("Treeview",background=PANEL,foreground=FG,fieldbackground=PANEL,rowheight=28,font=("Segoe UI",10)); s.configure("Treeview.Heading",background=PANEL2,foreground=FG,font=("Segoe UI",10,"bold")); s.map("Treeview",background=[("selected",PURPLE)]); s.configure("TProgressbar",troughcolor=PANEL2,background=GREEN,thickness=8); s.configure("TCombobox",fieldbackground=PANEL2,background=PANEL2,foreground=FG)
 def label(self,p,t,size=10,color=FG,bold=False): return tk.Label(p,text=t,bg=p.cget("bg"),fg=color,font=("Segoe UI",size,"bold" if bold else "normal"))
 def btn(self,p,t,fn,color=PURPLE): return tk.Button(p,text=t,command=fn,bg=color,fg="white",activebackground=color,relief="flat",bd=0,padx=11,pady=8,cursor="hand2",font=("Segoe UI",9,"bold"))
 def card(self,p): return tk.Frame(p,bg=PANEL,padx=14,pady=12,highlightthickness=1,highlightbackground="#263451")
 def shell(self):
    h=tk.Frame(self.r,bg=BG,padx=20,pady=14); h.pack(fill="x"); tk.Label(h,text="◈ STUDYHUB",bg=BG,fg="#c4b5fd",font=("Segoe UI",22,"bold")).pack(side="left"); tk.Label(h,text="SMART STUDY ASSISTANT • V3",bg=BG,fg=MUTED,font=("Segoe UI",10)).pack(side="left",padx=14); tk.Label(h,text=date.today().strftime("%A • %d %B %Y"),bg=BG,fg=FG,font=("Segoe UI",10,"bold")).pack(side="right")
    nav=tk.Frame(self.r,bg=BG,padx=20); nav.pack(fill="x",pady=(0,10))
    for n,f in [("Dashboard",self.dashboard),("Syllabus",self.syllabus),("Notes & Search",self.notes_page),("Flashcards / Quiz",self.quiz_page),("Calendar",self.calendar_page),("Study Log / Reports",self.log_page)]: self.btn(nav,n,f,PANEL2).pack(side="left",padx=(0,5))
    self.body=tk.Frame(self.r,bg=BG,padx=20); self.body.pack(fill="both",expand=True); tk.Label(self.r,text="Recall → Practice → Check mistakes → Schedule revision",bg=BG,fg=MUTED,pady=8,font=("Segoe UI",9)).pack(fill="x")
 def clear(self):
    for w in self.body.winfo_children(): w.destroy()
 def counts(self,s):
    a=self.d["topics"].get(s,[]); return sum(t["status"]=="Completed" for t in a),len(a)
 def priorities(self):
    scores={}; today=date.today()
    for s,dt in EXAMS.items():
     days=(dt-today).days
     if days<0: continue
     done,total=self.counts(s); urgency=1+28/max(2,days+2)
     if s=="CNM" and days>20: urgency+=.6
     if s=="DAA" and days>10: urgency+=.35
     if s=="SEPM" and days>25: urgency*=.45
     scores[s]=urgency*max(.1,(total-done)/max(1,total))
    return sorted(scores,key=scores.get,reverse=True)
 def next_topic(self,s):
    a=self.d["topics"].get(s,[]); due=[t for t in a if t.get("next_review") and t["next_review"]<=date.today().isoformat() and t["status"]!="Not started"]
    if due:return sorted(due,key=lambda t:(t["confidence"],t["next_review"]))[0]
    pending=[t for t in a if t["status"]!="Completed"] or a; order={"Not started":0,"In progress":1,"Revised":2,"Completed":3}
    return sorted(pending,key=lambda t:(order.get(t["status"],0),t["confidence"],t.get("last","")))[0] if pending else None
 def due(self): return [(s,t) for s,a in self.d["topics"].items() for t in a if t.get("next_review") and t["next_review"]<=date.today().isoformat() and t["status"]!="Not started"]
 def scan(self):
    NOTES.mkdir(exist_ok=True); self.notes=[{"path":str(p),"name":p.name,"subject":subj(p)} for p in NOTES.rglob("*") if p.is_file() and p.suffix.lower() in EXTS and not p.name.startswith("ADD_YOUR") and not p.name.startswith("~$")]
 def dashboard(self):
    self.clear(); self.label(self.body,"Your study cockpit",24,FG,True).pack(anchor="w"); self.label(self.body,"Daily plan, revision queue, notes and exam countdowns.",11,MUTED).pack(anchor="w",pady=(4,12))
    m=tk.Frame(self.body,bg=BG); m.pack(fill="x",pady=(0,12)); done=sum(self.counts(s)[0] for s in EXAMS); total=sum(self.counts(s)[1] for s in EXAMS)
    for title,val,sub in [("SYLLABUS",f"{done}/{total}",f"{done/max(1,total):.0%} complete"),("NOTES FILES",str(len(self.notes)),"Imported resources"),("REVIEWS DUE",str(len(self.due())),"Spaced repetition"),("STUDY SESSIONS",str(len(self.d["log"])),"Logged sessions")]:
     c=self.card(m); c.pack(side="left",fill="both",expand=True,padx=(0,8)); self.label(c,title,9,MUTED,True).pack(anchor="w"); self.label(c,val,22,FG,True).pack(anchor="w",pady=(4,0)); self.label(c,sub,9,MUTED).pack(anchor="w")
    row=tk.Frame(self.body,bg=BG); row.pack(fill="both",expand=True); left=self.card(row); left.pack(side="left",fill="both",expand=True,padx=(0,10)); self.label(left,"TODAY'S RECOMMENDED PLAN",12,"#c4b5fd",True).pack(anchor="w")
    for i,s in enumerate(self.priorities()[:3]):
     t=self.next_topic(s)
     if not t:continue
     x=tk.Frame(left,bg=PANEL2,padx=10,pady=10); x.pack(fill="x",pady=5); tk.Label(x,text=f"{i+1:02}  {s}",bg=PANEL2,fg=COLORS[s],font=("Segoe UI",11,"bold")).pack(side="left",padx=(0,12)); tk.Label(x,text=f"{t['unit']} • {t['name']}",bg=PANEL2,fg=FG,wraplength=430,justify="left",font=("Segoe UI",10,"bold")).pack(side="left",fill="x",expand=True); tk.Label(x,text=f"{[90,45,30][i]} min",bg=PANEL2,fg=GREEN).pack(side="right")
    self.btn(left,"Start quiz",self.quiz_page).pack(anchor="w",pady=(8,0))
    right=self.card(row); right.pack(side="right",fill="y"); self.label(right,"SUBJECT PROGRESS",11,"#c4b5fd",True).pack(anchor="w")
    for s in EXAMS:
     d,n=self.counts(s); self.label(right,f"{s}  {d}/{n}  ({d/max(1,n):.0%})",9,COLORS[s],True).pack(anchor="w",pady=(5,0)); ttk.Progressbar(right,maximum=100,value=d/max(1,n)*100,length=230).pack(fill="x",pady=(2,3))
 def syllabus(self):
    self.clear(); self.label(self.body,"Syllabus & spaced repetition",22,FG,True).pack(anchor="w"); self.label(self.body,"Update status, confidence and weak-topic notes. Reviews are scheduled at 1, 3, 7 and 14 days.",10,MUTED).pack(anchor="w",pady=(4,10))
    top=tk.Frame(self.body,bg=BG); top.pack(fill="x",pady=(0,8)); self.svar=tk.StringVar(value=self.subject); ttk.Combobox(top,textvariable=self.svar,values=list(EXAMS),state="readonly",width=10).pack(side="left")
    self.tree=ttk.Treeview(self.body,columns=("unit","status","conf","review"),show="tree headings")
    for c,t in [("#0","Topic"),("unit","Unit"),("status","Status"),("conf","Confidence / 5"),("review","Next review")]: self.tree.heading(c,text=t)
    self.tree.column("#0",width=430); self.tree.column("unit",width=150); self.tree.column("status",width=125); self.tree.column("conf",width=110); self.tree.column("review",width=130); self.tree.pack(fill="both",expand=True); self.svar.trace_add("write",lambda *_:self.fill_topics())
    c=tk.Frame(self.body,bg=BG,pady=8); c.pack(fill="x"); self.st=tk.StringVar(value="In progress"); ttk.Combobox(c,textvariable=self.st,values=["Not started","In progress","Completed","Revised"],state="readonly",width=14).pack(side="left",padx=(0,7)); self.cf=tk.StringVar(value="3"); ttk.Combobox(c,textvariable=self.cf,values=list("012345"),state="readonly",width=5).pack(side="left",padx=(0,7)); self.note=tk.StringVar(); tk.Entry(c,textvariable=self.note,bg=PANEL2,fg=FG,insertbackground=FG,relief="flat",width=32).pack(side="left",ipady=7,padx=(0,7)); self.btn(c,"Save selected",self.save_topic).pack(side="left"); self.fill_topics()
 def fill_topics(self):
    self.subject=self.svar.get()
    for i in self.tree.get_children():self.tree.delete(i)
    for i,t in enumerate(self.d["topics"].get(self.subject,[])):self.tree.insert("","end",iid=str(i),text=t["name"],values=(t["unit"],t["status"],t["confidence"],t.get("next_review","—") or "—"))
    self.tree.bind("<<TreeviewSelect>>",self.select_topic)
 def select_topic(self,e=None):
    sel=self.tree.selection()
    if sel:
     t=self.d["topics"][self.subject][int(sel[0])]; self.st.set(t["status"]); self.cf.set(str(t["confidence"])); self.note.set(t.get("notes",""))
 def schedule_review(self,t,known=True):
    stage=int(t.get("stage",0)); delay=DELAYS[min(stage,3)] if known else 1; t["next_review"]=(date.today()+timedelta(days=delay)).isoformat(); t["stage"]=min(stage+1,3) if known else 0
 def save_topic(self):
    sel=self.tree.selection()
    if not sel:messagebox.showinfo("Select topic","Select a topic first.");return
    t=self.d["topics"][self.subject][int(sel[0])];t.update(status=self.st.get(),confidence=int(self.cf.get()),notes=self.note.get(),last=date.today().isoformat())
    if t["status"] in {"Completed","Revised"}:self.schedule_review(t)
    save(self.d);self.fill_topics();self.tree.selection_set(sel[0]);messagebox.showinfo("Saved","Progress saved and next review scheduled.")
 def notes_page(self):
    self.scan();self.clear();self.label(self.body,"Notes library & search",22,FG,True).pack(anchor="w");self.label(self.body,"Import a folder or files. Search extracted text, preview and open originals.",10,MUTED).pack(anchor="w",pady=(4,10))
    bar=tk.Frame(self.body,bg=BG);bar.pack(fill="x",pady=(0,8));self.q=tk.StringVar();tk.Entry(bar,textvariable=self.q,bg=PANEL2,fg=FG,insertbackground=FG,relief="flat").pack(side="left",fill="x",expand=True,ipady=8,padx=(0,7));self.btn(bar,"Search",self.search_notes).pack(side="left",padx=3);self.btn(bar,"Import folder",self.import_folder,"#37466b").pack(side="left",padx=3);self.btn(bar,"Add files",self.add_files,"#37466b").pack(side="left",padx=3)
    b=tk.Frame(self.body,bg=BG);b.pack(fill="both",expand=True);self.nl=tk.Listbox(b,bg=PANEL,fg=FG,selectbackground=PURPLE,width=36,font=("Segoe UI",10),relief="flat");self.nl.pack(side="left",fill="y",padx=(0,8));self.nl.bind("<<ListboxSelect>>",self.preview);right=self.card(b);right.pack(side="left",fill="both",expand=True);self.nt=tk.Label(right,text="Select a note",bg=PANEL,fg="#c4b5fd",anchor="w",font=("Segoe UI",12,"bold"));self.nt.pack(fill="x");self.pv=tk.Text(right,bg="#0f172a",fg=FG,wrap="word",relief="flat",font=("Consolas",10));self.pv.pack(fill="both",expand=True,pady=8);self.btn(right,"Open original",self.open_note,"#37466b").pack(anchor="w");self.render_notes(self.notes)
 def render_notes(self,items):
    self.displayed=items;self.nl.delete(0,"end")
    for n in items:self.nl.insert("end",f"[{n['subject']}] {n['name']}")
 def search_notes(self):
    q=self.q.get().strip().lower()
    if not q:self.render_notes(self.notes);return
    found=[]
    for n in self.notes:
     p=Path(n["path"])
     if q in (n["name"]+" "+n["subject"]+" "+extract(p)).lower():found.append(n)
    self.render_notes(found)
    if not found:messagebox.showinfo("No matches","No match found. Install pypdf/python-docx for PDF/DOCX extraction; scanned PDFs may need OCR.")
 def preview(self,e=None):
    sel=self.nl.curselection()
    if not sel:return
    self.current_note=self.displayed[sel[0]];p=Path(self.current_note["path"]);self.nt.config(text=f"[{self.current_note['subject']}] {p.name}");self.pv.delete("1.0","end");self.pv.insert("1.0",extract(p)[:100000])
 def open_note(self):
    if not self.current_note:messagebox.showinfo("Select note","Select a note first.");return
    p=self.current_note["path"]
    try:
     if sys.platform.startswith("win"):os.startfile(p)
     elif sys.platform=="darwin":subprocess.Popen(["open",p])
     else:subprocess.Popen(["xdg-open",p])
    except Exception as e:messagebox.showerror("Open failed",str(e))
 def import_folder(self):
    folder=filedialog.askdirectory(title="Select folder with your study notes")
    if not folder:return
    src=Path(folder);count=0
    for p in src.rglob("*"):
     if p.is_file() and p.suffix.lower() in EXTS and not p.name.startswith("~$"):
      destdir=NOTES/src.name;destdir.mkdir(parents=True,exist_ok=True);dest=destdir/p.name;i=1
      while dest.exists():dest=destdir/f"{p.stem}_{i}{p.suffix}";i+=1
      try:shutil.copy2(p,dest);count+=1
      except Exception:pass
    self.scan();self.render_notes(self.notes);messagebox.showinfo("Imported",f"Imported {count} files. Original files unchanged.")
 def add_files(self):
    fs=filedialog.askopenfilenames(filetypes=[("Study notes","*.pdf *.docx *.txt *.md *.rtf *.py *.c *.cpp *.java *.html *.csv"),("All files","*.*")]);count=0
    for f in fs:
     p=Path(f)
     if p.suffix.lower() not in EXTS:continue
     dest=NOTES/p.name;i=1
     while dest.exists():dest=NOTES/f"{p.stem}_{i}{p.suffix}";i+=1
     shutil.copy2(p,dest);count+=1
    self.scan();self.render_notes(self.notes);messagebox.showinfo("Added",f"Added {count} files.")
 def calendar_page(self):
    self.clear();self.label(self.body,"Exam & practical calendar",22,FG,True).pack(anchor="w");self.label(self.body,"Dates currently configured from your plan.",10,MUTED).pack(anchor="w",pady=(4,10));tree=ttk.Treeview(self.body,columns=("date","left","time"),show="tree headings")
    for c,t in [("#0","Event"),("date","Date"),("left","Days remaining"),("time","Time")]:tree.heading(c,text=t)
    tree.column("#0",width=460);tree.column("date",width=150);tree.column("left",width=130);tree.column("time",width=210)
    for ds,n,tm in EVENTS:
     d=date.fromisoformat(ds);delta=(d-date.today()).days;tree.insert("","end",text=n,values=(d.strftime("%d %b %Y"),str(delta) if delta>=0 else "Passed",tm))
    tree.pack(fill="both",expand=True);self.btn(self.body,"Export calendar CSV",self.export_calendar).pack(anchor="w",pady=10)
 def export_calendar(self):
    p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="exam_calendar.csv")
    if not p:return
    with open(p,"w",newline="",encoding="utf-8") as f:
     w=csv.writer(f);w.writerow(["Date","Event","Time"]);w.writerows(EVENTS)
    messagebox.showinfo("Exported",f"Saved {p}")
 def quiz_page(self):
    self.clear();self.label(self.body,"Flashcards & quick quiz",22,FG,True).pack(anchor="w");self.label(self.body,"Topic prompts are syllabus-based. Note-derived cards quote extracted source text for you to review.",10,MUTED).pack(anchor="w",pady=(4,10))
    bar=tk.Frame(self.body,bg=BG);bar.pack(fill="x",pady=(0,8));self.qsub=tk.StringVar(value=self.subject);ttk.Combobox(bar,textvariable=self.qsub,values=list(EXAMS),state="readonly",width=10).pack(side="left",padx=(0,7));self.btn(bar,"Quiz syllabus",self.topic_quiz).pack(side="left",padx=3);self.btn(bar,"Generate prompts from selected note",self.note_cards,"#37466b").pack(side="left",padx=3);self.btn(bar,"Create flashcard",self.manual_card,"#37466b").pack(side="left",padx=3)
    c=self.card(self.body);c.pack(fill="both",expand=True,pady=(8,0));self.quiztext=tk.Text(c,bg="#0f172a",fg=FG,wrap="word",font=("Segoe UI",13),relief="flat",padx=14,pady=14);self.quiztext.pack(fill="both",expand=True);row=tk.Frame(c,bg=PANEL);row.pack(fill="x",pady=(8,0))
    self.btn(row,"Reveal answer",self.reveal,"#37466b").pack(side="left",padx=3);self.btn(row,"I knew it ✓",lambda:self.rate(True),GREEN).pack(side="left",padx=3);self.btn(row,"Review again",lambda:self.rate(False),"#b45309").pack(side="left",padx=3);self.btn(row,"Next",self.next_card).pack(side="left",padx=3)
    self.items=[];self.idx=0;self.card_now=None;self.quiztext.insert("1.0","Choose a quiz mode or create flashcards to begin.")
 def topic_quiz(self):
    s=self.qsub.get();arr=self.d["topics"][s];self.items=[{"q":f"Explain or solve: {t['name']} ({t['unit']})","a":"Answer from your class notes: state the definition or method, write formulas/steps, and work through an example. Verify against your notes.","subject":s,"topic":t["name"]} for t in arr if t["status"]!="Completed"] or [{"q":f"Revise {t['name']}","a":"Recall key points and one example from your notes.","subject":s,"topic":t["name"]} for t in arr];self.idx=0;self.next_card()
 def note_cards(self):
    if not self.current_note or not Path(self.current_note["path"]).exists():messagebox.showinfo("Select a note","Open Notes & Search and select a note first.");return
    content=extract(Path(self.current_note["path"]));paras=[x.strip() for x in re.split(r"\n\s*\n",content) if len(x.strip())>60]
    if not paras:messagebox.showinfo("No readable text","This file has no extractable text. Scanned PDFs need OCR.");return
    self.items=[{"q":"Explain this point in your own words:\n\n"+p[:220],"a":p[:2500],"subject":self.current_note["subject"] if self.current_note["subject"] in EXAMS else "PS","topic":self.current_note["name"]} for p in paras[:80]];self.idx=0;self.next_card();messagebox.showinfo("Prompts created",f"Created {len(self.items)} prompts from extracted text. They are not independently verified Q&A.")
 def manual_card(self):
    w=tk.Toplevel(self.r);w.title("Create flashcard");w.geometry("560x390");w.configure(bg=BG);q=tk.Text(w,height=5,bg=PANEL2,fg=FG);a=tk.Text(w,height=8,bg=PANEL2,fg=FG)
    self.label(w,"Question / prompt",10,FG,True).pack(anchor="w",padx=12,pady=(12,4));q.pack(fill="x",padx=12);self.label(w,"Answer / key points",10,FG,True).pack(anchor="w",padx=12,pady=(8,4));a.pack(fill="both",expand=True,padx=12)
    def savecard():
     question=q.get("1.0","end").strip();answer=a.get("1.0","end").strip()
     if not question or not answer:messagebox.showwarning("Missing","Enter both question and answer.");return
     self.d["cards"].append({"q":question,"a":answer,"subject":self.subject,"topic":"Manual flashcard"});save(self.d);w.destroy();messagebox.showinfo("Saved","Card saved.")
    self.btn(w,"Save flashcard",savecard).pack(pady=10)
 def next_card(self):
    if not self.items:self.items=list(self.d.get("cards",[]))
    if not self.items:self.quiztext.delete("1.0","end");self.quiztext.insert("1.0","No cards yet. Start a syllabus quiz or create a flashcard.");return
    self.card_now=self.items[self.idx%len(self.items)];self.quiztext.delete("1.0","end");self.quiztext.insert("1.0","QUESTION / PROMPT\n\n"+self.card_now["q"]+"\n\nTry to answer before revealing.")
 def reveal(self):
    if self.card_now:self.quiztext.insert("end","\n\nANSWER / SOURCE EXTRACT\n\n"+self.card_now["a"])
 def rate(self,knew):
    if not self.card_now:return
    s=self.card_now.get("subject","PS");name=self.card_now.get("topic","");t=next((x for x in self.d["topics"].get(s,[]) if x["name"]==name),None)
    conf=0
    if t:
     t["confidence"]=min(5,t["confidence"]+1) if knew else max(0,t["confidence"]-1);t["status"]="Revised";t["last"]=date.today().isoformat();self.schedule(t,knew);conf=t["confidence"]
    self.d["log"].append({"date":date.today().isoformat(),"subject":s,"topic":name,"result":"Quiz knew it" if knew else "Quiz review again","minutes":0,"confidence":conf,"note":""});save(self.d);self.idx+=1;self.next_card()
 def schedule(self,t,knew=True):
    stage=int(t.get("stage",0));t["next_review"]=(date.today()+timedelta(days=DELAYS[min(stage,3)] if knew else 1)).isoformat();t["stage"]=min(stage+1,3) if knew else 0
 def log_page(self):
    self.clear();self.label(self.body,"Study log & daily reports",22,FG,True).pack(anchor="w");self.label(self.body,"Record work and export your daily report or complete session history.",10,MUTED).pack(anchor="w",pady=(4,10));c=self.card(self.body);c.pack(fill="x")
    row=tk.Frame(c,bg=PANEL);row.pack(fill="x");self.lsub=tk.StringVar(value=self.subject);self.lres=tk.StringVar(value="Completed");self.lmin=tk.StringVar(value="30");self.lconf=tk.StringVar(value="3");self.lnote=tk.StringVar()
    for lab,var,vals,width in [("Subject",self.lsub,list(EXAMS),9),("Result",self.lres,["Completed","Partially done","Revision","Skipped"],15),("Confidence",self.lconf,list("012345"),6)]:
     col=tk.Frame(row,bg=PANEL);col.pack(side="left",padx=(0,12));self.label(col,lab,9,MUTED,True).pack(anchor="w");ttk.Combobox(col,textvariable=var,values=vals,state="readonly",width=width).pack(pady=(4,0))
    col=tk.Frame(row,bg=PANEL);col.pack(side="left");self.label(col,"Minutes",9,MUTED,True).pack(anchor="w");tk.Entry(col,textvariable=self.lmin,bg=PANEL2,fg=FG,width=7,relief="flat").pack(pady=(4,0),ipady=5)
    self.label(c,"Topic / difficulty note",9,MUTED,True).pack(anchor="w",pady=(10,4));tk.Entry(c,textvariable=self.lnote,bg=PANEL2,fg=FG,insertbackground=FG,relief="flat").pack(fill="x",ipady=7);self.btn(c,"Save session",self.save_log).pack(anchor="w",pady=(10,0))
    b=tk.Frame(self.body,bg=BG);b.pack(fill="both",expand=True,pady=(10,0));h=self.card(b);h.pack(side="left",fill="both",expand=True,padx=(0,8));self.label(h,"RECENT SESSIONS",11,"#c4b5fd",True).pack(anchor="w");self.logtext=tk.Text(h,bg="#0f172a",fg=FG,relief="flat",font=("Consolas",10));self.logtext.pack(fill="both",expand=True,pady=(7,0));a=self.card(b);a.pack(side="right",fill="y");self.label(a,"REPORTS",11,"#c4b5fd",True).pack(anchor="w");self.btn(a,"Export study log CSV",self.export_log,"#37466b").pack(fill="x",pady=(10,6));self.btn(a,"Save today's report",self.today_report,"#37466b").pack(fill="x",pady=6);self.render_log()
 def save_log(self):
    s=self.lsub.get();t=self.next_topic(s);result=self.lres.get()
    if not t:return
    if result=="Completed":t["status"]="Completed"
    elif result=="Partially done":t["status"]="In progress"
    elif result=="Revision":t["status"]="Revised"
    t["confidence"]=int(self.lconf.get());t["last"]=date.today().isoformat();note=self.lnote.get().strip()
    if note:t["notes"]=note
    try:mins=max(0,int(self.lmin.get()))
    except:mins=30
    if result in {"Completed","Revision"}:self.schedule(t)
    self.d["log"].append({"date":date.today().isoformat(),"subject":s,"topic":t["name"],"result":result,"minutes":mins,"confidence":t["confidence"],"note":note});save(self.d);self.render_log();messagebox.showinfo("Saved","Session recorded.")
 def render_log(self):
    if not hasattr(self,"logtext"):return
    self.logtext.delete("1.0","end")
    for x in self.d["log"][-100:][::-1]:self.logtext.insert("end",f"{x['date']} | {x['subject']} | {x['minutes']} min | {x['result']}\n  {x['topic']} | confidence {x['confidence']}/5\n  {x.get('note','')}\n\n")
 def export_log(self):
    p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="study_log.csv")
    if not p:return
    with open(p,"w",newline="",encoding="utf-8") as f:w=csv.DictWriter(f,fieldnames=["date","subject","topic","result","minutes","confidence","note"]);w.writeheader();w.writerows(self.d["log"])
    messagebox.showinfo("Exported",f"Saved {p}")
 def today_report(self):
    today=date.today().isoformat();items=[x for x in self.d["log"] if x["date"]==today];mins=sum(x.get("minutes",0) for x in items);lines=[f"StudyHub report — {today}",f"Sessions: {len(items)}",f"Minutes studied: {mins}",f"Hours studied: {mins/60:.2f}","","Sessions:"]
    lines += [f"- {x['subject']}: {x['topic']} — {x['result']} ({x.get('minutes',0)} min)" for x in items];lines+=["","Low-confidence topics:"]
    lines += [f"- {s}: {t['name']} ({t['confidence']}/5)" for s,a in self.d["topics"].items() for t in a if t["confidence"]<=2 and t["status"] in {"In progress","Revised","Completed"}]
    p=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text report","*.txt")],initialfile=f"study_report_{today}.txt")
    if p:Path(p).write_text("\n".join(lines),encoding="utf-8");messagebox.showinfo("Saved",f"Report saved to {p}")

if __name__=="__main__":
 NOTES.mkdir(exist_ok=True); root=tk.Tk(); app=App(root); root.mainloop()

#!/usr/bin/env python3
"""
Exam Study Tracker
A local-first, dependency-free study planner for the user's 2026 exam schedule.

Run:
    python exam_tracker.py

Data is saved in exam_tracker_data.json beside this script.
Edit TOPICS below to customize the syllabus.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "exam_tracker_data.json"
TODAY = date.today()

# Exam dates supplied by the user. PS is set to 28 October based on the latest
# timetable correction in the conversation. Change dates here if your college
# publishes a different final schedule.
EXAMS = {
    "PS": date(2026, 10, 28),
    "IAM": date(2026, 11, 23),
    "ICS": date(2026, 11, 25),
    "AIMLT": date(2026, 11, 27),
    "DAA": date(2026, 12, 1),
    "CNM": date(2026, 12, 2),
    "SEPM": date(2026, 12, 22),
}

EVENTS = [
    {"date": "2026-10-26", "time": "2:15–4:15 PM", "name": "PBL III external practical"},
    {"date": "2026-10-27", "time": "2:15–4:15 PM (may take all day)", "name": "FSDL internal practical"},
    {"date": "2026-10-29", "time": "2:15–4:15 PM", "name": "AIMLT oral exam"},
    {"date": "2026-10-30", "time": "2:15–4:15 PM", "name": "ICS oral exam"},
    {"date": "2026-10-31", "time": "2:15–4:15 PM", "name": "IAM oral exam"},
]

# Source-derived topic lists from the uploaded syllabus. CNM entries are
# transcribed conservatively from the handwritten syllabus image; edit unclear
# wording to match your class notes.
TOPICS = {
    "PS": {
        "Unit I": [
            "Introduction to basic statistics", "Mean and median",
            "Standard deviation and examples", "Dispersion and coefficient of variation",
            "Moments", "Skewness and kurtosis",
        ],
        "Unit II": [
            "Introduction to random variables", "Discrete random variables and examples",
            "Continuous random variables and distribution functions",
            "Cumulative distribution function (CDF)", "Mathematical expectation",
            "Variance and standard deviation", "Joint distribution and joint density function",
        ],
        "Unit III": [
            "Rank correlation for distinct ranks", "Rank correlation for repeated ranks",
            "Coefficient of correlation", "Linear regression",
            "Method of least squares: fit a straight line",
            "Fitting an exponential curve", "Fitting a parabolic curve",
        ],
        "Unit IV": [
            "Basic probability and conditional probability", "Independent events",
            "Bayes' theorem and examples", "Binomial distribution",
            "Poisson distribution", "Normal distribution",
            "Geometric distribution", "Exponential distribution",
        ],
        "Unit V": [
            "Population, sample and sampling", "Estimation of parameters and standard error",
            "Statistical hypothesis and testing a hypothesis",
            "One-tailed and two-tailed tests; Type I and Type II errors",
            "Level of significance", "Student's t-test and problems",
            "Chi-square goodness-of-fit test", "Chi-square test of independence",
            "F-test",
        ],
    },
    "CNM": {
        "Unit I / Differential equations": [
            "Linear differential equations", "Auxiliary equation and complementary function",
            "Particular integral (PI)", "Differential equations: practice problems",
        ],
        "Unit II / PDE and transforms": [
            "Formation/solution of PDE (verify exact topic from notes)",
            "Lagrange's method", "Laplace transforms",
            "Inverse Laplace transforms", "Applications of Laplace transforms",
        ],
        "Unit III / Applications": [
            "Applications: Fourier shift", "Second shift theorem",
            "Direct delta / impulse function (verify wording from notes)",
        ],
        "Unit IV / Numerical methods": [
            "Difference tables", "Forward and backward differences",
            "Newton forward interpolation", "Newton backward interpolation",
            "Lagrange interpolation", "Numerical integration: trapezoidal rule",
            "Simpson's 1/3 rule", "Simpson's 3/8 rule",
            "Numerical solution methods: Euler's method",
            "Runge-Kutta order 2", "Runge-Kutta order 4",
        ],
    },
    "IAM": {
        "Unit I": [
            "Identity, entitlement, provisioning and de-provisioning",
            "IAM lifecycle and consequences of weak identity management",
            "Authentication factors and multi-factor authentication",
            "Physical/logical access, segregation of duties and IAAA",
            "IAM framework and principle of least privilege",
            "Identification proofing, biometrics, RFID and data visibility",
            "Assets, perimeter security and Consumer IAM",
        ],
        "Unit II": [
            "Access control models: MAC, DAC and RBAC",
            "Access matrix model", "RBAC flow, hierarchy and separation of duty",
            "RBAC consistency properties", "Schematic protection model and SPM rules",
            "Privileged access management and access-control attacks",
            "BLP and BIBA models; information-flow comparison",
            "Chinese wall problem", "Take-grant protection model and safety problem",
        ],
        "Unit III": [
            "IAM governance and stakeholders", "Self-service and automation",
            "Organizational processes and approval", "Culture and awareness",
            "Centralized vs decentralized approaches", "Federated identity management",
            "Single Sign-On (SSO)", "IAM guidance, standards, policy vs procedure",
        ],
        "Unit IV": [
            "Cloud services and cloud service models", "Cloud IAM use cases and requirements",
            "MFA concepts and implementation", "IAM implementation and password options",
            "Cloud considerations", "Firebase Backend-as-a-Service",
        ],
        "Unit V": [
            "Kerberos", "TACACS/TACACS+ and DIAMETER", "RADIUS",
            "SAML, OAuth and OpenID comparison", "Trust paradigms and attribute certificates",
            "IAM case studies in retail/banking", "OSI model, SSL and TLS",
            "XACML components", "Active Directory and LDAP",
            "PKI and trust establishment", "Commercial IAM tools and current issues",
        ],
    },
    "ICS": {
        "Unit I": [
            "Information security fundamentals and security attacks",
            "Cryptography, cryptanalysis and network security model",
            "Substitution/transposition: Caesar, Playfair and Rail Fence",
            "One-time pad and steganography", "Block vs stream ciphers and modes",
            "DES and AES", "RC5 and Blowfish",
        ],
        "Unit II": [
            "Prime numbers and modular arithmetic", "Euclidean algorithm",
            "RSA algorithm and numerical problems", "Public-key cryptography",
            "Chinese remainder theorem", "Fermat and Euler theorems",
            "Miller-Rabin primality test", "Discrete logarithm",
            "Elliptic-curve cryptography (ECC)", "Homomorphic encryption",
        ],
        "Unit III": [
            "Diffie-Hellman key exchange", "Message authentication and digital signatures",
            "MD5 and SHA secure hash functions", "Symmetric key distribution",
            "Kerberos security", "Password, two-way and biometric authentication",
            "X.509 certificates and PKI", "Distribution of public keys",
        ],
        "Unit IV": [
            "Network security fundamentals and layer-wise concerns",
            "Packet-filtering, stateless and stateful firewalls",
            "Social engineering, cyberstalking and ransomware",
            "Cybercrime types, criminals, tools and legal perspectives",
            "IPSec security", "Email security: PGP and S/MIME",
            "Wireless security", "Host-based vs network-based IDS", "SSL security",
        ],
        "Unit V": [
            "Proxy servers, anonymizers and phishing",
            "Password cracking tools, keyloggers and spyware",
            "Cybersecurity safeguards and access control/audit/authentication",
            "Indian cyber laws and IT Act", "ISO 27000 and NIST security models",
            "Man-in-the-middle attacks and covert channels", "SQL injection",
            "DoS/DDoS, viruses, worms, trapdoors and salami attack",
            "Real-world cyber incident case studies",
        ],
    },
    "AIMLT": {
        "Unit I": [
            "AI definition, techniques and applications", "State-space problem formulation",
            "BFS and DFS", "Best-first search and A* algorithm",
            "Hill climbing", "Minimax algorithm", "Production systems",
            "Knowledge representation issues and approaches",
        ],
        "Unit II": [
            "Predicate logic and representing facts", "Forward and backward reasoning",
            "Non-monotonic reasoning", "Symbolic reasoning under uncertainty",
            "Expert systems", "Ontology and knowledge graphs",
            "Logic programming", "Procedural vs declarative knowledge",
            "Computable functions and predicates",
        ],
        "Unit III": [
            "Probability and Bayes theorem", "Bayesian networks and Markov networks",
            "Certainty factors", "Fuzzy logic and applications",
            "Types of ML: supervised, unsupervised, semi-supervised and reinforcement",
            "Regression vs classification", "Learning from data",
            "Anomaly detection/security analytics", "Malware detection",
        ],
        "Unit IV": [
            "Single-variable linear regression", "Multivariable regression",
            "Cost function and gradient descent", "Normal equation and non-invertibility",
            "Logistic regression and decision boundary", "Decision tree classifier",
            "Support vector machines", "Overfitting and regularization",
            "Multiclass classification: one-vs-all", "Advanced optimization",
        ],
        "Unit V": [
            "Biological neurons and model representation", "Neural-network intuition",
            "Weight initialization and training", "Backpropagation",
            "Convolutional neural networks (CNNs)", "RNNs and LSTMs",
            "Reinforcement learning", "K-means and optimization objective",
            "Multiclass cost function", "Unsupervised clustering types",
        ],
    },
    "DAA": {
        "Unit I": [
            "Linear/sequential search and binary search", "Algorithm efficiency framework",
            "Big-O, Big-Theta and Big-Omega", "Non-recursive algorithm analysis",
            "Recursive algorithm analysis", "Master theorem",
            "Recurrence solving by substitution",
        ],
        "Unit II": [
            "Divide-and-conquer principle and control abstraction",
            "Quick sort and dry runs", "Merge sort and dry runs",
            "Strassen matrix multiplication", "Greedy strategy",
            "Knapsack problem", "Job sequencing with deadlines", "Huffman encoding",
        ],
        "Unit III": [
            "Dynamic programming and principle of optimality",
            "Graph terminology and representations", "Topological sorting",
            "Dijkstra shortest path", "Prim and Kruskal MST algorithms",
            "0/1 knapsack", "AVL trees and symbol tables",
            "Optimal binary search tree", "Travelling salesperson problem",
            "Longest common subsequence", "Multistage graph",
        ],
        "Unit IV": [
            "Recursive and iterative backtracking", "8-Queens problem",
            "Hamiltonian cycle", "Branch and bound", "FIFO branch and bound",
            "Least-cost branch and bound", "0/1 knapsack using branch and bound",
        ],
        "Unit V": [
            "Hash tables and hash functions", "Good hash function properties",
            "Division, multiplication, extraction, mid-square, folding and universal hashing",
            "Collisions, probes, synonyms and overflow", "Open addressing and chaining",
            "Load factor, load density, rehashing and perfect hashing",
            "Computational complexity", "NP, NP-complete and NP-hard",
        ],
    },
    "SEPM": {
        "Unit I": [
            "Importance of software engineering and process", "Software myths",
            "Waterfall and prototype models", "Spiral and Agile models",
            "Iterative development and RUP", "Process vs project",
            "User/system requirements and SRS", "Functional vs non-functional requirements",
            "Requirements traceability, prioritization and management",
            "Security requirements engineering",
        ],
        "Unit II": [
            "OOAD and UML overview", "Use-case and activity diagrams",
            "Class and object diagrams", "Sequence, communication and timing diagrams",
            "State-machine and interaction-overview diagrams",
            "Component, deployment, package and composite-structure diagrams",
            "ER diagrams and data-flow diagrams", "Abstraction and modularity",
            "Cohesion and coupling", "Design patterns and SOA/microservices",
        ],
        "Unit III": [
            "Project management principles and metrics", "Function point analysis and LOC",
            "Make/buy decision and COCOMO II", "DevOps toolchain and continuous delivery",
            "Agile manifesto, practices and Extreme Programming",
            "JIRA/Trello and Scrum", "Team building and risk management",
            "Project planning, SWOT and manager functions",
            "IoT, data science, cloud, cybersecurity and AI-assisted development",
        ],
        "Unit IV": [
            "Software testing concepts and principles", "Verification vs validation",
            "V-model", "Unit, integration, system and acceptance testing",
            "Alpha vs beta testing", "White-box vs black-box testing",
            "Basis path and equivalence testing", "Graph-based testing and test cases",
            "Test plan and defect management", "Performance and security testing",
            "Selenium/JUnit automation", "Penetration testing, fuzzing and static analysis",
        ],
    },
}

# Subject priorities change as exams approach. Earlier dates receive a larger
# urgency boost, while CNM and DAA are deliberately kept active before December.
BASE_MINUTES = {
    "PS": 100, "CNM": 35, "IAM": 25, "ICS": 25, "AIMLT": 20, "DAA": 25, "SEPM": 10
}

def default_data() -> dict[str, Any]:
    topics = {}
    for subject, units in TOPICS.items():
        topics[subject] = []
        for unit, names in units.items():
            for name in names:
                topics[subject].append({
                    "unit": unit, "name": name, "status": "not_started",
                    "confidence": 0, "last_studied": None, "notes": ""
                })
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "topics": topics,
        "study_log": [],
        "settings": {"daily_target_hours": 3, "college_days": "weekdays"},
    }

def load_data() -> dict[str, Any]:
    if not DATA_FILE.exists():
        data = default_data()
        save_data(data)
        return data
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        # Preserve progress while adding any topics introduced in a later version.
        for subject, units in TOPICS.items():
            data.setdefault("topics", {}).setdefault(subject, [])
            existing = {x["name"] for x in data["topics"][subject]}
            for unit, names in units.items():
                for name in names:
                    if name not in existing:
                        data["topics"][subject].append({
                            "unit": unit, "name": name, "status": "not_started",
                            "confidence": 0, "last_studied": None, "notes": ""
                        })
        data.setdefault("study_log", [])
        data.setdefault("settings", {"daily_target_hours": 3})
        return data
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Could not read progress file: {exc}")
        print("Rename exam_tracker_data.json to keep it as a backup; starting fresh.")
        return default_data()

def save_data(data: dict[str, Any]) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def all_topics(data: dict[str, Any], subject: str) -> list[dict[str, Any]]:
    return data["topics"].get(subject, [])

def counts(data: dict[str, Any], subject: str) -> tuple[int, int, int]:
    ts = all_topics(data, subject)
    completed = sum(t["status"] == "completed" for t in ts)
    revised = sum(t["status"] == "revised" for t in ts)
    return completed, revised, len(ts)

def days_until(d: date) -> int:
    return (d - date.today()).days

def subject_priority(subject: str, data: dict[str, Any]) -> float:
    exam = EXAMS[subject]
    days = days_until(exam)
    completed, revised, total = counts(data, subject)
    unfinished = max(0, total - completed)
    completion_factor = unfinished / max(1, total)
    urgency = 1.0 + 28.0 / max(2, days + 2)
    if subject == "CNM" and days > 20:
        urgency += 0.6  # CNM follows DAA by one day; prepare it early.
    if subject == "DAA" and days > 10:
        urgency += 0.35
    if subject == "SEPM" and days > 25:
        urgency *= 0.45
    # Do not make a fully completed subject disappear: it still needs revision.
    revision_need = 0.25 if unfinished == 0 else 1.0
    return urgency * completion_factor * revision_need

def next_topic(data: dict[str, Any], subject: str) -> dict[str, Any] | None:
    ts = all_topics(data, subject)
    pending = [t for t in ts if t["status"] != "completed"]
    if not pending:
        # Revisit topics not revised recently; first pick never-revised ones.
        pending = [t for t in ts if t["status"] == "completed"]
    if not pending:
        return None
    # Prioritize not-started, then low confidence, then oldest study date.
    def key(t: dict[str, Any]) -> tuple:
        status_order = {"not_started": 0, "in_progress": 1, "revised": 2, "completed": 3}
        last = t.get("last_studied") or "0000-00-00"
        return (status_order.get(t["status"], 0), int(t.get("confidence", 0)), last)
    return min(pending, key=key)

def event_reminders() -> list[str]:
    out = []
    today = date.today()
    for event in EVENTS:
        event_date = date.fromisoformat(event["date"])
        delta = (event_date - today).days
        if 0 <= delta <= 3:
            when = "TODAY" if delta == 0 else ("tomorrow" if delta == 1 else f"in {delta} days")
            out.append(f"  ! {event['name']} — {when}, {event['time']}")
    return out

def show_plan(data: dict[str, Any]) -> None:
    today = date.today()
    print("\n" + "=" * 64)
    print(f"STUDY PLAN — {today.strftime('%A, %d %B %Y')}")
    print("=" * 64)
    upcoming = sorted((d, s) for s, d in EXAMS.items() if d >= today)
    if upcoming:
        print("\nUpcoming exams:")
        for d, subject in upcoming[:4]:
            print(f"  {subject:6} | {d.strftime('%d %b')} | {days_until(d)} day(s) left")
    reminders = event_reminders()
    if reminders:
        print("\nPractical/oral reminders:")
        print("\n".join(reminders))

    print("\nRecommended study blocks:")
    # Keep 2–3 subjects per day. The first subject receives the largest block.
    candidates = sorted(EXAMS, key=lambda s: subject_priority(s, data), reverse=True)
    selected = []
    for subject in candidates:
        if EXAMS[subject] < today:
            continue
        topic = next_topic(data, subject)
        if topic is not None and subject_priority(subject, data) > 0.18:
            selected.append((subject, topic))
        if len(selected) == 3:
            break
    if not selected:
        print("  All listed syllabus topics are marked completed. Use revision/mock mode.")
        return
    durations = [90, 45, 30]
    for idx, (subject, topic) in enumerate(selected):
        mins = durations[idx]
        if subject == "PS" and days_until(EXAMS["PS"]) <= 3:
            mins = 60
        status_label = topic["status"].replace("_", " ")
        print(f"\n  {idx + 1}. {subject} — {mins} minutes")
        print(f"     {topic['unit']}: {topic['name']}")
        print(f"     Status: {status_label}; confidence: {topic.get('confidence', 0)}/5")
        print("     Method: learn/recall → solve or write an answer → check mistakes.")
    print("\nFinish with 10 minutes of closed-book recall.")
    print("Use 'Log study progress' after each block so tomorrow's plan adapts.")
    print("=" * 64)

def progress_dashboard(data: dict[str, Any]) -> None:
    print("\nSYLLABUS PROGRESS")
    print("-" * 64)
    for subject in EXAMS:
        ts = all_topics(data, subject)
        total = len(ts)
        done = sum(t["status"] == "completed" for t in ts)
        in_progress = sum(t["status"] == "in_progress" for t in ts)
        revised = sum(t["status"] == "revised" for t in ts)
        pct = (done / total * 100) if total else 0
        bar = "#" * int(pct // 5) + "-" * (20 - int(pct // 5))
        print(f"{subject:6} [{bar}] {pct:5.1f}%  completed {done}/{total}, active {in_progress}, revised {revised}")
    print("\nLatest study log:")
    for entry in data["study_log"][-5:][::-1]:
        print(f"  {entry['date']} | {entry['subject']} | {entry['topic']} | {entry['result']} | {entry.get('minutes', 0)} min")

def list_topics(data: dict[str, Any]) -> None:
    subjects = list(EXAMS)
    print("\nSubjects:", ", ".join(subjects))
    subject = input("Choose subject: ").strip().upper()
    if subject not in data["topics"]:
        print("Unknown subject.")
        return
    for i, t in enumerate(all_topics(data, subject), 1):
        status = t["status"].replace("_", " ")
        print(f"{i:3}. [{status:11}] {t['unit']} — {t['name']} (confidence {t.get('confidence',0)}/5)")
    raw = input("\nEnter topic number to update, or press Enter to go back: ").strip()
    if not raw:
        return
    try:
        idx = int(raw) - 1
        topic = all_topics(data, subject)[idx]
    except (ValueError, IndexError):
        print("Invalid topic number.")
        return
    print("Statuses: 1=not started, 2=in progress, 3=completed, 4=revised")
    choices = {"1": "not_started", "2": "in_progress", "3": "completed", "4": "revised"}
    status = input("New status: ").strip()
    if status in choices:
        topic["status"] = choices[status]
        topic["last_studied"] = date.today().isoformat()
    confidence = input("Confidence 0–5 (Enter to keep current): ").strip()
    if confidence:
        try:
            topic["confidence"] = max(0, min(5, int(confidence)))
        except ValueError:
            print("Confidence unchanged.")
    notes = input("Short note/mistake (Enter to keep current): ").strip()
    if notes:
        topic["notes"] = notes
    save_data(data)
    print("Progress saved.")

def log_progress(data: dict[str, Any]) -> None:
    subject = input("Subject (PS/CNM/IAM/ICS/AIMLT/DAA/SEPM): ").strip().upper()
    if subject not in data["topics"]:
        print("Unknown subject.")
        return
    ts = all_topics(data, subject)
    for i, t in enumerate(ts, 1):
        print(f"{i:3}. [{t['status']}] {t['unit']} — {t['name']}")
    raw = input("Topic number: ").strip()
    try:
        topic = ts[int(raw) - 1]
    except (ValueError, IndexError):
        print("Invalid topic number.")
        return
    print("Result: 1=completed, 2=partially done, 3=revision, 4=not done")
    result = input("Choose result: ").strip()
    mapping = {"1": ("completed", "completed"), "2": ("in_progress", "partially done"),
               "3": ("revised", "revision"), "4": (topic["status"], "not done")}
    if result not in mapping:
        print("Invalid result.")
        return
    status, result_label = mapping[result]
    topic["status"] = status
    topic["last_studied"] = date.today().isoformat()
    confidence = input("Confidence after studying (0–5): ").strip()
    try:
        topic["confidence"] = max(0, min(5, int(confidence))) if confidence else topic.get("confidence", 0)
    except ValueError:
        pass
    minutes = input("Minutes spent (default 30): ").strip()
    try:
        minutes_value = max(0, int(minutes)) if minutes else 30
    except ValueError:
        minutes_value = 30
    note = input("What was difficult? (optional): ").strip()
    if note:
        topic["notes"] = note
    data["study_log"].append({
        "date": date.today().isoformat(), "subject": subject, "topic": topic["name"],
        "result": result_label, "minutes": minutes_value, "confidence": topic["confidence"],
        "note": note,
    })
    save_data(data)
    print("Saved. Tomorrow's recommendation will use this progress.")

def add_topic(data: dict[str, Any]) -> None:
    subject = input("Subject: ").strip().upper()
    if subject not in data["topics"]:
        print("Unknown subject.")
        return
    unit = input("Unit/section label: ").strip() or "Extra topic"
    name = input("Topic name: ").strip()
    if not name:
        print("Topic name cannot be blank.")
        return
    if any(t["name"].casefold() == name.casefold() for t in all_topics(data, subject)):
        print("That topic already exists.")
        return
    data["topics"][subject].append({
        "unit": unit, "name": name, "status": "not_started",
        "confidence": 0, "last_studied": None, "notes": ""
    })
    save_data(data)
    print("Topic added.")

def show_settings(data: dict[str, Any]) -> None:
    print("Current target:", data.get("settings", {}).get("daily_target_hours", 3), "hours/day")
    raw = input("New target hours (1–12, Enter to keep): ").strip()
    if raw:
        try:
            value = max(1, min(12, int(raw)))
            data["settings"]["daily_target_hours"] = value
            save_data(data)
            print("Target updated.")
        except ValueError:
            print("Enter a whole number.")

def main() -> None:
    data = load_data()
    while True:
        print("\n" + "=" * 48)
        print("       EXAM STUDY TRACKER")
        print("=" * 48)
        print("1. Today's recommended study plan")
        print("2. Log study progress")
        print("3. View syllabus progress dashboard")
        print("4. List/update topic status")
        print("5. Add a syllabus topic")
        print("6. Change daily study-hour target")
        print("7. Exit")
        choice = input("\nChoose 1–7: ").strip()
        if choice == "1":
            show_plan(data)
        elif choice == "2":
            log_progress(data)
        elif choice == "3":
            progress_dashboard(data)
        elif choice == "4":
            list_topics(data)
        elif choice == "5":
            add_topic(data)
        elif choice == "6":
            show_settings(data)
        elif choice == "7":
            print(f"Progress is saved in: {DATA_FILE}")
            print("Good work. Consistency beats one exhausting study day.")
            break
        else:
            print("Please choose a number from 1 to 7.")

if __name__ == "__main__":
    main()

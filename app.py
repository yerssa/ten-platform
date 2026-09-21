import streamlit as st
import pandas as pd
import numpy as np
import random
import datetime
import json
import os
import streamlit.components.v1 as components

# Проверка библиотеки для PDF
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

# ==========================================
# ТРАНСЛИТЕРАЦИЯ (Қазақша/Орысша әріптерді PDF үшін ағылшыншаға ауыстыру)
# ==========================================
def transliterate(text):
    cyrillic_to_latin = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'Қ': 'Q', 'қ': 'q', 'Ң': 'N', 'ң': 'n', 'Ғ': 'Gh', 'ғ': 'gh', 'Ү': 'U', 'ү': 'u', 'Ұ': 'U', 'ұ': 'u', 'Ө': 'O', 'ө': 'o', 'Ә': 'A', 'ә': 'a', 'І': 'I', 'і': 'i'
    }
    return ''.join(cyrillic_to_latin.get(c, c) for c in text)

# ==========================================
# МУЛЬТИЯЗЫЧНОСТЬ: ИНТЕРФЕЙС И ВОПРОСЫ
# ==========================================
UI = {
    "RU": {
        "title": "ПЛАТФОРМА TEN",
        "subtitle": "> ИНТЕЛЛЕКТУАЛЬНАЯ ОЛИМПИАДА НОВОГО ПОКОЛЕНИЯ",
        "name_input": "Ваш ник или ФИО:",
        "login_btn": "ВОЙТИ 🚀",
        "logout": "ВЫЙТИ ИЗ СИСТЕМЫ",
        "dash": "🏠 Дашборд",
        "logic": "🧩 TEN LOGIC",
        "math": "📐 TEN MATH",
        "certs": "🏆 Рейтинг и Сертификат",
        "welcome": "Добро пожаловать",
        "score": "Ваш балл TEN",
        "rank": "Глобальный рейтинг",
        "best_cat": "Лучшая категория",
        "achievements": "🏅 Ваши достижения",
        "start_logic": "Начать тест TEN LOGIC",
        "start_mod1": "Начать Module 1",
        "start_mod2": "Начать Module 2 🔓",
        "start_mod3": "Начать Module 3 🔓",
        "randomize": "🔄 Перемешать вопросы",
        "submit": "Отправить и завершить",
        "completed": "✅ Завершено!",
        "not_tested": "Не сдавал",
        "leaderboard": "🏆 ТАБЛИЦА ЛИДЕРОВ TEN",
        "cert_title": "🎓 Официальный Сертификат",
        "locked": "🔒 ЗАБЛОКИРОВАНО! Пройдите TEN LOGIC и TEN MATH для получения сертификата.",
        "download_cert": "🎓 СКАЧАТЬ PDF СЕРТИФИКАТ",
        "answer": "Ответ:",
        "participant": "Участник",
        "total_score": "Общий балл",
        "no_users": "Пока нет участников.",
        "time": "Время:",
        "time_up": "ВРЕМЯ ВЫШЛО!",
        "rand_success": "Вопросы успешно перемешаны!"
    },
    "EN": {
        "title": "TEN PLATFORM",
        "subtitle": "> NEXT-GEN INTELLECTUAL OLYMPIAD",
        "name_input": "Nickname or Full Name:",
        "login_btn": "ENTER 🚀",
        "logout": "LOGOUT",
        "dash": "🏠 Dashboard",
        "logic": "🧩 TEN LOGIC",
        "math": "📐 TEN MATH",
        "certs": "🏆 Leaderboard & Certs",
        "welcome": "Welcome back",
        "score": "Your TEN Score",
        "rank": "Global Rank",
        "best_cat": "Best Category",
        "achievements": "🏅 Your Achievements",
        "start_logic": "Start TEN LOGIC",
        "start_mod1": "Start Module 1",
        "start_mod2": "Start Module 2 🔓",
        "start_mod3": "Start Module 3 🔓",
        "randomize": "🔄 Randomize Questions",
        "submit": "Submit and Finish",
        "completed": "✅ Completed!",
        "not_tested": "Not tested",
        "leaderboard": "🏆 TEN LEADERBOARD",
        "cert_title": "🎓 Official Certificate",
        "locked": "🔒 LOCKED! Complete TEN LOGIC and TEN MATH to get your certificate.",
        "download_cert": "🎓 DOWNLOAD PDF CERTIFICATE",
        "answer": "Answer:",
        "participant": "Participant",
        "total_score": "Total Score",
        "no_users": "No participants yet.",
        "time": "Time:",
        "time_up": "TIME UP!",
        "rand_success": "Questions randomized successfully!"
    }
}

QUIZ_DATA = {
    "RU": {
        "logic": [
            {"q": "В исследовании 80% участников, которые пьют кофе каждый день, сообщили о высокой продуктивности. Какой вывод наиболее обоснован?", "opts": ["Кофе повышает продуктивность.", "Продуктивные люди чаще пьют кофе.", "Между употреблением кофе и продуктивностью есть связь, но причинность не доказана.", "Кофе никак не связан с продуктивностью."], "ans_idx": 2},
            {"q": "«Мой дедушка курил всю жизнь и прожил до 90 лет. Поэтому курение не обязательно вредно». Какая ошибка здесь допущена?", "opts": ["«Твой дедушка просто был исключением».", "Это доказывает, что курение безопасно.", "Один пример не отменяет статистические данные.", "Значит, всё зависит только от генетики."], "ans_idx": 2},
            {"q": "Человек говорит: «Этот план либо сработает, либо полностью провалится». Что стоит поставить под сомнение?", "opts": ["Сам план", "Его уверенность", "Предположение, что существует только два результата", "Его опыт"], "ans_idx": 2},
            {"q": "Если два сайта дают разную информацию, что лучше сделать?", "opts": ["Выбрать тот, который первым появился", "Выбрать тот, который нравится", "Проверить несколько надёжных источников", "Выбрать тот, где звучит убедительнее"], "ans_idx": 2},
            {"q": "Если человек сделал правильный поступок, но только потому, что боялся наказания — можно ли назвать его поступок моральным?", "opts": ["Да", "Нет", "Зависит от ситуации", "Важнее результат, чем причина"], "ans_idx": 1},
            {"q": "Что важнее при принятии решения: намерение человека или последствия его поступка?", "opts": ["Намерение", "Последствия", "Оба одинаково важны", "Зависит от ситуации"], "ans_idx": 2},
            {"q": "Если большинство людей уверены в чём-то, но у одного человека есть доказательства обратного — кому ты поверишь?", "opts": ["Большинству", "Одному человеку", "Тому, у кого сильнее доказательства", "Никому"], "ans_idx": 2},
            {"q": "Если невозможно доказать, что утверждение ложно, означает ли это, что оно может считаться истинным?", "opts": ["Да", "Нет, отсутствие опровержения не является доказательством", "Иногда", "Если большинство верит"], "ans_idx": 1},
            {"q": "Что сильнее влияет на убеждения человека?", "opts": ["Факты", "Личный опыт", "Окружение", "Всё перечисленное"], "ans_idx": 3},
            {"q": "Если человек изменил своё мнение после появления новых доказательств, это скорее говорит о том, что он:", "opts": ["Не уверен в себе", "Непостоянен", "Способен критически пересматривать свои убеждения", "Не имеет позиции"], "ans_idx": 2}
        ],
        "mod1": [
            {"q": "Если $3x - y = 12$ и $y = 3$, чему равно $x$?", "opts": ["3", "4", "5", "6"], "ans_idx": 2},
            {"q": "Чему равно 15% от 80?", "opts": ["10", "12", "15", "18"], "ans_idx": 1},
            {"q": "В прямоугольном треугольнике один острый угол равен 35°. Чему равен второй острый угол?", "opts": ["45°", "55°", "65°", "90°"], "ans_idx": 1}
        ],
        "mod2h": [
            {"q": "Если $f(x) = x^2 - 4x + 3$, чему равно $f(2)$?", "opts": ["-1", "0", "1", "3"], "ans_idx": 0},
            {"q": "Система уравнений: $x + y = 10$ и $x - y = 2$. Найдите значение $x \cdot y$.", "opts": ["16", "20", "24", "25"], "ans_idx": 2},
            {"q": "Площадь круга равна 49π. Чему равна длина его окружности?", "opts": ["7π", "14π", "21π", "49π"], "ans_idx": 1}
        ],
        "mod2e": [
            {"q": "Если $2x = 10$, чему равно $x + 3$?", "opts": ["5", "8", "10", "13"], "ans_idx": 1},
            {"q": "Чему равен периметр прямоугольника с длиной 5 и шириной 3?", "opts": ["8", "15", "16", "20"], "ans_idx": 2},
            {"q": "Упростите: $3x + 2y - x + 4y$", "opts": ["2x + 6y", "4x + 6y", "2x + 2y", "x + y"], "ans_idx": 0}
        ],
        "mod3": [
            {"q": "Если $x^2 + y^2 = 25$ и $xy = 12$, чему равно значение $(x+y)^2$?", "opts": ["37", "49", "60", "144"], "ans_idx": 1},
            {"q": "Объем шара равен $36\pi$. Чему равен его радиус?", "opts": ["2", "3", "4", "6"], "ans_idx": 1},
            {"q": "Если $3^{x+1} = 81$, чему равно $x$?", "opts": ["2", "3", "4", "5"], "ans_idx": 1}
        ]
    },
    "EN": {
        "logic": [
            {"q": "In a study, 80% of participants who drink coffee daily reported high productivity. Which conclusion is most justified?", "opts": ["Coffee increases productivity.", "Productive people drink coffee more often.", "There is a correlation between coffee and productivity, but causation is not proven.", "Coffee is not related to productivity."], "ans_idx": 2},
            {"q": "«My grandfather smoked his whole life and lived to 90. Therefore, smoking is not necessarily harmful.» What is the error here?", "opts": ["«Your grandfather was just an exception.»", "This proves that smoking is safe.", "A single example does not invalidate statistical data.", "It means everything depends only on genetics."], "ans_idx": 2},
            {"q": "A person says: «This plan will either work perfectly or fail completely.» What should be questioned?", "opts": ["The plan itself", "His confidence", "The assumption that there are only two outcomes", "His experience"], "ans_idx": 2},
            {"q": "If two websites provide different information, what is the best course of action?", "opts": ["Choose the one that appeared first", "Choose the one you like more", "Check multiple reliable sources", "Choose the one that sounds more convincing"], "ans_idx": 2},
            {"q": "If a person did the right thing only because they feared punishment, can their action be considered moral?", "opts": ["Yes", "No", "Depends on the situation", "The result is more important than the reason"], "ans_idx": 1},
            {"q": "What is more important when making a decision: a person's intention or the consequences of their action?", "opts": ["Intention", "Consequences", "Both are equally important", "Depends on the situation"], "ans_idx": 2},
            {"q": "If most people are certain of something, but one person has evidence to the contrary, who would you believe?", "opts": ["The majority", "The one person", "The one with stronger evidence", "No one"], "ans_idx": 2},
            {"q": "If it is impossible to prove a statement false, does that mean it can be considered true?", "opts": ["Yes", "No, the absence of refutation is not proof", "Sometimes", "If the majority believes it"], "ans_idx": 1},
            {"q": "What has the strongest influence on a person's beliefs?", "opts": ["Facts", "Personal experience", "Environment", "All of the above"], "ans_idx": 3},
            {"q": "If a person changes their mind after new evidence appears, this most likely indicates that they are:", "opts": ["Insecure", "Inconsistent", "Capable of critically revising their beliefs", "Without a firm position"], "ans_idx": 2}
        ],
        "mod1": [
            {"q": "If $3x - y = 12$ and $y = 3$, what is the value of $x$?", "opts": ["3", "4", "5", "6"], "ans_idx": 2},
            {"q": "What is 15% of 80?", "opts": ["10", "12", "15", "18"], "ans_idx": 1},
            {"q": "In a right triangle, one acute angle is 35°. What is the other acute angle?", "opts": ["45°", "55°", "65°", "90°"], "ans_idx": 1}
        ],
        "mod2h": [
            {"q": "If $f(x) = x^2 - 4x + 3$, what is $f(2)$?", "opts": ["-1", "0", "1", "3"], "ans_idx": 0},
            {"q": "System of equations: $x + y = 10$ and $x - y = 2$. Find the value of $x \cdot y$.", "opts": ["16", "20", "24", "25"], "ans_idx": 2},
            {"q": "A circle has an area of 49π. What is its circumference?", "opts": ["7π", "14π", "21π", "49π"], "ans_idx": 1}
        ],
        "mod2e": [
            {"q": "If $2x = 10$, what is $x + 3$?", "opts": ["5", "8", "10", "13"], "ans_idx": 1},
            {"q": "What is the perimeter of a rectangle with length 5 and width 3?", "opts": ["8", "15", "16", "20"], "ans_idx": 2},
            {"q": "Simplify: $3x + 2y - x + 4y$", "opts": ["2x + 6y", "4x + 6y", "2x + 2y", "x + y"], "ans_idx": 0}
        ],
        "mod3": [
            {"q": "If $x^2 + y^2 = 25$ and $xy = 12$, what is the value of $(x+y)^2$?", "opts": ["37", "49", "60", "144"], "ans_idx": 1},
            {"q": "A sphere has a volume of $36\pi$. What is its radius?", "opts": ["2", "3", "4", "6"], "ans_idx": 1},
            {"q": "If $3^{x+1} = 81$, what is $x$?", "opts": ["2", "3", "4", "5"], "ans_idx": 1}
        ]
    }
}

# ==========================================
# ДЕРЕКТЕР БАЗАСЫ
# ==========================================
DB_FILE = "ten_database.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', encoding='utf-8') as f: 
            json.dump({"users": {}, "logs": []}, f, ensure_ascii=False, indent=4)

def load_db():
    init_db()
    with open(DB_FILE, 'r', encoding='utf-8') as f: db = json.load(f)
    fake_users = ["Ayan", "Dias", "Alikhan", "НУ"]
    changed = False
    for fake in fake_users:
        if fake in db.get("users", {}):
            del db["users"][fake]
            changed = True
    if changed: save_db(db)
    return db

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

def log_action(username, action):
    db = load_db()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["logs"].insert(0, {"Уақыты": timestamp, "Қолданушы": username, "Әрекет": action})
    save_db(db)

def update_user_score(username, logic, math_score, total):
    db = load_db()
    if total == 0 and username in db.get("users", {}): pass 
    else:
        db["users"][username] = {"logic": logic, "math": math_score, "total": total}
        save_db(db)

# ==========================================
# БАПТАУЛАР МЕН ДИЗАЙН (CSS)
# ==========================================
st.set_page_config(page_title="TEN Competition Platform", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d0d0d; color: #ffffff; }
    h1, h2, h3, p, label, span { font-family: 'Courier New', Courier, monospace; color: #ffffff !important; }
    
    .stButton > button, .stDownloadButton > button { 
        border: 2px solid #ffffff !important; border-radius: 0px !important; 
        background-color: #000000 !important; color: #ffffff !important; 
        font-weight: bold !important; width: 100% !important; transition: 0.2s; 
    }
    .stButton > button:hover, .stDownloadButton > button:hover { 
        background-color: #ffffff !important; color: #000000 !important; border: 2px solid #ffffff !important; 
    }
    
    .stTextInput>div>div>input { background-color: #1a1a1a !important; color: #ffffff !important; border: 1px solid #ffffff !important; border-radius: 0px; font-family: 'Courier New', Courier, monospace; }
    
    div[data-baseweb="select"] > div { background-color: #1a1a1a !important; color: #ffffff !important; border: 1px solid #ffffff !important; }
    ul[data-baseweb="menu"] { background-color: #1a1a1a !important; }
    li[data-baseweb="menu-item"] { color: #ffffff !important; background-color: transparent !important; }
    li[data-baseweb="menu-item"]:hover { background-color: #333333 !important; }
    
    [data-testid="stAlert"] { background-color: #1a1a1a !important; border: 1px solid #ffffff !important; }
    [data-testid="stAlert"] * { color: #ffffff !important; }
    
    .unselectable { -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; }
    .badge { display: inline-block; padding: 5px 10px; margin: 5px; border: 1px solid #d4af37; border-radius: 5px; background-color: #1a1500; font-size: 14px; font-weight: bold; color: #d4af37; }
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# СЕССИЯ ЖАДЫ
# ==========================================
if 'lang' not in st.session_state: st.session_state.lang = "RU"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'cert_id' not in st.session_state: st.session_state.cert_id = f"TEN-2026-{random.randint(10000,99999)}"

if 'logic_started' not in st.session_state: st.session_state.logic_started = False
if 'logic_submitted' not in st.session_state: st.session_state.logic_submitted = False
if 'logic_score_100' not in st.session_state: st.session_state.logic_score_100 = 0.0

if 'math_mod1_started' not in st.session_state: st.session_state.math_mod1_started = False
if 'math_mod1_submitted' not in st.session_state: st.session_state.math_mod1_submitted = False
if 'math_mod1_score' not in st.session_state: st.session_state.math_mod1_score = 0

if 'math_mod2_started' not in st.session_state: st.session_state.math_mod2_started = False
if 'math_mod2_submitted' not in st.session_state: st.session_state.math_mod2_submitted = False
if 'math_mod2_score' not in st.session_state: st.session_state.math_mod2_score = 0
if 'math_mod2_type' not in st.session_state: st.session_state.math_mod2_type = "Hard"

if 'math_mod3_started' not in st.session_state: st.session_state.math_mod3_started = False
if 'math_mod3_submitted' not in st.session_state: st.session_state.math_mod3_submitted = False
if 'math_mod3_score' not in st.session_state: st.session_state.math_mod3_score = 0

if 'math_total_score_100' not in st.session_state: st.session_state.math_total_score_100 = 0.0

if 'seeds' not in st.session_state:
    st.session_state.seeds = {
        'logic': random.randint(1, 10000), 'mod1': random.randint(1, 10000),
        'mod2h': random.randint(1, 10000), 'mod2e': random.randint(1, 10000), 'mod3': random.randint(1, 10000)
    }

def get_shuffled_quiz(quiz_type, lang):
    rng = random.Random(st.session_state.seeds[quiz_type])
    questions = QUIZ_DATA[lang][quiz_type][:]
    q_objs = []
    for q in questions:
        opts = q["opts"][:]
        ans_text = opts[q["ans_idx"]]
        rng.shuffle(opts)
        q_objs.append({"q": q["q"], "options": opts, "answer": ans_text})
    rng.shuffle(q_objs)
    return q_objs

def reroll_seed(quiz_type):
    st.session_state.seeds[quiz_type] = random.randint(1, 10000)

# ==========================================
# 1. АВТОРИЗАЦИЯ
# ==========================================
if not st.session_state.logged_in:
    col_lang, _ = st.columns([1, 5])
    with col_lang:
        st.session_state.lang = st.selectbox("🌐 Language", ["RU", "EN"])
    
    t = UI[st.session_state.lang]
    st.title(t["title"])
    st.markdown(t["subtitle"])
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name = st.text_input(t["name_input"])
        if st.button(t["login_btn"]):
            if name:
                if name.strip().upper() == "TEN10Y":
                    st.session_state.is_admin = True
                    st.session_state.user_name = "FOUNDER"
                    log_action("FOUNDER", "Admin logged in")
                else:
                    st.session_state.is_admin = False
                    st.session_state.user_name = name.strip()
                    log_action(st.session_state.user_name, "User logged in")
                st.session_state.logged_in = True
                st.rerun()

# ==========================================
# 2. ОСНОВАТЕЛЬ КАБИНЕТІ (АДМИН)
# ==========================================
elif st.session_state.is_admin:
    st.sidebar.markdown("### 👑 FOUNDER")
    if st.sidebar.button("LOGOUT"):
        st.session_state.clear()
        st.rerun()

    st.title("👑 FOUNDER DASHBOARD")
    st.write("---")
    db = load_db()
    
    tab_users, tab_logs = st.tabs(["👥 Users", "🕵️ Logs"])
    with tab_users:
        if db.get("users"):
            users_list = [{"Participant": u, "TEN LOGIC (40%)": d["logic"], "TEN MATH (60%)": d["math"], "Total Score": d["total"]} for u, d in db["users"].items()]
            df_users = pd.DataFrame(users_list).sort_values(by="Total Score", ascending=False).reset_index(drop=True)
            df_users.insert(0, 'Rank', [f"#{i+1}" for i in range(len(df_users))])
            st.dataframe(df_users, use_container_width=True, hide_index=True)
            
    with tab_logs:
        if db.get("logs"): st.dataframe(pd.DataFrame(db["logs"]), use_container_width=True, hide_index=True)

# ==========================================
# 3. ҚАРАПАЙЫМ ОҚУШЫЛАР КАБИНЕТІ
# ==========================================
else:
    t = UI[st.session_state.lang]
    st.sidebar.selectbox("🌐 Language", ["RU", "EN"], key="lang_selector", on_change=lambda: st.session_state.update(lang=st.session_state.lang_selector))
    t = UI[st.session_state.lang]
    
    user_logic_score = round(st.session_state.logic_score_100, 1)
    user_math_score = round(st.session_state.math_total_score_100, 1)
    
    raw_total = (user_logic_score * 0.4) + (user_math_score * 0.6) if user_math_score > 0 else (user_logic_score * 0.4)
    total_score = round(raw_total, 1)

    current_user_name = st.session_state.user_name
    update_user_score(current_user_name, user_logic_score, user_math_score, total_score)
    
    db = load_db()
    users_list = [{t["participant"]: u, "TEN LOGIC": d["logic"], "TEN MATH": d["math"], t["total_score"]: d["total"]} for u, d in db.get("users", {}).items()]
    ld_data = pd.DataFrame(users_list).sort_values(by=t["total_score"], ascending=False).reset_index(drop=True)
    
    if not ld_data.empty:
        ld_data.insert(0, 'Rank', [f"#{i+1}" for i in range(len(ld_data))])
        user_idx_list = ld_data[ld_data[t["participant"]] == current_user_name].index
        user_idx = user_idx_list[0] if len(user_idx_list) > 0 else 0
        
        if total_score == 0.0:
            rank_display = t["not_tested"]
            best_cat = "N/A"
        else:
            rank_percent = max(1, round(((user_idx + 1) / len(ld_data)) * 100))
            rank_display = f"#{user_idx + 1} (Top {rank_percent}%)"
            if user_logic_score > user_math_score: best_cat = "🧠 TEN LOGIC"
            elif user_math_score > user_logic_score: best_cat = "📐 TEN MATH"
            else: best_cat = "🧠 TEN LOGIC & 📐 TEN MATH"
    else:
        rank_display = "N/A"
        best_cat = "N/A"

    st.sidebar.markdown(f"### 👤 {current_user_name}")
    st.sidebar.write(f"**{t['total_score']}:** {total_score} / 100")
    st.sidebar.write("---")
    st.sidebar.write(f"🧠 TEN LOGIC (40%): {user_logic_score}")
    st.sidebar.write(f"📐 TEN MATH (60%): {user_math_score}")
    st.sidebar.divider()
    if st.sidebar.button(t["logout"]):
        log_action(current_user_name, "Logout")
        st.session_state.clear()
        st.rerun()

    st.title(t["title"])
    st.write("---")

    tab1, tab2, tab3, tab4 = st.tabs([t["dash"], t["logic"], t["math"], t["certs"]])

    with tab1:
        st.subheader(f"{t['welcome']}, {current_user_name}! 👋")
        col1, col2, col3 = st.columns(3)
        col1.metric(t["score"], f"{total_score}")
        col2.metric(t["rank"], rank_display)
        col3.metric(t["best_cat"], best_cat)
        
        st.write("---")
        st.subheader(t["achievements"])
        badges = []
        if total_score > 0:
            if user_logic_score >= 90: badges.append("🧠 Logic Master (90%+)")
            if user_math_score >= 90: badges.append("📐 Math Genius (90%+)")
            if total_score > 85: badges.append("🔥 Top Elite")
            if not badges: badges.append("👍 Good Start")
        else:
            badges.append("🚀 Rising Star")
        st.markdown("".join([f"<span class='badge'>{b}</span>" for b in badges]), unsafe_allow_html=True)

    with tab2:
        st.subheader(t["logic"])
        if not st.session_state.logic_started:
            if st.button(t["randomize"], key="rand_log"):
                reroll_seed('logic')
                st.success(t["rand_success"])
            if st.button(t["start_logic"]):
                st.session_state.logic_started = True
                st.rerun()
        elif not st.session_state.logic_submitted:
            components.html(
                f"""
                <div id="ltimer" style="font-family: monospace; font-size: 20px; font-weight: bold; color: #fff; border: 1px solid #fff; padding: 10px; width: 200px; text-align: center;">15:00</div>
                <script>
                    var time = 900;
                    var timer = setInterval(function() {{
                        var m = Math.floor(time / 60); var s = time % 60;
                        document.getElementById("ltimer").innerHTML = "{t['time']} " + m + ":" + (s<10?"0":"") + s;
                        time--;
                        if (time < 0) {{ clearInterval(timer); document.getElementById("ltimer").innerHTML = "{t['time_up']}"; }}
                    }}, 1000);
                </script>
                """, height=50
            )
            with st.form("logic_form"):
                answers = []
                quiz_list = get_shuffled_quiz('logic', st.session_state.lang)
                for i, q in enumerate(quiz_list):
                    st.markdown(f"<div style='background:#1a1a1a; padding:10px; margin-bottom:5px;'><b>{i+1}. {q['q']}</b></div>", unsafe_allow_html=True)
                    ans = st.radio(t["answer"], q['options'], key=f"logic_q_{i}", label_visibility="collapsed", index=None)
                    answers.append((ans, q['answer']))
                    st.write("---")
                if st.form_submit_button(t["submit"]):
                    correct = sum(1 for a, truth in answers if a and truth in a)
                    st.session_state.logic_score_100 = (correct / len(quiz_list)) * 100
                    st.session_state.logic_submitted = True
                    st.rerun()
        else: 
            st.success(t["completed"])
            st.markdown(f"<h2>🧠 TEN LOGIC SCORE: {user_logic_score} / 100</h2>", unsafe_allow_html=True)

    with tab3:
        st.subheader(t["math"])
        if not st.session_state.math_mod1_started:
            if st.button(t["randomize"], key="rand_math"):
                reroll_seed('mod1')
                reroll_seed('mod2h')
                reroll_seed('mod2e')
                reroll_seed('mod3')
                st.success(t["rand_success"])
            if st.button(t["start_mod1"]):
                st.session_state.math_mod1_started = True
                st.rerun()
        elif not st.session_state.math_mod1_submitted:
            with st.form("mod1_form"):
                ans1 = []
                quiz_mod1 = get_shuffled_quiz('mod1', st.session_state.lang)
                for i, q in enumerate(quiz_mod1):
                    st.write(f"**{i+1}. {q['q']}**")
                    ans = st.radio(t["answer"], q['options'], key=f"m1_{i}", label_visibility="collapsed", index=None)
                    ans1.append((ans, q['answer']))
                if st.form_submit_button(t["submit"]):
                    corr = sum(1 for a, truth in ans1 if a and truth in a)
                    st.session_state.math_mod1_score = corr
                    st.session_state.math_mod1_submitted = True
                    if corr >= 2: st.session_state.math_mod2_type = "Hard"
                    else: st.session_state.math_mod2_type = "Easy"
                    st.rerun()
        else:
            st.success(f"✅ Module 1 Completed! Score: {st.session_state.math_mod1_score}")
            if not st.session_state.math_mod2_started:
                if st.button(t["start_mod2"]):
                    st.session_state.math_mod2_started = True
                    st.rerun()
            elif not st.session_state.math_mod2_submitted:
                with st.form("mod2_form"):
                    ans2 = []
                    t_type = 'mod2h' if st.session_state.math_mod2_type == "Hard" else 'mod2e'
                    quiz_mod2 = get_shuffled_quiz(t_type, st.session_state.lang)
                    for i, q in enumerate(quiz_mod2):
                        st.write(f"**{i+1}. {q['q']}**")
                        ans = st.radio(t["answer"], q['options'], key=f"m2_{i}", label_visibility="collapsed", index=None)
                        ans2.append((ans, q['answer']))
                    if st.form_submit_button(t["submit"]):
                        st.session_state.math_mod2_score = sum(1 for a, truth in ans2 if a and truth in a)
                        st.session_state.math_mod2_submitted = True
                        st.rerun()
            else:
                st.success(f"✅ Module 2 Completed! Score: {st.session_state.math_mod2_score}")
                if not st.session_state.math_mod3_started:
                    if st.button(t["start_mod3"]):
                        st.session_state.math_mod3_started = True
                        st.rerun()
                elif not st.session_state.math_mod3_submitted:
                    with st.form("mod3_form"):
                        ans3 = []
                        quiz_mod3 = get_shuffled_quiz('mod3', st.session_state.lang)
                        for i, q in enumerate(quiz_mod3):
                            st.write(f"**{i+1}. {q['q']}**")
                            ans = st.radio(t["answer"], q['options'], key=f"m3_{i}", label_visibility="collapsed", index=None)
                            ans3.append((ans, q['answer']))
                        if st.form_submit_button(t["submit"]):
                            st.session_state.math_mod3_score = sum(1 for a, truth in ans3 if a and truth in a)
                            st.session_state.math_mod3_submitted = True
                            
                            tot = st.session_state.math_mod1_score + st.session_state.math_mod2_score + st.session_state.math_mod3_score
                            total_q = len(QUIZ_DATA[st.session_state.lang]['mod1']) + len(QUIZ_DATA[st.session_state.lang]['mod2h']) + len(QUIZ_DATA[st.session_state.lang]['mod3'])
                            st.session_state.math_total_score_100 = (tot / total_q) * 100
                            st.rerun()
                else:
                    st.success(t["completed"])
                    st.markdown(f"<h2>📐 TEN MATH SCORE: {user_math_score} / 100</h2>", unsafe_allow_html=True)

    with tab4:
        col_lead, col_stats = st.columns([1.5, 1])
        with col_lead:
            st.subheader(t["leaderboard"])
            if not ld_data.empty: st.dataframe(ld_data, hide_index=True, use_container_width=True)
            else: st.info(t["no_users"])
            
        with col_stats:
            st.subheader(t["cert_title"])
            if not st.session_state.logic_submitted or not st.session_state.math_mod3_submitted:
                st.error(t["locked"])
            else:
                if not HAS_FPDF: st.error("pip install fpdf")
                else:
                    def create_pdf(name, logic, math_val, total, cert_id, rank):
                        pdf = FPDF(orientation='L', unit='mm', format='A4')
                        pdf.add_page()
                        
                        pdf.set_draw_color(212, 175, 55)
                        pdf.set_line_width(2)
                        pdf.rect(10, 10, 277, 190)
                        
                        pdf.set_draw_color(30, 30, 30)
                        pdf.set_line_width(0.5)
                        pdf.rect(13, 13, 271, 184)
                        
                        pdf.ln(15)
                        pdf.set_font("Times", 'B', 32)
                        pdf.cell(0, 15, "TEN CERTIFICATE", ln=True, align='C')
                        pdf.cell(0, 15, "OF ACHIEVEMENT", ln=True, align='C')
                        
                        pdf.set_text_color(212, 175, 55)
                        pdf.set_font("Times", 'B', 16)
                        pdf.cell(0, 10, "- + -", ln=True, align='C')
                        pdf.set_text_color(0, 0, 0)
                        
                        pdf.set_font("Times", 'I', 16)
                        pdf.cell(0, 15, "This certificate is awarded to", ln=True, align='C')
                        
                        safe_name = transliterate(str(name)).encode('ascii', 'replace').decode('ascii')
                        pdf.set_font("Times", 'B', 34)
                        pdf.cell(0, 20, safe_name, ln=True, align='C')
                        
                        pdf.line(60, 110, 237, 110)
                        
                        pdf.set_font("Times", '', 14)
                        pdf.cell(0, 15, "for successfully completing the TEN Competition with the following results:", ln=True, align='C')
                        
                        pdf.ln(5)
                        pdf.set_font("Times", 'B', 16)
                        pdf.cell(0, 8, f"TEN LOGIC: {logic} / 100", ln=True, align='C')
                        pdf.cell(0, 8, f"TEN MATH: {math_val} / 100", ln=True, align='C')
                        pdf.cell(0, 8, f"Overall TEN Score: {total} / 100", ln=True, align='C')
                        pdf.cell(0, 8, f"Overall Rank: {rank}", ln=True, align='C')
                        
                        pdf.set_y(165)
                        pdf.set_font("Times", '', 12)
                        date_str = datetime.datetime.now().strftime("%d.%m.%Y")
                        
                        pdf.set_x(40)
                        pdf.cell(50, 8, date_str, ln=False, align='C')
                        pdf.line(40, 173, 90, 173)
                        pdf.set_y(174)
                        pdf.set_x(40)
                        pdf.set_font("Times", 'I', 10)
                        pdf.cell(50, 5, "Date", ln=False, align='C')
                        
                        # Блок подписи
                        if os.path.exists("sign.jpg"):
                            pdf.image("sign.jpg", x=215, y=145, w=30)
                        else:
                            pdf.set_y(160)
                            pdf.set_x(200)
                            pdf.set_font("Times", 'I', 18)
                            pdf.cell(60, 8, "YRS", ln=False, align='C')
                            
                        pdf.line(200, 173, 260, 173)
                        
                        pdf.set_y(174)
                        pdf.set_x(200)
                        pdf.set_font("Times", 'B', 10)
                        pdf.cell(60, 5, "FOUNDER", ln=False, align='C')
                        
                        pdf.set_y(179)
                        pdf.set_x(200)
                        pdf.set_font("Times", 'I', 10)
                        pdf.cell(60, 5, "CEO MEIMANKHAN YERSAIYN", ln=False, align='C')
                        
                        pdf.set_y(165)
                        pdf.set_x(135)
                        pdf.set_text_color(212, 175, 55)
                        pdf.set_font("Times", 'B', 24)
                        pdf.cell(30, 10, "(TEN)", ln=False, align='C')
                        
                        pdf.set_y(185)
                        pdf.set_text_color(100, 100, 100)
                        pdf.set_font("Times", '', 10)
                        pdf.cell(0, 5, f"Certificate ID: {cert_id}", ln=True, align='C')
                        
                        return pdf.output(dest='S').encode('latin-1')

                    pdf_data = create_pdf(current_user_name, user_logic_score, user_math_score, total_score, st.session_state.cert_id, rank_display)
                    st.download_button(label=t["download_cert"], data=pdf_data, file_name=f"{st.session_state.cert_id}.pdf", mime="application/pdf")
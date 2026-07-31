# -*- coding: utf-8 -*-
"""SQLite 데이터 접근 계층. app.py는 이 모듈을 통해서만 DB에 접근한다."""
import datetime
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "quiz.db")


def get_connection():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def get_all_questions(con):
    return con.execute("SELECT * FROM questions ORDER BY id").fetchall()


def get_question(con, qid):
    return con.execute("SELECT * FROM questions WHERE id=?", (qid,)).fetchone()


def record_attempt(con, user, question_id, chosen, is_correct):
    con.execute(
        "INSERT INTO attempts(user, question_id, chosen, is_correct, ts) VALUES (?,?,?,?,?)",
        (user, question_id, chosen, int(is_correct), datetime.datetime.now().isoformat()),
    )
    con.commit()


def get_overall_stats(con, user):
    row = con.execute(
        "SELECT COUNT(*) AS seen, SUM(is_correct) AS correct FROM attempts WHERE user=?",
        (user,),
    ).fetchone()
    seen = row["seen"] or 0
    correct = row["correct"] or 0
    rate = round(correct / seen * 100) if seen else 0
    return {"seen": seen, "correct": correct, "rate": rate}


def get_per_question_stats(con, user):
    """qid -> {seen, correct, wrong, last_result, last_chosen, last_ts}"""
    rows = con.execute(
        "SELECT question_id, chosen, is_correct, ts FROM attempts WHERE user=? ORDER BY ts ASC",
        (user,),
    ).fetchall()
    stats = {}
    for r in rows:
        qid = r["question_id"]
        s = stats.setdefault(
            qid,
            {"seen": 0, "correct": 0, "wrong": 0, "last_result": None, "last_chosen": None, "last_ts": None},
        )
        s["seen"] += 1
        if r["is_correct"]:
            s["correct"] += 1
            s["last_result"] = "O"
        else:
            s["wrong"] += 1
            s["last_result"] = "X"
        s["last_chosen"] = r["chosen"]
        s["last_ts"] = r["ts"]
    return stats


def get_wrong_question_ids(con, user):
    """복습 필요(최근 결과가 오답) / 복습 완료(과거엔 틀렸지만 최근엔 맞음) 목록을 함께 반환"""
    stats = get_per_question_stats(con, user)
    need, done = [], []
    for qid, s in stats.items():
        if s["wrong"] == 0:
            continue
        (need if s["last_result"] == "X" else done).append(qid)
    need.sort(key=lambda qid: stats[qid]["last_ts"], reverse=True)
    done.sort(key=lambda qid: stats[qid]["last_ts"], reverse=True)
    return need, done, stats


def get_tag_stats(con, user):
    rows = con.execute(
        """
        SELECT q.subject AS subject, q.tag AS tag, a.question_id AS qid, a.is_correct AS is_correct
        FROM attempts a JOIN questions q ON a.question_id = q.id
        WHERE a.user = ?
        """,
        (user,),
    ).fetchall()
    agg = {}
    for r in rows:
        key = (r["subject"], r["tag"])
        d = agg.setdefault(key, {"subject": r["subject"], "tag": r["tag"], "seen": 0, "wrong": 0, "qids": set()})
        d["seen"] += 1
        if not r["is_correct"]:
            d["wrong"] += 1
        d["qids"].add(r["qid"])
    result = [v for v in agg.values() if v["wrong"] > 0]
    result.sort(key=lambda v: (-v["wrong"], -(v["wrong"] / v["seen"])))
    return result


def reset_user(con, user):
    con.execute("DELETE FROM attempts WHERE user=?", (user,))
    con.commit()


def clear_question_history(con, user, qid):
    con.execute("DELETE FROM attempts WHERE user=? AND question_id=?", (user, qid))
    con.commit()

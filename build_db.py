# -*- coding: utf-8 -*-
"""
data/questions.csv를 읽어 SQLite DB(data/quiz.db)를 만든다.
- questions 테이블: 문제 은행(매 실행마다 CSV 기준으로 재생성됨)
- attempts 테이블: 사용자별 풀이 기록(재실행해도 보존됨 = 오답노트/통계 데이터)
"""
import csv
import os
import sqlite3

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "data", "questions.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "quiz.db")


def main():
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f"CSV가 없습니다: {CSV_PATH}  (먼저 generate_questions.py를 실행하세요)")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("DROP TABLE IF EXISTS questions")
    cur.execute("""
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY,
            subject INTEGER NOT NULL,
            tag TEXT NOT NULL,
            question TEXT NOT NULL,
            choice1 TEXT NOT NULL,
            choice2 TEXT NOT NULL,
            choice3 TEXT NOT NULL,
            choice4 TEXT NOT NULL,
            answer INTEGER NOT NULL,
            explanation TEXT NOT NULL
        )
    """)

    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                int(r["id"]), int(r["subject"]), r["tag"], r["question"],
                r["choice1"], r["choice2"], r["choice3"], r["choice4"],
                int(r["answer"]), r["explanation"],
            )
            for r in reader
        ]
    cur.executemany(
        "INSERT INTO questions VALUES (?,?,?,?,?,?,?,?,?,?)", rows
    )

    # attempts 테이블은 재실행 시에도 유지(사용자 학습 기록 보존)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            question_id INTEGER NOT NULL REFERENCES questions(id),
            chosen INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            ts TEXT NOT NULL
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_attempts_q ON attempts(question_id)")

    con.commit()
    n_q = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    n_a = cur.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
    con.close()
    print(f"questions: {n_q}행 적재 완료, attempts: 기존 기록 {n_a}행 보존 -> {DB_PATH}")


if __name__ == "__main__":
    main()

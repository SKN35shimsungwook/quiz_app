# -*- coding: utf-8 -*-
"""정보처리산업기사 핵심요약 퀴즈 (Streamlit + SQLite)"""
import os
import random

import streamlit as st

import build_db
import db

if not os.path.exists(db.DB_PATH):
    build_db.main()

st.set_page_config(page_title="정보처리산업기사 핵심요약 퀴즈", page_icon="📝", layout="centered")

SUBJECT_LABEL = {1: "1과목 정보시스템 기반 기술", 2: "2과목 프로그래밍 언어 활용", 3: "3과목 데이터베이스 활용"}
CIRCLE = ["①", "②", "③", "④"]

st.markdown(
    """
    <style>
    .pill{display:inline-block;font-size:.75rem;font-weight:600;padding:2px 10px;
          border-radius:999px;background:#E6EDF7;color:#1F4E8C;margin-right:6px;}
    .pill-tag{background:#F1F3F6;color:#545E72;border:1px solid #D8DEE8;}
    .qbox{font-size:1.15rem;font-weight:700;line-height:1.5;margin:10px 0 18px;}
    .choice-row{padding:10px 14px;border:1px solid #D8DEE8;border-radius:8px;margin-bottom:8px;}
    .choice-correct{background:#E4F3EC;border-color:#2F7D5D;color:#2F7D5D;font-weight:700;}
    .choice-wrong{background:#FBE7E5;border-color:#C23B33;color:#C23B33;font-weight:700;}
    .bar-track{height:8px;background:#EFF2F6;border-radius:99px;border:1px solid #D8DEE8;overflow:hidden;}
    .bar-fill{height:100%;border-radius:99px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_con():
    return db.get_connection()


@st.cache_data
def get_questions_by_id():
    con = get_con()
    return {r["id"]: dict(r) for r in db.get_all_questions(con)}


QUESTIONS = get_questions_by_id()
ALL_IDS = list(QUESTIONS.keys())

# ---------- session state ----------
ss = st.session_state
ss.setdefault("user", "")
ss.setdefault("nav", "퀴즈")
ss.setdefault("queue", None)
ss.setdefault("pos", 0)
ss.setdefault("answered", False)
ss.setdefault("chosen", None)
ss.setdefault("correct_count", 0)
ss.setdefault("wrong_ids", [])
ss.setdefault("quiz_title", "")


def start_quiz(ids, title, shuffle_q=True, limit=None):
    pool = list(ids)
    if shuffle_q:
        random.shuffle(pool)
    if limit:
        pool = pool[:limit]
    ss.queue = pool
    ss.pos = 0
    ss.answered = False
    ss.chosen = None
    ss.correct_count = 0
    ss.wrong_ids = []
    ss.quiz_title = title
    ss.nav = "퀴즈"


def quit_quiz():
    ss.queue = None
    ss.pos = 0
    ss.answered = False
    ss.chosen = None


# ---------- sidebar ----------
with st.sidebar:
    st.header("정보처리산업기사 핵심요약 퀴즈")
    st.caption("핵심요약집 기반 4지선다 자가 학습")
    user_input = st.text_input("닉네임 (풀이 기록 저장용)", value=ss.user, placeholder="예: 홍길동")
    ss.user = user_input.strip()
    st.divider()
    ss.nav = st.radio("메뉴", ["퀴즈", "오답노트", "자주 틀리는 개념"], index=["퀴즈", "오답노트", "자주 틀리는 개념"].index(ss.nav))
    if ss.queue is not None:
        st.divider()
        if st.button("퀴즈 그만하기", width="stretch"):
            quit_quiz()
            st.rerun()

if not ss.user:
    st.info("사이드바에 닉네임을 입력하면 풀이 기록(오답노트·통계)이 저장됩니다.")
    ss.user = "guest"

con = get_con()

# ---------- top stats ----------
overall = db.get_overall_stats(con, ss.user)
need_ids, done_ids, _ = db.get_wrong_question_ids(con, ss.user)
c1, c2, c3 = st.columns(3)
c1.metric("누적 풀이", overall["seen"])
c2.metric("정답률", f"{overall['rate']}%")
c3.metric("복습 필요", len(need_ids))

st.divider()

# ============ 퀴즈 뷰 ============
if ss.nav == "퀴즈":
    if ss.queue is None:
        st.subheader("퀴즈 시작하기")
        subject_choice = st.radio(
            "과목 선택", ["전체", "1과목", "2과목", "3과목"], horizontal=True
        )
        count_choice = st.radio("문제 수", ["10문제", "20문제", "30문제", "전체"], horizontal=True, index=1)

        if need_ids:
            st.warning(f"복습이 필요한 오답이 {len(need_ids)}개 있어요.")
            if st.button("오답 복습으로 바로 시작"):
                start_quiz(need_ids, "오답 복습", shuffle_q=True)
                st.rerun()

        if st.button("퀴즈 시작", type="primary", width="stretch"):
            if subject_choice == "전체":
                ids = ALL_IDS
                title = "전체 문제"
            else:
                sub_num = int(subject_choice[0])
                ids = [i for i in ALL_IDS if QUESTIONS[i]["subject"] == sub_num]
                title = SUBJECT_LABEL[sub_num]
            limit = None if count_choice == "전체" else int(count_choice.replace("문제", ""))
            start_quiz(ids, title, limit=limit)
            st.rerun()

    elif ss.pos < len(ss.queue):
        total = len(ss.queue)
        qid = ss.queue[ss.pos]
        q = QUESTIONS[qid]
        st.progress(ss.pos / total, text=f"{ss.quiz_title} · {ss.pos + 1} / {total}")
        st.markdown(
            f'<span class="pill">{SUBJECT_LABEL[q["subject"]]}</span>'
            f'<span class="pill pill-tag">{q["tag"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="qbox">{q["question"]}</div>', unsafe_allow_html=True)

        choices = [q["choice1"], q["choice2"], q["choice3"], q["choice4"]]
        answer_idx = q["answer"] - 1

        if not ss.answered:
            for ci, choice_text in enumerate(choices):
                if st.button(f"{CIRCLE[ci]}  {choice_text}", key=f"choice_{qid}_{ci}", width="stretch"):
                    is_correct = ci == answer_idx
                    db.record_attempt(con, ss.user, int(qid), ci, is_correct)
                    ss.answered = True
                    ss.chosen = ci
                    if is_correct:
                        ss.correct_count += 1
                    else:
                        ss.wrong_ids.append(qid)
                    st.rerun()
        else:
            for ci, choice_text in enumerate(choices):
                cls = "choice-row"
                if ci == answer_idx:
                    cls += " choice-correct"
                elif ci == ss.chosen:
                    cls += " choice-wrong"
                st.markdown(f'<div class="{cls}">{CIRCLE[ci]}  {choice_text}</div>', unsafe_allow_html=True)
            verdict = "정답입니다." if ss.chosen == answer_idx else "오답입니다."
            st.info(f"**{verdict}** {q['explanation']}")
            if st.button("다음 문제" if ss.pos + 1 < total else "결과 보기", type="primary"):
                ss.pos += 1
                ss.answered = False
                ss.chosen = None
                st.rerun()
    else:
        total = len(ss.queue)
        rate = round(ss.correct_count / total * 100) if total else 0
        st.subheader("결과")
        st.metric(f"{ss.quiz_title} 결과", f"{ss.correct_count} / {total}", f"정답률 {rate}%")
        if ss.wrong_ids:
            with st.expander(f"이번 회차 오답 {len(ss.wrong_ids)}개 보기"):
                for wid in ss.wrong_ids:
                    st.markdown(f"- {QUESTIONS[wid]['question']}")
            if st.button("방금 틀린 문제만 다시 풀기"):
                start_quiz(ss.wrong_ids, "방금 틀린 문제", shuffle_q=False)
                st.rerun()
        if st.button("새 퀴즈 시작하기"):
            quit_quiz()
            st.rerun()

# ============ 오답노트 뷰 ============
elif ss.nav == "오답노트":
    st.subheader("오답노트")
    if not need_ids and not done_ids:
        st.caption("아직 오답 기록이 없습니다. 퀴즈를 풀면 틀린 문제가 여기에 쌓여요.")
    else:
        if need_ids and st.button(f"복습 필요 {len(need_ids)}개 다시 풀기", type="primary"):
            start_quiz(need_ids, "오답 복습")
            st.rerun()

        _, _, stat_map = db.get_wrong_question_ids(con, ss.user)

        def render_wrong_item(qid):
            q = QUESTIONS[qid]
            s = stat_map[qid]
            choices = [q["choice1"], q["choice2"], q["choice3"], q["choice4"]]
            answer_idx = q["answer"] - 1
            with st.container(border=True):
                st.markdown(
                    f'<span class="pill">{SUBJECT_LABEL[q["subject"]]}</span>'
                    f'<span class="pill pill-tag">{q["tag"]}</span>'
                    f'<span style="float:right;color:#C23B33;font-size:.8rem;">오답 {s["wrong"]}회</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{q['question']}**")
                if s["last_chosen"] is not None and s["last_chosen"] != answer_idx:
                    st.caption(f"마지막 선택: {CIRCLE[s['last_chosen']]} {choices[s['last_chosen']]}")
                st.markdown(f":green[정답: {CIRCLE[answer_idx]} {choices[answer_idx]}]")
                st.caption(q["explanation"])
                if st.button("이 기록 삭제", key=f"clear_{qid}"):
                    db.clear_question_history(con, ss.user, qid)
                    st.rerun()

        if need_ids:
            st.markdown("#### 복습 필요")
            for qid in need_ids:
                render_wrong_item(qid)
        if done_ids:
            st.markdown("#### 복습 완료")
            for qid in done_ids:
                render_wrong_item(qid)

# ============ 자주 틀리는 개념 뷰 ============
else:
    st.subheader("자주 틀리는 개념")
    rows = db.get_tag_stats(con, ss.user)
    if not rows:
        st.caption("아직 통계가 부족합니다. 퀴즈를 더 풀어보세요.")
    else:
        max_wrong = max(r["wrong"] for r in rows)
        for r in rows:
            rate = round(r["wrong"] / r["seen"] * 100)
            width = round(r["wrong"] / max_wrong * 100)
            color = "#C23B33" if rate >= 60 else "#B9790E"
            with st.container(border=True):
                st.markdown(
                    f"**{r['tag']}** · {SUBJECT_LABEL[r['subject']]}  \n"
                    f"오답 {r['wrong']} / 시도 {r['seen']} ({rate}%)"
                )
                st.markdown(
                    f'<div class="bar-track"><div class="bar-fill" '
                    f'style="width:{width}%;background:{color};"></div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("이 개념 집중 풀기", key=f"drill_{r['subject']}_{r['tag']}"):
                    start_quiz(list(r["qids"]), f"{r['tag']} 집중풀기")
                    st.rerun()

# 📝 정보처리산업기사 핵심요약 퀴즈

**🔗 바로 실행해 보기:** https://quizapp-huxvdafaoxbxcpr7g3eyyp.streamlit.app

**정보처리산업기사**를 준비하면서 핵심 요약을 4지선다로 풀어 보려고 만든 퀴즈입니다.
휴대폰에서도 풀 수 있게 Streamlit 앱과, 휴대폰에 설치할 수 있는 웹앱(PWA) 두 가지로 만들었습니다.

## 실행 방법 두 가지

### 1) Streamlit 앱

```bash
pip install -r requirements.txt
streamlit run app.py
```

SQLite DB(`db.py`, `build_db.py`)로 문제은행을 관리하고, 과목별(정보시스템 기반 기술 /
프로그래밍 언어 활용 / 데이터베이스 활용)로 문제를 풀 수 있습니다.

### 2) 설치형 웹앱 (PWA)

`pwa_quiz.html` 하나만 있으면 되는 **독립 실행형 PWA**입니다. 아이콘까지 파일 안에 base64로 넣어 두어서, 이 파일 하나만 올려도 스마트폰·PC에 앱처럼 설치됩니다. Streamlit 없이 브라우저로 열어도 동작합니다.

## 기술 스택

| 기술 | 역할 |
|---|---|
| **Streamlit** | `app.py` 버전의 퀴즈 화면 |
| **SQLite** | 문제은행 저장 (`db.py`, `build_db.py`) |
| **HTML/CSS/JS + PWA manifest** | `pwa_quiz.html` — 설치 가능한 독립형 버전 (오답노트, 자주 틀리는 개념 통계 포함) |

## 파일 구조

```
quiz_app/
├── app.py                # Streamlit 앱 진입점
├── db.py                  # SQLite 연결 및 조회
├── build_db.py             # CSV → SQLite DB 빌드
├── generate_questions.py    # 문제 데이터 생성/정리 스크립트
├── pwa_quiz.html             # 독립 실행형 PWA 버전 (아이콘 base64 내장)
├── assets/                  # PWA 아이콘 base64 원본 텍스트
├── data/questions.csv        # 원본 문제 데이터
└── requirements.txt
```

## 만들면서 겪은 문제

**배포하고 나니 문제은행이 비어 보이거나, 문제를 고쳐도 반영이 안 됐습니다**

- 원인: 빌드 결과물인 `data/quiz.db`와 `__pycache__/*.pyc`를 **저장소에 그대로 커밋**해 두었습니다. 제 PC에서는 있던 DB를 계속 써서 문제가 없어 보였습니다. 하지만 배포 환경에는 예전 DB가 그대로 올라가서, `questions.csv`를 고쳐도 서비스되는 DB는 옛날 그대로였습니다.
- 해결: `quiz.db`와 `__pycache__`를 저장소에서 빼고(`.gitignore`), 앱이 시작할 때 DB가 없으면 CSV로 새로 만들게 바꿨습니다. 빌드 결과물은 커밋하지 않는다는 걸 이 문제로 확실히 익혔습니다.

```diff
+ import os
  import random
  import streamlit as st
+ import build_db
  import db

+ if not os.path.exists(db.DB_PATH):
+     build_db.main()
```

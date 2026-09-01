# 📝 정보처리산업기사 핵심요약 퀴즈

**정보처리산업기사** 핵심 요약 문제를 4지선다로 풀면서 공부하는 퀴즈예요. 두 가지 방식으로
실행할 수 있게 만들어져 있어요.

## 실행 방법 두 가지

### 1) Streamlit 앱

```bash
pip install -r requirements.txt
streamlit run app.py
```

SQLite DB(`db.py`, `build_db.py`)로 문제은행을 관리하고, 과목별(정보시스템 기반 기술 /
프로그래밍 언어 활용 / 데이터베이스 활용)로 문제를 풀 수 있어요.

### 2) 설치형 웹앱 (PWA)

`pwa_quiz.html` 하나만 있으면 되는 **독립 실행형 PWA**예요. 아이콘까지 파일 안에
base64로 통째로 넣어뒀기 때문에, 이 파일 하나만 서버에 올려도 스마트폰/PC에 앱처럼
설치할 수 있어요. Streamlit 없이 그냥 브라우저로 열어도 동작해요.

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

---

🤖 이 저장소의 README는 Claude Code와 함께 작성했어요.

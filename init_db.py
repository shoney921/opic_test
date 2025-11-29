import sqlite3
import os

# 데이터베이스 파일 경로
DB_PATH = "questions.db"

# 데이터베이스 초기화
def init_database():
    """SQLite 데이터베이스를 생성하고 초기 질문 데이터를 삽입합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 질문 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 답변 테이블 생성 (1:N 관계, 난이도 포함)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            answer TEXT NOT NULL,
            difficulty INTEGER NOT NULL CHECK(difficulty >= 1 AND difficulty <= 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
        )
    ''')
    
    # 샘플 질문 데이터
    sample_questions = [
        "What is your favorite hobby and why?",
        "Describe a memorable trip you've taken.",
        "What are your career goals for the next 5 years?",
        "How do you handle stress in your daily life?",
        "What book or movie has influenced you the most?",
    ]
    
    # 기존 데이터 확인
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    
    # 데이터가 없으면 샘플 데이터 삽입
    if count == 0:
        for question in sample_questions:
            cursor.execute("INSERT INTO questions (question) VALUES (?)", (question,))
        print(f"{len(sample_questions)}개의 질문이 데이터베이스에 추가되었습니다.")
    else:
        print(f"데이터베이스에 이미 {count}개의 질문이 있습니다.")
    
    conn.commit()
    conn.close()
    print(f"데이터베이스 초기화 완료: {DB_PATH}")

if __name__ == "__main__":
    init_database()

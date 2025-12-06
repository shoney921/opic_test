import sqlite3
import os

# 데이터베이스 파일 경로
DB_PATH = "questions.db"

# 데이터베이스 초기화
def init_database():
    """SQLite 데이터베이스를 생성하고 초기 질문 데이터를 삽입합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 테이블 존재 여부 확인 함수
    def table_exists(table_name):
        """테이블이 존재하는지 확인합니다."""
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        ''', (table_name,))
        return cursor.fetchone() is not None
    
    # 질문 테이블 생성
    if not table_exists('questions'):
        cursor.execute('''
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("questions 테이블이 생성되었습니다.")
    else:
        print("questions 테이블이 이미 존재합니다.")
    
    # 답변 테이블 생성 (1:N 관계, 난이도 포함)
    if not table_exists('answers'):
        cursor.execute('''
            CREATE TABLE answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                answer TEXT NOT NULL,
                difficulty INTEGER NOT NULL CHECK(difficulty >= 1 AND difficulty <= 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
            )
        ''')
        print("answers 테이블이 생성되었습니다.")
    else:
        print("answers 테이블이 이미 존재합니다.")
    
    # 피드백 테이블 생성 (답변에 대한 피드백, 1:1 관계)
    if not table_exists('feedbacks'):
        cursor.execute('''
            CREATE TABLE feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                answer_id INTEGER NOT NULL UNIQUE,
                feedback_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (answer_id) REFERENCES answers (id) ON DELETE CASCADE
            )
        ''')
        print("feedbacks 테이블이 생성되었습니다.")
    else:
        print("feedbacks 테이블이 이미 존재합니다.")
    
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

import sqlite3
from typing import List, Dict, Optional


class QuestionRepository:
    """질문 및 답변 데이터베이스 접근을 담당하는 Repository 클래스"""
    
    def __init__(self, db_path: str = "questions.db"):
        """
        Repository 초기화
        
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path
    
    def get_all_questions(self) -> List[Dict]:
        """데이터베이스에서 모든 질문을 가져옵니다."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, question FROM questions ORDER BY id")
        questions = [{"id": row["id"], "question": row["question"]} for row in cursor.fetchall()]
        
        conn.close()
        return questions
    
    def get_question_answer_count(self, question_id: int) -> int:
        """질문의 답변 개수를 반환합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM answers
            WHERE question_id = ?
        ''', (question_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 0
    
    def save_answer(self, question_id: int, answer: str, difficulty: int) -> bool:
        """
        답변을 데이터베이스에 저장합니다.
        
        Args:
            question_id: 질문 ID
            answer: 답변 내용
            difficulty: 난이도 (1-5)
        
        Returns:
            저장 성공 여부
        """
        if not answer.strip():
            return False
        
        if difficulty < 1 or difficulty > 5:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO answers (question_id, answer, difficulty) 
            VALUES (?, ?, ?)
        ''', (question_id, answer, difficulty))
        
        conn.commit()
        conn.close()
        return True

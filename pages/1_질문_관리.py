import streamlit as st
import sqlite3
from typing import List, Dict, Optional

# 데이터베이스 파일 경로
DB_PATH = "questions.db"

def get_all_questions() -> List[Dict]:
    """데이터베이스에서 모든 질문을 가져옵니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, question, type, created_at FROM questions ORDER BY id")
    questions = [
        {
            "id": row["id"],
            "question": row["question"],
            "type": row["type"],
            "created_at": row["created_at"]
        }
        for row in cursor.fetchall()
    ]
    
    conn.close()
    return questions

def add_question(question: str) -> bool:
    """새 질문을 데이터베이스에 추가합니다."""
    if not question.strip():
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO questions (question) VALUES (?)", (question,))
    
    conn.commit()
    conn.close()
    return True

def get_question_avg_difficulty(question_id: int) -> Optional[float]:
    """질문의 평균 난이도를 계산합니다."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT AVG(difficulty) as avg_difficulty, COUNT(*) as count
        FROM answers
        WHERE question_id = ?
    ''', (question_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0] is not None:
        return round(row[0], 2)
    return None

def get_question_answers(question_id: int) -> List[Dict]:
    """특정 질문의 모든 답변을 가져옵니다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, answer, difficulty, created_at
        FROM answers
        WHERE question_id = ?
        ORDER BY created_at DESC
    ''', (question_id,))
    
    answers = [
        {
            "id": row["id"],
            "answer": row["answer"],
            "difficulty": row["difficulty"],
            "created_at": row["created_at"]
        }
        for row in cursor.fetchall()
    ]
    
    conn.close()
    return answers

def delete_question(question_id: int) -> bool:
    """질문을 삭제합니다 (CASCADE로 관련 답변도 삭제됨)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    
    conn.commit()
    conn.close()
    return True

def main():
    st.title("📝 질문 관리")
    st.markdown("---")
    
    try:
        # 질문 추가 섹션
        with st.expander("➕ 새 질문 추가", expanded=False):
            new_question = st.text_area(
                "질문 내용을 입력하세요:",
                height=100,
                placeholder="예: What is your favorite hobby and why?",
                key="new_question_input"
            )
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("추가", type="primary"):
                    if new_question.strip():
                        if add_question(new_question.strip()):
                            st.success("질문이 추가되었습니다!")
                            st.rerun()
                        else:
                            st.error("질문 추가 중 오류가 발생했습니다.")
                    else:
                        st.warning("질문 내용을 입력해주세요.")
        
        st.markdown("---")
        
        # --- 메인 화면: 질문 목록 / 상세 보기 토글 ---
        selected_question_id = st.session_state.get("selected_question_id")

        # 1) 질문 상세(답변 목록) 화면
        if selected_question_id is not None:
            # 뒤로가기 버튼
            if st.button("← 질문 목록으로 돌아가기"):
                st.session_state.selected_question_id = None
                st.experimental_rerun()

            st.markdown("---")

            # 선택된 질문 정보 및 답변 로드
            questions = get_all_questions()
            question = next((q for q in questions if q["id"] == selected_question_id), None)

            if question is None:
                st.error("선택한 질문을 찾을 수 없습니다.")
                return

            avg_difficulty = get_question_avg_difficulty(selected_question_id)
            answers = get_question_answers(selected_question_id)

            # 질문 정보
            st.subheader(f"질문 {selected_question_id}")
            st.info(f"**{question['question']}**")
            st.caption(f"생성일: {question['created_at']}")

            # 통계 정보
            col1, col2 = st.columns(2)
            with col1:
                if avg_difficulty is not None:
                    difficulty_labels = {
                        1: "매우 쉬움",
                        2: "쉬움",
                        3: "보통",
                        4: "어려움",
                        5: "매우 어려움",
                    }
                    difficulty_label = difficulty_labels.get(int(avg_difficulty), "보통")
                    st.metric("평균 난이도", f"{avg_difficulty:.2f}")
                    st.caption(f"({difficulty_label})")
                else:
                    st.metric("평균 난이도", "-")
                    st.caption("(답변 없음)")

            with col2:
                st.metric("총 답변 수", len(answers))

            st.markdown("---")

            # 답변 목록
            st.subheader("📋 답변 목록")

            if not answers:
                st.info("이 질문에 대한 답변이 아직 없습니다.")
                st.caption("'문제 풀기' 화면에서 이 질문에 답변을 작성할 수 있습니다.")
            else:
                for idx, answer in enumerate(answers, 1):
                    difficulty_labels = {
                        1: "매우 쉬움",
                        2: "쉬움",
                        3: "보통",
                        4: "어려움",
                        5: "매우 어려움",
                    }
                    difficulty_label = difficulty_labels.get(answer["difficulty"], "보통")

                    with st.container():
                        header_col1, header_col2 = st.columns([3, 1])
                        with header_col1:
                            st.markdown(f"**답변 {idx}**")
                        with header_col2:
                            st.markdown(f"난이도: **{answer['difficulty']}** ({difficulty_label})")

                        st.text_area(
                            "답변 내용",
                            value=answer["answer"],
                            height=200,
                            disabled=True,
                            key=f"answer_view_{answer['id']}",
                        )
                        st.caption(f"작성일: {answer['created_at']}")

                        if idx < len(answers):
                            st.markdown("---")

        # 2) 질문 목록 화면
        else:
            # 질문 목록
            st.subheader("📋 질문 목록")

            questions = get_all_questions()

            st.text(f"questions: {questions}")

            if not questions:
                st.info("등록된 질문이 없습니다. 위의 '새 질문 추가'를 사용하여 질문을 추가하세요.")
            else:
                st.text(f"총 질문 수: {len(questions)}")

                # 각 질문에 통계 정보(답변 수, 평균 난이도) 미리 계산
                question_stats = []
                for q in questions:
                    q_id = q["id"]
                    avg_difficulty = get_question_avg_difficulty(q_id)
                    answers = get_question_answers(q_id)
                    q_data = dict(q)
                    q_data["avg_difficulty"] = avg_difficulty
                    q_data["answers_count"] = len(answers)
                    question_stats.append(q_data)

                # --- 컬럼 헤더 버튼으로 정렬 상태 관리 ---
                # 정렬 상태 초기값 설정
                if "question_sort_key" not in st.session_state:
                    st.session_state.question_sort_key = "id"  # 기본: ID
                if "question_sort_order" not in st.session_state:
                    st.session_state.question_sort_order = "none"  # none → asc → desc 순서로 토글

                def toggle_sort(column_key: str):
                    current_key = st.session_state.question_sort_key
                    current_order = st.session_state.question_sort_order

                    if current_key != column_key:
                        # 다른 컬럼을 클릭하면 해당 컬럼 오름차순으로 시작
                            st.session_state.question_sort_key = column_key
                            st.session_state.question_sort_order = "asc"
                    else:
                        # 같은 컬럼을 반복 클릭하면 none → asc → desc → none 순환
                        if current_order == "none":
                            st.session_state.question_sort_order = "asc"
                        elif current_order == "asc":
                            st.session_state.question_sort_order = "desc"
                        else:
                            st.session_state.question_sort_order = "none"

                sort_key = st.session_state.question_sort_key
                sort_order = st.session_state.question_sort_order

                # 컬럼 헤더 버튼 렌더링
                header_col1, header_col2, header_col3, header_col4 = st.columns([4, 1, 1, 1])

                # 질문(ID) 컬럼 헤더
                with header_col1:
                    label = "질문(ID)"
                    if sort_key == "id":
                        if sort_order == "asc":
                            label += " ↑"
                        elif sort_order == "desc":
                            label += " ↓"
                    if st.button(label, key="sort_by_id"):
                        toggle_sort("id")
                        st.experimental_rerun()

                # 유형 컬럼 헤더
                with header_col2:
                    label = "유형"
                    if sort_key == "type":
                        if sort_order == "asc":
                            label += " ↑"
                        elif sort_order == "desc":
                            label += " ↓"
                    if st.button(label, key="sort_by_type"):
                        toggle_sort("type")
                        st.experimental_rerun()

                # 답변 수 컬럼 헤더
                with header_col3:
                    label = "답변 수"
                    if sort_key == "answers":
                        if sort_order == "asc":
                            label += " ↑"
                        elif sort_order == "desc":
                            label += " ↓"
                    if st.button(label, key="sort_by_answers"):
                        toggle_sort("answers")
                        st.experimental_rerun()

                                # 평균 난이도 컬럼 헤더
                with header_col4:
                    label = "평균 난이도"
                    if sort_key == "difficulty":
                        if sort_order == "asc":
                            label += " ↑"
                        elif sort_order == "desc":
                            label += " ↓"
                    if st.button(label, key="sort_by_difficulty"):
                        toggle_sort("difficulty")
                        st.experimental_rerun()

                # 선택된 정렬 기준/순서에 따라 question_stats 정렬
                if sort_order != "none":
                    reverse = sort_order == "desc"
                    if sort_key == "answers":
                        question_stats.sort(
                            key=lambda x: x["answers_count"],
                            reverse=reverse,
                        )
                    elif sort_key == "difficulty":
                        # 평균 난이도가 없는 경우를 위해 기본값 설정
                        question_stats.sort(
                            key=lambda x: (
                                x["avg_difficulty"]
                                if x["avg_difficulty"] is not None
                                else -1
                            ),
                            reverse=reverse,
                        )
                    else:
                        # 기본: 질문 ID 기준
                        question_stats.sort(key=lambda x: x["id"], reverse=reverse)

                # 각 질문 카드
                for question in question_stats:
                    question_id = question["id"]
                    avg_difficulty = question.get("avg_difficulty")
                    answers_count = question.get("answers_count", 0)

                    with st.container():
                        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])

                        with col1:
                            # 질문 클릭 시 상세(답변 목록) 보기로 전환
                            if st.button(
                                f"**{question_id}** : {question['question']}",
                                key=f"btn_{question_id}",
                                use_container_width=True,
                            ):
                                st.session_state.selected_question_id = question_id
                                st.experimental_rerun()

                        with col2:
                            st.badge(question['type'], color="red", width="content")

                        with col3:
                            st.badge(f"{answers_count}개", color="green", width="content")

                        with col4:
                            # 평균 난이도 표시
                            if avg_difficulty is not None:
                                difficulty_labels = {
                                    1: "매우 쉬움",
                                    2: "쉬움",
                                    3: "보통",
                                    4: "어려움",
                                    5: "매우 어려움",
                                }
                                difficulty_label = difficulty_labels.get(int(avg_difficulty), "보통")
                                st.badge(f"{avg_difficulty:.2f} ({difficulty_label})", color="blue", width="content")
                            else:
                                st.badge("없음", color="gray", width="content")


    except sqlite3.OperationalError:
        st.error(f"데이터베이스 파일을 찾을 수 없습니다. 먼저 `python init_db.py`를 실행하여 데이터베이스를 초기화하세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()


import streamlit as st
import sqlite3
import random
from typing import List, Dict, Optional
from repository import QuestionRepository
from ai_service import OpenAIService

# 데이터베이스 파일 경로
DB_PATH = "questions.db"

# Repository 인스턴스 생성
question_repository = QuestionRepository(DB_PATH)

# ai
ai_service = OpenAIService()

# 페이지 설정
st.set_page_config(
    page_title="질문 답변 연습",
    page_icon="❓",
    layout="wide"
)

def filter_questions_by_max_answer_count(questions: List[Dict]) -> List[Dict]:
    """답변 개수가 최대값과 같은 질문들을 제외한 질문 리스트를 반환합니다."""
    if not questions:
        return questions
    
    # 각 질문의 답변 개수 계산
    question_answer_counts = {}
    max_count = 0
    
    for question in questions:
        count = question_repository.get_question_answer_count(question["id"])
        question_answer_counts[question["id"]] = count
        max_count = max(max_count, count)
    
    # 최대 답변 개수가 0이면 모든 질문 반환 (답변이 없는 경우)
    if max_count == 0:
        return questions
    
    # 최대 답변 개수와 다른 질문들만 필터링
    filtered_questions = [
        question for question in questions
        if question_answer_counts[question["id"]] < max_count
    ]
    
    return filtered_questions

def main():
    st.title("❓ 문제 풀기")
    st.markdown("---")
    
    try:
        all_questions = question_repository.get_all_questions()
        
        if not all_questions:
            st.warning("데이터베이스에 질문이 없습니다. '질문 관리' 페이지에서 질문을 추가하세요.")
            return
        
        # 답변 개수가 최대값과 같은 질문들을 제외
        filtered_questions = filter_questions_by_max_answer_count(all_questions)
        
        if not filtered_questions:
            st.warning("모든 질문이 최대 답변 개수를 가지고 있어 표시할 질문이 없습니다.")
            return
        
        # 질문 셔플 여부 선택
        shuffle_questions = st.checkbox(
            "질문 순서를 랜덤으로 섞기",
            value=st.session_state.get("shuffle_questions", True),
        )
        st.session_state.shuffle_questions = shuffle_questions
        
        # 세션 상태 초기화 (셔플 옵션 변경 시에도 초기화)
        need_init = (
            "shuffled_questions" not in st.session_state
            or "current_index" not in st.session_state
            or st.session_state.get("last_shuffle_option") != shuffle_questions
            or st.session_state.get("last_filtered_questions_count") != len(filtered_questions)
        )
        if need_init:
            if shuffle_questions:
                st.session_state.shuffled_questions = random.sample(filtered_questions, len(filtered_questions))
            else:
                # 셔플하지 않고 등록된 순서대로 사용
                st.session_state.shuffled_questions = filtered_questions[:]
            st.session_state.current_index = 0
            st.session_state.last_shuffle_option = shuffle_questions
            st.session_state.last_filtered_questions_count = len(filtered_questions)
        
        questions = st.session_state.shuffled_questions
        current_idx = st.session_state.current_index
        
        if current_idx < len(questions):
            current_question = questions[current_idx]
            
            # 진행 상황 표시
            progress = (current_idx + 1) / len(questions)
            st.progress(progress)
            st.caption(f"진행률: {current_idx + 1} / {len(questions)} ({int(progress * 100)}%)")
            
            st.markdown("---")
            
            # 질문 표시
            st.subheader(f"질문 {current_idx + 1}")
            st.info(f"**{current_question['question']}**")
            
            st.markdown("---")
            
            # 답변 입력 영역
            st.subheader("💬 답변 작성")
            
            # 답변 텍스트 박스
            answer_key = f"answer_{current_question['id']}_{current_idx}"
            if answer_key not in st.session_state:
                st.session_state[answer_key] = ""
            
            answer = st.text_area(
                "답변을 입력하세요:",
                height=300,
                placeholder="여기에 답변을 타이핑하세요...",
                key=answer_key
            )
            
            # 난이도 선택
            st.subheader("📊 난이도 선택")
            difficulty_key = f"difficulty_{current_question['id']}_{current_idx}"
            if difficulty_key not in st.session_state:
                st.session_state[difficulty_key] = 3
            
            difficulty = st.slider(
                "난이도 (1: 매우 쉬움 ~ 5: 매우 어려움)",
                min_value=1,
                max_value=5,
                key=difficulty_key
            )
            
            # 난이도 설명
            difficulty_labels = {
                1: "매우 쉬움",
                2: "쉬움",
                3: "보통",
                4: "어려움",
                5: "매우 어려움"
            }
            st.caption(f"선택한 난이도: {difficulty} ({difficulty_labels[difficulty]})")
            
            st.markdown("---")
            
            # 다음 버튼
            col1, col2, col3 = st.columns([1, 1, 1])
            ai_result = ""
            with col1:
                if st.button("오픽 선생님 조언 받기", type="primary", use_container_width=True):
                    ai_result = ai_service.ask_advise(current_question["question"], answer).content

            with col3:
                if st.button("저장 후 다음 ▶️", type="primary", use_container_width=True):
                    # 답변 저장
                    if answer.strip():
                        if question_repository.save_answer(current_question["id"], answer, difficulty):
                            st.session_state.current_index = current_idx + 1
                            # 다음 질문을 위해 세션 상태 초기화
                            if current_idx + 1 < len(questions):
                                next_question = questions[current_idx + 1]
                                next_answer_key = f"answer_{next_question['id']}_{current_idx + 1}"
                                next_difficulty_key = f"difficulty_{next_question['id']}_{current_idx + 1}"
                                if next_answer_key not in st.session_state:
                                    st.session_state[next_answer_key] = ""
                                if next_difficulty_key not in st.session_state:
                                    st.session_state[next_difficulty_key] = 3
                            
                            st.rerun()
                        else:
                            st.error("답변 저장 중 오류가 발생했습니다.")
                    else:
                        st.warning("답변을 입력해주세요.")

            if ai_result:
                st.subheader("💬 오픽 선생님 조언")
                st.markdown(f"{ai_result}")
                print(ai_result)
        
        else:
            st.success("🎉 모든 문제를 완료했습니다!")
            st.balloons()
            
            if st.button("🔄 다시 시작"):
                # 다시 시작 시에도 현재 셔플 옵션과 필터링을 반영
                filtered_questions = filter_questions_by_max_answer_count(all_questions)
                shuffle_questions = st.session_state.get("shuffle_questions", True)
                if shuffle_questions:
                    st.session_state.shuffled_questions = random.sample(filtered_questions, len(filtered_questions))
                else:
                    st.session_state.shuffled_questions = filtered_questions[:]
                st.session_state.current_index = 0
                st.session_state.last_shuffle_option = shuffle_questions
                st.session_state.last_filtered_questions_count = len(filtered_questions)
                st.rerun()
    
    except sqlite3.OperationalError:
        st.error(f"데이터베이스 파일을 찾을 수 없습니다. 먼저 `python init_db.py`를 실행하여 데이터베이스를 초기화하세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main()

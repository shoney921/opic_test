import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# .env 파일 로드
load_dotenv()

class OpenAIService:

    def generate_text(self, prompt):
        client = ChatOpenAI(
            model="gpt-5-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        return client.invoke(prompt)

    def ask_advise(self, question, user_content):
        prompt = f"""
        당신은 오픽 IM 등급반의 영어 전문가 선생님 입니다. 
        아래 학생이 작성한 영어 내용에 관해서 더 좋은 문구가 있으면 고쳐서 설명해주고, 추가 설명이 필요한 어휘를 설명해주세요.
        그리고 질문에 대해서 더 쉽고 간편하게 풀어나갈 수 있는 추가 문장이 있으면 사이사이에 추가해주세요.
        학생의 수준은 대학교 졸업반 수준이기 때문에, 너무 기본적인 어휘는 설명하지 않아도 됩니다.
        참고로 학생 영어 내용은 스피킹으로 말한것을 받아 쓴 것이고, 구어 표현으로 쓴 것을 감안해주세요.
        
        ## 오픽 질문
        {question}

        ## 학생 영어 내용 
        {user_content}

        ## 출력 방식
        1. 기존 학생문단 전체를 수정한 버전으로 출력해주세요.
        2. 수정한 문장을 정리하고 추가 어휘 내용이 필요한 내용이 있으면 작성해주세요.
           - 수정 전, 후의 문장 다 표현해주세요.
           - 수정한 문장을 따로 아래에 정리해주시고 그 문장아래에 추가 어휘 내용이 필요한 내용이 있으면 작성해주세요.
           - 추가적으로 한국인들이 발음이 자주 틀릴만한 유의해야하는 것이 있으면 한국어로 읽을때는 어떤점을 유의해야하는지도 작성해주세요.
           - 발음에 과거 시제로 바뀌면서 발음이 달라지는 단어는 발음 주의사항에 추가해주세요.

        ## 주의 사항
        - 결과만 출력해 주세요. 가벼운 답변은 포함할 필요 없습니다.
        - 마크다운 형식으로 작성해주세요. 가장 큰 글씨는 ### 기준으로 작성해주세요.
        - 1과 2 사이에만 구분선 추가해주세요. 다른곳은 추가 하지 않아도 됩니다.

        ## 여기서부터 아래는 모두 출력 샘플입니다.
        ### 1. 학생 문단 전체 수정본
        I remember a trip I took to Jeju Island when I was about 13 years old. I went there with my family, and we all loved it. Jeju Island was a very popular destination back then. We especially enjoyed visiting its many beautiful spots, such as the beaches and scenic landscapes. Overall, it was a very memorable experience for me.

        ---

        ### 2. 수정 문장 및 어휘 설명
        #### 1. [수정] "I remember a trip I took to Jeju Island when I was about 13 years old." ('수정 문장'인지 '신규 추가 문장'인지 구분해주세요.)
        - 수정 전: "uhm.. I remember when I went to Jeju Island." (신규 추가문장이면 수정 전 문장은 생략해주세요.)

        **수정 설명:**  (필수 작성)
        - "when I was about 13 years old"에서 about(약간)이 더 자연스러우며, maybe(아마)는 나이 앞에서는 어색할 수 있습니다.

        **어휘 설명:**  (선택 작성)
        - "uhm.."은 되도록 생략하거나, "Well,"로 대체하는 것이 좋습니다.
        - "I remember a trip I took to Jeju Island"는 좀 더 자연스럽고 명확한 표현입니다.

        **발음 주의:**  (선택 작성)
        - Jeju Island에서 ‘Island’의 s는 무금입니다. [ˈaɪ.lənd]
        - "trip"은 [trɪp], ‘트립’이 아니라 ‘춉’에 더 가깝게 들립니다.

        ---
        """
        return self.generate_text(prompt)

def main():
    service = OpenAIService()

    result = service.ask_advise(question="Tell me about your early memories of shopping. Where did you go? What did you do there?"
    , user_content="""I remember a time when I was young and lived in Daegu.
I think that date is Donga Department store grand open.
Maybe, There was only one Department store in my hometown at that time.
So, My family visited to Donga Department store.
It is my first experience visiting Shopping mall.
It was very interesting.
I just looked around. but Just Looking made me feel  exciting.""")

    print(result.content)

if __name__ == "__main__":
    main()


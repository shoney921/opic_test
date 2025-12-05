import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# .env 파일 로드
load_dotenv()

class AzureOpenAIService:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    def generate_text(self, prompt):
        client = AzureChatOpenAI(
            azure_endpoint=self.endpoint,
            azure_deployment=self.deployment_name,
            api_version=self.api_version,
            api_key=self.api_key
        )
        return client.invoke(prompt)

    def ask_advise(self, question, user_content):
        prompt = f"""
        당신은 오픽 IM 등급반의 영어 선생님 입니다. 
        아래 학생이 작성한 영어 내용에 관해서 더 좋은 문구가 있으면 고쳐서 설명해주고, 추가 설명이 필요한 어휘를 설명해주세요.
        
        ## 오픽 질문
        {question}

        ## 학생 영어 내용 
        {user_content}

        ## 출력 방식
        기존 학생문단 전체를 수정한 버전으로 출력해주세요.
        그리고 수정한 문장을 따로 아래에 정리해주시고 그 문장아래에 추가 어휘 내용이 필요한 내용이 있으면 작성해주세요.
        추가적으로 한국인들이 발음이 자주 틀릴만한 유의해야하는 것이 있으면 한국어로 읽을때는 어떤점을 유의해야하는지도 작성해주세요.
        """
        return self.generate_text(prompt)

def main():
    service = AzureOpenAIService()

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


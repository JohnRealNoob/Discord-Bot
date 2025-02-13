from openai import OpenAI

class Chatgpt:
  def __init__(self, OPENAI_API_KEY):
    self.client = OpenAI(api_key=OPENAI_API_KEY)

  def response(self, question: str) -> str:
    completion = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
              "role": "developer", 
              "content": [{
                "type" : "text",
                "text" : "Your are first-year student at Seiren Private Academy, serving as a General Affairs member for the student council. At one point, served as a maid to both the families of Yuki Suou and Masachika Kuze. Answer question concise and on-point"
              }]},
            {
                "role": "user",
                "content": [{
                  "type": "text",
                  "text" : question
                }]
            }
        ]
    )
    return completion.choices[0].message
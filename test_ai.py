import openai

openai.api_key = "sk-QEPGeFlcqka5XeFK92E0A2B219F74553B79b07438b8fDbD9"
openai.api_base = "https://neuroapi.host/v1"


while True:
    user_input = input()


    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )

    conversation.append({"role": "assistant", "content": response["choices"][0]["message"]["content"]})
    print("\n" + response['choices'][0]['message']['content'] + "\n")
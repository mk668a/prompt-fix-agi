#!/usr/bin/env python3
import os
import re
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def openai_call(prompt, tools=None, tool_choice=None):
    response = client.chat.completions.create(
        model=OPENAI_API_MODEL,
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice=tool_choice,
    )
    return response.choices[0].message.content


def prompt_fix_agent(prompt: str, ideal_answer: str) -> str:
    prompt = f"""
# Instruction
The [prompt] needs to be improved to obtain [ideal answer]. 
Please modify [prompt] to include more specific instructions to obtain [ideal_answer].
The modified prompt should not include the content of [ideal answer].

## prompt
{prompt}

## ideal answer
{ideal_answer}

# Output
modified prompt
"""
    return openai_call(prompt)


def answer_check_agent(answer: str, ideal_answer: str) -> int:
    prompt = f"""
# Instruction
Evaluate whether the information conveyed by the [answer] and [ideal_answer] sentences is likewise relevant.
10 points if they are exactly the same, 0 points if they are completely different.

## answer
{answer}

## ideal_answer
{ideal_answer}

# Output
point
"""
    response = openai_call(prompt)
    return float(re.findall(r"\d+\.\d+|\d+", response)[0])


def main():
    # Set the number of retries. If None, the number of retries is infinite.
    retry = None
    # Set the minimum point to stop the process.
    minimum_point = 8
    # Set the test case.
    test_case = [
        {
            "prompt": "what is pizza.",
            "ideal_answer": """
- 500g of strong flour
- 200ml of water
- 1 teaspoon of salt
- 1 teaspoon of dry yeast
- 2 tablespoons of olive oil.
""",
        }
    ]

    for i, case in enumerate(test_case):
        print("Start.")

        prompt = case["prompt"]
        print(f"\n[prompt]")
        print(f"{prompt}")

        ideal_answer = case["ideal_answer"]
        print(f"\n[ideal_answer]")
        print(f"{ideal_answer}")

        def loop_process(i, prompt):
            print(f"\n------------------ loop {i+1} ------------------")
            print(f"\n[prompt_fix_agent fixed prompt]")
            print(f"{prompt}")
            print(f"↓")
            response = prompt_fix_agent(prompt, ideal_answer)
            print(f"{response}")
            answer = openai_call(response)
            point = answer_check_agent(answer, ideal_answer)
            print(f"\n[llm answer]")
            print(f"{answer}")
            print(f"\n【point: {point}】")
            return response, point

        if retry is None:
            i = 0
            while True:
                response, point = loop_process(i, prompt)
                prompt = response
                if point >= minimum_point:
                    print("\nDone.")
                    break
                i += 1
        else:
            for i in range(retry):
                response, point = loop_process(i, prompt)
                prompt = response
                if point >= minimum_point:
                    print("\nDone.")
                    break


if __name__ == "__main__":
    main()

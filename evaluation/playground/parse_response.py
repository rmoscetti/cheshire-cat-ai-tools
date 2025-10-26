"""
Parse an answer using an LLM model to get a machine readable response.
"""

from openai import OpenAI
from dotenv import dotenv_values
from pyprojroot import here

env = dotenv_values(here('.env.local'))

client = OpenAI(
    api_key=env['OPENAI_API_KEY'],
)

def call_llm(prompt: str) -> str:
    """
    Call the LLM model to parse the response.

    Args:
        prompt: The prompt to send to the LLM model.

    Returns:
        The response from the LLM model.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o",
    )

    return chat_completion.choices[0].message.content

def parse_time_to_finish_response(response: str) -> int:
    """
    Parse the response from the time_to_finish tool.

    Args:
        response: The response from the time_to_finish tool.

    Returns:
        The time to finish in minutes.
    """
    prompt = f"""Parse the following text and extract from it it time in minutes. If is not possible to extract the time in min, return -1.
    In any case always return only a single number (don't explain what you did just return the correct result).

    ```txt
    {response}
    ```
    """
    return call_llm(prompt)
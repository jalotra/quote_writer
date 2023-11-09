import json 
from pathlib import Path
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union
from fastapi import APIRouter
import fire
import openai
from cleantext import clean
from tqdm.auto import tqdm
from datetime import datetime

router = APIRouter()

AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
    "text-davinci-003",
    "code-davinci-002",
    "gpt-4-1106-preview"
]


def validate_model(model):
    if model not in AVAILABLE_MODELS:
        raise ValueError(
            f"Invalid model '{model}', available models: {', '.join(AVAILABLE_MODELS)}"
        )


def chat_generate_text(
    name : str,
    prompt: str,
    openai_api_key: str = None,
    model: str = "gpt-3.5-turbo",
    system_prompt : str = "You are great at generating truthful and are an assistant, given a user prompt make sure you generate what the user prompt wants, think step by step !",
    temperature: float = 0.5,
    max_tokens: int = 256,
    n: int = 1,
    stop: Optional[Union[str, list]] = None,
    presence_penalty: float = 0,
    frequency_penalty: float = 0.1,
) -> List[str]:
    if openai_api_key is None:
        openai_api_key = os.environ.get("OPENAI_API_KEY", None)
    assert openai_api_key is not None, "OpenAI API key not found."

    openai.api_key = openai_api_key

    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        n=n,
        stop=stop,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
    )

    generated_texts = [
        choice.message["content"].strip() for choice in response["choices"]
    ]
    return generated_texts


# UTILS


def get_timestamp():
    """Returns the current timestamp in the format YYYYMMDD_HHMM"""
    return datetime.now().strftime("%Y%b%d_%H-%M")


def read_and_clean_file(file_path, lower=False):
    """
    Reads the content of a file and cleans the text using the cleantext package.

    :param file_path: The path to the file.

    :return: The cleaned text.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        context = clean(f.read(), lower=lower)
    return context



@router.get("/motivate/{name}")
def main(
    name : Optional[str] = None,
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gpt-4-1106-preview",
    system_prompt: str = "You are a helpful assistant.",
    temperature: float = 0.5,
    max_tokens: int = 256,
    n: int = 1,
    stop: Optional[Union[str, list]] = None,
    presence_penalty: float = 0.0,
    frequency_penalty: float = 0.0,
    input_path = "./gpt/prompt_text.txt",
):
    FOLDER_NAME = "./gpt/day_wise_outputs"
    # Adding a day level file level cache 
    if not os.path.isdir(FOLDER_NAME):
        Path(FOLDER_NAME).mkdir(parents=True)
    
    date_today = datetime.today().strftime('%Y-%m-%d')

    if os.path.exists(os.path.join(FOLDER_NAME, date_today)):
        quote = json.loads(open(os.path.join(FOLDER_NAME, date_today)).read())[0]
        quote = quote.replace("NAME", name)
        return {
        "id" : str(date_today),
        "quote" : quote,
        "author" : f"For {name} with love from GPT !"
    }

    openai.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
    assert (
        openai.api_key is not None
    ), "API key not found - pass as arg or set environment variable OPENAI_API_KEY"

    prompts = []
    if input_path:
        prompt = prompt if prompt else ""
        input_path = Path(input_path)
        assert input_path.exists(), f"Path {input_path} does not exist."
        if input_path.is_file():
            with open(input_path, "r") as f:
                content = f.read()
            prompts.append(prompt + "\n" + content)
    else:
        raise Exception("Where is prompt man ?")

    assert len(prompts) > 0, "No prompts found."
    validate_model(model)

    print(prompt)
    

    generated_texts = chat_generate_text(
        name,
        prompt=prompts[0],
        model=model,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        n=n,
        stop=stop,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
    )
    # Save the output 
    with open(os.path.join(FOLDER_NAME, date_today), "w") as f:
        f.write(json.dumps(generated_texts))
    quote = str(generated_texts[0])
    quote = quote.replace("NAME", name)
    
    return {
        "id" : str(date_today),
        "quote" : quote,
        "author" : f"For {name} with love from GPT!"
    }


if __name__ == "__main__":
    fire.Fire(main)
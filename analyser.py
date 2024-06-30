import os
import re
import base64
import mimetypes
from openai import AzureOpenAI
from config import *


client = AzureOpenAI(
    azure_endpoint= api_base,
    api_key= api_key,
    api_version= api_version
)


def read_file_contents(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def prompt_action(system_content, user_input):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
    )
    # print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)


def prompt_action_vision_mode(system_content, user_input, prompt_images_base64):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # {
            #     "role": "system",
            #     "content": system_content
            # },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": system_content + "\n" + user_input
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": next(iter(prompt_images_base64.values()))
                        }
                    }
                ],
            }
        ]
    )
    # print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)


def encode_image_to_base64(image_path):
    """Reads an image, converts it to a base64 encoded string, and formats it with MIME type."""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    data_uri = f"data:{mime_type};base64,{encoded_string}"
    return data_uri


def process_markdown_for_images(markdown_content, directory):
    """
    Processes Markdown content to find image references, encode the images in base64
    with the correct format, and returns modified content without image references
    and a dictionary of images.
    """
    image_refs = re.findall(r'!\[.*?\]\((.*?)\)', markdown_content)
    images_base64 = {}
    for image_ref in image_refs:
        image_path = os.path.join(directory, image_ref)
        if os.path.exists(image_path):
            data_uri = encode_image_to_base64(image_path)
            images_base64[image_ref] = data_uri
            # Remove the image reference from markdown_content
            markdown_content = markdown_content.replace(f'![{image_ref}]', '')
        else:
            print(f"Image file not found: {image_ref}")
    return markdown_content, images_base64


def main_script(user_prompt, image_path):
    # EXPECTED INPUT IS SYSTEM.MD, INPUT.MD & IMAGE DIAGRAM IN THE SAME FOLDER
    system_prompt = open("system_prompt.md", "r")
    system_prompt = system_prompt.read()

    user_prompt_modified, prompt_images_base64 = process_markdown_for_images(user_prompt, image_path)

    if prompt_images_base64:
        response = prompt_action_vision_mode(system_prompt, user_prompt_modified, prompt_images_base64)
    else:
        response = prompt_action(system_prompt, user_prompt_modified)
    return str(response)




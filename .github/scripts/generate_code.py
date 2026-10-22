import os
import re
from google import genai
from google.genai import types

MODEL_NAME = "gemini-3.8-flash"


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)

    issue_title = os.environ.get("ISSUE_TITLE", "")
    issue_body = os.environ.get("ISSUE_BODY", "")

    file_path = "index.html"

    with open(file_path, "r", encoding="utf-8") as f:
        current_code = f.read()

    prompt = f"""
You are an expert web developer. You are updating a single-file web application for a user.
Here is the current code of the application:

<CODE_START>
{current_code}
<CODE_END>

The user has requested the following changes in a GitHub issue:
Title: {issue_title}
Body: {issue_body}

CRITICAL RULES:
1. Return ONLY the complete, updated HTML code from <!DOCTYPE html> to </html>.
2. Wrap your entire HTML output between <HTML_OUTPUT> and </HTML_OUTPUT> tags.
3. Do NOT truncate the code or use placeholders like <!-- rest of code -->.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=65536,
            temperature=0.2,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response. Aborting to protect index.html.")

    new_code = response.text.strip()

    ticks = chr(96) * 3
    match_tags = re.search(r"<HTML_OUTPUT>\s*(.*?)\s*</HTML_OUTPUT>", new_code, re.DOTALL)
    match_md = re.search(ticks + r"(?:html)?\s*(.*?)\s*" + ticks, new_code, re.DOTALL)

    if match_tags:
        new_code = match_tags.group(1)
    elif match_md:
        new_code = match_md.group(1)

    if "<!DOCTYPE html>" in new_code and "</html>" in new_code:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_code)
    else:
        raise ValueError("Gemini did not return a complete HTML file. Aborting to protect index.html.")


if __name__ == "__main__":
    main()

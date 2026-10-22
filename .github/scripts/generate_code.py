import os
import re
import google.generativeai as genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    issue_title = os.environ.get("ISSUE_TITLE", "")
    issue_body = os.environ.get("ISSUE_BODY", "")
    
    # This assumes your website code is in index.html
    file_path = "index.html" 
    
    with open(file_path, "r", encoding="utf-8") as f:
        current_code = f.read()

    # FIXED: Properly closed the f-string and included the issue details
    prompt = f"""
You are an expert web developer. You are updating a single-file web application for a user.
Here is the current code of the application:

```html
{current_code}

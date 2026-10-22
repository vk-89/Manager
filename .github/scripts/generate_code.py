import os
import re
import google.generativeai as genai

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

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

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    
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

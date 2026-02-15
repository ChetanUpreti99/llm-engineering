import os
from dotenv import load_dotenv
from openai import OpenAI
import json

from scraper import fetch_website_links

load_dotenv(override=True)

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")


SYSTEM_PROMPT = """You are a subject-line generator for emails.

Given the email content, produce ONE short, clear, professional subject line.

Rules:
- Output ONLY the subject line text. No quotes, no labels, no extra commentary.
- Keep it concise: ideally 4–9 words, never more than 60 characters unless absolutely necessary.
- Capture the main intent (request / update / decision needed / meeting / follow-up / invoice / access / issue).
- If there is a clear call-to-action, start with a strong verb (Review, Approve, Confirm, Action needed).
- Preserve key identifiers ONLY if present (ticket IDs, order/invoice numbers, project names, dates).
- Do NOT invent details not explicitly in the email.
- Avoid sensitive personal data in the subject (passwords, OTPs, bank details, etc.).
- If multiple topics exist, choose the most actionable/important.
Return exactly one subject line.
"""
MODEL = 'gpt-5-nano'
openAI = OpenAI()


link_system_prompt = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

def get_links_user_prompt(url):
    user_prompt = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt


def select_relevant_links(url: str):
    response = openAI.responses.create(
        model=MODEL,
        instructions=link_system_prompt.strip(),
        input=get_links_user_prompt(url),
        text={"format": {"type": "json_object"}},
    )

    raw = (response.output_text or "").strip()
    return json.loads(raw)


print(select_relevant_links("https://react.dev/"))
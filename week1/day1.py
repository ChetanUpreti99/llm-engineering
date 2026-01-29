import os
from dotenv import load_dotenv
from openai import OpenAI

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


message = "Hello, GPT! This is my first ever message to you! Hi!"
messages = [{"role": "user", "content": message}]

openAI = OpenAI()


# response = openAI.chat.completions.create(model="gpt-5-nano", messages=messages)
# print(response.choices[0].message.content)


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

def suggest_subject(email_text: str, model: str = "gpt-5.2") -> str:
    resp = openAI.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=email_text,
        temperature=0.2          
    )
    subject = (resp.output_text or "").strip()
    return subject


if __name__ == "__main__":
    email_body = """
        Hi Navid,

        Sharing an update on the ECS situation in the TEST environment and what I’ve checked so far.

        Context
        - We noticed that new tasks are not staying up for long. They either fail to start or stop shortly after starting.
        - The last successful deployment visible in the console looks very old (it shows ~118 days ago), so it’s not clear if recent changes are even rolling out correctly.

        What I’m seeing
        1) Service events / symptoms
        - “task failed to start” appears repeatedly in the service events.
        - When I try to force a new deployment, tasks attempt to launch but don’t stabilize.
        - Desired count is > 0, but running count keeps dropping back.

        2) Things I already checked (to avoid duplicating effort)
        - Task definition revision looks correct at a glance (image tag, env vars, ports).
        - Security group inbound/outbound rules look unchanged from prior working setup.
        - I don’t see obvious CPU/memory over-allocation for the task size, but I’m not 100% sure about account-wide capacity.

        3) Suspects / quick hypotheses
        - Capacity / placement: cluster may not have enough available resources (CPU, memory) or there could be a constraint that prevents placement.
        - Networking: ENI/IP exhaustion in subnets (especially if we’re on awsvpc mode).
        - Image pull: ECR auth/pull issues or a missing image tag.
        - Permissions: IAM role regression (task role vs execution role) impacting image pull, logs, secrets, etc.
        - Health checks: container comes up but fails health checks and gets killed, so it looks like “starts then stops”.

        What I need help with
        If you can help validate these, we’ll get to root-cause quickly:

        A) Can you check the ECS service events and the stopped task reason details?
        - Specifically the “stopped reason” and exit code for the latest stopped task.
        - Also whether the service is failing placement vs failing after container start.

        B) Can you confirm cluster capacity / placement constraints?
        - Any recent changes to EC2 capacity, autoscaling, instance types, or capacity providers?
        - If we’re running out of IPs in subnets, we may need to expand subnets or adjust networking.

        C) If logs exist, can you confirm whether the container is failing health checks?
        - CloudWatch log group / stream for the task should show whether the app starts and then crashes or fails readiness.

        Impact
        - This blocks testing for the ongoing API/UI changes in TEST and is slowing down validation work.

        If you’re okay with it, I can jump on a quick 15-minute call today and share my screen while we look at the ECS events + stopped reason together. I’m free between 3:30–5:30 PM IST.

        Thanks,
        Chetan

    """
    print(suggest_subject(email_body))
import os, requests
def chat(messages, temperature=0):
    """Calls any OpenAI-compatible chat endpoint using YOUR free key."""
    r = requests.post(os.environ["LLM_BASE_URL"].rstrip("/") + "/chat/completions",
        headers={"Authorization": "Bearer " + os.environ["LLM_API_KEY"]},
        json={"model": os.environ["LLM_MODEL"], "messages": messages, "temperature": temperature}, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def synthesize_ebird(observations, context: str = "") -> str:
    """
    Pass raw eBird observations (list of dicts) or a pre-formatted string
    to Claude and get back a short natural language summary.
    """
    if isinstance(observations, list):
        if not observations:
            return "No recent bird observations found for your area."
        obs_text = "\n".join([
            f"{obs.get('comName', 'Unknown')} ({obs.get('howMany', '?')})"
            f" at {obs.get('locName', 'unknown location')}"
            f" on {obs.get('obsDt', 'unknown date')}"
            for obs in observations
        ])
    else:
        obs_text = observations

    context_line = f"Context: {context}\n\n" if context else ""

    prompt = f"""{context_line}Data pulled from eBird:

{obs_text}

Write a short, engaging summary of what birds have been seen recently in this area. 
Keep it under 1800 characters. 
Focus on what's interesting or notable — common patterns, any species worth highlighting, 
or seasonal context if relevant. 
Write in plain language, not a bulleted list.
Do not invent any observations that aren't in the data."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text
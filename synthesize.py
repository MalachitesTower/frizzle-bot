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

Write a short, engaging summary of what birds have been seen in this area. 
Rules: 
- Only mention species and locations that appear in the provided data. Never fabricate or infer observations.
- Keep it under 1990 characters. 
- Lead with the most interesting or unusual sightings. Rare visitor > an early arrival > charismatic species > common, noncharismatic species as prioritization.
- Name the species and where it was seen. Exact counts and dates are low priority unless the number itself is notable.
- Add a sentence of context for highlighted species — why it's interesting, what it tells us about the season, or what makes the habitat relevant.
- If historic data is available, use it to suggest what else an observer might look for in this area, not to compare against current sightings.
- Write in plain, conversational prose. Bold common names of birds. No bullet points, no headers, no jargon. Keep paragraphs short. Do not title reports. 
- Do not pad with filler or generic birding language. If the data is thin, write less."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def synthesize_inat(observations, context: str = "") -> str:
    """
    Pass raw iNaturalist observations (list of dicts) or a pre-formatted string
    to Claude and get back a short natural language summary.
    """
    if isinstance(observations, list):
        if not observations:
            return "No recent nature observations found for your area."
        obs_text = "\n".join([
            f"{(obs.get('taxon') or {}).get('preferred_common_name') or (obs.get('taxon') or {}).get('name', 'Unknown species')}"
            f" at {obs.get('place_guess', 'unknown location')}"
            f" on {obs.get('observed_on', 'unknown date')}"
            for obs in observations
        ])
    else:
        obs_text = observations

    context_line = f"Context: {context}\n\n" if context else ""

    prompt = f"""{context_line}Data pulled from iNaturalist:

{obs_text}

Write a short, engaging summary of plants and non-bird fauna that have been observed in this area.
Rules: 
- Only mention species and locations that appear in the provided data. Never fabricate or infer observations.
- Keep it under 1990 characters. 
- Lead with the most interesting or unusual sightings. Rare visitor > an early arrival > charismatic species > common, noncharismatic species as prioritization.
- Name the species and where it was seen. Exact counts and dates are low priority unless the number itself is notable.
- Add a sentence of context for highlighted species — why it's interesting, what it tells us about the season, or what makes the habitat relevant.
- If historic data is available, use it to suggest what else an observer might look for in this area, not to compare against current sightings.
- Write in plain, conversational prose. Bold common names of fauna and flora. No bullet points, no headers, no jargon. Keep paragraphs short. Do not title reports. 
- Do not pad with filler or generic language. If the data is thin, write less."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

def synthesize_all(text: str, context: str = "") -> str:
    """
    Synthesize a combined natural history summary from pre-formatted eBird and iNaturalist data.
    Accepts a pre-formatted string covering birds and other taxa.
    """
    context_line = f"Context: {context}\n\n" if context else ""

    prompt = f"""{context_line}Data pulled from eBird and iNaturalist:

{text}

Write a short, engaging natural history summary of what birds, flora, and fauna have been observed recently in this area.
Rules:
- Only mention species and locations that appear in the provided data. Never fabricate or infer observations.
- Keep it under 1990 characters.
- Lead with the most interesting or unusual sightings across all taxa. Rare visitor > early seasonal arrival > charismatic species > common, noncharismatic species.
- Name the species and where it was seen. Exact counts and dates are low priority unless the number itself is notable.
- Add a sentence of context for highlighted species — why it's interesting, what it tells us about the season, or what makes the habitat relevant.
- If historic data is available, use it to suggest what else an observer might look for in this area, not to compare against current sightings.
- Write in plain, conversational prose. Bold common names of bird, fauna, and flora. No bullet points, no headers, no jargon. Keep paragraphs short. Do not title reports. 
- Do not pad with filler. If the data is thin, write less."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text

import json

import markdown
from django.conf import settings
from django.utils.safestring import mark_safe
from openai import OpenAI


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _section_count_for_length(desired_length):
    """Return the number of body sections appropriate for the desired word count."""
    length = int(desired_length or 1800)
    if length <= 600:
        return 2
    elif length <= 1000:
        return 3
    elif length <= 1500:
        return 4
    elif length <= 2200:
        return 5
    elif length <= 3000:
        return 6
    else:
        return 7


def generate_outline_from_brief(brief):
    num_sections = _section_count_for_length(brief.desired_length)
    # Distribute words: intro ~15%, conclusion ~15%, body sections split the rest
    total_words = int(brief.desired_length or 1800)
    intro_words = max(60, round(total_words * 0.15))
    conclusion_words = max(60, round(total_words * 0.15))
    body_words = total_words - intro_words - conclusion_words
    per_section_words = max(60, round(body_words / num_sections))

    prompt = f"""
You are a professional blog content strategist.

Based on the content brief below, generate a blog outline that fits the desired total length of {total_words} words.

Return ONLY valid JSON in this exact format:
{{
  "raw_outline": [
    {{
      "heading": "Heading 1",
      "notes": "A paragraph explaining exactly what this section should cover, including key points and direction."
    }},
    {{
      "heading": "Heading 2",
      "notes": "A paragraph explaining exactly what this section should cover, including key points and direction."
    }}
  ],
  "intro_instruction": "A paragraph explaining how to write the introduction",
  "conclusion_instruction": "A paragraph explaining how to write the conclusion"
}}

IMPORTANT REQUIREMENTS:
- Generate EXACTLY {num_sections} body sections inside "raw_outline"
- Do not generate fewer or more than {num_sections} body sections
- Each heading must be distinct, useful, and logically ordered
- The sections must flow naturally from one to the next
- The intro should be written in approximately {intro_words} words
- The conclusion should be written in approximately {conclusion_words} words
- Each body section should be written in approximately {per_section_words} words
- Tailor the depth and detail of the notes to match the target section length above
- Always return strict JSON only

Content brief:
Prompt: {brief.prompt}
Title guidance: {brief.title_guidance}
Tone: {brief.tone}
Audience: {brief.audience}
Objective: {brief.objective}
Keywords: {brief.keywords}
Writing style: {brief.writing_style}
Instructions: {brief.instructions}
Desired total length: {total_words} words
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You generate blog outlines. Generate EXACTLY {num_sections} body sections in raw_outline. Always return strict JSON only."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.7,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "", 1).strip()
    if content.startswith("```"):
        content = content.replace("```", "", 1).strip()
    if content.endswith("```"):
        content = content[:-3].strip()

    return json.loads(content)


def generate_section_content(title, instruction, tone="", audience="", writing_style="", word_limit=None):
    word_instruction = f"- Write approximately {word_limit} words. Do not significantly exceed this limit." if word_limit else "- Write clear, coherent, and informative content."
    prompt = f"""
You are an expert blog writer.

Write a complete, publication-ready section for a blog post.

Section title: {title}
Instruction: {instruction}
Tone: {tone}
Audience: {audience}
Writing style: {writing_style}

Requirements:
- Return plain text only (no markdown code fences).
{word_instruction}
- Use examples when useful.
- Keep the section focused on the title and instruction.
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write high-quality blog sections as plain text.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
    )

    return (response.choices[0].message.content or "").strip()


def generate_sections_from_outline(project):
    outline = project.outline
    brief = project.brief

    total_words = int(brief.desired_length or 1800)
    num_body = len(outline.raw_outline)
    intro_words = max(60, round(total_words * 0.15))
    conclusion_words = max(60, round(total_words * 0.15))
    body_words = total_words - intro_words - conclusion_words
    per_section_words = max(60, round(body_words / num_body)) if num_body else 200

    sections = []
    order = 0

    intro_content = generate_section_content(
        title="Introduction",
        instruction=outline.intro_instruction,
        tone=brief.tone,
        audience=brief.audience,
        writing_style=brief.writing_style,
        word_limit=intro_words,
    )
    sections.append({
        "section_type": "intro",
        "heading": "Introduction",
        "order": order,
        "content": intro_content,
        "generation_prompt": outline.intro_instruction,
    })
    order += 1

    for item in outline.raw_outline:
        heading = item.get("heading", "")
        notes = item.get("notes", "")
        content = generate_section_content(
            title=heading,
            instruction=notes,
            tone=brief.tone,
            audience=brief.audience,
            writing_style=brief.writing_style,
            word_limit=per_section_words,
        )
        sections.append({
            "section_type": "body",
            "heading": heading,
            "order": order,
            "content": content,
            "generation_prompt": notes,
        })
        order += 1

    conclusion_content = generate_section_content(
        title="Conclusion",
        instruction=outline.conclusion_instruction,
        tone=brief.tone,
        audience=brief.audience,
        writing_style=brief.writing_style,
        word_limit=conclusion_words,
    )
    sections.append({
        "section_type": "conclusion",
        "heading": "Conclusion",
        "order": order,
        "content": conclusion_content,
        "generation_prompt": outline.conclusion_instruction,
    })

    return sections


def assemble_full_blog(project):
    sections = project.sections.all().order_by("order")

    full_content = []

    for section in sections:
        content = section.content.strip()

        if section.heading and content.lower().startswith(section.heading.lower()):
            content = content[len(section.heading):].strip()

        full_content.append(f"\n\n## {section.heading}\n\n{content}")

    return "".join(full_content).strip()


def render_blog_markdown(raw_markdown: str):
    """
    Turn assembled blog Markdown into HTML. Single entry point for the web UI
    and API so all projects render consistently.
    """
    if not (raw_markdown or "").strip():
        return ""
    return mark_safe(
        markdown.markdown(
            raw_markdown.strip(),
            extensions=["extra", "nl2br"],
        )
    )
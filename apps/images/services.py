import base64
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from openai import OpenAI


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _save_generated_image(image_b64: str) -> str:
    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception as exc:
        raise ValueError("Image data returned by provider was not valid base64.") from exc

    file_name = f"generated-images/{uuid.uuid4().hex}.png"
    saved_path = default_storage.save(file_name, ContentFile(image_bytes))
    return default_storage.url(saved_path)


def generate_hero_image_prompt(project):
    brief = getattr(project, "brief", None)
    full_blog = getattr(project, "sections", None)

    blog_context = []
    if full_blog:
        for section in project.sections.all().order_by("order"):
            if section.content:
                blog_context.append(section.content[:500])

    joined_context = "\n\n".join(blog_context[:3])

    prompt = f"""
You are an expert prompt writer for AI image generation.

Create a high-quality image generation prompt for a blog hero image.

Requirements:
- The image should be a wide horizontal rectangle hero banner
- It should feel modern, clean, editorial, and professional
- It should visually match the blog topic
- It should not contain readable text inside the image
- It should be suitable for a tech or educational blog header
- Return only the image prompt text, nothing else

Blog information:
Project name: {project.name}
Prompt: {brief.prompt if brief else ""}
Tone: {brief.tone if brief else ""}
Audience: {brief.audience if brief else ""}
Objective: {brief.objective if brief else ""}

Blog context:
{joined_context}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write excellent prompts for AI-generated blog images."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.7,
    )

    return (response.choices[0].message.content or "").strip()


def generate_section_image_prompt(section):
    project = section.project
    brief = getattr(project, "brief", None)

    prompt = f"""
You are an expert prompt writer for AI image generation.

Create a high-quality image generation prompt for a blog section image.

Requirements:
- The image should be a smaller horizontal rectangle
- It should visually represent the section topic
- It should feel modern, clean, editorial, and professional
- It should not contain readable text inside the image
- It should be suitable for a technical or educational blog
- Return only the image prompt text, nothing else

Project name: {project.name}
Section heading: {section.heading}
Section type: {section.section_type}
Section content:
{section.content[:1200]}

Tone: {brief.tone if brief else ""}
Audience: {brief.audience if brief else ""}
Writing style: {brief.writing_style if brief else ""}
""".strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You write excellent prompts for AI-generated blog section images."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.7,
    )

    return (response.choices[0].message.content or "").strip()

def generate_image_from_prompt(prompt):
    # gpt-image-1 currently supports: 1024x1024, 1024x1536, 1536x1024, auto
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
    )

    image_data = response.data[0] if response.data else None
    image_url = getattr(image_data, "url", None)
    if image_url:
        return image_url

    # Some gpt-image-1 responses return base64 image bytes instead of a hosted URL.
    image_b64 = getattr(image_data, "b64_json", None)
    if image_b64:
        return _save_generated_image(image_b64)

    raise ValueError("Image generation succeeded but returned no image data.")
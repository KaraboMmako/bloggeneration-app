from django.contrib.auth import authenticate, login, logout, get_user_model
from apps.generation.services import assemble_full_blog, render_blog_markdown, generate_section_content
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from apps.blogs.models import BlogProject
from apps.generation.models import BlogSection
from apps.images.models import BlogImage
from apps.images.services import generate_section_image_prompt, generate_image_from_prompt


User = get_user_model()



# AUTH VIEWS

def login_page(request):
    if request.user.is_authenticated:
        return redirect("frontend:dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("frontend:dashboard")

        messages.error(request, "Invalid email or password.")

    return render(request, "frontend/login.html")


def register_page(request):
    if request.user.is_authenticated:
        return redirect("frontend:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("frontend:register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("frontend:register")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)
        return redirect("frontend:dashboard")

    return render(request, "frontend/register.html")

def forgot_password_page(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        form = PasswordResetForm({"email": email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="registration/password_reset_email.html",
                subject_template_name="registration/password_reset_subject.txt",
                from_email=settings.DEFAULT_FROM_EMAIL,
                extra_email_context={"domain": request.get_host()},
            )
        messages.success(
            request,
            "Reset link sent! Check your inbox. If you don't receive an email, that address isn't registered."
        )
        return redirect("frontend:forgot_password")

    return render(request, "frontend/forgot_password.html")

def logout_page(request):
    from django.contrib.messages import get_messages
    list(get_messages(request))  # consume and discard all pending messages
    logout(request)
    return redirect("frontend:login")


# APP PAGES


@login_required(login_url="frontend:login")
def dashboard_page(request):
    query = request.GET.get("q", "")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    status_filter = request.GET.get("status", "")

    my_projects = BlogProject.objects.filter(user=request.user)

    if query:
        my_projects = my_projects.filter(name__icontains=query)

    if date_from:
        my_projects = my_projects.filter(created_at__date__gte=date_from)

    if date_to:
        my_projects = my_projects.filter(created_at__date__lte=date_to)

    if status_filter in ("draft", "published", "completed"):
        my_projects = my_projects.filter(status=status_filter)

    my_projects = my_projects.order_by("-created_at")

    community_blogs = (
        BlogProject.objects
        .filter(status="published")
        .exclude(user=request.user)
        .order_by("-updated_at")
    )
    if query:
        community_blogs = community_blogs.filter(name__icontains=query)

    return render(request, "frontend/dashboard.html", {
        "projects": my_projects,
        "community_blogs": community_blogs,
        "query": query,
        "date_from": date_from,
        "date_to": date_to,
        "status_filter": status_filter,
    })


@login_required(login_url="frontend:login")
def blog_detail_page(request, pk):
    try:
        project = BlogProject.objects.get(pk=pk)
    except BlogProject.DoesNotExist:
        messages.error(request, "Blog project not found.")
        return redirect("frontend:dashboard")

    if project.user != request.user and project.status != "published":
        messages.error(request, "This blog is not available.")
        return redirect("frontend:dashboard")

    sections = project.sections.all().order_by("order")

    hero_image = BlogImage.objects.filter(
        project=project,
        image_type="hero",
        section__isnull=True,
    ).first()

    section_images = BlogImage.objects.filter(
        project=project,
        image_type="section",
        section__isnull=False,
    )

    image_map = {
        image.section_id: image
        for image in section_images
    }

    review = request.GET.get("review") == "1" and project.user == request.user

    return render(request, "frontend/blog_detail.html", {
        "project": project,
        "sections": sections,
        "hero_image": hero_image,
        "image_map": image_map,
        "review": review,
    })


@login_required(login_url="frontend:login")
def generate_blog_page(request):
    if request.method == "POST":
        name = request.POST.get("name")
        prompt = request.POST.get("prompt")
        title_guidance = request.POST.get("title_guidance", "")
        tone = request.POST.get("tone", "Professional")
        audience = request.POST.get("audience", "")
        objective = request.POST.get("objective", "")
        writing_style = request.POST.get("writing_style", "Blog-style")
        instructions = request.POST.get("instructions", "")
        desired_length = request.POST.get("desired_length") or 1800
        keywords_raw = request.POST.get("keywords", "")

        keywords = [
            keyword.strip()
            for keyword in keywords_raw.split(",")
            if keyword.strip()
        ]

        project = BlogProject.objects.create(
            user=request.user,
            name=name,
        )

        from apps.prompts.models import ContentBrief
        from apps.generation.models import BlogOutline, BlogSection
        from apps.generation.services import generate_outline_from_brief, generate_sections_from_outline
        from apps.images.models import BlogImage
        from apps.images.services import generate_hero_image_prompt, generate_image_from_prompt

        brief = ContentBrief.objects.create(
            project=project,
            prompt=prompt,
            title_guidance=title_guidance,
            tone=tone,
            audience=audience,
            objective=objective,
            keywords=keywords,
            writing_style=writing_style,
            instructions=instructions,
            desired_length=desired_length,
        )

        outline_data = generate_outline_from_brief(brief)

        BlogOutline.objects.update_or_create(
            project=project,
            defaults={
                "raw_outline": outline_data.get("raw_outline", []),
                "intro_instruction": outline_data.get("intro_instruction", ""),
                "conclusion_instruction": outline_data.get("conclusion_instruction", ""),
            },
        )

        generated_sections = generate_sections_from_outline(project)

        BlogSection.objects.filter(project=project).delete()

        for section_data in generated_sections:
            BlogSection.objects.create(
                project=project,
                section_type=section_data["section_type"],
                heading=section_data["heading"],
                order=section_data["order"],
                content=section_data["content"],
                generation_prompt=section_data["generation_prompt"],
                is_generated=True,
            )

        try:
            image_prompt = generate_hero_image_prompt(project)
            image_url = generate_image_from_prompt(image_prompt)

            BlogImage.objects.update_or_create(
                project=project,
                section=None,
                image_type="hero",
                defaults={
                    "prompt": image_prompt,
                    "image_url": image_url,
                    "alt_text": f"Hero image for {project.name}",
                    "order": 0,
                    "is_generated": True,
                },
            )
        except Exception:
            pass

        project.status = "draft"
        project.save(update_fields=["status"])

        from django.urls import reverse
        return redirect(reverse("frontend:blog_detail", kwargs={"pk": project.id}) + "?review=1")

    return render(request, "frontend/generate_blog.html")


@login_required(login_url="frontend:login")
def update_section_page(request, section_id):
    try:
        section = BlogSection.objects.select_related("project").get(
            id=section_id,
            project__user=request.user,
        )
    except BlogSection.DoesNotExist:
        messages.error(request, "Section not found.")
        return redirect("frontend:dashboard")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            section.content = content
            section.save(update_fields=["content", "updated_at"])
            messages.success(request, "Section updated successfully.")

    return redirect("frontend:blog_detail", pk=section.project.id)


@login_required(login_url="frontend:login")
def regenerate_section_page(request, section_id):
    try:
        section = BlogSection.objects.select_related("project").get(
            id=section_id,
            project__user=request.user,
        )
    except BlogSection.DoesNotExist:
        messages.error(request, "Section not found.")
        return redirect("frontend:dashboard")

    if request.method == "POST":
        brief = getattr(section.project, "brief", None)

        extra_instruction = request.POST.get("extra_instruction", "")

        instruction = section.generation_prompt or ""

        if extra_instruction:
            instruction += f"\n\nAdditional instruction:\n{extra_instruction}"

        # Calculate a per-section word target from the brief if available
        word_limit = None
        if brief and brief.desired_length:
            total_sections = section.project.sections.count() or 1
            total_words = int(brief.desired_length)
            word_limit = max(60, round(total_words / total_sections))

        section.content = generate_section_content(
            title=section.heading,
            instruction=instruction,
            tone=brief.tone if brief else "",
            audience=brief.audience if brief else "",
            writing_style=brief.writing_style if brief else "",
            word_limit=word_limit,
        )
        section.is_generated = True
        section.save(update_fields=["content", "is_generated", "updated_at"])

        messages.success(request, "Section regenerated successfully.")
        return redirect("frontend:blog_detail", pk=section.project.id)

    return redirect("frontend:blog_detail", pk=section.project.id)


@login_required(login_url="frontend:login")
def generate_section_image_page(request, section_id):
    try:
        section = BlogSection.objects.select_related("project").get(
            id=section_id,
            project__user=request.user,
        )
    except BlogSection.DoesNotExist:
        messages.error(request, "Section not found.")
        return redirect("frontend:dashboard")

    if request.method == "POST":
        prompt = generate_section_image_prompt(section)
        image_url = generate_image_from_prompt(prompt)

        BlogImage.objects.update_or_create(
            project=section.project,
            section=section,
            image_type="section",
            defaults={
                "prompt": prompt,
                "image_url": image_url,
                "alt_text": f"Image for section {section.heading}",
                "order": section.order,
                "is_generated": True,
            },
        )

        messages.success(request, "Section image generated successfully.")
        return redirect("frontend:blog_detail", pk=section.project.id)

    return redirect("frontend:blog_detail", pk=section.project.id)


@login_required(login_url="frontend:login")
def regenerate_blog_page(request, pk):
    from apps.generation.models import BlogOutline, BlogSection
    from apps.generation.services import generate_outline_from_brief, generate_sections_from_outline
    from apps.images.services import generate_hero_image_prompt, generate_image_from_prompt

    project = BlogProject.objects.filter(pk=pk, user=request.user).first()
    if not project:
        return redirect("frontend:dashboard")

    if request.method == "POST":
        try:
            brief = project.brief
        except Exception:
            messages.error(request, "No brief found for this blog. Cannot regenerate.")
            return redirect("frontend:blog_detail", pk=project.id)

        outline_data = generate_outline_from_brief(brief)

        BlogOutline.objects.update_or_create(
            project=project,
            defaults={
                "raw_outline": outline_data.get("raw_outline", []),
                "intro_instruction": outline_data.get("intro_instruction", ""),
                "conclusion_instruction": outline_data.get("conclusion_instruction", ""),
            },
        )

        generated_sections = generate_sections_from_outline(project)

        BlogSection.objects.filter(project=project).delete()

        for section_data in generated_sections:
            BlogSection.objects.create(
                project=project,
                section_type=section_data["section_type"],
                heading=section_data["heading"],
                order=section_data["order"],
                content=section_data["content"],
                generation_prompt=section_data["generation_prompt"],
                is_generated=True,
            )

        try:
            image_prompt = generate_hero_image_prompt(project)
            image_url = generate_image_from_prompt(image_prompt)
            BlogImage.objects.update_or_create(
                project=project,
                section=None,
                image_type="hero",
                defaults={
                    "prompt": image_prompt,
                    "image_url": image_url,
                    "alt_text": f"Hero image for {project.name}",
                    "order": 0,
                    "is_generated": True,
                },
            )
        except Exception:
            pass

        project.status = "draft"
        project.save(update_fields=["status"])
        messages.success(request, f'"{project.name}" has been regenerated successfully.')

        from django.urls import reverse
        return redirect(reverse("frontend:blog_detail", kwargs={"pk": project.id}) + "?review=1")

    return redirect("frontend:blog_detail", pk=project.id)


@login_required(login_url="frontend:login")
def set_blog_status_page(request, pk):
    project = BlogProject.objects.filter(pk=pk, user=request.user).first()
    if not project:
        return redirect("frontend:dashboard")

    if request.method == "POST":
        status = request.POST.get("status")
        if status in ("draft", "completed"):
            project.status = status
            project.save(update_fields=["status", "updated_at"])
            label = "Draft" if status == "draft" else "Completed"
            messages.success(request, f'"{project.name}" saved as {label}.')

    return redirect("frontend:dashboard")


@login_required(login_url="frontend:login")
def publish_blog_page(request, pk):
    project = BlogProject.objects.filter(pk=pk, user=request.user).first()
    if not project:
        return redirect("frontend:dashboard")

    if request.method == "POST":
        if project.status == "published":
            project.status = "draft"
            project.save(update_fields=["status", "updated_at"])
            messages.success(request, f'"{project.name}" has been unpublished.')
        else:
            project.status = "published"
            project.save(update_fields=["status", "updated_at"])
            messages.success(request, f'"{project.name}" is now published and visible to everyone.')

    next_url = request.POST.get("next", "frontend:dashboard")
    if next_url == "detail":
        return redirect("frontend:blog_detail", pk=project.id)
    return redirect("frontend:dashboard")


@login_required(login_url="frontend:login")
def delete_blog_page(request, pk):
    project = BlogProject.objects.filter(pk=pk, user=request.user).first()
    if not project:
        return redirect("frontend:dashboard")

    if request.method == "POST":
        project.delete()
        messages.success(request, f'"{project.name}" has been deleted.')

    return redirect("frontend:dashboard")
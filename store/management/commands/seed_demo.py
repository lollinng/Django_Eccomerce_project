"""
Fill a local database with demo data: categories, books with generated cover
images, a staff account for the admin and a customer account.

    python manage.py seed_demo
    python manage.py seed_demo --password "something-else"

Safe to run more than once: rows are matched by slug or email and updated.
Every name, title and email address here is made up.
"""

import datetime
import math
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from account.models import UserBase
from store.models import Category, Product

CATEGORIES = [
    ("Python", "python"),
    ("Web Development", "web-development"),
    ("Data & AI", "data-ai"),
    ("Software Design", "software-design"),
]

# (category slug, slug, title, author, price, description, colours, motif)
# colours: (gradient top, gradient bottom, accent)
BOOKS = [
    ("python", "python-from-scratch", "Python from Scratch", "Nina Varga", "24.99",
     "A hands-on first book on Python 3: variables, functions, data structures and modules, "
     "built up one small project at a time. Every chapter ends with exercises and a worked "
     "solution, so you finish with a set of scripts you actually understand.",
     ("#1d4e89", "#0b2545", "#ffd166"), "rings"),
    ("web-development", "shipping-django", "Shipping Django", "Ravi Menon", "29.99",
     "From startproject to production: models and migrations, the ORM, views, forms, sessions, "
     "authentication and the admin. Finishes with settings, static files and a deployment "
     "checklist you can reuse on your next project.",
     ("#0f5132", "#06281a", "#9be7c4"), "stripes"),
    ("data-ai", "vectors-and-search", "Vectors and Search", "Ivy Chen", "38.00",
     "How embeddings, vector indexes and hybrid ranking work, and how to build semantic search "
     "over your own documents. Covers chunking, evaluation and keeping an index fresh as the "
     "documents change.",
     ("#4b2c83", "#1e1036", "#f4a6ff"), "grid"),
    ("software-design", "designing-small-services", "Designing Small Services", "Hugo Lindqvist", "36.00",
     "When to split a monolith and when not to. Service boundaries, messaging, consistency, "
     "observability and the operational cost of every new service, with case studies from "
     "teams of five to fifty.",
     ("#2f3e46", "#141c20", "#f6bd60"), "blocks"),
    ("python", "async-python-in-practice", "Async Python in Practice", "Tomas Reyes", "32.50",
     "asyncio without the mystery. Event loops, tasks, cancellation and backpressure, explained "
     "through a crawler, a chat server and a rate-limited API client, plus the debugging habits "
     "that save hours when coroutines go quiet.",
     ("#f2a541", "#c4561f", "#fff4d6"), "waves"),
    ("web-development", "rest-api-field-guide", "REST API Field Guide", "Clara Jensen", "34.00",
     "Resource design, status codes, pagination, filtering, versioning and authentication for "
     "HTTP APIs. Each pattern comes with its trade-offs and a reference implementation you can "
     "adapt to your own service.",
     ("#e76f51", "#9c3020", "#ffe8d6"), "rings"),
    ("data-ai", "data-pipelines-that-last", "Data Pipelines That Last", "Marco Bellini", "31.25",
     "Design batch and streaming pipelines that survive bad input and schema changes: "
     "idempotent loads, retries, data contracts, monitoring and backfills, with runnable "
     "examples for each failure mode.",
     ("#264653", "#10232b", "#2a9d8f"), "stripes"),
    ("software-design", "sql-for-backend-devs", "SQL for Backend Devs", "Sara Whitfield", "26.75",
     "Joins, indexes, transactions and query plans for developers who use an ORM every day. "
     "Learn to read EXPLAIN output and fix the slow query before it reaches production.",
     ("#e9c46a", "#b9832b", "#3d2c00"), "grid"),
    ("python", "testing-python-apps", "Testing Python Apps", "Lena Okoro", "27.00",
     "Write tests you trust. Covers pytest fixtures, parametrisation, mocking at the right "
     "boundary, testing Django views and models, and keeping a suite fast as the codebase grows.",
     ("#2b9348", "#0d4f22", "#eeef20"), "blocks"),
    ("web-development", "html-css-layout-recipes", "HTML & CSS Layout Recipes", "Omar Haddad", "19.50",
     "Flexbox and grid recipes for the layouts you build every week: navbars, card grids, "
     "sidebars, forms and responsive product pages, with notes on accessibility and browser quirks.",
     ("#5e60ce", "#2d2f8f", "#80ffdb"), "waves"),
    ("data-ai", "small-models-big-results", "Small Models, Big Results", "Priya Nair", "36.50",
     "Get more from compact machine-learning models: feature work, fine-tuning, quantisation "
     "and serving on modest hardware, with benchmarks that show what each step buys.",
     ("#d00000", "#6a040f", "#ffba08"), "rings"),
    ("software-design", "caching-in-practice", "Caching in Practice", "Felix Adeyemi", "23.40",
     "Where caches pay off and where they bite: HTTP caching, per-view and per-object caches, "
     "invalidation strategies, cache stampedes and how to measure the hit rate.",
     ("#457b9d", "#1d3557", "#f1faee"), "stripes"),
    ("python", "python-for-automation", "Python for Automation", "Dev Malhotra", "21.99",
     "Turn repetitive work into scripts: files and folders, spreadsheets, PDFs, HTTP APIs and "
     "scheduled jobs. Practical recipes with error handling and logging so the scripts keep "
     "running unattended.",
     ("#3a0ca3", "#10002b", "#4cc9f0"), "grid"),
    ("web-development", "web-security-basics", "Web Security Basics", "Hana Sato", "28.00",
     "CSRF, XSS, SQL injection, session handling and password storage explained with small, "
     "runnable examples, and the framework settings that close each hole.",
     ("#343a40", "#121416", "#ff6b6b"), "blocks"),
    ("data-ai", "applied-llm-engineering", "Applied LLM Engineering", "Sam Achebe", "42.00",
     "Build reliable features on large language models: prompt design, retrieval, tool calling, "
     "evaluation sets and guardrails, with cost and latency budgets kept in view.",
     ("#06d6a0", "#047857", "#073b4c"), "waves"),
]

ADMIN = {"email": "admin@example.com", "user_name": "admin", "first_name": "Admin"}
CUSTOMER = {"email": "demo@example.com", "user_name": "asharao", "first_name": "Asha Rao",
            "country": "GB", "town_city": "Leeds"}

# Cover size on disk (about the shape of a paperback) and the factor it is
# drawn at before downscaling, which smooths the edges of the shapes.
COVER_SIZE = (600, 840)
SUPERSAMPLE = 2

BOLD_FONTS = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf"]
REGULAR_FONTS = ["DejaVuSans.ttf", "arial.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"]


def _font(size, bold=False):
    for name in BOLD_FONTS if bold else REGULAR_FONTS:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _rgb(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    return tuple(int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))


def _wrap(text, font, width):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if font.getlength(candidate) <= width or not line:
            line = candidate
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def _luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def draw_cover(path, title, author, category, colours, motif):
    w, h = COVER_SIZE[0] * SUPERSAMPLE, COVER_SIZE[1] * SUPERSAMPLE
    top, bottom, accent = (_rgb(c) for c in colours)
    text = (20, 20, 20) if _luminance(top) > 150 else (250, 250, 250)

    img = Image.new("RGB", (w, h))
    px = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        px.line([(0, y), (w, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))

    # the motif sits in a band between the title and the author line
    band_top, band_bottom = int(h * 0.48), h - 290
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = accent + (120,)
    if motif == "rings":
        cx, cy = int(w * 0.74), (band_top + band_bottom) // 2
        for r in range(60, 760, 64):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=a, width=14)
    elif motif == "stripes":
        for x in range(-h, w, 110):
            d.polygon([(x, band_bottom), (x + 50, band_bottom),
                       (x + 50 + (band_bottom - band_top), band_top), (x + (band_bottom - band_top), band_top)], fill=a)
    elif motif == "grid":
        for gx in range(150, w - 100, 90):
            for gy in range(band_top + 40, band_bottom - 20, 90):
                d.ellipse([gx - 12, gy - 12, gx + 12, gy + 12], fill=a)
    elif motif == "blocks":
        heights = [0.35, 0.6, 0.48, 0.78, 0.56, 0.95]
        bw = (w - 260) // len(heights)
        for i, frac in enumerate(heights):
            x0 = 130 + i * bw
            d.rectangle([x0 + 12, band_bottom - int((band_bottom - band_top) * frac), x0 + bw - 12, band_bottom], fill=a)
    elif motif == "waves":
        for k in range(6):
            base = band_top + 80 + k * 85
            pts = [(x, base + 55 * math.sin(x / 180 + k * 0.6)) for x in range(0, w + 20, 20)]
            d.line(pts, fill=a, width=16)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rectangle([0, band_top, w, band_bottom], fill=255)
    clipped = Image.composite(layer, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask)
    # darker band on the left, like a book's spine
    d = ImageDraw.Draw(clipped)
    for x in range(70):
        d.line([(x, 0), (x, h)], fill=(0, 0, 0, int(90 * (1 - x / 70))))
    img = Image.alpha_composite(img.convert("RGBA"), clipped).convert("RGB")

    d = ImageDraw.Draw(img)
    margin = 130
    label = _font(44, bold=True)
    d.text((margin, 150), category.upper(), font=label, fill=accent)
    d.rectangle([margin, 225, margin + 120, 235], fill=accent)

    size = 132
    while True:
        font = _font(size, bold=True)
        lines = _wrap(title, font, w - 2 * margin)
        if (len(lines) <= 4 and all(font.getlength(line) <= w - 2 * margin for line in lines)) or size <= 60:
            break
        size -= 8
    y = 300
    for line in lines:
        d.text((margin, y), line, font=font, fill=text)
        y += int(size * 1.18)

    d.rectangle([margin, h - 230, w - margin, h - 226], fill=text)
    d.text((margin, h - 190), author, font=_font(56), fill=text)

    img = img.resize(COVER_SIZE, Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=90, optimize=True)


class Command(BaseCommand):
    help = "Create demo categories, books with generated covers, an admin and a customer account."

    def add_arguments(self, parser):
        parser.add_argument("--password", default="demo12345",
                            help="Password for both demo accounts (default: demo12345).")
        parser.add_argument("--force", action="store_true",
                            help="Run even when DEBUG is off. Never use this on a real site.")

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG and not options["force"]:
            raise CommandError("DEBUG is off: seed_demo writes demo accounts with a known password. "
                               "Pass --force only for a throwaway database.")
        password = options["password"]

        admin = self._user(ADMIN, password, is_staff=True, is_superuser=True)
        self._user(CUSTOMER, password)

        categories = {}
        for name, slug in CATEGORIES:
            categories[slug], _ = Category.objects.update_or_create(slug=slug, defaults={"name": name})

        media = Path(settings.MEDIA_ROOT)
        now = timezone.now()
        for position, (cat, slug, title, author, price, description, colours, motif) in enumerate(BOOKS):
            image = f"images/demo/{slug}.jpg"
            draw_cover(media / image, title, author, categories[cat].name, colours, motif)
            product, _ = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": categories[cat],
                    "created_by": admin,
                    "title": title,
                    "author": author,
                    "description": description,
                    "image": image,
                    "price": price,
                    "in_stock": True,
                    "is_active": True,
                },
            )
            # the shop lists newest first: keep the order of BOOKS
            Product.objects.filter(pk=product.pk).update(created=now - datetime.timedelta(minutes=position))

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(CATEGORIES)} categories and {len(BOOKS)} books (covers in {media / 'images' / 'demo'})."))
        self.stdout.write(f"Admin:    {ADMIN['email']} / {password}  (http://127.0.0.1:8000/admin/)")
        self.stdout.write(f"Customer: {CUSTOMER['email']} / {password}  (http://127.0.0.1:8000/account/login/)")

    def _user(self, fields, password, is_staff=False, is_superuser=False):
        fields = dict(fields)
        email = fields.pop("email")
        user = UserBase.objects.filter(email=email).first()
        if user is None:
            user = UserBase(email=email)
        for key, value in fields.items():
            setattr(user, key, value)
        user.is_active = True
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.set_password(password)
        user.save()
        return user

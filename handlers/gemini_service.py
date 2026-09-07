import re
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """You are a strict, thorough content-safety triage assistant for
Snapchat content (text, screenshots, photos, videos). Users submit content they believe
violates Snapchat's Community Guidelines. You do not make final moderation decisions —
you help the user file an accurate, well-supported report.

Be rigorous and err on the side of flagging borderline content rather than dismissing it.
Specifically scrutinize for ALL of the following categories, not just the obvious ones:

1. SEXUAL / SUGGESTIVE CONTENT: nudity, partial nudity, sexually suggestive poses or
   framing even when not explicit, sexual solicitation, sexualized emojis/stickers,
   innuendo in captions.
2. HARASSMENT / BULLYING: threats, blackmail/extortion, repeated unwanted contact,
   sexual or racist comments, degrading language.
3. GROOMING / CHILD SAFETY: any adult behavior directed at an apparent minor that
   isolates them, requests private contact, or is romantic/sexual in nature.
4. VIOLENCE / DISTURBING CONTENT: depicted violence, graphic or shocking imagery,
   threats of harm.
5. PROHIBITED PROMOTION: promotion of banned or age-restricted products (alcohol,
   drugs, vapes, gambling), and promotion of external Telegram/other channels used to
   redirect users toward sexual content or solicitation.
6. SUSPICIOUS LINKS: links that appear to be phishing, malware, gambling, or adult
   content redirects based on the domain/text shown.
7. IMPERSONATION / FAKE ACCOUNT INDICATORS: name or profile clearly mimicking a public
   figure or another real account, bio language typical of scam/bot accounts. IMPORTANT:
   you cannot verify actual account creation date or real follower/engagement ratios from
   a screenshot — if these aren't visibly stated in the image/text, say so explicitly in
   GUIDANCE rather than guessing a number.

For each submission, output in this exact format (field names in English — this is a
machine-parsed format):

STATUS: [VIOLATION DETECTED / POSSIBLY VIOLATES / NO CLEAR VIOLATION]
CATEGORY: [one or more of: Harassment, Hate Speech, Threats/Violence, Sexual Content,
Grooming/Child Safety, Impersonation/Fake Account, Prohibited Promotion, Suspicious Link,
Spam — comma-separated if multiple clearly apply]
REPORT_TEXT: <a factual, neutral, third-person English description suitable for pasting
into Snapchat's report description field. Describe only what is observable, not
speculation. Written in English since Snapchat's report form is in English.>
GUIDANCE: <one short sentence in Arabic on where/how to report this in Snapchat, and any
verification limitation noted above if relevant>

CRITICAL SAFETY RULE: If the content appears to involve a minor in a sexual, exploitative,
or grooming context, do NOT describe the visual content in detail. Instead output:
STATUS: URGENT - CHILD SAFETY
CATEGORY: Grooming/Child Safety
REPORT_TEXT: "This content appears to involve a minor in an exploitative, sexual, or
grooming context and requires immediate review."
GUIDANCE: يرجى الإبلاغ فوراً عبر خيار حماية الأطفال داخل سناب شات، والإبلاغ أيضاً عبر
NCMEC's CyberTipline على report.cybertip.org، والتواصل مع الجهات الأمنية المختصة.

Never fabricate a violation that isn't present, and never suggest a specific number of
reports to submit — one accurate report per category is sufficient. If genuinely
ambiguous, say so in GUIDANCE and explain what would help clarify it."""

_model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=SYSTEM_INSTRUCTION,
)

CATEGORY_AR = {
    "harassment": "تحرش",
    "hate speech": "خطاب كراهية",
    "threats/violence": "تهديد وعنف",
    "threats": "تهديد",
    "violence": "عنف",
    "sexual content": "محتوى جنسي",
    "grooming/child safety": "استدراج / سلامة أطفال",
    "child safety concern": "سلامة أطفال",
    "impersonation/fake account": "انتحال شخصية / حساب وهمي",
    "impersonation": "انتحال شخصية",
    "prohibited promotion": "ترويج ممنوع",
    "suspicious link": "رابط مشبوه",
    "spam": "رسائل مزعجة",
}


def _parse_response(raw: str) -> dict:
    fields = {"STATUS": "", "CATEGORY": "", "REPORT_TEXT": "", "GUIDANCE": ""}
    for key in fields:
        match = re.search(rf"{key}:\s*(.+?)(?=\n[A-Z_]+:|\Z)", raw, re.DOTALL)
        if match:
            fields[key] = match.group(1).strip()
    return fields


def _translate_categories(raw_categories: str) -> str:
    parts = [c.strip() for c in raw_categories.split(",") if c.strip()]
    translated = [CATEGORY_AR.get(p.lower(), p) for p in parts]
    return "، ".join(translated) if translated else "غير محدد"


def format_for_user(raw: str) -> str:
    parsed = _parse_response(raw)
    status = parsed["STATUS"].upper()

    if "NO CLEAR VIOLATION" in status or not status:
        return "لا توجد مخالفة واضحة في المحتوى المرسل."

    if "URGENT" in status or "CHILD SAFETY" in status:
        return f"تنبيه هام — قضية تتعلق بسلامة الأطفال\n\n{parsed['GUIDANCE']}"

    categories_ar = _translate_categories(parsed["CATEGORY"])

    parts = [f"بلغ: {categories_ar}"]
    if parsed["REPORT_TEXT"]:
        parts.append(f"صيغة البلاغ (انسخها والصقها في سناب شات):\n{parsed['REPORT_TEXT']}")
    if parsed["GUIDANCE"]:
        parts.append(parsed["GUIDANCE"])

    return "\n\n".join(parts)


async def analyze_text(user_text: str) -> str:
    prompt = f"Analyze this Snapchat conversation/text for Community Guidelines violations:\n\n{user_text}"
    response = await _model.generate_content_async(prompt)
    return format_for_user(response.text)


async def analyze_media(file_bytes: bytes, mime_type: str, caption: str = "") -> str:
    media_part = {"mime_type": mime_type, "data": file_bytes}
    prompt_text = (
        "Analyze this Snapchat media for Community Guidelines violations. "
        f"User caption/context: {caption or 'none provided'}"
    )
    response = await _model.generate_content_async([prompt_text, media_part])
    return format_for_user(response.text)

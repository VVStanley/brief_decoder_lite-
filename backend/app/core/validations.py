import re

from app.core.exceptions import BriefInputValidationError


def validate_brief_text(text: str) -> str:
    """Validates and cleans brief input text, rejecting spam, symbols, and gibberish."""
    stripped = text.strip()
    if len(stripped) < 10:
        raise BriefInputValidationError(
            "Brief text must be at least 10 characters after trimming."
        )

    # 1. Extract pure alphabetical words (Unicode letters only, length >= 2)
    alpha_words = re.findall(r"\b[^\W\d_]{2,}\b", stripped, flags=re.UNICODE)
    if len(alpha_words) < 3:
        raise BriefInputValidationError(
            "Brief text must contain at least 3 meaningful alphabetical words."
        )

    # 2. Check for high ratio of special/punctuation characters (> 50%)
    non_alphanumeric = re.findall(r"[^\w\s]", stripped, flags=re.UNICODE)
    if len(non_alphanumeric) / len(stripped) > 0.5:
        raise BriefInputValidationError(
            "Brief text contains excessive symbols or punctuation."
        )

    # 3. Check for excessive single-character repetition (e.g., 'aaaaaaaaaa')
    if re.search(r"(.)\1{9,}", stripped):
        raise BriefInputValidationError(
            "Brief text contains repetitive spam or meaningless sequences."
        )

    # 4. Check for consonant keyboard mash (alphabetical words >= 4 chars without vowels)
    vowels_pattern = re.compile(r"[аеёиоуыэюяaeiouy]", flags=re.IGNORECASE)
    consonant_mash_words = [
        w for w in alpha_words if len(w) >= 4 and not vowels_pattern.search(w)
    ]
    if (
        len(consonant_mash_words) >= 1
        and len(consonant_mash_words) / len(alpha_words) >= 0.3
    ):
        raise BriefInputValidationError(
            "Brief text contains words without vowels (consonant keyboard mash)."
        )

    # 5. Check for letter-digit sandwiches inside words (e.g., 'test123abc', 'foo456bar')
    sandwiches = re.findall(r"[^\W\d_]+\d+[^\W\d_]+", stripped, flags=re.UNICODE)
    if len(sandwiches) >= 1 and len(sandwiches) / max(len(alpha_words), 1) >= 0.2:
        raise BriefInputValidationError(
            "Brief text contains unnatural letter-digit combinations inside words."
        )

    # 6. Check for alternating case mash in words (e.g., 'qWeRtY', 'ПрИвЕтМмМ', 'aSdFgHjKl')
    alt_case_pattern = (
        r"\b[^\s]*(?:[a-zа-яё][A-ZА-ЯЁ][a-zа-яё][A-ZА-ЯЁ]"
        r"|[A-ZА-ЯЁ][a-zа-яё][A-ZА-ЯЁ][a-zа-яё])[^\s]*\b"
    )
    alt_case_mash = re.findall(alt_case_pattern, stripped, flags=re.UNICODE)
    if len(alt_case_mash) >= 1 and len(alt_case_mash) / max(len(alpha_words), 1) >= 0.2:
        raise BriefInputValidationError(
            "Brief text contains words with unnatural alternating case mash."
        )

    return stripped

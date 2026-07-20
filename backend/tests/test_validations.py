import pytest

from app.core.exceptions import BriefInputValidationError
from app.core.validations import validate_brief_text


def test_validate_brief_text_broken_briefs():
    """Test that 15 different broken, gibberish, or spam briefs are rejected."""
    broken_briefs = [
        # 1. User example: digits + symbols + mixed case/digit mash
        "Привет!348578№?*ТвАЫТ7Т3А   ",
        # 2. Pure symbol soup / punctuation without letters
        "- - - - - - - - - - - - - - - - - -",
        # 3. Too few alphabetical words (< 3 words)
        "Hello world",
        # 4. Excessive single-character repetition
        "We need a mobile app. aaaaaaaaaaaaaa bbbbbbbbbbbbb",
        # 5. High ratio of special symbols (> 50%)
        "*** Hello *** !!! $$$ @@@ ### %%% ^&&& * * *",
        # 6. Pure numbers / digits without alphabetical words
        "123456 789012 345678 901234",
        # 7. English keyboard mash without vowels
        "asdfgh jklzxc qwerty zxcvbn",
        # 8. Russian consonant keyboard mash without vowels
        "бвгджз клмнпр стфхцч шщбвгд",
        # 9. Only 2 alphabetical words mixed with long digits
        "CRM app 1234567890",
        # 10. Single-character letters only (no words of length >= 2)
        "a b c d e f g h i j k l m n o",
        # 11. Single short word (< 10 chars total and < 3 words)
        "Тест",
        # 12. Alternating upper-lower case English mash
        "qWeRtYuIoP aSdFgHjKl zXcVbNm",
        # 13. Alternating upper-lower case Cyrillic mash
        "ПрИвЕтМмМ аБвГдЕжЗ кЛмНпР",
        # 14. Digits sandwiched inside alphabetical letters across words
        "test123abc foo456bar baz789qux",
        # 15. Pure symbols with leading/trailing spaces (length >= 10, no words)
        " $$$ !!! ??? @@@ ### %%% ^^^ &&& * * * ",
    ]

    for idx, brief in enumerate(broken_briefs, start=1):
        with pytest.raises(BriefInputValidationError) as exc_info:
            validate_brief_text(brief)
        assert exc_info.value is not None, f"Brief #{idx} should have raised an error."


def test_validate_brief_text_valid_briefs():
    """Test that 5 normal, realistic project briefs pass validation successfully."""
    valid_briefs = [
        # 1. Standard English project brief with numbers and punctuation
        "We need a mobile app for food delivery. Budget is 15k USD. Deadline: 3 months.",
        # 2. Standard Russian project brief with numbers and punctuation
        "Нам нужно мобильное приложение для доставки еды. Бюджет 15000 рублей, срок 2 месяца.",
        # 3. Technical brief in Russian with Vue.js, Python/FastAPI, 1C
        "Разработать интернет-магазин автозапчастей на Vue.js и Python/FastAPI с интеграцией 1C.",
        # 4. English brief with technical stack terms and acronyms
        "Create an automated AI workflow using Gemini API, Next.js frontend, and PostgreSQL DB.",
        # 5. Russian UX/UI redesign brief with slashes and numbers
        "Необходимо провести редизайн корпоративного портала, улучшить UX/UI и ускорить в 2 раза.",
    ]

    for idx, brief in enumerate(valid_briefs, start=1):
        cleaned = validate_brief_text(brief)
        assert cleaned == brief.strip(), f"Valid brief #{idx} failed unexpectedly."

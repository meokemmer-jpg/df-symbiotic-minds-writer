import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# [CRUX-MK]
from symbiotic_minds_writer import (
    BOOK_SUBTITLE,
    BOOK_TITLE,
    TRINITY_ROLES,
    build_book_skeleton,
    is_kaestner_clear,
    mission_manifest,
    request_chapter_draft,
    validate_trinity_balance,
)


def test_mission_manifest_captures_strict_conditions_and_outline():
    manifest = mission_manifest()

    assert manifest["book_title"] == BOOK_TITLE
    assert manifest["subtitle"] == BOOK_SUBTITLE
    assert manifest["wave"] == 44
    assert manifest["default_mode"] == "mock"
    assert manifest["strict_conditions"]["auto_push_allowed"] is False
    assert manifest["strict_conditions"]["cashflow_allowed"] is False
    assert len(manifest["outline"]) == 14
    assert manifest["outline"][0].number == 1
    assert "Definition + Abgrenzung" in manifest["outline"][0].title


def test_build_book_skeleton_uses_mock_mode_by_default():
    skeleton = build_book_skeleton()

    assert skeleton["book_title"] == BOOK_TITLE
    assert skeleton["subtitle"] == BOOK_SUBTITLE
    assert skeleton["wave"] == 44
    assert skeleton["mode"] == "mock"
    assert len(skeleton["chapters"]) == 14

    first = skeleton["chapters"][0]
    assert first.number == 1
    assert first.mode == "mock"
    assert first.trinity_roles == TRINITY_ROLES
    assert first.real_generation_allowed is False
    assert first.style_ok is True
    assert "Phronesis" in first.body
    assert "Pattern-Recognition" in first.body
    assert "AI + Mensch > Mensch allein > AI allein" in first.body


def test_real_mode_requires_env_gate_and_ticket():
    try:
        request_chapter_draft(1, env={}, mode="real")
    except PermissionError as exc:
        assert "DF_BOOK_REAL_ENABLED=true" in str(exc)
        assert "PHRONESIS_TICKET" in str(exc)
    else:
        raise AssertionError("PermissionError erwartet")


def test_real_mode_accepts_callable_when_gate_is_open():
    draft = request_chapter_draft(
        4,
        env={
            "DF_BOOK_REAL_ENABLED": "true",
            "PHRONESIS_TICKET": "ticket-44",
        },
        mode="real",
        llm_callable=lambda number, title: (
            f"Kapitel {number} zeigt {title}.\n\n"
            "Menschen halten Urteil und Richtung.\n\n"
            "Die KI testet Muster und Gegenmuster.\n\n"
            "Die conservative Stimme schuetzt Substanz.\n\n"
            "Die aggressive Stimme sucht Hebel.\n\n"
            "Die contrarian Stimme prueft blinde Flecken."
        ),
    )

    assert draft.mode == "real"
    assert draft.number == 4
    assert "Trinity-Pattern" in draft.title
    assert "Gegenmuster" in draft.body
    assert draft.real_generation_allowed is True
    assert draft.style_ok is True


def test_style_check_rejects_dense_single_paragraph_text():
    text = (
        "Dies ist ein ueberladener Absatz ohne Atem ohne klare Trennung und mit sehr vielen "
        "Worten in einer einzigen langen Satzkette die bewusst jede Kaestner Klarheit verfehlt "
        "weil sie weder Pausen noch saubere Struktur noch kurze Saetze zulaesst."
    )

    assert is_kaestner_clear(text) is False


def test_trinity_balance_requires_all_three_roles():
    assert validate_trinity_balance(
        "Die conservative Position prueft Risiken. Die aggressive Position sucht Hebel. "
        "Die contrarian Position schaut auf blinde Flecken."
    ) is True
    assert validate_trinity_balance(
        "Die conservative Position prueft Risiken. Die aggressive Position sucht Hebel."
    ) is False

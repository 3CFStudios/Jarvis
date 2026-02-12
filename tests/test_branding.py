from jarviso import branding


def test_branding_constants_non_empty() -> None:
    required = [
        branding.APP_NAME,
        branding.BRAND_LINE,
        branding.COPYRIGHT_LINE,
        branding.STARTUP_BANNER,
        branding.UI_WATERMARK_TEXT,
        branding.STATUSBAR_TEXT,
        branding.ABOUT_TEXT,
    ]
    assert all(isinstance(item, str) and item.strip() for item in required)


def test_banner_contains_arya() -> None:
    assert "Arya" in branding.banner()


def test_watermark_and_status_contain_arya() -> None:
    assert "Arya" in branding.watermark_text()
    assert "Arya" in branding.status_text()


def test_about_contains_arya() -> None:
    assert "Arya" in branding.ABOUT_TEXT

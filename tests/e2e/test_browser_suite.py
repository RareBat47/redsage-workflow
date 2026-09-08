import os

import pytest
from playwright.sync_api import Page, expect


BASE_URL = os.getenv("REDSAGE_E2E_URL", "http://127.0.0.1:8000")


@pytest.mark.e2e
def test_full_magic_demo_flow(page: Page):
    page.goto(BASE_URL)
    expect(page.get_by_text("Authorized testing, documented.")).to_be_visible()

    page.once("dialog", lambda dialog: dialog.accept("E2E Hardening Project"))
    page.get_by_role("button", name="+ New Project").click()
    expect(page.locator("header span").filter(has_text="E2E Hardening Project")).to_be_visible()

    page.once("dialog", lambda dialog: dialog.accept("juice-shop.local"))
    page.get_by_role("button", name="Configure & Lock Scope").click()
    expect(page.get_by_text("SCOPE LOCKED", exact=True)).to_be_visible()

    task_button = page.get_by_role("button", name="○ 2.2 Web Content & Directory Discovery")
    expect(task_button).to_be_visible()
    task_button.click()
    evidence = page.get_by_placeholder("Paste untrusted tool output here. RedSage never executes it.")
    evidence.fill("/login [Status: 200]\n/backup.zip [Status: 200]")
    verify = page.get_by_role("button", name="Verify Evidence")
    verify.click()
    expect(verify).to_be_disabled()
    verdict = page.get_by_text("PASS").or_(page.get_by_text("INCONCLUSIVE"))
    expect(verdict.first).to_be_visible(timeout=10000)

    page.get_by_role("button", name="Report Studio").click()
    expect(page.get_by_text("Formal engagement report")).to_be_visible()

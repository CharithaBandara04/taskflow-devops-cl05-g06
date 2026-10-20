from playwright.sync_api import Page, expect


def test_homepage_loads(page: Page):
    page.goto("/")

    expect(page).to_have_title("TaskFlow")
    expect(page.locator("#task-form")).to_be_visible()
    expect(page.locator("#task-list")).to_be_visible()
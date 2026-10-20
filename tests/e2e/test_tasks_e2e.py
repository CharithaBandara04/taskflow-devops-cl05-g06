import re
import uuid

from playwright.sync_api import Page, expect


def unique_title(label):
    return f"E2E {label} {uuid.uuid4().hex[:8]}"


def create_task(page: Page, title, description=""):
    page.fill("#task-title", title)
    page.fill("#task-description", description)
    page.click("#add-task-btn")
    task = page.locator("#task-list li", has_text=title)
    expect(task).to_be_visible()
    return task


def delete_task(page: Page, task):
    page.once("dialog", lambda dialog: dialog.accept())
    task.locator(".delete-task-btn").click()
    expect(task).to_have_count(0)


def test_create_task(page: Page):
    page.goto("/")
    title = unique_title("create")

    task = create_task(page, title, "Created by Playwright")

    expect(task.locator(".task-status")).to_have_text("pending")
    expect(task.locator(".task-description")).to_have_text("Created by Playwright")
    delete_task(page, task)


def test_blank_title_shows_error(page: Page):
    page.goto("/")

    page.fill("#task-title", "   ")
    page.click("#add-task-btn")

    expect(page.locator("#form-error")).to_have_text("Task title is required")


def test_toggle_task_status(page: Page):
    page.goto("/")
    task = create_task(page, unique_title("toggle"))

    task.locator(".toggle-status-btn").click()
    expect(task.locator(".task-status")).to_have_text("completed")
    expect(task).to_have_class(re.compile("task-completed"))
    expect(task.locator(".toggle-status-btn")).to_have_text("Mark pending")

    task.locator(".toggle-status-btn").click()
    expect(task.locator(".task-status")).to_have_text("pending")
    delete_task(page, task)


def test_edit_task(page: Page):
    page.goto("/")
    old_title = unique_title("edit-before")
    new_title = unique_title("edit-after")
    task = create_task(page, old_title)

    task.locator(".edit-task-btn").click()
    expect(page.locator("#edit-modal")).to_be_visible()
    expect(page.locator("#edit-title")).to_have_value(old_title)

    page.fill("#edit-title", new_title)
    page.fill("#edit-description", "Edited by Playwright")
    page.click("#save-edit-btn")

    expect(page.locator("#edit-modal")).to_be_hidden()
    edited = page.locator("#task-list li", has_text=new_title)
    expect(edited.locator(".task-description")).to_have_text("Edited by Playwright")
    expect(page.locator("#task-list li", has_text=old_title)).to_have_count(0)
    delete_task(page, edited)


def test_cancel_delete_keeps_task(page: Page):
    page.goto("/")
    task = create_task(page, unique_title("keep"))

    page.once("dialog", lambda dialog: dialog.dismiss())
    task.locator(".delete-task-btn").click()

    expect(task).to_be_visible()
    delete_task(page, task)


def test_delete_task(page: Page):
    page.goto("/")
    task = create_task(page, unique_title("delete"))

    delete_task(page, task)
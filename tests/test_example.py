import pytest
import os
from playwright.sync_api import expect


def get_env_var(key):
    if key not in os.environ:
        if os.environ.get("CI", "false") == "true":
            extra_info = "Please define CI secrets as described in the README file."
        else:
            extra_info = "Please create an `.env` file as described in the README file."
        raise ValueError(f"Environment variable `{key}` not defined. {extra_info}")
    return os.environ[key]


@pytest.fixture
def user1_email():
    get_env_var("E2E_USER1_EMAIL")


@pytest.fixture
def user1_password():
    get_env_var("E2E_USER1_PASSWORD")


@pytest.fixture
def user2_email():
    get_env_var("E2E_USER2_EMAIL")


@pytest.fixture
def user2_password():
    get_env_var("E2E_USER2_PASSWORD")


def test_inveniordm_login(page, user1_email, user1_password):
    # Make the viewport big enough to have the desktop layout.
    page.set_viewport_size({"width": 1600, "height": 1000})

    page.goto("https://inveniordm.web.cern.ch/")

    page.get_by_role("link", name=" Log in").click()
    expect(page.get_by_role("heading")).to_contain_text("Log in to account")
    page.get_by_placeholder("Email Address").fill(user1_email)
    page.get_by_placeholder("Password").fill(user1_password)
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("#user-profile-dropdown")).to_be_visible()

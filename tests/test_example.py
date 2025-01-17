"""E2E tests."""

import os
import random
import re
import string
import time

import pytest
from playwright.sync_api import Page, expect, sync_playwright


def get_env_var(key):
    error_msg = ""
    if key not in os.environ:
        error_msg = f"Environment variable `{key}` not defined."
    elif os.environ[key].strip() == "":
        error_msg = f"Environment variable `{key}` defined but empty."

    if error_msg:
        if os.environ.get("CI", "false") == "true":
            extra_info = "Please define CI secrets as described in the README file."
        else:
            extra_info = "Please create an `.env` file as described in the README file."
        raise ValueError(f"{error_msg} {extra_info}")

    return os.environ[key]


@pytest.fixture
def user1_email():
    return get_env_var("E2E_USER1_EMAIL")


@pytest.fixture
def user1_password():
    return get_env_var("E2E_USER1_PASSWORD")


@pytest.fixture
def user2_email():
    return get_env_var("E2E_USER2_EMAIL")


@pytest.fixture
def user2_password():
    return get_env_var("E2E_USER2_PASSWORD")


def _generate_random_id(length=8):
    # Generate a random string of uppercase letters and digits
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def perform_login(page, username, password):
    """Login to the account."""
    page.goto("https://inveniordm.web.cern.ch/login/")
    page.get_by_placeholder("Email Address").fill(username)
    page.get_by_placeholder("Password").fill(password)
    page.get_by_role("button", name="Log in").click()
    expect(page.locator("#user-profile-dropdown")).to_be_visible()


def perform_logout(page):
    """Logout of the account."""
    user_profile_dropdown = page.locator('[id="user-profile-dropdown-btn"]')
    user_profile_dropdown.click()
    page.locator("#user-profile-menu >> text= Log out ").click()


def create_a_community(page, community_name, community_slug):
    """Create a new community."""
    # starting from /communities/new
    assert page.url == "https://inveniordm.web.cern.ch/communities/new"
    expect(page.locator("text=Setup your new community")).to_be_visible()

    # fill in the form and create a community
    page.locator('[id="metadata.title"]').fill(community_name)
    page.locator('[id="slug"]').fill(community_slug)
    page.locator('label.field-label-class:has-text("Public")').click()
    page.locator("text=Create community").click()

    # check that community is created
    expected_url = (
        f"https://inveniordm.web.cern.ch/communities/{community_slug.lower()}/settings"
    )
    page.wait_for_url(expected_url)  # Wait for the redirect
    assert page.url == expected_url


def create_minimal_record(page, record_title):
    """Create a basic record."""
    # Upload
    page.goto("https://inveniordm.web.cern.ch/uploads/new")

    # Title
    page.get_by_label("Title").fill(record_title)

    # Resource tye
    page.get_by_label("Resource type").first.click()
    page.get_by_role("option", name="Dataset").click()

    # DOI
    page.get_by_text("No", exact=True).first.click()

    # Creator
    page.get_by_role("button", name="Add creator").click()
    page.locator("#creators").fill("lars holm nielsen")
    page.get_by_text("Nielsen, Lars Holm (0000-0001").click()
    page.get_by_role("button", name="Save", exact=True).click()

    # File
    # See: https://playwright.dev/python/docs/api/class-filechooser
    with page.expect_file_chooser() as fc_info:
        page.get_by_role("button", name="Upload files", exact=True).click()
        file_chooser = fc_info.value
        file_chooser.set_files("tests/data/test_example.txt")
    # Leave enough time for the upload to finish and for the progress bar to show the success (green) status.
    expect(page.locator(".progress.success")).to_be_visible(timeout=30_000)

    # Publish
    page.get_by_role("button", name="Publish").click()
    page.get_by_role("button", name="Publish").nth(1).click()

    expect(page.locator("#record-title")).to_contain_text("Playwright test")
    expect(
        page.get_by_label("Creators and contributors").locator("span")
    ).to_contain_text("Nielsen, Lars Holm")


def submit_a_record_to_community(page, community_name):
    """Submit a record to a community."""
    # starting from /record/id
    expected_url_pattern = (
        r"https://inveniordm.web.cern.ch/records/[a-zA-Z0-9]+"  # Matches any numeric ID
    )
    expect(page).to_have_url(re.compile(expected_url_pattern))

    # open a dropdown
    page.locator('[id="modal-dropdown"]').click()
    page.locator('[id="submit-to-community"]').click()
    expect(page.locator("#community-modal-header")).to_contain_text(
        "Select a community"
    )

    # search for community
    page.fill('input[placeholder="Search in all communities"]', community_name)
    page.locator('div.ui.fluid.action.input button[aria-label="Search"]').click()

    # select a community
    page.get_by_role("button", name=f"Select {community_name}").click()
    assert page.locator('div.header:text("Submit to community")').count() > 0
    page.locator('label[for="acceptAccessToRecord"]').click()
    page.locator('button[name="submitReview"]').click()


def accept_a_request(page, community_name, record_title):
    """Accept a community inclution request."""
    assert page.url == "https://inveniordm.web.cern.ch/"
    page.locator('nav #invenio-menu a:has-text("My dashboard")').click()
    page.locator(
        'div.ui.container.secondary.pointing.menu.page-subheader a:has-text("Communities")'
    ).click()

    # search for a community requests
    page.get_by_role("textbox", name="Search in my communities...").fill(community_name)
    page.locator("#invenio-search-config").get_by_role("button", name="Search").click()
    page.locator(f'a.ui.medium.header.mb-0:has-text("{community_name}")').click()
    page.locator("a.item", has_text="Requests").click()

    # Accept a request
    page.locator("div.content").filter(has_text=record_title).get_by_role(
        "button", name="Accept"
    ).click()
    page.get_by_label("accept").get_by_role("button", name="Accept").click()

    # verify that record is in the community now
    page.locator("a.item", has_text="Records").click()
    assert page.locator(f'h2.header:has-text("{record_title}")').is_visible()


def test_create_community_and_include_record_to_it(
    page, user1_email, user1_password, user2_email, user2_password
):
    """Test create a community, create a record, create and accept an inclusion request."""

    # Make the viewport big enough to have the desktop layout.
    page.set_viewport_size({"width": 1500, "height": 1080})

    # login to the website
    perform_login(page, user2_email, user2_password)

    # get to the create community form
    page.locator('[id="quick-create-dropdown"]').click()
    page.locator("#quick-create-menu >> text=New community").click()
    community_slug = _generate_random_id()
    community_name = f"Community Test Playwright {community_slug}"
    create_a_community(page, community_name, community_slug)

    # logout
    perform_logout(page)

    # login as a different user
    perform_login(page, user1_email, user1_password)

    # create a record
    record_title = "Playwright test"
    create_minimal_record(page, record_title)

    # submit it to a community
    submit_a_record_to_community(page, community_name)

    # logout
    perform_logout(page)

    # login as a community owner
    perform_login(page, user2_email, user2_password)

    # accept the community inclusion request
    accept_a_request(page, community_name, record_title)

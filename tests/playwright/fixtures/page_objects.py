# tests/playwright/fixtures/page_objects.py
from playwright.sync_api import Page, expect
import re

class AdminPage:
    """Page object for the admin dashboard."""

    def __init__(self, page: Page):
        self.page = page

    def login(self, username: str = "admin@example.com", password: str = "changeme"):
        """Login to the admin interface."""
        self.page.goto("/admin")

        if re.search(r"login", self.page.url):
            self.page.fill('[name="email"]', username)
            self.page.fill('[name="password"]', password)
            self.page.click('button[type="submit"]')
            self.page.wait_for_url(re.compile(r".*admin"))

    def navigate_to_tab(self, tab_name: str):
        """Navigate to a specific tab."""
        self.page.click(f"#tab-{tab_name}")
        self.page.wait_for_selector(f"#{tab_name}-panel", state="visible")

    def create_tool(self, tool_data: dict):
        """Create a new tool via the modal form."""
        self.navigate_to_tab("tools")
        self.page.click('button:has-text("Add Tool")')
        expect(self.page.locator("#create-tool-modal")).to_be_visible()

        self._fill_tool_form(tool_data)
        self.page.click('#create-tool-modal button[type="submit"]')
        expect(self.page.locator("#create-tool-modal")).to_be_hidden()

    def _fill_tool_form(self, data: dict):
        """Fill the tool creation form."""
        for field, value in data.items():
            if field == "integrationType":
                self.page.select_option(f'[name="{field}"]', value)
            else:
                self.page.fill(f'[name="{field}"]', value)

    def get_tool_by_name(self, name: str):
        """Get a tool row by name."""
        return self.page.locator(f'#tools-table tbody tr:has-text("{name}")')

    def delete_tool(self, name: str):
        """Delete a tool by name."""
        tool_row = self.get_tool_by_name(name)
        tool_row.locator('button:has-text("Delete")').click()

        # Confirm deletion in modal
        confirm_button = self.page.locator('#delete-confirmation-modal button:has-text("Confirm")')
        if confirm_button.is_visible():
            confirm_button.click()

class ToolsPage:
    """Page object specifically for tools management."""

    def __init__(self, page: Page):
        self.page = page
        self.admin_page = AdminPage(page)

    def setup(self):
        """Setup the tools page."""
        self.admin_page.login()
        self.admin_page.navigate_to_tab("tools")

    def execute_tool(self, tool_name: str, parameters: dict = None):
        """Execute a tool with optional parameters."""
        tool_row = self.admin_page.get_tool_by_name(tool_name)
        tool_row.locator('button:has-text("Execute")').click()

        expect(self.page.locator("#tool-execution-modal")).to_be_visible()

        if parameters:
            import json
            self.page.fill('[name="tool-params"]', json.dumps(parameters))

        self.page.click('button:has-text("Run Tool")')
        self.page.wait_for_selector(".tool-result", timeout=10000)

        return self.page.locator(".tool-result").text_content()
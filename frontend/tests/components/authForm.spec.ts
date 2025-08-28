import { test, expect } from "@playwright/test";
import { testUser } from "../utils/constants";
import { signupUser } from "../utils/authApi";

test.describe.configure({ mode: "serial" });

test.describe("Auth Form", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector('[id^="category-section"]', { timeout: 10000 });
  });

  test("login form displays all required elements", async ({ page }) => {
    const authButton = page
      .getByRole("button")
      .filter({ hasText: /authorize/i });
    await authButton.click();

    const loginForm = page.locator('[id="auth-form"]');
    await expect(loginForm).toBeVisible();

    const formFields = [
      { label: "Username", name: "username" },
      { label: "Password", name: "password" },
    ];

    for (const field of formFields) {
      const label = loginForm.locator("label", { hasText: field.label });
      const input = loginForm.locator(`input[name="${field.name}"]`);
      await expect(label).toBeVisible();
      await expect(input).toBeVisible();
    }

    await expect(
      loginForm.getByRole("button", { name: "Login" }),
    ).toBeVisible();
    await expect(loginForm.getByText("Forgot password?")).toBeVisible();
    await expect(
      loginForm.getByText("Don't have an account? Signup"),
    ).toBeVisible();

    const closeButton = page.getByRole("button", { name: "Close" });
    await closeButton.click();
    await expect(loginForm).not.toBeVisible();
  });

  test("signup form displays all required elements", async ({ page }) => {
    const authButton = page
      .getByRole("button")
      .filter({ hasText: /authorize/i });
    await authButton.click();

    const signupLink = page.getByText("Don't have an account? Signup");
    await signupLink.click();

    const signupForm = page.locator('[id="auth-form"]');
    await expect(signupForm).toBeVisible();

    const formFields = [
      { label: "Full name", name: "full_name" },
      { label: "Email", name: "email" },
      { label: "Username", name: "username" },
      { label: "Password", name: "password" },
    ];

    for (const field of formFields) {
      const label = signupForm.locator("label", { hasText: field.label });
      const input = signupForm.locator(`input[name="${field.name}"]`);
      await expect(label).toBeVisible();
      await expect(input).toBeVisible();
    }

    await expect(
      signupForm.getByRole("button", { name: "Signup" }),
    ).toBeVisible();
    await expect(
      signupForm.getByText("Already have an account? Login"),
    ).toBeVisible();

    const closeButton = page.getByRole("button", { name: "Close" });
    await closeButton.click();
    await expect(signupForm).not.toBeVisible();
  });

  test("user info displays correctly after signup", async ({ page }) => {
    const suffix = String(Date.now()).slice(-6);
    await signupUser(page, testUser, suffix);

    const userInfo = page.locator("#user-info");
    await expect(userInfo).toBeVisible({ timeout: 10000 });

    const userFields = ["ID", "Username", "Full Name", "Email", "Role"];

    for (const fieldLabel of userFields) {
      const label = userInfo.locator("label", { hasText: fieldLabel });
      const input = label.locator("xpath=..").locator("input");

      await expect(label).toBeVisible();
      await expect(input).toBeVisible();
      await expect(input).toBeDisabled();

      await expect(async () => {
        const value = await input.getAttribute("value");
        expect(value?.length).toBeGreaterThan(0);
      }).toPass();
    }

    await expect(
      userInfo.getByRole("button", { name: "Logout" }),
    ).toBeVisible();

    const closeButton = page.getByRole("button", { name: "Close" });
    await closeButton.click();
    await expect(userInfo).not.toBeVisible();

    await expect(
      page.getByRole("button").filter({ hasText: /authorize/i }),
    ).toBeVisible();
  });
});

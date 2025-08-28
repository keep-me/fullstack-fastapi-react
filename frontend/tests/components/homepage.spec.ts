import { test, expect } from "@playwright/test";

test.describe.configure({ mode: "serial" });

test.describe("Homepage", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector('[id^="category-section"]', { timeout: 10000 });
  });

  test("header is visible", async ({ page }) => {
    const headerComponent = page.locator('[id="header"]');
    await expect(headerComponent).toBeVisible();
  });

  test("header title is correct", async ({ page }) => {
    const headerTitle = page.getByRole("heading", {
      name: "Fullstack FastAPI Template",
    });
    await expect(headerTitle).toBeVisible();
  });

  test("color mode button is visible", async ({ page }) => {
    const colorModeButton = page.getByRole("button", { name: /color mode/i });
    await expect(colorModeButton).toBeVisible();
  });

  test("auth button is visible", async ({ page }) => {
    const authButton = page
      .getByRole("button")
      .filter({ hasText: /authorize/i });
    await expect(authButton).toBeVisible();
  });

  test("category sections are loaded", async ({ page }) => {
    const categorySections = page.locator('[id^="category-section"]');
    const categorySectionsCount = await categorySections.count();
    await expect(categorySectionsCount).toBeGreaterThan(0);
  });
});

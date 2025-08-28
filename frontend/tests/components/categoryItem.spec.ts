import { test, expect } from "@playwright/test";

test.describe.configure({ mode: "serial" });

test.describe("Category Section", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector('[id^="category-section"]', { timeout: 10000 });
  });

  test("should have at least one category section", async ({ page }) => {
    const categorySection = page.locator('[id^="category-section"]');
    const categorySectionCount = await categorySection.count();
    await expect(categorySectionCount).toBeGreaterThan(0);
  });

  test("should display category title and subtitle", async ({ page }) => {
    const categorySection = page.locator('[id^="category-section"]').first();

    const title = categorySection.getByRole("heading", { name: /.+/ });
    await expect(title).toBeVisible();
    await expect(title).not.toBeEmpty();

    const subtitle = categorySection.getByText(/.+/i).nth(1);
    await expect(subtitle).toBeVisible();
    await expect(subtitle).not.toBeEmpty();
  });

  test("should have at least one endpoint item", async ({ page }) => {
    const categorySection = page.locator('[id^="category-section"]').first();
    const endpointItems = categorySection.locator('[id^="endpoint-item-"]');
    const endpointCount = await endpointItems.count();
    await expect(endpointCount).toBeGreaterThan(0);
  });

  test("should collapse and expand endpoint items", async ({ page }) => {
    const categorySection = page.locator('[id^="category-section"]').first();
    const endpointItem = categorySection
      .locator('[id^="endpoint-item-"]')
      .first();

    await expect(endpointItem).toBeVisible({ timeout: 10000 });

    const collapseButton = categorySection
      .getByRole("button", { name: "Collapse" })
      .first();

    await collapseButton.click();
    await expect(endpointItem).not.toBeVisible({ timeout: 10000 });

    const expandButton = categorySection
      .getByRole("button", { name: "Expand" })
      .first();

    await expandButton.click();
    await expect(endpointItem).toBeVisible({ timeout: 10000 });
  });
});

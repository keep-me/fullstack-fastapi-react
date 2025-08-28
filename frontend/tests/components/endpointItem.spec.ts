import { test, expect } from "@playwright/test";

test.describe.configure({ mode: "serial" });

test.describe("EndpointItem", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector('[id^="endpoint-item-"]', { timeout: 10000 });
  });

  test("should display all endpoint items with required elements", async ({
    page,
  }) => {
    const endpointItems = page.locator('[id^="endpoint-item-"]');
    const endpointItemsCount = await endpointItems.count();
    await expect(endpointItemsCount).toBeGreaterThan(0);

    for (let i = 0; i < endpointItemsCount; i++) {
      const endpointItem = endpointItems.nth(i);
      await expect(endpointItem).toBeVisible();

      const endpointBadge = endpointItem.locator('[id="endpoint-badge"]');
      await expect(endpointBadge).toBeVisible();
      await expect(endpointBadge).toHaveText(/^(GET|POST|PUT|PATCH|DELETE)$/);

      const endpointUrl = endpointItem.locator('[id="endpoint-url"]');
      await expect(endpointUrl).toBeVisible();
      await expect(await endpointUrl.textContent()).not.toBeNull();

      const endpointTitle = endpointItem.locator('[id="endpoint-title"]');
      await expect(endpointTitle).toBeVisible();
      await expect(await endpointTitle.textContent()).not.toBeNull();

      const expandCollapseButton = endpointItem.getByRole("button", {
        name: /(Expand|Collapse)/,
      });
      await expect(expandCollapseButton).toBeVisible();
    }
  });

  test("should expand and collapse endpoint details", async ({ page }) => {
    const endpointItem = page.locator('[id^="endpoint-item-"]').first();
    const header = endpointItem.locator("#endpoint-header");
    const endpointBody = endpointItem.locator("#endpoint-body");

    await expect(header).toBeVisible();
    await expect(endpointBody).not.toBeVisible();

    const expandButton = header.getByRole("button", { name: "Expand" });
    await expect(expandButton).toBeVisible();
    await expandButton.click();
    await expect(endpointBody).toBeVisible();

    const collapseButton = header.getByRole("button", { name: "Collapse" });
    await expect(collapseButton).toBeVisible();
    await collapseButton.click();
    await expect(endpointBody).not.toBeVisible();
  });

  test("should display endpoint body content correctly", async ({ page }) => {
    const endpointItem = page.locator('[id^="endpoint-item-"]').first();
    const header = endpointItem.locator("#endpoint-header");

    await header.getByRole("button", { name: "Expand" }).click();

    const endpointBody = endpointItem.locator("#endpoint-body");
    await expect(endpointBody).toBeVisible();

    const subheader = endpointBody.getByText(/.+/).first();
    await expect(subheader).toBeVisible();

    const tryButton = endpointBody.getByRole("button", { name: "Try it out" });
    await expect(tryButton).toBeVisible();
  });

  test("should display request body if present", async ({ page }) => {
    const endpointItem = page.locator('[id^="endpoint-item-"]').first();

    await endpointItem
      .locator("#endpoint-header")
      .getByRole("button", { name: "Expand" })
      .click();

    const requestBody = endpointItem.locator("#request-body");

    if (await requestBody.isVisible()) {
      const requestBodyHeader = requestBody.getByText("Request body").first();
      await expect(requestBodyHeader).toBeVisible();

      const requestBodyCodeArea = requestBody.locator("textarea");
      await expect(requestBodyCodeArea).toBeVisible();
      await expect(requestBodyCodeArea).toHaveText(/.+/);
    }
  });

  test("should display URL parameters if present", async ({ page }) => {
    const endpointItem = page.locator('[id^="endpoint-item-"]').first();

    await endpointItem
      .locator("#endpoint-header")
      .getByRole("button", { name: "Expand" })
      .click();

    const urlParams = endpointItem.locator("#url-params");

    if (await urlParams.isVisible()) {
      const urlParamsHeader = urlParams.getByText("URL Parameters").first();
      await expect(urlParamsHeader).toBeVisible();

      const urlParamForms = urlParams.locator("div");
      const urlParamFormsCount = await urlParamForms.count();
      await expect(urlParamFormsCount).toBeGreaterThan(0);

      for (let i = 0; i < urlParamFormsCount; i++) {
        const form = urlParamForms.nth(i);
        await expect(form.locator("label")).toBeVisible();
        await expect(form.locator("input")).toBeVisible();
      }
    }
  });
});

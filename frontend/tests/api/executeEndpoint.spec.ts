import { test, expect } from "@playwright/test";

test.describe.configure({ mode: "serial" });

test.describe("Execute Endpoint", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.waitForSelector('[id^="category-section"]', { timeout: 25000 });
    await page.waitForSelector('[id^="endpoint-item-"]', { timeout: 20000 });

    const endpointItem = page.locator('[id^="endpoint-item-"]').first();
    const expandCollapseButton = endpointItem.getByRole("button", {
      name: "Expand",
    });

    await expandCollapseButton.waitFor({ state: "visible", timeout: 20000 });
    await page.waitForTimeout(1000);
    await expandCollapseButton.click();

    const tryButton = endpointItem.getByRole("button", { name: "Try it out" });

    await tryButton.waitFor({ state: "visible", timeout: 20000 });
    await page.waitForTimeout(1000);
    await tryButton.click();
    await page.waitForSelector("#endpoint-response", { timeout: 25000 });
  });

  test("validates request and response data", async ({ page }) => {
    const response = page.locator("#endpoint-response");
    await expect(response).toBeVisible({ timeout: 15000 });

    const statusBadge = response.locator("#response-status-code");
    await expect(statusBadge).toBeVisible({ timeout: 15000 });
    await expect(statusBadge).toHaveText(/200 OK/);

    const responseCode = response.locator("#response-code");
    await expect(responseCode).toBeVisible({ timeout: 15000 });
    await expect(responseCode).toHaveText(/.+/);
  });

  test("displays response tab correctly", async ({ page }) => {
    const response = page.locator("#endpoint-response");
    const statusBadge = response.locator("#response-status-code");

    await expect(statusBadge).toBeVisible({ timeout: 15000 });
    await expect(statusBadge).toHaveText(/.+/);

    const responseTab = response.locator("#response-tab");
    await expect(responseTab).toBeVisible({ timeout: 15000 });
    await expect(responseTab).toHaveAttribute("aria-selected", "true");

    const responseTitle = response.locator("#response-title");
    await expect(responseTitle).toBeVisible({ timeout: 15000 });
    await expect(responseTitle).toHaveText("Response");

    const responseCode = response.locator("#response-code");
    await expect(responseCode).toBeVisible({ timeout: 15000 });
    await expect(responseCode).toHaveText(/.+/);
  });

  test("displays cURL tab correctly", async ({ page }) => {
    const response = page.locator("#endpoint-response");
    const curlTab = response.locator("#curl-tab");

    await expect(curlTab).toBeVisible({ timeout: 15000 });
    await expect(curlTab).toHaveAttribute("aria-selected", "false");
    await curlTab.click();
    await expect(curlTab).toHaveAttribute("aria-selected", "true");

    const curlTitle = response.locator("#curl-title");
    await expect(curlTitle).toBeVisible({ timeout: 15000 });
    await expect(curlTitle).toHaveText("cURL");

    const curlCode = response.locator("#curl-code");
    await expect(curlCode).toBeVisible({ timeout: 15000 });
    await expect(curlCode).toContainText(/curl -X GET "(https?:\/\/.+)"/);
  });

  test("displays request URL tab correctly", async ({ page }) => {
    const response = page.locator("#endpoint-response");
    const requestUrlTab = response.locator("#request-url-tab");

    await expect(requestUrlTab).toBeVisible({ timeout: 15000 });
    await expect(requestUrlTab).toHaveAttribute("aria-selected", "false");
    await requestUrlTab.click();
    await expect(requestUrlTab).toHaveAttribute("aria-selected", "true");

    const requestUrlTitle = response.locator("#request-url-title");
    await expect(requestUrlTitle).toBeVisible({ timeout: 15000 });
    await expect(requestUrlTitle).toHaveText("Request URL");

    const requestUrl = response.locator("#request-url-code");
    await expect(requestUrl).toBeVisible({ timeout: 15000 });
    await expect(requestUrl).toContainText("http");
    await expect(requestUrl).toContainText("health");
  });

  test("displays headers tab correctly", async ({ page }) => {
    const response = page.locator("#endpoint-response");

    const headersTab = response.locator("#headers-tab");
    await expect(headersTab).toBeVisible({ timeout: 15000 });
    await expect(headersTab).toHaveAttribute("aria-selected", "false");
    await headersTab.click();
    await expect(headersTab).toHaveAttribute("aria-selected", "true");

    const requestHeadersCode = response.locator("#request-headers-code");
    await expect(requestHeadersCode).toBeVisible({ timeout: 15000 });
    await expect(requestHeadersCode).toContainText("accept");

    const responseHeadersTitle = response.locator("#response-headers-title");
    await expect(responseHeadersTitle).toBeVisible({ timeout: 15000 });
    await expect(responseHeadersTitle).toHaveText("Response Headers");

    const responseHeadersCode = response.locator("#response-headers-code");
    await expect(responseHeadersCode).toBeVisible({ timeout: 15000 });
    await expect(responseHeadersCode).not.toBeEmpty();
  });

  test("resets endpoint state correctly", async ({ page }) => {
    const endpointItem = page.locator('[id^="endpoint-item-"]').first();
    const response = page.locator("#endpoint-response");

    await expect(response).toBeVisible({ timeout: 15000 });

    const resetButton = endpointItem.getByRole("button", { name: "Reset" });
    await resetButton.waitFor({ state: "visible", timeout: 20000 });
    await resetButton.click();

    await expect(response).not.toBeVisible({ timeout: 20000 });
  });
});

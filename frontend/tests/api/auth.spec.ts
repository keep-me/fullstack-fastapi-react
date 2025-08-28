import { test, expect } from "@playwright/test";
import { testUser } from "../utils/constants";
import { loginUser, logoutUser, signupUser } from "../utils/authApi";

test.describe.configure({ mode: "serial" });

let createdUser: typeof testUser | null = null;

test.describe("Auth flow", () => {

  test("should successfully signup new user", async ({ browser }) => {
    const page = await browser.newPage();
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const suffix = String(Date.now()).slice(-6);

    await signupUser(page, testUser, suffix);

    await page.waitForSelector("#user-info", { timeout: 20000 });

    const userInfo = page.locator("#user-info");
    await expect(userInfo).toBeVisible();

    createdUser = {
      ...testUser,
      fullName: testUser.fullName + suffix,
      email: testUser.email.replace("@", `${suffix}@`),
      username: testUser.username + suffix,
    };

    await page.close();
  });

  test("should successfully login with created user", async ({ browser }) => {
    if (!createdUser) {
      throw new Error("Test setup failed");
    }

    const page = await browser.newPage();
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await loginUser(page, createdUser);
    await page.waitForSelector("#user-info", { timeout: 20000 });

    const userInfo = page.locator("#user-info");
    await expect(userInfo).toBeVisible();

    await page.close();
  });

  test("should successfully logout user", async ({ browser }) => {
    if (!createdUser) {
      throw new Error("Test setup failed");
    }

    const page = await browser.newPage();
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await loginUser(page, createdUser);
    await page.waitForSelector("#user-info", { timeout: 20000 });

    await logoutUser(page);
    await page.waitForSelector("#auth-form", { timeout: 20000 });

    const authForm = page.locator("#auth-form");
    await expect(authForm).toBeVisible();

    await page.close();
  });

  test("should store access token after login", async ({ browser }) => {
    if (!createdUser) {
      throw new Error("Test setup failed");
    }

    const page = await browser.newPage();
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await loginUser(page, createdUser);
    await page.waitForSelector("#user-info", { timeout: 20000 });

    await expect(async () => {
      const localStorageContents = await page.evaluate(() => {
        const items: Record<string, string> = {};
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key) {
            items[key] = localStorage.getItem(key) as string;
          }
        }
        return items;
      });

      expect(localStorageContents["auth"]).toBeTruthy();
      expect(localStorageContents["user"]).toBeTruthy();

      const authData = JSON.parse(localStorageContents["auth"]);
      expect(authData["accessToken"]).toBeTruthy();
      expect(authData["isAuthenticated"]).toBe(true);

      if (!createdUser) throw new Error("createdUser is null");

      const userData = JSON.parse(localStorageContents["user"]);
      expect(userData["username"]).toBe(createdUser.username);
      expect(userData["full_name"]).toBe(createdUser.fullName);
      expect(userData["email"]).toBe(createdUser.email);
    }).toPass({ timeout: 20000 });

    await page.close();
  });

  test("should clear localStorage after logout", async ({ browser }) => {
    if (!createdUser) {
      throw new Error("Test setup failed");
    }

    const page = await browser.newPage();
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await loginUser(page, createdUser);
    await page.waitForSelector("#user-info", { timeout: 20000 });

    await logoutUser(page);
    await page.waitForSelector("#auth-form", { timeout: 20000 });

    await expect(async () => {
      const localStorageContents = await page.evaluate(() => {
        const items: Record<string, string> = {};
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key) {
            items[key] = localStorage.getItem(key) as string;
          }
        }
        return items;
      });

      expect(localStorageContents["auth"]).toBeFalsy();
      expect(localStorageContents["user"]).toBeFalsy();
    }).toPass({ timeout: 10000 });

    await page.close();
  });
});

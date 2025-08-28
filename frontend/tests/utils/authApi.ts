import { Page } from "@playwright/test";
import { testUser } from "./constants";

interface TestUser {
  fullName: string;
  email: string;
  username: string;
  password: string;
}

/**
 * Signs up a new user through the UI.
 * @param page - Playwright page instance
 * @param user - User data for signup
 * @param suffix - Optional suffix to append to user data for uniqueness
 * @returns Promise that resolves when signup is complete
 */
export async function signupUser(
  page: Page,
  user: TestUser = testUser,
  suffix: string = "",
): Promise<void> {
  const authButton = page.getByRole("button").filter({ hasText: /authorize/i });
  await authButton.waitFor({ state: "visible", timeout: 15000 });
  await authButton.click();

  const form = page.locator("#auth-form");
  await form.waitFor({ state: "visible", timeout: 15000 });

  const signupLink = form.getByText("Don't have an account? Signup");
  await signupLink.waitFor({ state: "visible", timeout: 15000 });
  await signupLink.click();

  const fullNameInput = form.locator('input[name="full_name"]');
  const emailInput = form.locator('input[name="email"]');
  const usernameInput = form.locator('input[name="username"]');
  const passwordInput = form.locator('input[name="password"]');

  await fullNameInput.waitFor({ state: "visible", timeout: 15000 });
  await emailInput.waitFor({ state: "visible", timeout: 15000 });
  await usernameInput.waitFor({ state: "visible", timeout: 15000 });
  await passwordInput.waitFor({ state: "visible", timeout: 15000 });

  await fullNameInput.fill(user.fullName + suffix);
  await emailInput.fill(user.email.replace("@", `${suffix}@`));
  await usernameInput.fill(user.username + suffix);
  await passwordInput.fill(user.password);

  const signupButton = form.getByRole("button", { name: "Signup" });
  await signupButton.waitFor({ state: "visible", timeout: 15000 });
  await signupButton.click();
}

/**
 * Logs in a user through the UI.
 * @param page - Playwright page instance
 * @param user - User credentials for login
 * @returns Promise that resolves when login is complete
 */
export async function loginUser(
  page: Page,
  user: TestUser = testUser,
): Promise<void> {
  const authButton = page.getByRole("button").filter({ hasText: /authorize/i });
  await authButton.waitFor({ state: "visible", timeout: 15000 });
  await authButton.click({ force: true });

  const form = page.locator("form");
  await page.waitForSelector("form", { state: "visible", timeout: 20000 });

  const usernameInput = form.locator('input[name="username"]');
  const passwordInput = form.locator('input[name="password"]');

  await usernameInput.waitFor({ state: "visible", timeout: 20000 });
  await passwordInput.waitFor({ state: "visible", timeout: 20000 });

  await usernameInput.fill(user.username);
  await passwordInput.fill(user.password);

  const loginButton = form.getByRole("button", { name: "Login" });
  await loginButton.waitFor({ state: "visible", timeout: 20000 });
  await loginButton.click();

  await page.waitForSelector("form", { state: "hidden", timeout: 20000 });
}

/**
 * Logs out the current user through the UI.
 * @param page - Playwright page instance
 * @returns Promise that resolves when logout is complete
 */
export async function logoutUser(page: Page): Promise<void> {
  const logoutButton = page.getByRole("button", { name: "Logout" });
  await logoutButton.waitFor({ state: "visible", timeout: 15000 });
  await logoutButton.click();

  const authForm = page.locator("auth-form");
  await authForm.waitFor({ state: "hidden", timeout: 20000 });
}

/**
 * Initiates password reset process through the UI.
 * @param page - Playwright page instance
 * @param email - Email address for password reset
 * @returns Promise that resolves when reset request is submitted
 */
export async function resetPassword(page: Page, email: string): Promise<void> {
  const resetPasswordLink = page.getByText("Forgot password?");
  await resetPasswordLink.waitFor({ state: "visible", timeout: 15000 });
  await resetPasswordLink.click();

  const resetPasswordForm = page.locator("form");
  await resetPasswordForm.waitFor({ state: "visible", timeout: 15000 });

  const emailInput = resetPasswordForm.locator('input[name="email"]');
  await emailInput.waitFor({ state: "visible", timeout: 15000 });
  await emailInput.fill(email);

  const submitButton = resetPasswordForm.getByRole("button", {
    name: "Reset password",
  });
  await submitButton.waitFor({ state: "visible", timeout: 15000 });
  await submitButton.click();
}

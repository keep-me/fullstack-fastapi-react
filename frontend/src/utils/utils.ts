export const fullnamePattern = {
  value: /^[A-Za-z][A-Za-z\s\u00C0-\u017F\-']{0,28}[A-Za-z]$/,
  message: "Invalid fullname",
};

export const usernamePattern = {
  value: /^[A-Za-z][A-Za-z0-9]{2,30}$/,
  message: "Username must be at least 3 characters and begin with a letter",
};

export const emailPattern = {
  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  message: "Invalid email address",
};

export const passwordRules = (isRequired = true) => {
  const rules: Record<string, unknown> = {
    minLength: {
      value: 8,
      message: "Password must be at least 8 characters",
    },
  };

  if (isRequired) {
    rules.required = "Password is required";
  }

  return rules;
};

export const confirmPasswordRules = (
  getValues: () => Record<string, unknown>,
  isRequired = true,
) => {
  const rules: Record<string, unknown> = {
    validate: (value: string) => {
      const password = getValues().password || getValues().new_password;
      return value === password ? true : "The passwords do not match";
    },
  };

  if (isRequired) {
    rules.required = "Password confirmation is required";
  }

  return rules;
};

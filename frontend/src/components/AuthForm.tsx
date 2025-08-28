import {
  useState,
  useEffect,
  useMemo,
  useCallback,
  Suspense,
  lazy,
} from "react";
import {
  Stack,
  Button,
  Text,
  Input,
  Field,
  Box,
  Link,
  Spinner,
  Flex,
} from "@chakra-ui/react";
import { PasswordInput } from "@/components/ui/password-input";
import { passwordRules, emailPattern, usernamePattern } from "@/utils/utils";
import type { AuthFormProps } from "@/types/components";

const ResetPassword = lazy(() => import("./ResetPassword"));
const VerifyCode = lazy(() => import("./VerifyCode"));
const NewPassword = lazy(() => import("./NewPassword"));

type ResetPasswordStep = "login" | "reset" | "verify" | "newPassword";

const LazyLoadingSpinner = () => (
  <Flex justify="center" align="center" py={8}>
    <Spinner size="lg" />
  </Flex>
);

const AuthForm: React.FC<AuthFormProps> = ({
  isSignupMode,
  onToggleMode,
  onSubmit,
  errors,
  isLoading,
  errorMessage,
  register,
}) => {
  const [resetStep, setResetStep] = useState<ResetPasswordStep>("login");
  const [resetEmail, setResetEmail] = useState("");
  const [verificationToken, setVerificationToken] = useState("");

  const defaultValues = useMemo(
    () => ({
      username: "",
      password: "",
      email: "",
      full_name: "",
    }),
    [],
  );

  const passwordValidationRules = useMemo(() => passwordRules(true), []);

  const fullNameValidation = useMemo(
    () => ({
      required: "Full name is required",
    }),
    [],
  );

  const emailValidation = useMemo(
    () => ({
      required: "Email is required",
      pattern: emailPattern,
    }),
    [],
  );

  const usernameValidation = useMemo(
    () => ({
      required: "Username is required",
      pattern: usernamePattern,
    }),
    [],
  );

  const stackGap = useMemo(() => ({ base: 3, sm: 4, md: 5 }), []);
  const buttonMarginTop = useMemo(() => ({ base: 2, md: 4 }), []);
  const buttonWidth = useMemo(
    () => ({ base: "120px", sm: "140px", md: "160px" }),
    [],
  );
  const buttonSize = useMemo(
    () => ({ base: "sm" as const, md: "md" as const }),
    [],
  );

  useEffect(() => {
    if (isSignupMode) {
      setResetStep("login");
      setResetEmail("");
      setVerificationToken("");
    }
  }, [isSignupMode]);

  const handleForgotPassword = useCallback(() => {
    setResetStep("reset");
  }, []);

  const handleBackToLogin = useCallback(() => {
    setResetStep("login");
    setResetEmail("");
    setVerificationToken("");
  }, []);

  const handleResetSuccess = useCallback((email: string, token: string) => {
    setResetEmail(email);
    setVerificationToken(token);
    setResetStep("verify");
  }, []);

  const handleVerifySuccess = useCallback((newToken: string) => {
    setVerificationToken(newToken);
    setResetStep("newPassword");
  }, []);

  const handleTokenUpdate = useCallback((newToken: string) => {
    setVerificationToken(newToken);
  }, []);

  const buttonText = useMemo(() => {
    return isSignupMode ? "Signup" : "Login";
  }, [isSignupMode]);

  const toggleModeText = useMemo(() => {
    return isSignupMode
      ? "Already have an account? Login"
      : "Don't have an account? Signup";
  }, [isSignupMode]);

  if (resetStep === "reset") {
    return (
      <Suspense fallback={<LazyLoadingSpinner />}>
        <ResetPassword onSuccess={handleResetSuccess} />
      </Suspense>
    );
  }

  if (resetStep === "verify") {
    return (
      <Suspense fallback={<LazyLoadingSpinner />}>
        <VerifyCode
          email={resetEmail}
          verificationToken={verificationToken}
          onSuccess={handleVerifySuccess}
          onTokenUpdate={handleTokenUpdate}
        />
      </Suspense>
    );
  }

  if (resetStep === "newPassword") {
    return (
      <Suspense fallback={<LazyLoadingSpinner />}>
        <NewPassword
          verificationToken={verificationToken}
          onBackToLogin={handleBackToLogin}
        />
      </Suspense>
    );
  }

  return (
    <form onSubmit={onSubmit}>
      <Stack gap={stackGap} align="flex-start" w="100%">
        {isSignupMode && (
          <>
            <Field.Root invalid={!!errors.full_name}>
              <Field.Label>Full name</Field.Label>
              <Input
                {...register("full_name", fullNameValidation)}
                defaultValue={defaultValues.full_name}
              />
              <Field.ErrorText>
                {errors.full_name?.message as string}
              </Field.ErrorText>
            </Field.Root>
            <Field.Root invalid={!!errors.email} required>
              <Field.Label>
                Email
                <Field.RequiredIndicator />
              </Field.Label>
              <Input
                {...register("email", emailValidation)}
                defaultValue={defaultValues.email}
              />
              <Field.ErrorText>
                {errors.email?.message as string}
              </Field.ErrorText>
            </Field.Root>
          </>
        )}
        <Field.Root invalid={!!errors.username} required={isSignupMode}>
          <Field.Label>
            Username
            {isSignupMode && <Field.RequiredIndicator />}
          </Field.Label>
          <Input
            {...register("username", usernameValidation)}
            defaultValue={defaultValues.username}
          />
          <Field.ErrorText>
            {errors.username?.message as string}
          </Field.ErrorText>
        </Field.Root>
        <Field.Root invalid={!!errors.password} required={isSignupMode}>
          <Field.Label>
            Password
            {isSignupMode && <Field.RequiredIndicator />}
          </Field.Label>
          <PasswordInput
            {...register("password", passwordValidationRules)}
            defaultValue={defaultValues.password}
          />
          <Field.ErrorText>
            {errors.password?.message as string}
          </Field.ErrorText>
        </Field.Root>

        {!isSignupMode && (
          <Box alignSelf="flex-end">
            <Link
              fontSize="sm"
              color="gray.500"
              cursor="pointer"
              onClick={handleForgotPassword}
              _hover={{ color: "gray.400" }}
            >
              Forgot password?
            </Link>
          </Box>
        )}

        {errorMessage && <Text color="red.500">{errorMessage}</Text>}

        <Button
          mt={buttonMarginTop}
          type="submit"
          loading={isLoading}
          alignSelf="center"
          w={buttonWidth}
          size={buttonSize}
        >
          {buttonText}
        </Button>
        <Text
          fontSize="sm"
          color="gray.500"
          alignSelf="center"
          cursor="pointer"
          onClick={onToggleMode}
          textAlign="center"
          lineClamp={2}
          _hover={{ color: "gray.400" }}
        >
          {toggleModeText}
        </Text>
      </Stack>
    </form>
  );
};

export default AuthForm;

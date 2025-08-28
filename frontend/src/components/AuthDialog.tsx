import { useState } from "react";
import { useAppDispatch } from "../redux/hooks";
import { useForm } from "react-hook-form";
import { Spinner, Flex, Box } from "@chakra-ui/react";
import { toaster } from "@/components/ui/toaster";
import { logout, clearAuth, login } from "@/redux/slices/auth";
import { clearUser } from "@/redux/slices/user";
import {
  useLogoutMutation,
  useLoginMutation,
  useSignupMutation,
} from "@/redux/services/authApi";
import { useGetUserMeQuery } from "@/redux/services/userApi";
import UserInfo from "./UserInfo";
import AuthForm from "./AuthForm";
import type { AuthDialogProps } from "@/types/components";
import { TOAST_DURATION } from "@/config/env";

const AuthDialog: React.FC<AuthDialogProps> = ({ isAuthenticated, user }) => {
  const dispatch = useAppDispatch();
  const [isSignupMode, setIsSignupMode] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isAuthLoading, setIsAuthLoading] = useState(false);
  const [showSpinner, setShowSpinner] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm();

  const [logoutUser, { isLoading: isLogoutLoading }] = useLogoutMutation();
  const [loginUser, { isLoading: isLoginLoading }] = useLoginMutation();
  const [signupUser, { isLoading: isSignupLoading }] = useSignupMutation();

  useGetUserMeQuery(undefined, {
    skip: !isAuthenticated,
    refetchOnMountOrArgChange: true,
  });

  const isLoading =
    isLoginLoading || isSignupLoading || isAuthLoading || isLogoutLoading;

  const onSubmit = handleSubmit(async (formData) => {
    try {
      setShowSpinner(true);
      setErrorMessage("");
      setIsAuthLoading(true);

      if (isSignupMode) {
        await handleSignup(formData);
      } else {
        await handleLogin(formData);
      }
    } catch {
      // Intentionally empty - error handling is done in individual handlers
    } finally {
      setIsAuthLoading(false);
      setShowSpinner(false);
    }
  });

  const handleSignup = async (formData: Record<string, unknown>) => {
    try {
      await signupUser(formData).unwrap();

      const loginResult = await loginUser({
        username: formData.username as string,
        password: formData.password as string,
      }).unwrap();

      if (loginResult && loginResult.access_token) {
        dispatch(login({ access_token: loginResult.access_token }));

        toaster.create({
          title: "Registration successful",
          description: "You are now registered and logged in",
          type: "success",
          duration: TOAST_DURATION,
        });
      } else {
        throw new Error("Server returned invalid data format after login");
      }
    } catch (error: unknown) {
      const errorMessage =
        (error as { data?: { message?: string }; message?: string })?.data
          ?.message ||
        (error as { message?: string })?.message ||
        "Error during registration";
      setErrorMessage(errorMessage);
      toaster.create({
        title: "Signup error",
        description: errorMessage,
        type: "error",
        duration: TOAST_DURATION,
      });
    }
  };

  const handleLogin = async (formData: Record<string, unknown>) => {
    try {
      const result = await loginUser(formData).unwrap();

      if (result && result.access_token) {
        dispatch(login({ access_token: result.access_token }));

        toaster.create({
          title: "Login",
          description: "You are logged in successfully",
          type: "success",
          duration: TOAST_DURATION,
        });
      } else {
        throw new Error("Server returned invalid data format");
      }
    } catch (error: unknown) {
      const errorMessage =
        (error as { data?: { message?: string } })?.data?.message ||
        "Invalid credentials";
      setErrorMessage(errorMessage);
      toaster.create({
        title: "Login error",
        description: errorMessage,
        type: "error",
        duration: TOAST_DURATION,
      });
    }
  };

  const handleLogout = async () => {
    setShowSpinner(true);
    setIsAuthLoading(true);

    try {
      await logoutUser({}).unwrap();

      toaster.create({
        title: "Logout",
        description: "You are logged out successfully",
        type: "success",
        duration: TOAST_DURATION,
      });
    } catch {
      toaster.create({
        title: "Logout",
        description: "You have been logged out locally",
        type: "warning",
        duration: TOAST_DURATION,
      });
    }

    setTimeout(() => {
      dispatch(logout());
      dispatch(clearAuth());
      dispatch(clearUser());

      reset();
      setShowSpinner(false);
      setIsAuthLoading(false);
    }, 100);
  };

  const toggleAuthMode = () => {
    setIsSignupMode(!isSignupMode);
    setErrorMessage("");
    reset();
  };

  if (showSpinner) {
    return (
      <Flex justify="center" align="center" py={8}>
        <Spinner size="xl" />
      </Flex>
    );
  }

  return (
    <Box
      w="100%"
      px={{ base: 1, sm: 2, md: 3 }}
      id={
        isAuthenticated
          ? "user-info"
          : isSignupMode
            ? "signup-form"
            : "login-form"
      }
    >
      {isAuthenticated ? (
        <UserInfo user={user} onLogout={handleLogout} />
      ) : (
        <AuthForm
          isSignupMode={isSignupMode}
          onToggleMode={toggleAuthMode}
          onSubmit={onSubmit}
          errors={errors}
          isLoading={isLoading}
          errorMessage={errorMessage}
          register={register}
        />
      )}
    </Box>
  );
};

export default AuthDialog;

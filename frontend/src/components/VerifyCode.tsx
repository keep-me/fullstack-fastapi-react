import { useState, useCallback, useEffect } from "react";
import { Stack, Text, Box, PinInput, Link } from "@chakra-ui/react";
import { toaster } from "@/components/ui/toaster";
import LoadingOverlay from "./LoadingOverlay";
import {
  useVerifyCodeMutation,
  useResetPasswordMutation,
} from "@/redux/services/authApi";
import {
  TOAST_DURATION,
  RESEND_CODE_TIMER_SECONDS,
  STORAGE_KEYS,
} from "@/config/env";

interface VerifyCodeProps {
  email: string;
  verificationToken: string;
  onSuccess: (newVerificationToken: string) => void;
  onTokenUpdate: (newToken: string) => void;
}

const VerifyCode: React.FC<VerifyCodeProps> = ({
  email,
  verificationToken,
  onSuccess,
  onTokenUpdate,
}) => {
  const [verifyCode, setVerifyCode] = useState<string[]>([
    "",
    "",
    "",
    "",
    "",
    "",
  ]);
  const [resendTimer, setResendTimer] = useState<number>(
    RESEND_CODE_TIMER_SECONDS,
  );
  const [verifyCodeMutation, { isLoading }] = useVerifyCodeMutation();
  const [resetPasswordMutation, { isLoading: isResendLoading }] =
    useResetPasswordMutation();

  useEffect(() => {
    if (!verificationToken) {
      // Intentionally empty - token validation is handled elsewhere
    }
  }, [verificationToken]);

  useEffect(() => {
    let interval: number;
    if (resendTimer > 0) {
      interval = window.setInterval(() => {
        setResendTimer((prev) => prev - 1);
      }, 1000);
    }
    return () => {
      if (interval) window.clearInterval(interval);
    };
  }, [resendTimer]);

  const handlePinChange = useCallback(
    async (value: string[]) => {
      setVerifyCode(value);

      if (value.every((digit) => digit !== "") && value.length === 6) {
        if (!verificationToken) {
          toaster.create({
            title: "Error",
            description: "Session expired. Please start over.",
            type: "error",
            duration: TOAST_DURATION,
          });
          return;
        }

        try {
          const code = value.join("");
          const mutationResult = await verifyCodeMutation({
            code,
            verificationToken,
          });

          if (mutationResult.error) {
            setVerifyCode(["", "", "", "", "", ""]);

            const errorMessage =
              (mutationResult.error as { data?: { message?: string } })?.data
                ?.message || "Invalid or expired code";

            toaster.create({
              title: "Error",
              description: errorMessage,
              type: "error",
              duration: TOAST_DURATION,
            });
            return;
          }

          if (mutationResult.data) {
            const newToken = mutationResult.data.resetToken;

            if (newToken) {
              localStorage.setItem(STORAGE_KEYS.RESET_TOKEN, newToken);

              toaster.create({
                title: "Success",
                description: "Code verified successfully",
                type: "success",
                duration: TOAST_DURATION,
              });
              onSuccess(newToken);
            } else {
              setVerifyCode(["", "", "", "", "", ""]);
              toaster.create({
                title: "Error",
                description: "Verification failed. Please try again.",
                type: "error",
                duration: TOAST_DURATION,
              });
            }
          }
        } catch (error: unknown) {
          setVerifyCode(["", "", "", "", "", ""]);

          const errorMessage =
            (error as { data?: { message?: string } })?.data?.message ||
            "Invalid or expired code";

          toaster.create({
            title: "Error",
            description: errorMessage,
            type: "error",
            duration: TOAST_DURATION,
          });
        }
      }
    },
    [verificationToken, verifyCodeMutation, onSuccess],
  );

  const handleResendCode = useCallback(async () => {
    if (resendTimer > 0 || !email) return;

    try {
      const mutationResult = await resetPasswordMutation(email.trim());

      if (mutationResult.data) {
        const newToken = mutationResult.data.resetToken;

        if (newToken) {
          localStorage.setItem(STORAGE_KEYS.RESET_TOKEN, newToken);
          onTokenUpdate(newToken);

          setResendTimer(RESEND_CODE_TIMER_SECONDS);

          toaster.create({
            title: "Success",
            description: `New verification code sent to ${email}`,
            type: "success",
            duration: TOAST_DURATION,
          });
        } else {
          throw new Error("No verification token received");
        }
      }

      if (mutationResult.error) {
        const errorMessage =
          (mutationResult.error as { data?: { message?: string } })?.data
            ?.message || "Failed to resend verification code";

        toaster.create({
          title: "Error",
          description: errorMessage,
          type: "error",
          duration: TOAST_DURATION,
        });
      }
    } catch (error: unknown) {
      const errorMessage =
        (error as { data?: { message?: string } })?.data?.message ||
        "Failed to resend verification code";

      toaster.create({
        title: "Error",
        description: errorMessage,
        type: "error",
        duration: TOAST_DURATION,
      });
    }
  }, [email, resetPasswordMutation, resendTimer, onTokenUpdate]);

  return (
    <Box w="100%" p={{ base: 1, sm: 2, md: 3 }} id="verify-code">
      <LoadingOverlay isLoading={isLoading || isResendLoading} />
      <Stack gap={{ base: 3, sm: 4, md: 5 }} align="center" w="100%">
        <Text textAlign="center" fontSize="sm" color="gray.600">
          Enter the 6-digit code sent to {email}
        </Text>

        <PinInput.Root
          value={verifyCode}
          onValueChange={(e) => handlePinChange(e.value)}
          blurOnComplete={true}
        >
          <PinInput.HiddenInput />
          <PinInput.Control>
            <PinInput.Input index={0} />
            <PinInput.Input index={1} />
            <PinInput.Input index={2} />
            <PinInput.Input index={3} />
            <PinInput.Input index={4} />
            <PinInput.Input index={5} />
          </PinInput.Control>
        </PinInput.Root>

        <Text fontSize="sm" color="gray.500" textAlign="center">
          Didn't receive the code?{" "}
          {resendTimer > 0 ? (
            <Text as="span" color="gray.400">
              Resend in {resendTimer}s
            </Text>
          ) : (
            <Link
              color="blue.500"
              cursor="pointer"
              onClick={handleResendCode}
              _hover={{ color: "blue.400", textDecoration: "underline" }}
            >
              Resend code
            </Link>
          )}
        </Text>
      </Stack>
    </Box>
  );
};

export default VerifyCode;

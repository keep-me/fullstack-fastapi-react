import { useCallback } from "react";
import { useForm, type FieldValues } from "react-hook-form";
import { Stack, Button, Input, Field, Box } from "@chakra-ui/react";
import { toaster } from "@/components/ui/toaster";
import LoadingOverlay from "./LoadingOverlay";
import { useResetPasswordMutation } from "@/redux/services/authApi";
import { emailPattern } from "@/utils/utils";
import { TOAST_DURATION, STORAGE_KEYS } from "@/config/env";

interface ResetPasswordProps {
  onBackToLogin?: () => void;
  onSuccess: (email: string, verificationToken: string) => void;
}

const ResetPassword: React.FC<ResetPasswordProps> = ({ onSuccess }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const [resetPasswordMutation, { isLoading }] = useResetPasswordMutation();

  const handleResetPassword = useCallback(
    async (formData: FieldValues) => {
      try {
        const mutationResult = await resetPasswordMutation(
          formData.email.trim(),
        );

        if (mutationResult.data) {
          const token = mutationResult.data.resetToken;

          if (token) {
            localStorage.setItem(STORAGE_KEYS.RESET_TOKEN, token);

            toaster.create({
              title: "Success",
              description: `Verification code sent to ${formData.email}`,
              type: "success",
              duration: TOAST_DURATION,
            });
            onSuccess(formData.email, token);
          } else {
            throw new Error("No verification token received");
          }
        }
        if (mutationResult.error) {
          const errorMessage =
            (mutationResult.error as { data?: { message?: string } })?.data
              ?.message || "Failed to send reset email";

          toaster.create({
            title: "Error",
            description: errorMessage,
            type: "error",
            duration: TOAST_DURATION,
          });
          return;
        }
      } catch (error: unknown) {
        const errorMessage =
          (error as { data?: { message?: string } })?.data?.message ||
          "Failed to send reset email";

        toaster.create({
          title: "Error",
          description: errorMessage,
          type: "error",
          duration: TOAST_DURATION,
        });
      }
    },
    [resetPasswordMutation, onSuccess],
  );

  const onSubmit = handleSubmit(handleResetPassword);

  return (
    <Box w="100%" p={{ base: 1, sm: 2, md: 3 }}>
      <LoadingOverlay isLoading={isLoading} />
      <form onSubmit={onSubmit}>
        <Stack gap={{ base: 3, sm: 4, md: 5 }} align="flex-start" w="100%">
          <Field.Root invalid={!!errors.email} required>
            <Field.Label>
              Email <Field.RequiredIndicator />
            </Field.Label>
            <Input
              type="email"
              {...register("email", {
                required: "Email is required",
                pattern: emailPattern,
              })}
              placeholder="Enter your email address"
              autoFocus={true}
            />
            <Field.ErrorText>{errors.email?.message as string}</Field.ErrorText>
          </Field.Root>

          <Button
            mt={{ base: 2, md: 4 }}
            type="submit"
            alignSelf="center"
            w={{ base: "140px", sm: "160px", md: "180px" }}
            size={{ base: "sm", md: "md" }}
          >
            Reset password
          </Button>
        </Stack>
      </form>
    </Box>
  );
};

export default ResetPassword;

import { useCallback } from "react";
import { useForm, useWatch, type FieldValues } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { Stack, Button, Field, Box } from "@chakra-ui/react";
import { PasswordInput } from "@/components/ui/password-input";
import { toaster } from "@/components/ui/toaster";
import LoadingOverlay from "./LoadingOverlay";
import { useSetNewPasswordMutation } from "@/redux/services/authApi";
import { passwordRules, confirmPasswordRules } from "@/utils/utils";
import {
  TOAST_DURATION,
  PASSWORD_RESET_REDIRECT_DELAY,
  STORAGE_KEYS,
} from "@/config/env";

interface NewPasswordProps {
  verificationToken: string;
  onBackToLogin: () => void;
}

const NewPassword: React.FC<NewPasswordProps> = ({
  verificationToken,
  onBackToLogin,
}) => {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    getValues,
    control,
  } = useForm({
    mode: "onChange",
  });

  const watchedFields = useWatch({
    control,
    name: ["new_password", "confirm_new_password"],
  });

  const [setNewPasswordMutation, { isLoading }] = useSetNewPasswordMutation();

  const isFormValid =
    isValid &&
    watchedFields?.[0] &&
    watchedFields?.[1] &&
    watchedFields[0] === watchedFields[1];

  const handleSetNewPassword = useCallback(
    async (formData: FieldValues) => {
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
        const mutationResult = await setNewPasswordMutation({
          new_password: formData.new_password,
          confirm_new_password: formData.confirm_new_password,
          verificationToken,
        });

        if (mutationResult.error) {
          const errorMessage =
            (mutationResult.error as { data?: { message?: string } })?.data
              ?.message || "Failed to update password";

          toaster.create({
            title: "Error",
            description: errorMessage,
            type: "error",
            duration: TOAST_DURATION,
          });
          return;
        }

        localStorage.removeItem(STORAGE_KEYS.RESET_TOKEN);

        toaster.create({
          title: "Success",
          description: "Password changed successfully. Please login again.",
          type: "success",
          duration: TOAST_DURATION,
        });

        navigate("/");

        setTimeout(() => {
          onBackToLogin();
        }, PASSWORD_RESET_REDIRECT_DELAY);
      } catch (error: unknown) {
        const errorMessage =
          (error as { data?: { message?: string } })?.data?.message ||
          "Failed to update password";

        toaster.create({
          title: "Error",
          description: errorMessage,
          type: "error",
          duration: TOAST_DURATION,
        });
      }
    },
    [verificationToken, setNewPasswordMutation, navigate, onBackToLogin],
  );

  const onSubmit = handleSubmit(handleSetNewPassword);

  return (
    <Box w="100%" p={{ base: 1, sm: 2, md: 3 }} id="new-password">
      <LoadingOverlay isLoading={isLoading} />
      <form onSubmit={onSubmit}>
        <Stack gap={{ base: 3, sm: 4, md: 5 }} align="flex-start" w="100%">
          <Field.Root invalid={!!errors.new_password} required>
            <Field.Label>
              New Password
              <Field.RequiredIndicator />
            </Field.Label>
            <PasswordInput
              {...register("new_password", passwordRules(true))}
              placeholder="Enter new password"
              autoFocus={true}
            />
            <Field.ErrorText>
              {errors.new_password?.message as string}
            </Field.ErrorText>
          </Field.Root>

          <Field.Root invalid={!!errors.confirm_new_password} required>
            <Field.Label>
              Confirm New Password
              <Field.RequiredIndicator />
            </Field.Label>
            <PasswordInput
              {...register(
                "confirm_new_password",
                confirmPasswordRules(getValues, true),
              )}
              placeholder="Confirm new password"
            />
            <Field.ErrorText>
              {errors.confirm_new_password?.message as string}
            </Field.ErrorText>
          </Field.Root>

          <Button
            mt={{ base: 2, md: 4 }}
            type="submit"
            disabled={!isFormValid}
            alignSelf="center"
            w={{ base: "140px", sm: "160px", md: "180px" }}
            size={{ base: "sm", md: "md" }}
          >
            Save password
          </Button>
        </Stack>
      </form>
    </Box>
  );
};

export default NewPassword;

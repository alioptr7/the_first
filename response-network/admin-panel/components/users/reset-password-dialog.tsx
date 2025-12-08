"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { userService } from "@/lib/services/admin-api";
import type { User } from "@/lib/services/admin-api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const formSchema = z.object({
    new_password: z
        .string()
        .min(8, "رمز عبور باید حداقل ۸ کاراکتر باشد")
        .regex(/[A-Z]/, "رمز عبور باید شامل حداقل یک حرف بزرگ باشد")
        .regex(/[a-z]/, "رمز عبور باید شامل حداقل یک حرف کوچک باشد")
        .regex(/[0-9]/, "رمز عبور باید شامل حداقل یک عدد باشد"),
    confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
    message: "رمز عبور و تکرار آن مطابقت ندارند",
    path: ["confirm_password"],
});

type ResetPasswordFormData = z.infer<typeof formSchema>;

interface ResetPasswordDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    user: User | null;
}

export function ResetPasswordDialog({
    open,
    onOpenChange,
    user,
}: ResetPasswordDialogProps) {
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const form = useForm<ResetPasswordFormData>({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            new_password: "",
            confirm_password: "",
        },
    });

    const onSubmit = async (values: ResetPasswordFormData) => {
        if (!user) return;

        try {
            setError(null);
            setSuccessMessage(null);
            await userService.resetPassword(user.id, values.new_password);
            setSuccessMessage(`رمز عبور کاربر ${user.username} با موفقیت تغییر کرد.`);
            form.reset();

            // Close dialog after 2 seconds
            setTimeout(() => {
                onOpenChange(false);
                setSuccessMessage(null);
            }, 2000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error resetting password:", err);
            setError(
                err.response?.data?.detail || "خطا در تغییر رمز عبور. لطفاً مجدداً تلاش کنید."
            );
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>تغییر رمز عبور کاربر</DialogTitle>
                    <DialogDescription>
                        تغییر رمز عبور برای کاربر <span className="font-bold">{user?.username}</span>.
                        <br />
                        <span className="text-yellow-600 dark:text-yellow-500 text-xs">
                            توجه: رمز عبور ادمین‌ها از اینجا قابل تغییر نیست.
                        </span>
                    </DialogDescription>
                </DialogHeader>

                {successMessage ? (
                    <Alert className="bg-green-50 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-900">
                        <AlertDescription>{successMessage}</AlertDescription>
                    </Alert>
                ) : (
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                            {error && (
                                <Alert variant="destructive">
                                    <AlertCircle className="h-4 w-4" />
                                    <AlertTitle>خطا</AlertTitle>
                                    <AlertDescription>{error}</AlertDescription>
                                </Alert>
                            )}

                            <FormField
                                control={form.control}
                                name="new_password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>رمز عبور جدید</FormLabel>
                                        <FormControl>
                                            <Input type="password" {...field} className="text-left" dir="ltr" />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="confirm_password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>تکرار رمز عبور جدید</FormLabel>
                                        <FormControl>
                                            <Input type="password" {...field} className="text-left" dir="ltr" />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <DialogFooter>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => onOpenChange(false)}
                                >
                                    انصراف
                                </Button>
                                <Button type="submit" disabled={form.formState.isSubmitting}>
                                    {form.formState.isSubmitting && (
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    )}
                                    تغییر رمز عبور
                                </Button>
                            </DialogFooter>
                        </form>
                    </Form>
                )}
            </DialogContent>
        </Dialog>
    );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function AlertCircle(props: any) {
    return (
        <svg
            {...props}
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" x2="12" y1="8" y2="12" />
            <line x1="12" x2="12.01" y1="16" y2="16" />
        </svg>
    );
}

"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

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
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { ProfileType, RequestType } from "@/lib/services/admin-api";

const formSchema = z.object({
    daily_limit: z.number().min(0, "محدودیت روزانه باید عدد مثبت باشد").optional(),
    monthly_limit: z.number().min(0, "محدودیت ماهانه باید عدد مثبت باشد").optional(),
});

interface ProfileTypeLimitsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
    profileType: ProfileType | null;
    requestType: RequestType | null;
}

export function ProfileTypeLimitsDialog({
    open,
    onOpenChange,
    onSuccess,
    profileType,
    requestType,
}: ProfileTypeLimitsDialogProps) {
    const [error, setError] = useState<string | null>(null);

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            daily_limit: undefined,
            monthly_limit: undefined,
        },
    });

    const onSubmit = async (values: z.infer<typeof formSchema>) => {
        if (!profileType || !requestType) return;

        try {
            setError(null);
            // TODO: Implement API call to set profile type limits for request type
            // await requestService.setProfileTypeLimits(requestType.id, profileType.id, values);

            console.log("Setting limits:", {
                profileType: profileType.name,
                requestType: requestType.name,
                limits: values,
            });

            onSuccess();
            onOpenChange(false);
            form.reset();
        } catch (err: unknown) {
            console.error("Error setting limits:", err);
            if (err && typeof err === 'object' && 'response' in err) {
                const response = err as { response?: { data?: { detail?: string } } };
                setError(response.response?.data?.detail || "خطا در تنظیم محدودیت‌ها");
            } else {
                setError("خطا در تنظیم محدودیت‌ها");
            }
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>تنظیم محدودیت‌های پروفایل</DialogTitle>
                    <DialogDescription>
                        تنظیم محدودیت درخواست برای پروفایل {profileType?.name} در نوع درخواست {requestType?.name}
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        {error && (
                            <Alert variant="destructive">
                                <AlertDescription>{error}</AlertDescription>
                            </Alert>
                        )}

                        <FormField
                            control={form.control}
                            name="daily_limit"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>محدودیت روزانه</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="number"
                                            placeholder="مثال: 100"
                                            {...field}
                                            onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                                            value={field.value ?? ""}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="monthly_limit"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>محدودیت ماهانه</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="number"
                                            placeholder="مثال: 3000"
                                            {...field}
                                            onChange={(e) => field.onChange(e.target.value ? parseInt(e.target.value) : undefined)}
                                            value={field.value ?? ""}
                                        />
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
                                لغو
                            </Button>
                            <Button type="submit" disabled={form.formState.isSubmitting}>
                                {form.formState.isSubmitting && (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                )}
                                ذخیره
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}

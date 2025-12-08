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
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { profileTypeService } from "@/lib/services/admin-api";
import { Alert, AlertDescription } from "@/components/ui/alert";

const formSchema = z.object({
    name: z
        .string()
        .min(3, "نام باید حداقل ۳ کاراکتر باشد")
        .regex(/^[a-zA-Z0-9_-]+$/, "نام فقط می‌تواند شامل حروف انگلیسی، اعداد و خط تیره باشد"),
    description: z.string().optional(),
    daily_request_limit: z.coerce.number().min(0, "محدودیت نمی‌تواند منفی باشد"),
    monthly_request_limit: z.coerce.number().min(0, "محدودیت نمی‌تواند منفی باشد"),
    is_active: z.boolean().default(true),
});

type CreateProfileTypeFormData = z.infer<typeof formSchema>;

interface CreateProfileTypeDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
}

export function CreateProfileTypeDialog({
    open,
    onOpenChange,
    onSuccess,
}: CreateProfileTypeDialogProps) {
    const [error, setError] = useState<string | null>(null);

    const form = useForm<CreateProfileTypeFormData>({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            name: "",
            description: "",
            daily_request_limit: 100,
            monthly_request_limit: 3000,
            is_active: true,
        },
    });

    const onSubmit = async (data: CreateProfileTypeFormData) => {
        try {
            setError(null);
            await profileTypeService.createProfileType(data);
            form.reset();
            onSuccess();
            onOpenChange(false);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error creating profile type:", err);
            setError(
                err.response?.data?.detail || "خطا در ایجاد نوع پروفایل. لطفاً مجدداً تلاش کنید."
            );
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px]">
                <DialogHeader>
                    <DialogTitle>ایجاد نوع پروفایل جدید</DialogTitle>
                    <DialogDescription>
                        اطلاعات نوع پروفایل جدید را وارد کنید. نام باید یکتا باشد.
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
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>نام (شناسه)</FormLabel>
                                    <FormControl>
                                        <Input placeholder="مثال: gold-plan" {...field} className="text-left" dir="ltr" />
                                    </FormControl>
                                    <FormDescription>
                                        نام یکتا برای شناسایی در سیستم (فقط حروف انگلیسی)
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>توضیحات</FormLabel>
                                    <FormControl>
                                        <Input placeholder="توضیحات اختیاری..." {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className="grid grid-cols-2 gap-4">
                            <FormField
                                control={form.control}
                                name="daily_request_limit"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>محدودیت روزانه</FormLabel>
                                        <FormControl>
                                            <Input type="number" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <FormField
                                control={form.control}
                                name="monthly_request_limit"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>محدودیت ماهانه</FormLabel>
                                        <FormControl>
                                            <Input type="number" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                        </div>

                        <FormField
                            control={form.control}
                            name="is_active"
                            render={({ field }) => (
                                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                                    <div className="space-y-0.5">
                                        <FormLabel className="text-base">وضعیت فعال</FormLabel>
                                        <FormDescription>
                                            آیا این نوع پروفایل قابل استفاده است؟
                                        </FormDescription>
                                    </div>
                                    <FormControl>
                                        <Switch
                                            checked={field.value}
                                            onCheckedChange={field.onChange}
                                        />
                                    </FormControl>
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
                                ایجاد پروفایل
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}

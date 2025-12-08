"use client";

import { useEffect, useState } from "react";
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
import { Textarea } from "@/components/ui/textarea";
import { requestService } from "@/lib/services/admin-api";
import type { RequestType } from "@/lib/services/admin-api";
import { Alert, AlertDescription } from "@/components/ui/alert";

const formSchema = z.object({
    elasticsearch_query_template: z.string().min(2, "کوئری نمی‌تواند خالی باشد"),
});

type ConfigureQueryFormData = z.infer<typeof formSchema>;

interface ConfigureQueryDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
    requestType: RequestType | null;
}

export function ConfigureQueryDialog({
    open,
    onOpenChange,
    onSuccess,
    requestType,
}: ConfigureQueryDialogProps) {
    const [error, setError] = useState<string | null>(null);

    const form = useForm<ConfigureQueryFormData>({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            elasticsearch_query_template: "{}",
        },
    });

    useEffect(() => {
        if (open && requestType) {
            const queryTemplate = requestType.elasticsearch_query_template
                ? JSON.stringify(requestType.elasticsearch_query_template, null, 2)
                : "{}";
            form.reset({
                elasticsearch_query_template: queryTemplate,
            });
        } else if (!open) {
            form.reset({
                elasticsearch_query_template: "{}",
            });
            setError(null);
        }
    }, [requestType, form, open]);

    const onSubmit = async (data: ConfigureQueryFormData) => {
        if (!requestType) return;

        try {
            setError(null);
            // Validate JSON
            const parsedQuery = JSON.parse(data.elasticsearch_query_template);

            await requestService.configureRequestTypeQuery(requestType.id, {
                elasticsearch_query_template: parsedQuery,
            });
            onSuccess();
            onOpenChange(false);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error configuring query:", err);
            if (err instanceof SyntaxError) {
                setError("فرمت JSON نامعتبر است. لطفاً کوئری را بررسی کنید.");
            } else {
                setError(
                    err.response?.data?.detail || "خطا در تنظیم کوئری. لطفاً مجدداً تلاش کنید."
                );
            }
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[700px]">
                <DialogHeader>
                    <DialogTitle>تنظیم کوئری Elasticsearch</DialogTitle>
                    <DialogDescription>
                        تنظیم الگوی کوئری برای نوع درخواست {requestType?.name}
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
                            name="elasticsearch_query_template"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>الگوی کوئری (JSON)</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            {...field}
                                            rows={15}
                                            className="font-mono text-sm"
                                            dir="ltr"
                                            placeholder='{\n  "query": {\n    "match_all": {}\n  }\n}'
                                        />
                                    </FormControl>
                                    <FormDescription>
                                        کوئری Elasticsearch را به صورت JSON وارد کنید. می‌توانید از متغیرهای پارامتر استفاده کنید.
                                    </FormDescription>
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
                                ذخیره کوئری
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}

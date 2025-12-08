"use client";

import { useState } from "react";
import { Loader2, Download, CheckCircle2, AlertCircle } from "lucide-react";

import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { userService } from "@/lib/services/admin-api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface ExportUsersDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function ExportUsersDialog({
    open,
    onOpenChange,
}: ExportUsersDialogProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleExport = async () => {
        try {
            setLoading(true);
            setError(null);
            setSuccess(null);
            const result = await userService.exportUsers();
            setSuccess(`درخواست خروجی با شناسه ${result.task_id} ثبت شد.`);

            // Close dialog after 3 seconds
            setTimeout(() => {
                onOpenChange(false);
                setSuccess(null);
            }, 3000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error exporting users:", err);
            setError(
                err.response?.data?.detail || "خطا در ثبت درخواست خروجی. لطفاً مجدداً تلاش کنید."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle className="flex items-center gap-2">
                        <Download className="h-5 w-5" />
                        خروجی گرفتن از کاربران
                    </AlertDialogTitle>
                    <AlertDialogDescription>
                        آیا می‌خواهید لیست تمام کاربران را به Request Network صادر کنید؟
                        این عملیات ممکن است زمان‌بر باشد و در پس‌زمینه انجام می‌شود.
                    </AlertDialogDescription>
                </AlertDialogHeader>

                {error && (
                    <Alert variant="destructive" className="my-2">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>خطا</AlertTitle>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {success && (
                    <Alert className="my-2 bg-green-50 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-900">
                        <CheckCircle2 className="h-4 w-4" />
                        <AlertTitle>موفقیت</AlertTitle>
                        <AlertDescription>{success}</AlertDescription>
                    </Alert>
                )}

                <AlertDialogFooter>
                    <AlertDialogCancel disabled={loading || !!success}>انصراف</AlertDialogCancel>
                    <AlertDialogAction
                        onClick={(e) => {
                            e.preventDefault();
                            handleExport();
                        }}
                        disabled={loading || !!success}
                    >
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        تایید و شروع خروجی
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}

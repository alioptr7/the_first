"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";

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
import { profileTypeService } from "@/lib/services/admin-api";
import type { ProfileType } from "@/lib/services/admin-api";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface DeleteProfileTypeDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
    profileType: ProfileType | null;
}

export function DeleteProfileTypeDialog({
    open,
    onOpenChange,
    onSuccess,
    profileType,
}: DeleteProfileTypeDialogProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleDelete = async () => {
        if (!profileType) return;

        try {
            setLoading(true);
            setError(null);
            await profileTypeService.deleteProfileType(profileType.name);
            onSuccess();
            onOpenChange(false);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error deleting profile type:", err);
            setError(
                err.response?.data?.detail || "خطا در حذف نوع پروفایل. لطفاً مجدداً تلاش کنید."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>آیا از حذف این نوع پروفایل اطمینان دارید؟</AlertDialogTitle>
                    <AlertDialogDescription>
                        شما در حال حذف نوع پروفایل <span className="font-bold text-foreground">{profileType?.name}</span> هستید.
                        این عمل غیرقابل بازگشت است.
                    </AlertDialogDescription>
                </AlertDialogHeader>

                {error && (
                    <Alert variant="destructive" className="my-2">
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                <AlertDialogFooter>
                    <AlertDialogCancel disabled={loading}>انصراف</AlertDialogCancel>
                    <AlertDialogAction
                        onClick={(e) => {
                            e.preventDefault();
                            handleDelete();
                        }}
                        disabled={loading}
                        className="bg-red-600 hover:bg-red-700 text-white"
                    >
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        حذف پروفایل
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}

"use client";

import { useState } from "react";
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
import { Loader2 } from "lucide-react";
import { userService, type User } from "@/lib/services/admin-api";

interface DeleteUserDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
    user: User | null;
}

export function DeleteUserDialog({
    open,
    onOpenChange,
    onSuccess,
    user,
}: DeleteUserDialogProps) {
    const [isLoading, setIsLoading] = useState(false);

    const handleDelete = async () => {
        if (!user) return;

        try {
            setIsLoading(true);
            await userService.deleteUser(user.id);
            onSuccess();
            onOpenChange(false);
        } catch (error) {
            console.error("Error deleting user:", error);
            alert("خطا در حذف کاربر");
        } finally {
            setIsLoading(false);
        }
    };

    if (!user) return null;

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>آیا مطمئن هستید؟</AlertDialogTitle>
                    <AlertDialogDescription className="space-y-2">
                        <p>
                            شما در حال حذف کاربر <strong>{user.username}</strong> هستید.
                        </p>
                        <p className="text-red-600 dark:text-red-400">
                            این عمل قابل بازگشت نیست و تمام اطلاعات کاربر حذف خواهد شد.
                        </p>
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel disabled={isLoading}>انصراف</AlertDialogCancel>
                    <AlertDialogAction
                        onClick={handleDelete}
                        disabled={isLoading}
                        className="bg-red-600 hover:bg-red-700"
                    >
                        {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        حذف کاربر
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}

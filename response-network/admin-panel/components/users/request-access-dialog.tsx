"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2, Trash2, Plus, AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { userService, requestService } from "@/lib/services/admin-api";
import type { User, UserRequestAccess, RequestType } from "@/lib/services/admin-api";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

const formSchema = z.object({
    request_type_id: z.string().min(1, "انتخاب نوع درخواست الزامی است"),
    max_requests_per_hour: z.coerce.number().min(0, "تعداد درخواست باید عدد مثبت باشد"),
    is_active: z.boolean().default(true),
});

type GrantAccessFormData = z.infer<typeof formSchema>;

interface RequestAccessDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    user: User | null;
}

export function RequestAccessDialog({
    open,
    onOpenChange,
    user,
}: RequestAccessDialogProps) {
    const [accessList, setAccessList] = useState<UserRequestAccess[]>([]);
    const [requestTypes, setRequestTypes] = useState<RequestType[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    const form = useForm<GrantAccessFormData>({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        resolver: zodResolver(formSchema) as any,
        defaultValues: {
            request_type_id: "",
            max_requests_per_hour: 100,
            is_active: true,
        },
    });

    useEffect(() => {
        if (open && user) {
            fetchData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [open, user]);

    const fetchData = async () => {
        if (!user) return;
        setLoading(true);
        setError(null);
        try {
            const [accessData, typesData] = await Promise.all([
                userService.getUserRequestAccess(user.id),
                requestService.getRequestTypes(),
            ]);
            setAccessList(accessData);
            setRequestTypes(typesData);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error fetching data:", err);
            setError("خطا در دریافت اطلاعات. لطفاً مجدداً تلاش کنید.");
        } finally {
            setLoading(false);
        }
    };

    const handleGrantAccess = async (data: GrantAccessFormData) => {
        if (!user) return;
        try {
            setError(null);
            setSuccessMessage(null);
            await userService.grantRequestAccess(user.id, [{
                request_type_id: data.request_type_id,
                max_requests_per_hour: data.max_requests_per_hour,
                is_active: data.is_active,
            }]);
            setSuccessMessage("دسترسی با موفقیت اعطا شد.");
            form.reset();
            fetchData(); // Refresh list

            setTimeout(() => setSuccessMessage(null), 3000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error granting access:", err);
            setError(
                err.response?.data?.detail || "خطا در اعطای دسترسی."
            );
        }
    };

    const handleRevokeAccess = async (requestTypeId: string) => {
        if (!user) return;
        if (!confirm("آیا از لغو این دسترسی اطمینان دارید؟")) return;

        try {
            setError(null);
            await userService.revokeRequestAccess(user.id, requestTypeId);
            setSuccessMessage("دسترسی با موفقیت لغو شد.");
            fetchData(); // Refresh list
            setTimeout(() => setSuccessMessage(null), 3000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error revoking access:", err);
            setError(
                err.response?.data?.detail || "خطا در لغو دسترسی."
            );
        }
    };

    // Filter out request types that the user already has access to
    const availableRequestTypes = requestTypes.filter(
        (rt) => !accessList.some((access) => access.request_type_id === rt.id)
    );

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[700px]">
                <DialogHeader>
                    <DialogTitle>مدیریت دسترسی‌های کاربر</DialogTitle>
                    <DialogDescription>
                        مدیریت دسترسی‌های اختصاصی برای کاربر <span className="font-bold">{user?.username}</span>.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-6">
                    {/* Existing Access List */}
                    <div>
                        <h3 className="text-sm font-medium mb-2">دسترسی‌های فعلی</h3>
                        {loading && accessList.length === 0 ? (
                            <div className="flex justify-center p-4">
                                <Loader2 className="h-6 w-6 animate-spin" />
                            </div>
                        ) : accessList.length > 0 ? (
                            <div className="border rounded-md">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead className="text-right">نوع درخواست</TableHead>
                                            <TableHead className="text-center">محدودیت ساعتی</TableHead>
                                            <TableHead className="text-center">وضعیت</TableHead>
                                            <TableHead className="w-[50px]"></TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {accessList.map((access) => {
                                            const rt = requestTypes.find(t => t.id === access.request_type_id);
                                            return (
                                                <TableRow key={access.request_type_id}>
                                                    <TableCell className="font-medium">
                                                        {rt?.name || access.request_type_id}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        {access.max_requests_per_hour}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        {access.is_active ? (
                                                            <span className="text-green-600 text-xs bg-green-100 px-2 py-1 rounded-full">فعال</span>
                                                        ) : (
                                                            <span className="text-red-600 text-xs bg-red-100 px-2 py-1 rounded-full">غیرفعال</span>
                                                        )}
                                                    </TableCell>
                                                    <TableCell>
                                                        <Button
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-100"
                                                            onClick={() => handleRevokeAccess(access.request_type_id)}
                                                        >
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </TableCell>
                                                </TableRow>
                                            );
                                        })}
                                    </TableBody>
                                </Table>
                            </div>
                        ) : (
                            <p className="text-sm text-muted-foreground text-center border rounded-md p-4 bg-muted/50">
                                هیچ دسترسی اختصاصی برای این کاربر تعریف نشده است.
                            </p>
                        )}
                    </div>

                    <div className="border-t pt-4">
                        <h3 className="text-sm font-medium mb-4">افزودن دسترسی جدید</h3>

                        {successMessage && (
                            <Alert className="mb-4 bg-green-50 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-900">
                                <AlertDescription>{successMessage}</AlertDescription>
                            </Alert>
                        )}

                        {error && (
                            <Alert variant="destructive" className="mb-4">
                                <AlertCircle className="h-4 w-4" />
                                <AlertTitle>خطا</AlertTitle>
                                <AlertDescription>{error}</AlertDescription>
                            </Alert>
                        )}

                        <Form {...form}>
                            <form onSubmit={form.handleSubmit(handleGrantAccess)} className="flex gap-4 items-end">
                                <FormField
                                    control={form.control}
                                    name="request_type_id"
                                    render={({ field }) => (
                                        <FormItem className="flex-1">
                                            <FormLabel>نوع درخواست</FormLabel>
                                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                                                <FormControl>
                                                    <SelectTrigger>
                                                        <SelectValue placeholder="انتخاب کنید" />
                                                    </SelectTrigger>
                                                </FormControl>
                                                <SelectContent>
                                                    {availableRequestTypes.map((rt) => (
                                                        <SelectItem key={rt.id} value={rt.id}>
                                                            {rt.name}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={form.control}
                                    name="max_requests_per_hour"
                                    render={({ field }) => (
                                        <FormItem className="w-32">
                                            <FormLabel>محدودیت ساعتی</FormLabel>
                                            <FormControl>
                                                <Input type="number" {...field} className="text-center" />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />

                                <FormField
                                    control={form.control}
                                    name="is_active"
                                    render={({ field }) => (
                                        <FormItem className="flex flex-col gap-2 items-center pb-2">
                                            <FormLabel className="text-xs">فعال</FormLabel>
                                            <FormControl>
                                                <Switch
                                                    checked={field.value}
                                                    onCheckedChange={field.onChange}
                                                />
                                            </FormControl>
                                        </FormItem>
                                    )}
                                />

                                <Button type="submit" disabled={form.formState.isSubmitting || availableRequestTypes.length === 0}>
                                    {form.formState.isSubmitting ? (
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                        <Plus className="h-4 w-4" />
                                    )}
                                    <span className="mr-2">افزودن</span>
                                </Button>
                            </form>
                        </Form>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}

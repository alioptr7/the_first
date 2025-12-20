"use client";

import { useState, useEffect } from "react";
import { Loader2, Trash2, UserPlus, Users, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { requestService, profileTypeService, userService, type RequestType, type ProfileTypeAccess, type User } from "@/lib/services/admin-api";

interface ManageAccessDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
    requestType: RequestType | null;
}

interface UserAccess {
    id: string;
    user_id: string;
    request_type_id: string;
    max_requests_per_hour: number;
    is_active: boolean;
    user?: {
        id: string;
        username: string;
        email: string;
        full_name: string;
        profile_type: string;
    };
}

export function ManageAccessDialog({
    open,
    onOpenChange,
    onSuccess,
    requestType,
}: ManageAccessDialogProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [profileAccess, setProfileAccess] = useState<ProfileTypeAccess[]>([]);
    const [userAccess, setUserAccess] = useState<UserAccess[]>([]);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const [profileTypes, setProfileTypes] = useState<any[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [loadingUsers, setLoadingUsers] = useState(false);

    // Form states
    const [selectedProfileType, setSelectedProfileType] = useState<string>("");
    const [dailyLimit, setDailyLimit] = useState<string>("");
    const [monthlyLimit, setMonthlyLimit] = useState<string>("");

    const [selectedUser, setSelectedUser] = useState<string>("");
    const [userHourlyLimit, setUserHourlyLimit] = useState<string>("100");

    useEffect(() => {
        if (open && requestType) {
            fetchProfileAccess();
            fetchUserAccess();
            fetchProfileTypes();
            fetchUsers();
        }
    }, [open, requestType]);

    const fetchProfileAccess = async () => {
        if (!requestType) return;
        try {
            setLoading(true);
            const data = await requestService.getProfileTypeAccess(requestType.id);
            setProfileAccess(data);
        } catch (err) {
            console.error("Error fetching profile access:", err);
            setError("خطا در دریافت دسترسی‌های پروفایل");
        } finally {
            setLoading(false);
        }
    };

    const fetchUserAccess = async () => {
        if (!requestType) return;
        try {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const data = await requestService.getRequestTypeAccess(requestType.id) as any[];
            setUserAccess(data);
        } catch (err) {
            console.error("Error fetching user access:", err);
        }
    };

    const fetchProfileTypes = async () => {
        try {
            const data = await profileTypeService.getProfileTypes();
            setProfileTypes(data);
        } catch (err) {
            console.error("Error fetching profile types:", err);
        }
    };

    const fetchUsers = async () => {
        try {
            setLoadingUsers(true);
            const data = await userService.getUsers();
            setUsers(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error("Error fetching users:", err);
        } finally {
            setLoadingUsers(false);
        }
    };

    const handleGrantProfileAccess = async () => {
        if (!requestType || !selectedProfileType) return;

        try {
            setError(null);
            await requestService.grantProfileTypeAccess(requestType.id, {
                profile_type_ids: [selectedProfileType],
                max_requests_per_day: dailyLimit ? parseInt(dailyLimit) : undefined,
                max_requests_per_month: monthlyLimit ? parseInt(monthlyLimit) : undefined,
                is_active: true,
            });

            setSelectedProfileType("");
            setDailyLimit("");
            setMonthlyLimit("");
            await fetchProfileAccess();
            onSuccess();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error granting profile access:", err);
            setError(err.response?.data?.detail || "خطا در اعطای دسترسی");
        }
    };

    const handleGrantUserAccess = async () => {
        if (!requestType || !selectedUser) return;

        try {
            setError(null);
            await requestService.grantRequestTypeAccess(requestType.id, {
                user_ids: [selectedUser],
                max_requests_per_hour: parseInt(userHourlyLimit) || 100,
                is_active: true,
            });

            setSelectedUser("");
            setUserHourlyLimit("100");
            await fetchUserAccess();
            onSuccess();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error granting user access:", err);
            setError(err.response?.data?.detail || "خطا در اعطای دسترسی کاربر");
        }
    };

    const handleRevokeProfileAccess = async (profileTypeId: string) => {
        if (!requestType) return;

        try {
            setError(null);
            await requestService.revokeProfileTypeAccess(requestType.id, profileTypeId);
            await fetchProfileAccess();
            onSuccess();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error revoking profile access:", err);
            setError(err.response?.data?.detail || "خطا در لغو دسترسی");
        }
    };

    const handleRevokeUserAccess = async (userId: string) => {
        if (!requestType) return;

        try {
            setError(null);
            await requestService.revokeRequestTypeAccess(requestType.id, userId);
            await fetchUserAccess();
            onSuccess();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            console.error("Error revoking user access:", err);
            setError(err.response?.data?.detail || "خطا در لغو دسترسی کاربر");
        }
    };

    // Filter users that already have access
    const availableUsers = users.filter(user =>
        !userAccess.some(access => access.user_id === user.id)
    );

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[800px] max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>مدیریت دسترسی</DialogTitle>
                    <DialogDescription>
                        مدیریت دسترسی انواع پروفایل و کاربران به {requestType?.name}
                    </DialogDescription>
                </DialogHeader>

                <Tabs defaultValue="profile" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="profile">
                            <Users className="ml-2 h-4 w-4" />
                            دسترسی پروفایل‌ها
                        </TabsTrigger>
                        <TabsTrigger value="user">
                            <UserPlus className="ml-2 h-4 w-4" />
                            دسترسی کاربران
                        </TabsTrigger>
                    </TabsList>

                    {/* Profile Type Access Tab */}
                    <TabsContent value="profile" className="space-y-4">
                        {error && (
                            <Alert variant="destructive">
                                <AlertDescription>{error}</AlertDescription>
                            </Alert>
                        )}

                        {/* Add Profile Access Form */}
                        <div className="space-y-4 border rounded-lg p-4 bg-muted/50">
                            <h3 className="font-medium text-sm">اضافه کردن دسترسی جدید</h3>

                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                                <div className="space-y-2 md:col-span-1">
                                    <Label className="text-xs">نوع پروفایل</Label>
                                    <Select
                                        value={selectedProfileType}
                                        onValueChange={setSelectedProfileType}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="انتخاب کنید" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {profileTypes.map((pt) => (
                                                <SelectItem key={pt.name} value={pt.name}>
                                                    {pt.display_name || pt.name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-xs">محدودیت روزانه</Label>
                                    <Input
                                        type="number"
                                        placeholder="نامحدود"
                                        value={dailyLimit}
                                        onChange={(e) => setDailyLimit(e.target.value)}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-xs">محدودیت ماهانه</Label>
                                    <Input
                                        type="number"
                                        placeholder="نامحدود"
                                        value={monthlyLimit}
                                        onChange={(e) => setMonthlyLimit(e.target.value)}
                                    />
                                </div>

                                <Button
                                    onClick={handleGrantProfileAccess}
                                    disabled={!selectedProfileType}
                                    className="w-full"
                                >
                                    <UserPlus className="mr-2 h-4 w-4" />
                                    افزودن
                                </Button>
                            </div>
                        </div>

                        {/* Profile Access List */}
                        <div className="border rounded-lg overflow-hidden">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>نوع پروفایل</TableHead>
                                        <TableHead className="text-center">محدودیت روزانه</TableHead>
                                        <TableHead className="text-center">محدودیت ماهانه</TableHead>
                                        <TableHead className="text-center">وضعیت</TableHead>
                                        <TableHead className="text-center">عملیات</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {loading ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center py-8">
                                                <Loader2 className="h-6 w-6 animate-spin mx-auto text-primary" />
                                            </TableCell>
                                        </TableRow>
                                    ) : profileAccess.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                                هیچ دسترسی پروفایلی تعریف نشده است
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        profileAccess.map((access) => (
                                            <TableRow key={access.id}>
                                                <TableCell className="font-medium">
                                                    {access.profile_type_name || access.profile_type_id}
                                                </TableCell>
                                                <TableCell className="text-center">
                                                    {access.max_requests_per_day ? access.max_requests_per_day.toLocaleString() : "نامحدود"}
                                                </TableCell>
                                                <TableCell className="text-center">
                                                    {access.max_requests_per_month ? access.max_requests_per_month.toLocaleString() : "نامحدود"}
                                                </TableCell>
                                                <TableCell className="text-center">
                                                    <Badge variant={access.is_active ? "default" : "secondary"}>
                                                        {access.is_active ? "فعال" : "غیرفعال"}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="text-center">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                                                        onClick={() => handleRevokeProfileAccess(access.profile_type_id)}
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </div>
                    </TabsContent>

                    {/* User Access Tab */}
                    <TabsContent value="user" className="space-y-4">

                        {/* Add User Access Form */}
                        <div className="space-y-4 border rounded-lg p-4 bg-muted/50">
                            <h3 className="font-medium text-sm">اضافه کردن دسترسی کاربر</h3>

                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                                <div className="space-y-2 md:col-span-2">
                                    <Label className="text-xs">کاربر</Label>
                                    <Select
                                        value={selectedUser}
                                        onValueChange={setSelectedUser}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="جستجو و انتخاب کاربر..." />
                                        </SelectTrigger>
                                        <SelectContent className="max-h-[200px]">
                                            <div className="sticky top-0 p-2 bg-background border-b z-10">
                                                <div className="relative">
                                                    <Search className="absolute right-2 top-2.5 h-3 w-3 text-muted-foreground" />
                                                    <Input
                                                        placeholder="جستجو..."
                                                        className="h-8 pr-8 text-xs"
                                                        onKeyDown={(e) => e.stopPropagation()}
                                                    />
                                                </div>
                                            </div>
                                            {availableUsers.length > 0 ? (
                                                availableUsers.map((u) => (
                                                    <SelectItem key={u.id} value={u.id}>
                                                        {u.username} ({u.full_name || u.email})
                                                    </SelectItem>
                                                ))
                                            ) : (
                                                <div className="p-2 text-xs text-center text-muted-foreground">
                                                    کاربری یافت نشد
                                                </div>
                                            )}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-xs">محدودیت ساعتی</Label>
                                    <Input
                                        type="number"
                                        placeholder="100"
                                        value={userHourlyLimit}
                                        onChange={(e) => setUserHourlyLimit(e.target.value)}
                                    />
                                </div>

                                <Button
                                    onClick={handleGrantUserAccess}
                                    disabled={!selectedUser}
                                    className="w-full"
                                >
                                    <UserPlus className="mr-2 h-4 w-4" />
                                    افزودن
                                </Button>
                            </div>
                        </div>

                        {/* User Access List */}
                        <div className="border rounded-lg overflow-hidden">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>نام کاربری</TableHead>
                                        <TableHead>نام کامل</TableHead>
                                        <TableHead className="text-center">محدودیت ساعتی</TableHead>
                                        <TableHead className="text-center">تاریخ اعطا</TableHead>
                                        <TableHead className="text-center">عملیات</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {loading ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center py-8">
                                                <Loader2 className="h-6 w-6 animate-spin mx-auto text-primary" />
                                            </TableCell>
                                        </TableRow>
                                    ) : userAccess.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                                                هیچ دسترسی کاربری تعریف نشده است
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        userAccess.map((access) => (
                                            <TableRow key={access.id}>
                                                <TableCell className="font-medium">
                                                    {access.user?.username || access.user_id}
                                                </TableCell>
                                                <TableCell>
                                                    {access.user?.full_name || "-"}
                                                </TableCell>
                                                <TableCell className="text-center">
                                                    {access.max_requests_per_hour.toLocaleString()}
                                                </TableCell>
                                                <TableCell className="text-center" dir="ltr">
                                                    {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                                                    {access.created_at ? new Date((access as any).created_at).toLocaleDateString("fa-IR") : "-"}
                                                </TableCell>
                                                <TableCell className="text-center">
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                                                        onClick={() => handleRevokeUserAccess(access.user_id)}
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        ))
                                    )}
                                </TableBody>
                            </Table>
                        </div>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}

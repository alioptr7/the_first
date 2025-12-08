"use client";

import { useState, useEffect } from "react";
import { Loader2, Trash2, UserPlus, Users } from "lucide-react";

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
import { requestService, profileTypeService, type RequestType, type ProfileTypeAccess } from "@/lib/services/admin-api";

interface ManageAccessDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSuccess: () => void;
    requestType: RequestType | null;
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
    const [profileTypes, setProfileTypes] = useState<any[]>([]);
    const [selectedProfileType, setSelectedProfileType] = useState<string>("");
    const [dailyLimit, setDailyLimit] = useState<string>("");
    const [monthlyLimit, setMonthlyLimit] = useState<string>("");

    useEffect(() => {
        if (open && requestType) {
            fetchProfileAccess();
            fetchProfileTypes();
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

    const fetchProfileTypes = async () => {
        try {
            const data = await profileTypeService.getProfileTypes();
            setProfileTypes(data);
        } catch (err) {
            console.error("Error fetching profile types:", err);
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
        } catch (err: any) {
            console.error("Error granting profile access:", err);
            setError(err.response?.data?.detail || "خطا در اعطای دسترسی");
        }
    };

    const handleRevokeProfileAccess = async (profileTypeId: string) => {
        if (!requestType) return;

        try {
            setError(null);
            await requestService.revokeProfileTypeAccess(requestType.id, profileTypeId);
            await fetchProfileAccess();
            onSuccess();
        } catch (err: any) {
            console.error("Error revoking profile access:", err);
            setError(err.response?.data?.detail || "خطا در لغو دسترسی");
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
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
                        <div className="space-y-4 border rounded-lg p-4">
                            <h3 className="font-medium">اضافه کردن دسترسی پروفایل</h3>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>نوع پروفایل</Label>
                                    <select
                                        className="w-full rounded-md border border-input bg-background px-3 py-2"
                                        value={selectedProfileType}
                                        onChange={(e) => setSelectedProfileType(e.target.value)}
                                    >
                                        <option value="">انتخاب کنید...</option>
                                        {profileTypes.map((pt) => (
                                            <option key={pt.name} value={pt.name}>
                                                {pt.display_name || pt.name}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="space-y-2">
                                    <Label>محدودیت روزانه</Label>
                                    <Input
                                        type="number"
                                        placeholder="نامحدود"
                                        value={dailyLimit}
                                        onChange={(e) => setDailyLimit(e.target.value)}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label>محدودیت ماهانه</Label>
                                    <Input
                                        type="number"
                                        placeholder="نامحدود"
                                        value={monthlyLimit}
                                        onChange={(e) => setMonthlyLimit(e.target.value)}
                                    />
                                </div>

                                <div className="flex items-end">
                                    <Button
                                        onClick={handleGrantProfileAccess}
                                        disabled={!selectedProfileType}
                                        className="w-full"
                                    >
                                        اضافه کردن
                                    </Button>
                                </div>
                            </div>
                        </div>

                        {/* Profile Access List */}
                        <div className="border rounded-lg">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>نوع پروفایل</TableHead>
                                        <TableHead>محدودیت روزانه</TableHead>
                                        <TableHead>محدودیت ماهانه</TableHead>
                                        <TableHead>وضعیت</TableHead>
                                        <TableHead>عملیات</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {loading ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center">
                                                <Loader2 className="h-6 w-6 animate-spin mx-auto" />
                                            </TableCell>
                                        </TableRow>
                                    ) : profileAccess.length === 0 ? (
                                        <TableRow>
                                            <TableCell colSpan={5} className="text-center text-muted-foreground">
                                                هیچ دسترسی پروفایلی تعریف نشده
                                            </TableCell>
                                        </TableRow>
                                    ) : (
                                        profileAccess.map((access) => (
                                            <TableRow key={access.id}>
                                                <TableCell className="font-medium">
                                                    {access.profile_type_name || access.profile_type_id}
                                                </TableCell>
                                                <TableCell>
                                                    {access.max_requests_per_day || "نامحدود"}
                                                </TableCell>
                                                <TableCell>
                                                    {access.max_requests_per_month || "نامحدود"}
                                                </TableCell>
                                                <TableCell>
                                                    <Badge variant={access.is_active ? "default" : "secondary"}>
                                                        {access.is_active ? "فعال" : "غیرفعال"}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell>
                                                    <Button
                                                        variant="ghost"
                                                        size="sm"
                                                        onClick={() => handleRevokeProfileAccess(access.profile_type_id)}
                                                    >
                                                        <Trash2 className="h-4 w-4 text-destructive" />
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
                        <Alert>
                            <AlertDescription>
                                دسترسی کاربران خاص - کاربران می‌توانند محدودیت‌های متفاوتی از نوع پروفایل خود داشته باشند
                            </AlertDescription>
                        </Alert>
                        <div className="text-center text-muted-foreground py-8">
                            این بخش در نسخه بعدی پیاده‌سازی خواهد شد
                        </div>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}

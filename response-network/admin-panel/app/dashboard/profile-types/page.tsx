"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { profileTypeService } from "@/lib/services/admin-api";
import type { ProfileType } from "@/lib/services/admin-api";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, AlertCircle, RefreshCw, Plus, Edit, Trash2, Shield } from "lucide-react";
import { CreateProfileTypeDialog } from "@/components/profile-types/create-profile-type-dialog";
import { EditProfileTypeDialog } from "@/components/profile-types/edit-profile-type-dialog";
import { DeleteProfileTypeDialog } from "@/components/profile-types/delete-profile-type-dialog";

export default function ProfileTypesPage() {
    const router = useRouter();
    const { user: currentUser, isLoading: authLoading } = useAuthStore();
    const [profileTypes, setProfileTypes] = useState<ProfileType[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Dialog states
    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [selectedProfileType, setSelectedProfileType] = useState<ProfileType | null>(null);

    const fetchProfileTypes = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await profileTypeService.getProfileTypes();
            setProfileTypes(data);
        } catch (error) {
            console.error("Error fetching profile types:", error);
            setError("خطا در دریافت لیست انواع پروفایل");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (!authLoading && !currentUser) {
            router.push("/login");
        } else if (!authLoading && currentUser) {
            fetchProfileTypes();
        }
    }, [authLoading, currentUser, router]);

    const handleCreateSuccess = () => {
        fetchProfileTypes();
    };

    const handleEditClick = (pt: ProfileType) => {
        setSelectedProfileType(pt);
        setEditDialogOpen(true);
    };

    const handleDeleteClick = (pt: ProfileType) => {
        setSelectedProfileType(pt);
        setDeleteDialogOpen(true);
    };

    if (authLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin" />
            </div>
        );
    }

    if (!currentUser) return null;

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            {/* Header */}
            <div className="border-b bg-white dark:bg-gray-800">
                <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <Shield className="h-8 w-8" />
                                انواع پروفایل
                            </h1>
                            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                                مدیریت سطوح دسترسی و محدودیت‌های کاربران
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <Button
                                variant="default"
                                size="sm"
                                onClick={() => setCreateDialogOpen(true)}
                            >
                                <Plus className="h-4 w-4 mr-2" />
                                ایجاد پروفایل جدید
                            </Button>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={fetchProfileTypes}
                                disabled={loading}
                            >
                                <RefreshCw className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
                {error && (
                    <Alert variant="destructive" className="mb-6">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>خطا</AlertTitle>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                <Card>
                    <CardHeader>
                        <CardTitle>لیست پروفایل‌ها</CardTitle>
                        <CardDescription>{profileTypes.length} نوع پروفایل تعریف شده</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="flex justify-center py-8">
                                <Loader2 className="h-6 w-6 animate-spin" />
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>نام</TableHead>
                                            <TableHead>توضیحات</TableHead>
                                            <TableHead>محدودیت روزانه</TableHead>
                                            <TableHead>محدودیت ماهانه</TableHead>
                                            <TableHead>وضعیت</TableHead>
                                            <TableHead>نوع</TableHead>
                                            <TableHead className="text-left">عملیات</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {profileTypes.length > 0 ? (
                                            profileTypes.map((pt) => (
                                                <TableRow key={pt.name}>
                                                    <TableCell className="font-medium">{pt.name}</TableCell>
                                                    <TableCell>{pt.description || "-"}</TableCell>
                                                    <TableCell>{pt.daily_request_limit?.toLocaleString() || "-"}</TableCell>
                                                    <TableCell>{pt.monthly_request_limit?.toLocaleString() || "-"}</TableCell>
                                                    <TableCell>
                                                        <Badge
                                                            variant={pt.is_active ? "default" : "secondary"}
                                                            className={
                                                                pt.is_active
                                                                    ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                                                                    : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
                                                            }
                                                        >
                                                            {pt.is_active ? "فعال" : "غیرفعال"}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Badge variant={pt.is_builtin ? "secondary" : "outline"}>
                                                            {pt.is_builtin ? "سیستمی" : "سفارشی"}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex gap-2 justify-end">
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => handleEditClick(pt)}
                                                            >
                                                                <Edit className="h-4 w-4" />
                                                            </Button>
                                                            {!pt.is_builtin && (
                                                                <Button
                                                                    variant="ghost"
                                                                    size="sm"
                                                                    onClick={() => handleDeleteClick(pt)}
                                                                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                                                >
                                                                    <Trash2 className="h-4 w-4" />
                                                                </Button>
                                                            )}
                                                        </div>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        ) : (
                                            <TableRow>
                                                <TableCell colSpan={7} className="text-center py-8">
                                                    <p className="text-gray-500 dark:text-gray-400">
                                                        هیچ نوع پروفایلی یافت نشد
                                                    </p>
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Dialogs */}
            <CreateProfileTypeDialog
                open={createDialogOpen}
                onOpenChange={setCreateDialogOpen}
                onSuccess={handleCreateSuccess}
            />

            <EditProfileTypeDialog
                open={editDialogOpen}
                onOpenChange={setEditDialogOpen}
                onSuccess={handleCreateSuccess}
                profileType={selectedProfileType}
            />

            <DeleteProfileTypeDialog
                open={deleteDialogOpen}
                onOpenChange={setDeleteDialogOpen}
                onSuccess={handleCreateSuccess}
                profileType={selectedProfileType}
            />
        </div>
    );
}

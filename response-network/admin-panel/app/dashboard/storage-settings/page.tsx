"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Plus, RefreshCw, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

import { workerService } from "@/lib/services/admin-api";

export default function StorageSettingsPage() {
    const router = useRouter();
    const [settings, setSettings] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await workerService.getWorkerSettings();
            setSettings(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error("Error fetching settings:", err);
            setError("خطا در دریافت تنظیمات");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="border-b bg-white dark:bg-gray-800">
                <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                    <div className="flex items-center gap-4">
                        <Button variant="ghost" size="icon" onClick={() => router.back()}>
                            <ArrowLeft className="h-5 w-5" />
                        </Button>
                        <div className="flex-1">
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                تنظیمات Storage
                            </h1>
                            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                                مدیریت پیکربندی ذخیره‌سازی برای export ها
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <Button variant="outline" size="icon" onClick={fetchSettings} disabled={loading}>
                                <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                            </Button>
                            <Button onClick={() => router.push("/dashboard/storage-settings/create")}>
                                <Plus className="h-4 w-4 mr-2" />
                                افزودن Storage
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

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
                        <CardTitle>Storage Configurations ({settings.length})</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="flex justify-center py-8">
                                <Loader2 className="h-6 w-6 animate-spin" />
                            </div>
                        ) : (
                            <div className="rounded-md border">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead className="text-right">نوع</TableHead>
                                            <TableHead className="text-right">Storage Type</TableHead>
                                            <TableHead className="text-right">توضیحات</TableHead>
                                            <TableHead className="text-center">وضعیت</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {settings.length > 0 ? (
                                            settings.map((setting) => (
                                                <TableRow key={setting.id}>
                                                    <TableCell className="font-medium">{setting.worker_type}</TableCell>
                                                    <TableCell>
                                                        <Badge variant="outline">{setting.storage_type}</Badge>
                                                    </TableCell>
                                                    <TableCell className="text-sm text-muted-foreground">
                                                        {setting.description || "-"}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <Badge variant={setting.is_active ? "default" : "secondary"}>
                                                            {setting.is_active ? "فعال" : "غیرفعال"}
                                                        </Badge>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        ) : (
                                            <TableRow>
                                                <TableCell colSpan={4} className="text-center py-8">
                                                    <p className="text-muted-foreground">هیچ تنظیماتی یافت نشد</p>
                                                    <p className="text-sm text-muted-foreground mt-2">
                                                        برای شروع یک storage configuration اضافه کنید
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

                <Alert className="mt-6">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>نکته</AlertTitle>
                    <AlertDescription>
                        این تنظیمات برای پیکربندی پیشرفته ذخیره‌سازی است. برای export های ساده از تنظیمات صفحه "Exports" استفاده کنید.
                    </AlertDescription>
                </Alert>
            </div>
        </div>
    );
}

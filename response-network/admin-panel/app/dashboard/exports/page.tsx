"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { RefreshCw, AlertCircle, Save, TestTube } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";

import { exportConfigService, type ExportConfig } from "@/lib/services/admin-api";

export default function ExportsPage() {
    const router = useRouter();
    const { user: currentUser, isLoading: authLoading } = useAuthStore();
    const [config, setConfig] = useState<ExportConfig | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [status, setStatus] = useState<{ status: string; exports?: Record<string, { total_count: number; exported_at: string | null; error?: string; file?: string }> } | null>(null);
    const [loadingStatus, setLoadingStatus] = useState(false);

    useEffect(() => {
        if (!authLoading) {
            fetchConfig();
            fetchStatus();
        }
    }, [authLoading]);

    const fetchConfig = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await exportConfigService.getExportConfig();
            setConfig(data);
        } catch (err) {
            console.error("Error fetching export config:", err);
            setError("خطا در دریافت تنظیمات خروجی");
        } finally {
            setLoading(false);
        }
    };

    const fetchStatus = async () => {
        try {
            setLoadingStatus(true);
            const data = await exportConfigService.getExportStatus();
            setStatus(data);
        } catch (err) {
            console.error("Error fetching export status:", err);
        } finally {
            setLoadingStatus(false);
        }
    };

    const handleSave = async () => {
        if (!config) return;
        try {
            setSaving(true);
            setError(null);
            await exportConfigService.updateExportConfig(config);
            setSuccess("تنظیمات با موفقیت ذخیره شد");
            setTimeout(() => setSuccess(null), 3000);
        } catch (err) {
            console.error("Error saving config:", err);
            setError("خطا در ذخیره تنظیمات");
        } finally {
            setSaving(false);
        }
    };

    const handleManualExport = async () => {
        try {
            await exportConfigService.testExports();
            setSuccess("درخواست خروجی با موفقیت ثبت شد");
            setTimeout(() => setSuccess(null), 3000);
            // Refresh status after a short delay
            setTimeout(fetchStatus, 2000);
        } catch (err) {
            console.error("Error triggering manual export:", err);
            setError("خطا در درخواست خروجی دستی");
        }
    };

    if (authLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin" />
            </div>
        );
    }

    if (!currentUser) {
        router.push("/login");
        return null;
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="border-b bg-white dark:bg-gray-800">
                <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                تنظیمات خروجی
                            </h1>
                            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                                پیکربندی سیستم خروجی داده‌ها
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <Button variant="outline" size="icon" onClick={() => { fetchConfig(); fetchStatus(); }} disabled={loading || loadingStatus}>
                                <RefreshCw className={`h-4 w-4 ${loading || loadingStatus ? "animate-spin" : ""}`} />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
                {error && (
                    <Alert variant="destructive" className="mb-6">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>خطا</AlertTitle>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {success && (
                    <Alert className="mb-6 bg-green-50 text-green-800 border-green-200">
                        <AlertDescription>{success}</AlertDescription>
                    </Alert>
                )}

                <Card>
                    <CardHeader>
                        <CardTitle>تنظیمات خروجی</CardTitle>
                        <CardDescription>پیکربندی نحوه خروجی گرفتن از داده‌های سیستم</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="flex justify-center py-8">
                                <Loader2 className="h-6 w-6 animate-spin" />
                            </div>
                        ) : config ? (
                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <Label htmlFor="enabled">فعال‌سازی خروجی خودکار</Label>
                                    <Switch
                                        id="enabled"
                                        checked={config.enabled}
                                        onCheckedChange={(checked) =>
                                            setConfig({ ...config, enabled: checked })
                                        }
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="format">فرمت خروجی</Label>
                                    <Input
                                        id="format"
                                        value={config.format}
                                        onChange={(e) => setConfig({ ...config, format: e.target.value })}
                                        placeholder="مثال: JSON, CSV, Excel"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="destination_type">نوع مقصد</Label>
                                    <select
                                        id="destination_type"
                                        className="w-full rounded-md border border-input bg-background px-3 py-2"
                                        value={config.destination_type}
                                        onChange={(e) => setConfig({ ...config, destination_type: e.target.value as 'local' | 'ftp' })}
                                    >
                                        <option value="local">محلی (Local)</option>
                                        <option value="ftp">FTP/SFTP</option>
                                    </select>
                                </div>

                                {/* Local Configuration */}
                                {config.destination_type === 'local' && (
                                    <div className="space-y-2 rounded-lg border p-4 bg-muted/50">
                                        <h3 className="font-medium text-sm">تنظیمات محلی</h3>
                                        <div>
                                            <Label htmlFor="local_path">مسیر محلی</Label>
                                            <Input
                                                id="local_path"
                                                value={config.local_path || ''}
                                                onChange={(e) => setConfig({ ...config, local_path: e.target.value })}
                                                placeholder="./exports"
                                            />
                                            <p className="text-xs text-muted-foreground mt-1">
                                                مثال: ./exports یا /var/exports
                                            </p>
                                        </div>
                                    </div>
                                )}

                                {/* FTP Configuration */}
                                {config.destination_type === 'ftp' && (
                                    <div className="space-y-4 rounded-lg border p-4 bg-muted/50">
                                        <h3 className="font-medium text-sm">تنظیمات FTP</h3>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <Label htmlFor="ftp_host">آدرس سرور</Label>
                                                <Input
                                                    id="ftp_host"
                                                    value={config.ftp_host || ''}
                                                    onChange={(e) => setConfig({ ...config, ftp_host: e.target.value })}
                                                    placeholder="ftp.example.com"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="ftp_port">پورت</Label>
                                                <Input
                                                    id="ftp_port"
                                                    type="number"
                                                    value={config.ftp_port || 21}
                                                    onChange={(e) => setConfig({ ...config, ftp_port: parseInt(e.target.value) })}
                                                    placeholder="21"
                                                />
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <Label htmlFor="ftp_username">نام کاربری</Label>
                                                <Input
                                                    id="ftp_username"
                                                    value={config.ftp_username || ''}
                                                    onChange={(e) => setConfig({ ...config, ftp_username: e.target.value })}
                                                    placeholder="username"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="ftp_password">رمز عبور</Label>
                                                <Input
                                                    id="ftp_password"
                                                    type="password"
                                                    value={config.ftp_password || ''}
                                                    onChange={(e) => setConfig({ ...config, ftp_password: e.target.value })}
                                                    placeholder="••••••••"
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <Label htmlFor="ftp_path">مسیر روی سرور</Label>
                                            <Input
                                                id="ftp_path"
                                                value={config.ftp_path || ''}
                                                onChange={(e) => setConfig({ ...config, ftp_path: e.target.value })}
                                                placeholder="/exports"
                                            />
                                        </div>

                                        <div className="flex items-center space-x-2 space-x-reverse">
                                            <Switch
                                                id="ftp_use_tls"
                                                checked={config.ftp_use_tls || false}
                                                onCheckedChange={(checked) => setConfig({ ...config, ftp_use_tls: checked })}
                                            />
                                            <Label htmlFor="ftp_use_tls">استفاده از TLS/SSL</Label>
                                        </div>
                                    </div>
                                )}

                                <div className="space-y-2">
                                    <Label htmlFor="schedule">زمان‌بندی (اختیاری)</Label>
                                    <Input
                                        id="schedule"
                                        value={config.schedule || ""}
                                        onChange={(e) => setConfig({ ...config, schedule: e.target.value })}
                                        placeholder="مثال: 0 0 * * * (هر روز نیمه‌شب)"
                                    />
                                </div>

                                <div className="flex gap-2 pt-4">
                                    <Button onClick={handleSave} disabled={saving}>
                                        {saving ? (
                                            <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                        ) : (
                                            <Save className="h-4 w-4 mr-2" />
                                        )}
                                        ذخیره تنظیمات
                                    </Button>
                                    <Button onClick={handleManualExport}>
                                        <TestTube className="h-4 w-4 mr-2" />
                                        خروجی گرفتن دستی
                                    </Button>
                                </div>
                            </div>
                        ) : (
                            <p className="text-center text-muted-foreground py-8">
                                تنظیماتی یافت نشد
                            </p>
                        )}
                    </CardContent>
                </Card>

                {/* Status Card */}
                <Card className="mt-6">
                    <CardHeader>
                        <CardTitle>وضعیت آخرین خروجی‌ها</CardTitle>
                        <CardDescription>اطلاعات مربوط به آخرین فایل‌های خروجی گرفته شده</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loadingStatus ? (
                            <div className="flex justify-center py-8">
                                <Loader2 className="h-6 w-6 animate-spin" />
                            </div>
                        ) : status && status.exports ? (
                            <div className="grid gap-4 md:grid-cols-3">
                                {Object.entries(status.exports).map(([key, value]) => (
                                    <div key={key} className="rounded-lg border p-4">
                                        <h4 className="font-semibold mb-2 capitalize">{key.replace('_', ' ')}</h4>
                                        {value.error ? (
                                            <p className="text-sm text-red-500">{value.error}</p>
                                        ) : (
                                            <div className="space-y-1 text-sm">
                                                <p><span className="text-muted-foreground">تعداد:</span> {value.total_count}</p>
                                                <p><span className="text-muted-foreground">تاریخ:</span> {value.exported_at ? new Date(value.exported_at).toLocaleString('fa-IR') : '-'}</p>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-center text-muted-foreground py-8">
                                اطلاعاتی موجود نیست
                            </p>
                        )}
                    </CardContent>
                </Card>

                {/* Storage Configurations */}
                <Card className="mt-6">
                    <CardHeader>
                        <CardTitle>تنظیمات Storage</CardTitle>
                        <p className="text-sm text-muted-foreground mt-2">
                            پیکربندی ذخیره‌سازی برای export ها (Local, FTP, S3)
                        </p>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-4 border rounded-lg">
                                <div>
                                    <h3 className="font-medium">Storage Configurations</h3>
                                    <p className="text-sm text-muted-foreground">
                                        مدیریت تنظیمات ذخیره‌سازی برای انواع مختلف export
                                    </p>
                                </div>
                                <Button
                                    onClick={() => router.push("/dashboard/storage-settings")}
                                    variant="outline"
                                >
                                    مدیریت Storage
                                </Button>
                            </div>

                            <Alert>
                                <AlertCircle className="h-4 w-4" />
                                <AlertTitle>راهنما</AlertTitle>
                                <AlertDescription>
                                    تنظیمات بالا (Destination Type) برای export های دستی است.
                                    برای تنظیمات پیشرفته storage و زمان‌بندی خودکار، از بخش "مدیریت Storage" استفاده کنید.
                                </AlertDescription>
                            </Alert>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

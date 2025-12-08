"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { RefreshCw, AlertCircle, Activity, Users, Clock, Server } from "lucide-react";
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

import { adminTasksService } from "@/lib/services/admin-api";

export default function TasksPage() {
    const router = useRouter();
    const { user: currentUser, isLoading: authLoading } = useAuthStore();
    const [queueStats, setQueueStats] = useState<any>(null);
    const [workersStats, setWorkersStats] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!authLoading) {
            fetchStats();
            const interval = setInterval(fetchStats, 10000); // 10 seconds
            return () => clearInterval(interval);
        }
    }, [authLoading]);

    const fetchStats = async () => {
        try {
            setError(null);
            const [queue, workers] = await Promise.all([
                adminTasksService.getQueueStats(),
                adminTasksService.getWorkersStats(),
            ]);
            setQueueStats(queue);
            setWorkersStats(workers);
        } catch (err) {
            console.error("Error fetching stats:", err);
            setError("خطا در دریافت آمار");
        } finally {
            setLoading(false);
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
                                مانیتورینگ Celery
                            </h1>
                            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                                وضعیت Workers و صف Tasks
                            </p>
                        </div>
                        <Button variant="outline" size="icon" onClick={fetchStats} disabled={loading}>
                            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                        </Button>
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

                {/* Stats Cards */}
                <div className="grid gap-6 md:grid-cols-3 mb-6">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Tasks در صف</CardTitle>
                            <Clock className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {queueStats?.total_queued?.toLocaleString() || 0}
                            </div>
                            <p className="text-xs text-muted-foreground">در انتظار اجرا</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Tasks فعال</CardTitle>
                            <Activity className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{queueStats?.total_active || 0}</div>
                            <p className="text-xs text-muted-foreground">در حال اجرا</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Workers فعال</CardTitle>
                            <Users className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{queueStats?.active_workers || 0}</div>
                            <p className="text-xs text-muted-foreground">آماده پردازش</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Workers Table */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Server className="h-5 w-5" />
                            Celery Workers ({workersStats.length})
                        </CardTitle>
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
                                            <TableHead className="text-right">نام Worker</TableHead>
                                            <TableHead className="text-right">نوع Pool</TableHead>
                                            <TableHead className="text-center">Concurrency</TableHead>
                                            <TableHead className="text-center">Tasks فعال</TableHead>
                                            <TableHead className="text-center">پردازش شده</TableHead>
                                            <TableHead className="text-center">وضعیت</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {workersStats.length > 0 ? (
                                            workersStats.map((worker) => (
                                                <TableRow key={worker.worker_name}>
                                                    <TableCell className="font-medium">{worker.worker_name}</TableCell>
                                                    <TableCell className="text-sm">
                                                        {worker.pool_type.split(":").pop()}
                                                    </TableCell>
                                                    <TableCell className="text-center">{worker.max_concurrency}</TableCell>
                                                    <TableCell className="text-center">{worker.active_tasks}</TableCell>
                                                    <TableCell className="text-center">
                                                        {worker.processed_tasks.toLocaleString()}
                                                    </TableCell>
                                                    <TableCell className="text-center">
                                                        <Badge variant={worker.offline ? "destructive" : "default"}>
                                                            {worker.offline ? "آفلاین" : "آنلاین"}
                                                        </Badge>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        ) : (
                                            <TableRow>
                                                <TableCell colSpan={6} className="text-center py-8">
                                                    <p className="text-muted-foreground">هیچ worker فعالی یافت نشد</p>
                                                    <p className="text-sm text-muted-foreground mt-2">
                                                        Celery worker را start کنید
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

                {/* Active Tasks */}
                {queueStats?.details && queueStats.details.length > 0 && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Tasks در حال اجرا ({queueStats.details.length})</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="rounded-md border">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead className="text-right">نام Task</TableHead>
                                            <TableHead className="text-right">Worker</TableHead>
                                            <TableHead className="text-center">وضعیت</TableHead>
                                            <TableHead className="text-right">Task ID</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {queueStats.details.map((task: any) => (
                                            <TableRow key={task.task_id}>
                                                <TableCell className="font-medium text-sm">
                                                    {task.name.split(".").pop()}
                                                </TableCell>
                                                <TableCell className="text-sm">{task.worker}</TableCell>
                                                <TableCell className="text-center">
                                                    <Badge variant="default">{task.state}</Badge>
                                                </TableCell>
                                                <TableCell className="font-mono text-xs">
                                                    {task.task_id.substring(0, 8)}...
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Info Card */}
                <Card className="mt-6 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
                    <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                            <div className="space-y-1">
                                <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                                    نکته مهم
                                </p>
                                <p className="text-sm text-blue-700 dark:text-blue-300">
                                    این صفحه فقط برای مانیتورینگ Celery workers است. برای تنظیمات export و storage به صفحه "Exports" بروید.
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}

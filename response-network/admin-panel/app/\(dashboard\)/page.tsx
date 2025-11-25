"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { healthService, statsService } from "@/lib/services/admin-api";
import type { HealthStatus, SystemStats } from "@/lib/services/admin-api";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, AlertCircle, CheckCircle2, XCircle, RefreshCw } from "lucide-react";

interface DashboardStats {
  health: HealthStatus | null;
  stats: SystemStats | null;
  loading: boolean;
  error: string | null;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout, isLoading: authLoading } = useAuthStore();
  const [dashData, setDashData] = useState<DashboardStats>({
    health: null,
    stats: null,
    loading: true,
    error: null,
  });

  // Fetch dashboard data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setDashData((prev) => ({ ...prev, loading: true, error: null }));

        // Fetch health and stats in parallel
        const [health, stats] = await Promise.all([
          healthService.getHealth(),
          statsService.getSystemStats(),
        ]);

        setDashData({
          health,
          stats,
          loading: false,
          error: null,
        });
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
        setDashData((prev) => ({
          ...prev,
          loading: false,
          error: "خطا در دریافت اطلاعات سیستم",
        }));
      }
    };

    if (!authLoading) {
      fetchData();
      // Refresh every 30 seconds
      const interval = setInterval(fetchData, 30000);
      return () => clearInterval(interval);
    }
  }, [authLoading]);

  const handleLogout = async () => {
    logout();
    router.push("/login");
  };

  const handleRefresh = async () => {
    try {
      setDashData((prev) => ({ ...prev, loading: true }));
      const [health, stats] = await Promise.all([
        healthService.getHealth(),
        statsService.getSystemStats(),
      ]);

      setDashData({
        health,
        stats,
        loading: false,
        error: null,
      });
    } catch (error) {
      setDashData((prev) => ({
        ...prev,
        loading: false,
        error: "خطا در تازه‌سازی اطلاعات",
      }));
    }
  };

  // Check auth
  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!user) {
    router.push("/login");
    return null;
  }

  const getServiceIcon = (status: string) => {
    if (status.includes("online") || status.includes("ok")) {
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    }
    if (status.includes("offline")) {
      return <XCircle className="h-4 w-4 text-red-500" />;
    }
    return <AlertCircle className="h-4 w-4 text-yellow-500" />;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b bg-white dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                داشبورد
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                خوش آمدید، {user.username}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={dashData.loading}
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                خروج
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Error Alert */}
        {dashData.error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>خطا</AlertTitle>
            <AlertDescription>{dashData.error}</AlertDescription>
          </Alert>
        )}

        {/* System Health */}
        <div className="mb-8 grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">وضعیت سیستم</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-2xl font-bold">
                  {dashData.health?.status === "ok" ? "✅" : "⚠️"}
                </span>
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {dashData.health?.status === "ok" ? "عادی" : "مشکل"}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Services Status */}
          {dashData.health && (
            <>
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">پایگاه داده</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center gap-2">
                  {getServiceIcon(dashData.health.services.database)}
                  <span className="text-sm">{dashData.health.services.database}</span>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Redis</CardTitle>
                </CardHeader>
                <CardContent className="flex items-center gap-2">
                  {getServiceIcon(dashData.health.services.redis)}
                  <span className="text-sm">{dashData.health.services.redis}</span>
                </CardContent>
              </Card>
            </>
          )}
        </Card>

        {/* Main Stats Grid */}
        {dashData.stats && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {/* Users */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">کاربران</CardTitle>
                <CardDescription>کل کاربران فعال</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{dashData.stats.users.total}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {dashData.stats.users.active} فعال
                </p>
              </CardContent>
            </Card>

            {/* Total Requests */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">درخواست‌ها</CardTitle>
                <CardDescription>کل درخواست‌ها</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{dashData.stats.requests.total}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {dashData.stats.requests.completed} تکمیل‌شده
                </p>
              </CardContent>
            </Card>

            {/* Processing */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">در حال پردازش</CardTitle>
                <CardDescription>درخواست‌های فعال</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {dashData.stats.requests.processing}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  فعال
                </p>
              </CardContent>
            </Card>

            {/* Failed */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">ناموفق</CardTitle>
                <CardDescription>درخواست‌های ناموفق</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">
                  {dashData.stats.requests.failed}
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  خطا
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Request Status Breakdown */}
        {dashData.stats && (
          <div className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>تفکیک درخواست‌ها</CardTitle>
                <CardDescription>وضعیت درخواست‌های سیستم</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Pending */}
                  <div className="flex items-center justify-between">
                    <span className="font-medium">در انتظار</span>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-40 bg-gray-200 rounded">
                        <div
                          className="h-2 bg-yellow-500 rounded"
                          style={{
                            width:
                              dashData.stats.requests.total > 0
                                ? `${(dashData.stats.requests.total - dashData.stats.requests.processing - dashData.stats.requests.completed - dashData.stats.requests.failed) / dashData.stats.requests.total * 100}%`
                                : "0%",
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">
                        {dashData.stats.requests.total -
                          dashData.stats.requests.processing -
                          dashData.stats.requests.completed -
                          dashData.stats.requests.failed}
                      </span>
                    </div>
                  </div>

                  {/* Processing */}
                  <div className="flex items-center justify-between">
                    <span className="font-medium">در حال پردازش</span>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-40 bg-gray-200 rounded">
                        <div
                          className="h-2 bg-blue-500 rounded"
                          style={{
                            width:
                              dashData.stats.requests.total > 0
                                ? `${(dashData.stats.requests.processing / dashData.stats.requests.total) * 100}%`
                                : "0%",
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">
                        {dashData.stats.requests.processing}
                      </span>
                    </div>
                  </div>

                  {/* Completed */}
                  <div className="flex items-center justify-between">
                    <span className="font-medium">تکمیل‌شده</span>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-40 bg-gray-200 rounded">
                        <div
                          className="h-2 bg-green-500 rounded"
                          style={{
                            width:
                              dashData.stats.requests.total > 0
                                ? `${(dashData.stats.requests.completed / dashData.stats.requests.total) * 100}%`
                                : "0%",
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">
                        {dashData.stats.requests.completed}
                      </span>
                    </div>
                  </div>

                  {/* Failed */}
                  <div className="flex items-center justify-between">
                    <span className="font-medium">ناموفق</span>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-40 bg-gray-200 rounded">
                        <div
                          className="h-2 bg-red-500 rounded"
                          style={{
                            width:
                              dashData.stats.requests.total > 0
                                ? `${(dashData.stats.requests.failed / dashData.stats.requests.total) * 100}%`
                                : "0%",
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">
                        {dashData.stats.requests.failed}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Database Size */}
        {dashData.stats && (
          <div className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>اطلاعات سیستم</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      حجم پایگاه داده
                    </p>
                    <p className="text-2xl font-bold mt-1">{dashData.stats.database.size}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                      کل نتایج
                    </p>
                    <p className="text-2xl font-bold mt-1">{dashData.stats.results.total}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

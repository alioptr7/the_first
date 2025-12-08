"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { cacheService, statsService } from "@/lib/services/admin-api";
import type { CacheStats } from "@/lib/services/admin-api";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Loader2,
  AlertCircle,
  RefreshCw,
  Trash2,
  Zap,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

interface CacheState {
  stats: CacheStats | null;
  loading: boolean;
  error: string | null;
  actionLoading: false | "clear" | "optimize";
  success: string | null;
}

export default function CachePage() {
  const router = useRouter();
  const { user: currentUser, isLoading: authLoading } = useAuthStore();
  const [state, setState] = useState<CacheState>({
    stats: null,
    loading: true,
    error: null,
    actionLoading: false,
    success: null,
  });

  // Fetch cache stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const data = await statsService.getCacheStats();
        setState((prev) => ({
          ...prev,
          stats: data,
          loading: false,
        }));
      } catch {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: "خطا در دریافت آمار کش",
        }));
      }
    };

    if (!authLoading) {
      fetchStats();
      // Refresh every 30 seconds
      const interval = setInterval(fetchStats, 30000);
      return () => clearInterval(interval);
    }
  }, [authLoading]);

  const handleClearCache = async () => {
    try {
      setState((prev) => ({ ...prev, actionLoading: "clear", error: null }));
      await cacheService.clearCache();
      setState((prev) => ({
        ...prev,
        actionLoading: false,
        success: "کش با موفقیت پاک شد",
      }));
      // Refresh stats
      setTimeout(() => {
        const fetchStats = async () => {
          const data = await statsService.getCacheStats();
          setState((prev) => ({
            ...prev,
            stats: data,
            success: null,
          }));
        };
        fetchStats();
      }, 1000);
    } catch {
      setState((prev) => ({
        ...prev,
        actionLoading: false,
        error: "خطا در پاک کردن کش",
      }));
    }
  };

  const handleOptimizeCache = async () => {
    try {
      setState((prev) => ({ ...prev, actionLoading: "optimize", error: null }));
      await cacheService.optimizeCache();
      setState((prev) => ({
        ...prev,
        actionLoading: false,
        success: "کش با موفقیت بهینه شد",
      }));
      // Refresh stats
      setTimeout(() => {
        const fetchStats = async () => {
          const data = await statsService.getCacheStats();
          setState((prev) => ({
            ...prev,
            stats: data,
            success: null,
          }));
        };
        fetchStats();
      }, 1000);
    } catch {
      setState((prev) => ({
        ...prev,
        actionLoading: false,
        error: "خطا در بهینه‌سازی کش",
      }));
    }
  };

  const handleRefresh = async () => {
    try {
      setState((prev) => ({ ...prev, loading: true }));
      const data = await statsService.getCacheStats();
      setState((prev) => ({
        ...prev,
        stats: data,
        loading: false,
      }));
    } catch {
      setState((prev) => ({
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

  if (!currentUser) {
    router.push("/login");
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b bg-white dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                کش و بهینه‌سازی
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                مدیریت کش و بهینه‌سازی سیستم
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={state.loading}
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Error Alert */}
        {state.error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>خطا</AlertTitle>
            <AlertDescription>{state.error}</AlertDescription>
          </Alert>
        )}

        {/* Success Alert */}
        {state.success && (
          <Alert className="mb-6 bg-green-50 dark:bg-green-900 border-green-200 dark:border-green-800">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertTitle className="text-green-900 dark:text-green-200">
              موفقیت
            </AlertTitle>
            <AlertDescription className="text-green-800 dark:text-green-300">
              {state.success}
            </AlertDescription>
          </Alert>
        )}

        {/* Action Buttons */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>عملیات کش</CardTitle>
            <CardDescription>مدیریت و بهینه‌سازی کش سیستم</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3 flex-col sm:flex-row">
              <Button
                onClick={handleClearCache}
                disabled={state.actionLoading !== false}
                variant="destructive"
                className="gap-2"
              >
                {state.actionLoading === "clear" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
                پاک کردن کش
              </Button>

              <Button
                onClick={handleOptimizeCache}
                disabled={state.actionLoading !== false}
                className="gap-2"
              >
                {state.actionLoading === "optimize" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Zap className="h-4 w-4" />
                )}
                بهینه‌سازی کش
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Cache Stats */}
        {state.stats && (
          <>
            {/* Main Stats */}
            <div className="grid gap-4 md:grid-cols-3 mb-6">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">اندازه کش</CardTitle>
                  <CardDescription>حجم کل کش</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{state.stats.size}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">موارد کش</CardTitle>
                  <CardDescription>تعداد کل موارد</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{state.stats.items}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">نرخ استفاده</CardTitle>
                  <CardDescription>درصد استفاده شده</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-blue-600">
                    {state.stats.hit_rate}%
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Stats */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>آمار دقیق کش</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Hits */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">موفقیت‌های کش (Hits)</span>
                      <span className="text-2xl font-bold text-green-600">
                        {state.stats.hits}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      تعداد دفعاتی که داده از کش دریافت شده است
                    </p>
                  </div>

                  {/* Misses */}
                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">عدم موفقیت‌های کش (Misses)</span>
                      <span className="text-2xl font-bold text-yellow-600">
                        {state.stats.misses}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      تعداد دفعاتی که داده در کش نبوده است
                    </p>
                  </div>

                  {/* Memory Usage */}
                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">حافظه استفاده شده</span>
                      <span className="text-2xl font-bold text-blue-600">
                        {state.stats.memory_used}
                      </span>
                    </div>
                    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-3 bg-blue-500"
                        style={{
                          width: `${(parseInt(state.stats.memory_used) / (parseInt(state.stats.memory_used) + 100)) * 100}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Memory Limit */}
                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium">حد حافظه</span>
                      <span className="text-lg font-bold">
                        {state.stats.memory_limit}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>معیارهای کارایی</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Hit Rate */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">نرخ موفقیت</span>
                      <div className="flex items-center gap-1 text-green-600">
                        <CheckCircle2 className="h-4 w-4" />
                        <span className="font-bold">{state.stats.hit_rate}%</span>
                      </div>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-2 bg-green-500"
                        style={{ width: `${state.stats.hit_rate}%` }}
                      />
                    </div>
                  </div>

                  {/* Eviction Rate */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">نرخ حذف</span>
                      <span className="font-bold">{state.stats.eviction_rate}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-2 bg-yellow-500"
                        style={{ width: `${state.stats.eviction_rate}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* Status */}
                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-800">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <p className="font-medium text-blue-900 dark:text-blue-200">
                        اطلاعات کش
                      </p>
                      <p className="text-sm text-blue-800 dark:text-blue-300 mt-1">
                        {state.stats.status}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {/* Loading State */}
        {state.loading && (
          <Card>
            <CardContent className="flex justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin" />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

"use client";

import { useAuthStore } from "@/lib/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { statsService, requestService } from "@/lib/services/admin-api";
import type { SystemStats, Request as ApiRequest } from "@/lib/services/admin-api";
import { Loader2 } from "lucide-react";

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [recentRequests, setRecentRequests] = useState<ApiRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch system stats
        const stats = await statsService.getSystemStats();
        setSystemStats(stats);

        // Fetch recent requests
        const requests = await requestService.getRecentRequests(5);
        setRecentRequests(requests);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">خوش آمدید، {user?.username}!</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Response Network Admin Panel
          </p>
        </div>
        <Button variant="outline" onClick={handleLogout}>
          خروج
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>اطلاعات کاربری</CardTitle>
            <CardDescription>جزئیات حساب کاربری شما</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="font-medium">نام کاربری:</span>
                <span>{user?.username}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">ایمیل:</span>
                <span>{user?.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">نقش:</span>
                <span className="capitalize">{user?.role === "admin" ? "مدیر" : "کاربر عادی"}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>آمار سیستم</CardTitle>
            <CardDescription>وضعیت کلی سرویس‌ها</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : systemStats ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>کل کاربران:</span>
                  <span className="font-bold">{systemStats.users?.total || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>کاربران فعال:</span>
                  <span className="font-bold text-green-600">{systemStats.users?.active || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span>درخواست‌های کل:</span>
                  <span className="font-bold">{systemStats.requests?.total || 0}</span>
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-600">خطا در بارگذاری</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>کارهای اخیر</CardTitle>
            <CardDescription>آخرین فعالیت‌های سیستم</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : recentRequests.length > 0 ? (
              <div className="space-y-2">
                {recentRequests.slice(0, 3).map((req, idx) => (
                  <div key={idx} className="text-sm border-b pb-2 last:border-0">
                    <div className="flex justify-between">
                      <span className="text-gray-600">درخواست #{req.id?.slice(0, 8)}</span>
                      <span className={`font-medium ${req.status === 'completed' ? 'text-green-600' :
                        req.status === 'failed' ? 'text-red-600' :
                          'text-yellow-600'
                        }`}>
                        {req.status === 'completed' ? 'تکمیل شده' :
                          req.status === 'failed' ? 'ناموفق' :
                            req.status === 'processing' ? 'در حال پردازش' : 'در انتظار'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-600">فعالیتی یافت نشد</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

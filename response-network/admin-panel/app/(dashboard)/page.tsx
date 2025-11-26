"use client";

import { useAuthStore } from "@/lib/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

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
            <p className="text-sm text-gray-600">در حال بارگذاری...</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>کارهای اخیر</CardTitle>
            <CardDescription>آخرین فعالیت‌های سیستم</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">در حال بارگذاری...</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

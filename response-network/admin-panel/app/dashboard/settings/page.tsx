"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useTheme } from "next-themes";
import { Loader2, CheckCircle2, Save } from "lucide-react";

interface SettingsState {
  autoRefresh: boolean;
  refreshInterval: string;
  notifications: boolean;
  theme: "light" | "dark" | "system";
  loading: boolean;
  saved: boolean;
}

export default function SettingsPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const [state, setState] = useState<SettingsState>({
    autoRefresh: true,
    refreshInterval: "30",
    notifications: true,
    theme: "system",
    loading: false,
    saved: false,
  });
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Load settings from localStorage
    const saved = localStorage.getItem("admin-settings");
    if (saved) {
      try {
        const settings = JSON.parse(saved);
        setState((prev) => ({
          ...prev,
          ...settings,
          theme: theme as "light" | "dark" | "system",
        }));
      } catch (e) {
        console.error("Error loading settings:", e);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const handleSave = async () => {
    try {
      setState((prev) => ({ ...prev, loading: true }));
      // Save to localStorage
      localStorage.setItem(
        "admin-settings",
        JSON.stringify({
          autoRefresh: state.autoRefresh,
          refreshInterval: state.refreshInterval,
          notifications: state.notifications,
        })
      );
      // Update theme
      setTheme(state.theme);
      setState((prev) => ({ ...prev, loading: false, saved: true }));
      // Reset saved message after 3 seconds
      setTimeout(() => {
        setState((prev) => ({ ...prev, saved: false }));
      }, 3000);
    } catch (error) {
      console.error("Error saving settings:", error);
      setState((prev) => ({ ...prev, loading: false }));
    }
  };

  // Check auth
  if (!mounted || authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b bg-white dark:bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            تنظیمات
          </h1>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
            مدیریت تنظیمات پنل ادمین
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Success Message */}
        {state.saved && (
          <Alert className="mb-6 bg-green-50 dark:bg-green-900 border-green-200 dark:border-green-800">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertTitle className="text-green-900 dark:text-green-200">
              موفقیت
            </AlertTitle>
            <AlertDescription className="text-green-800 dark:text-green-300">
              تنظیمات با موفقیت ذخیره شد
            </AlertDescription>
          </Alert>
        )}

        {/* Display Settings */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>تنظیمات نمایش</CardTitle>
            <CardDescription>تنظیمات رابط کاربری</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Theme */}
            <div className="space-y-3">
              <Label htmlFor="theme">پوسته</Label>
              <Select
                value={state.theme}
                onValueChange={(value: string) =>
                  setState((prev) => ({
                    ...prev,
                    theme: value as "light" | "dark" | "system",
                  }))
                }
              >
                <SelectTrigger id="theme">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">روشن</SelectItem>
                  <SelectItem value="dark">تیره</SelectItem>
                  <SelectItem value="system">سیستمی</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                انتخاب پوسته برای پنل ادمین
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Data Refresh Settings */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>تنظیمات تازه‌سازی داده‌ها</CardTitle>
            <CardDescription>تنظیم چگونگی به‌روزرسانی اطلاعات</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Auto Refresh Toggle */}
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="auto-refresh">تازه‌سازی خودکار</Label>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  به‌طور خودکار اطلاعات را تازه کن
                </p>
              </div>
              <Switch
                id="auto-refresh"
                checked={state.autoRefresh}
                onCheckedChange={(checked: boolean) =>
                  setState((prev) => ({ ...prev, autoRefresh: checked }))
                }
              />
            </div>

            {/* Refresh Interval */}
            {state.autoRefresh && (
              <div className="space-y-3">
                <Label htmlFor="refresh-interval">بازه زمانی تازه‌سازی (ثانیه)</Label>
                <Select value={state.refreshInterval} onValueChange={(value: string) =>
                  setState((prev) => ({ ...prev, refreshInterval: value }))
                }>
                  <SelectTrigger id="refresh-interval">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="10">10 ثانیه</SelectItem>
                    <SelectItem value="30">30 ثانیه</SelectItem>
                    <SelectItem value="60">1 دقیقه</SelectItem>
                    <SelectItem value="300">5 دقیقه</SelectItem>
                    <SelectItem value="600">10 دقیقه</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  هر {state.refreshInterval} ثانیه اطلاعات تازه می‌شود
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>تنظیمات اطلاع‌رسانی</CardTitle>
            <CardDescription>دریافت اطلاع‌رسانی‌های سیستم</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="notifications">اطلاع‌رسانی‌ها</Label>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  دریافت اطلاع‌رسانی برای رویدادهای مهم
                </p>
              </div>
              <Switch
                id="notifications"
                checked={state.notifications}
                onCheckedChange={(checked: boolean) =>
                  setState((prev) => ({ ...prev, notifications: checked }))
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Account Settings */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>تنظیمات حساب</CardTitle>
            <CardDescription>اطلاعات حساب کاربری شما</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm text-gray-600 dark:text-gray-400">
                نام کاربری
              </Label>
              <p className="mt-1 text-lg font-medium">{user.username}</p>
            </div>
            <div>
              <Label className="text-sm text-gray-600 dark:text-gray-400">
                ایمیل
              </Label>
              <p className="mt-1 text-lg font-medium">{user.email}</p>
            </div>
            <div>
              <Label className="text-sm text-gray-600 dark:text-gray-400">
                نقش
              </Label>
              <p className="mt-1 text-lg font-medium">
                {user.role === "admin" ? "مدیر" : "کاربر عادی"}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex gap-3">
          <Button
            onClick={handleSave}
            disabled={state.loading}
            size="lg"
            className="gap-2"
          >
            {state.loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            ذخیره تنظیمات
          </Button>
        </div>
      </div>
    </div>
  );
}

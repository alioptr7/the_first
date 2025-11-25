"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { userService } from "@/lib/services/admin-api";
import type { User } from "@/lib/services/admin-api";

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
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2, AlertCircle, RefreshCw, Search, ArrowUpDown } from "lucide-react";

interface UsersState {
  users: User[];
  loading: boolean;
  error: string | null;
  searchTerm: string;
  sortBy: "name" | "email" | "created" | "role";
  sortOrder: "asc" | "desc";
}

export default function UsersPage() {
  const router = useRouter();
  const { user: currentUser, isLoading: authLoading } = useAuthStore();
  const [state, setState] = useState<UsersState>({
    users: [],
    loading: true,
    error: null,
    searchTerm: "",
    sortBy: "created",
    sortOrder: "desc",
  });

  // Fetch users
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const data = await userService.getUsers();
        setState((prev) => ({
          ...prev,
          users: data.users,
          loading: false,
        }));
      } catch (error) {
        console.error("Error fetching users:", error);
        setState((prev) => ({
          ...prev,
          loading: false,
          error: "خطا در دریافت لیست کاربران",
        }));
      }
    };

    if (!authLoading) {
      fetchUsers();
    }
  }, [authLoading]);

  // Filter and sort users
  const filteredUsers = state.users
    .filter(
      (user) =>
        user.username.includes(state.searchTerm) ||
        user.email.includes(state.searchTerm)
    )
    .sort((a, b) => {
      let aValue, bValue;

      switch (state.sortBy) {
        case "name":
          aValue = a.username.toLowerCase();
          bValue = b.username.toLowerCase();
          break;
        case "email":
          aValue = a.email.toLowerCase();
          bValue = b.email.toLowerCase();
          break;
        case "created":
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case "role":
          aValue = a.role;
          bValue = b.role;
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return state.sortOrder === "asc" ? -1 : 1;
      if (aValue > bValue) return state.sortOrder === "asc" ? 1 : -1;
      return 0;
    });

  const handleRefresh = async () => {
    try {
      setState((prev) => ({ ...prev, loading: true }));
      const data = await userService.getUsers();
      setState((prev) => ({
        ...prev,
        users: data.users,
        loading: false,
      }));
    } catch (error) {
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
                کاربران
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                مدیریت و نظارت بر کاربران سیستم
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

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-3 mb-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">کل کاربران</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{state.users.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">کاربران فعال</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {state.users.filter((u) => u.is_active).length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">مدیران</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {state.users.filter((u) => u.role === "admin").length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Sort */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>جستجو و فیلتر</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="جستجو بر اساس نام یا ایمیل"
                  value={state.searchTerm}
                  onChange={(e) =>
                    setState((prev) => ({ ...prev, searchTerm: e.target.value }))
                  }
                  className="pl-10"
                />
              </div>

              <div className="flex gap-1">
                {(["name", "email", "created", "role"] as const).map((sort) => (
                  <Button
                    key={sort}
                    variant={state.sortBy === sort ? "default" : "outline"}
                    size="sm"
                    onClick={() => {
                      if (state.sortBy === sort) {
                        setState((prev) => ({
                          ...prev,
                          sortOrder: prev.sortOrder === "asc" ? "desc" : "asc",
                        }));
                      } else {
                        setState((prev) => ({
                          ...prev,
                          sortBy: sort,
                          sortOrder: "desc",
                        }));
                      }
                    }}
                  >
                    {sort === "name" && "نام"}
                    {sort === "email" && "ایمیل"}
                    {sort === "created" && "تاریخ"}
                    {sort === "role" && "نقش"}
                    {state.sortBy === sort && (
                      <ArrowUpDown className="h-3 w-3 ml-1" />
                    )}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Users Table */}
        <Card>
          <CardHeader>
            <CardTitle>لیست کاربران</CardTitle>
            <CardDescription>{filteredUsers.length} کاربر</CardDescription>
          </CardHeader>
          <CardContent>
            {state.loading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>نام کاربری</TableHead>
                      <TableHead>ایمیل</TableHead>
                      <TableHead>نقش</TableHead>
                      <TableHead>وضعیت</TableHead>
                      <TableHead>تاریخ ثبت</TableHead>
                      <TableHead>آخرین دسترسی</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.length > 0 ? (
                      filteredUsers.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell className="font-medium">
                            {user.username}
                          </TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                user.role === "admin" ? "default" : "secondary"
                              }
                            >
                              {user.role === "admin" ? "مدیر" : "کاربر عادی"}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={user.is_active ? "default" : "secondary"}
                              className={
                                user.is_active
                                  ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                                  : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
                              }
                            >
                              {user.is_active ? "فعال" : "غیرفعال"}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(user.created_at).toLocaleDateString("fa-IR")}
                          </TableCell>
                          <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                            {user.last_login
                              ? new Date(user.last_login).toLocaleDateString(
                                  "fa-IR"
                                )
                              : "هرگز"}
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-8">
                          <p className="text-gray-500 dark:text-gray-400">
                            کاربری یافت نشد
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
    </div>
  );
}

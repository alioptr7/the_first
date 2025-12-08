"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/stores/auth-store";
import { requestService } from "@/lib/services/admin-api";
import type { Request } from "@/lib/services/admin-api";

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
import { Loader2, AlertCircle, RefreshCw, Search } from "lucide-react";

interface RequestsState {
  requests: Request[];
  loading: boolean;
  error: string | null;
  searchTerm: string;
  statusFilter: "all" | "pending" | "processing" | "completed" | "failed";
}

export default function RequestsPage() {
  const router = useRouter();
  const { user: currentUser, isLoading: authLoading } = useAuthStore();
  const [state, setState] = useState<RequestsState>({
    requests: [],
    loading: true,
    error: null,
    searchTerm: "",
    statusFilter: "all",
  });

  // Fetch requests
  useEffect(() => {
    const fetchRequests = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const data = await requestService.getRecentRequests();
        setState((prev) => ({
          ...prev,
          requests: data,
          loading: false,
        }));
      } catch (error) {
        console.error("Error fetching requests:", error);
        setState((prev) => ({
          ...prev,
          loading: false,
          error: "خطا در دریافت لیست درخواست‌ها",
        }));
      }
    };

    if (!authLoading) {
      fetchRequests();
    }
  }, [authLoading]);

  // Filter requests
  const filteredRequests = state.requests.filter((req) => {
    const matchesSearch =
      req.id.includes(state.searchTerm) ||
      req.user_id.includes(state.searchTerm);
    const matchesStatus =
      state.statusFilter === "all" || req.status === state.statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleRefresh = async () => {
    try {
      setState((prev) => ({ ...prev, loading: true }));
      const data = await requestService.getRecentRequests();
      setState((prev) => ({
        ...prev,
        requests: Array.isArray(data) ? data : (data.requests || []),
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

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "completed":
        return "default";
      case "failed":
        return "destructive";
      case "processing":
        return "secondary";
      default:
        return "outline";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "pending":
        return "در انتظار";
      case "processing":
        return "در حال پردازش";
      case "completed":
        return "تکمیل‌شده";
      case "failed":
        return "ناموفق";
      default:
        return status;
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
                درخواست‌ها
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                نظارت و مدیریت درخواست‌های سیستم
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
        <div className="grid gap-4 md:grid-cols-4 mb-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">کل درخواست‌ها</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{state.requests.length}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">در انتظار</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">
                {state.requests.filter((r) => r.status === "pending").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">در حال پردازش</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {state.requests.filter((r) => r.status === "processing").length}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">ناموفق</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {state.requests.filter((r) => r.status === "failed").length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>جستجو و فیلتر</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2 flex-col sm:flex-row">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="جستجو بر اساس ID یا کاربر"
                  value={state.searchTerm}
                  onChange={(e) =>
                    setState((prev) => ({ ...prev, searchTerm: e.target.value }))
                  }
                  className="pl-10"
                />
              </div>

              <div className="flex gap-1 flex-wrap">
                {(["all", "pending", "processing", "completed", "failed"] as const).map(
                  (status) => (
                    <Button
                      key={status}
                      variant={state.statusFilter === status ? "default" : "outline"}
                      size="sm"
                      onClick={() =>
                        setState((prev) => ({
                          ...prev,
                          statusFilter: status,
                        }))
                      }
                    >
                      {status === "all" && "همه"}
                      {status === "pending" && "در انتظار"}
                      {status === "processing" && "پردازش"}
                      {status === "completed" && "تکمیل"}
                      {status === "failed" && "ناموفق"}
                    </Button>
                  )
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Requests Table */}
        <Card>
          <CardHeader>
            <CardTitle>لیست درخواست‌ها</CardTitle>
            <CardDescription>{filteredRequests.length} درخواست</CardDescription>
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
                      <TableHead>ID درخواست</TableHead>
                      <TableHead>کاربر</TableHead>
                      <TableHead>وضعیت</TableHead>
                      <TableHead>تاریخ ایجاد</TableHead>
                      <TableHead>آخرین به‌روز رسانی</TableHead>
                      <TableHead>پیش‌رفت</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredRequests.length > 0 ? (
                      filteredRequests.map((request) => (
                        <TableRow key={request.id}>
                          <TableCell className="font-mono text-sm">
                            {request.id.substring(0, 8)}...
                          </TableCell>
                          <TableCell>{request.user_id.substring(0, 8)}...</TableCell>
                          <TableCell>
                            <Badge variant={getStatusBadgeVariant(request.status)}>
                              {getStatusLabel(request.status)}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(request.created_at).toLocaleDateString("fa-IR", {
                              year: "numeric",
                              month: "2-digit",
                              day: "2-digit",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </TableCell>
                          <TableCell className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(request.updated_at).toLocaleDateString("fa-IR", {
                              year: "numeric",
                              month: "2-digit",
                              day: "2-digit",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </TableCell>
                          <TableCell>
                            <span className="text-xs text-gray-500">
                              {new Date(request.created_at).toLocaleDateString("fa-IR")}
                            </span>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center py-8">
                          <p className="text-gray-500 dark:text-gray-400">
                            درخواستی یافت نشد
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

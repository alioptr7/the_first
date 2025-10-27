"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { z } from "zod";

import api from "../api";
import { loginFormSchema } from "../types";



import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";

// Form validation schema
type FormSchema = z.infer<typeof loginFormSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<FormSchema>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      username: "admin@example.com",
      password: "",
    },
  });

  async function onSubmit(values: FormSchema) {
    setIsLoading(true);
    setError(null);

    try {
      // Create URLSearchParams for x-www-form-urlencoded format
      const formData = new URLSearchParams();
      formData.append("username", values.username);
      formData.append("password", values.password);

      console.log("Attempting login request...");
      const response = await api.post("/auth/login", formData);
      
      console.log("Login successful:", response.status);
      router.push("/");
      router.refresh();
    } catch (error: unknown) {
      console.error("Login error:", {
        error,
        type: error?.constructor?.name,
        keys: error && typeof error === 'object' ? Object.keys(error) : null
      });

      // Type guard for AxiosError
      const isAxiosError = (err: unknown): err is import('axios').AxiosError<{ detail?: string }> => {
        return typeof err === 'object' && err !== null && 'isAxiosError' in err;
      };

      if (isAxiosError(error)) {
        if (error.response) {
          // Server responded with error
          const status = error.response.status;
          const detail = error.response.data?.detail;
            
          if (status === 401) {
            setError(detail || "نام کاربری یا رمز عبور اشتباه است");
          } else {
            setError(detail || "خطای سرور: لطفا دوباره تلاش کنید");
          }
        } else if (error.request) {
          // Network error - request made but no response received
          console.error("Network error:", error.message);
          setError("خطا در ارتباط با سرور: لطفا اتصال اینترنت و VPN خود را بررسی کنید");
        } else {
          // Error in request setup
          console.error("Request setup error:", error.message);
          setError("خطای پیکربندی درخواست");
        }
      } else {
        console.error("Non-Axios error:", error);
        setError("خطای غیر منتظره");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="w-full max-w-sm space-y-6 rounded-lg border p-6 shadow-lg">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-bold">ورود به پنل مدیریت</h1>
          <p className="text-gray-500">لطفاً اطلاعات خود را وارد کنید</p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>خطا</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>نام کاربری</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="نام کاربری خود را وارد کنید"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>رمز عبور</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="رمز عبور خود را وارد کنید"
                      {...field}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button className="w-full" type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  در حال ورود...
                </>
              ) : (
                "ورود"
              )}
            </Button>
          </form>
        </Form>
      </div>
    </div>
  );
}
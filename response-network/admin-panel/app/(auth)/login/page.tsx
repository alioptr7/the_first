"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { useRouter } from "next/navigation";
import { useState } from "react";

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
import axios from "axios";

const formSchema = z.object({
  username: z.string().min(3, {
    message: "Username or email must be at least 3 characters.",
  }),
  password: z.string().min(6, {
    message: "Password must be at least 6 characters.",
  }),
});

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "admin@example.com",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true);
    setError(null);

    try {
      // The form data needs to be sent as `application/x-www-form-urlencoded`
      // for FastAPI's OAuth2PasswordRequestForm.
      const formData = new URLSearchParams();
      formData.append("username", values.username);
      formData.append("password", values.password);

      // Send the login request. This sets the HttpOnly cookie.
      // We use axios directly to ensure `withCredentials` is set.
      const response = await axios.post(
        // Ensure this URL is correct for your setup.
        // Using an environment variable is best practice.
        process.env.NEXT_PUBLIC_API_URL + "/auth/login",
        formData,
        {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          withCredentials: true, // Crucial for sending/receiving cookies
        }
      );

      if (response.status === 200) {
        router.push("/"); // Redirect to the dashboard
        router.refresh(); // Force a server-side refresh to apply middleware logic
      }
    } catch (err: any) {
      // --- Improved Error Handling ---
      let errorMessage = "An unexpected error occurred.";
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error("Login API Error:", err.response.data);
        if (err.response.status === 401) {
          // Specifically handle 401 Unauthorized errors
          errorMessage = err.response.data.detail || "Incorrect username or password.";
        } else {
          // Handle other server errors (e.g., 500, 404)
          errorMessage = `Server error: ${err.response.status}. ${err.response.data.detail || ''}`;
        }
      } else if (err.request) {
        // The request was made but no response was received
        console.error("Login Network Error:", err.request);
        errorMessage = "Network error. Could not connect to the server.";
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error("Login Setup Error:", err.message);
        errorMessage = `An error occurred: ${err.message}`;
      }
      setError(errorMessage);
      setIsLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-full max-w-md p-8 space-y-6 bg-card rounded-lg shadow-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Admin Login</h1>
          <p className="text-muted-foreground">Response Network Monitoring</p>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Login Failed</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Username or Email</FormLabel>
                  <FormControl>
                    <Input placeholder="admin@example.com" {...field} />
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
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="••••••••" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isLoading ? "Logging in..." : "Login"}
            </Button>
          </form>
        </Form>
      </div>
    </div>
  );
}
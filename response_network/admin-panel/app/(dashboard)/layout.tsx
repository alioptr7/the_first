import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard - Response Network Admin",
  description: "Admin panel for Response Network monitoring and management",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {children}
    </div>
  );
}

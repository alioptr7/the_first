import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // 1. Get the access token cookie
  const accessToken = request.cookies.get("access_token")?.value;

  // 2. Define public and protected paths
  const { pathname } = request.nextUrl;
  const isAuthPage = pathname.startsWith("/login");

  // 3. Redirect logic
  if (isAuthPage) {
    // If the user is on the login page but is already authenticated,
    // redirect them to the dashboard.
    if (accessToken) {
      return NextResponse.redirect(new URL("/", request.url));
    }
  } else {
    // If the user is trying to access a protected page without being authenticated,
    // redirect them to the login page.
    if (!accessToken) {
      // We can add the original path as a query param to redirect back after login
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // If none of the above conditions are met, allow the request to proceed.
  return NextResponse.next();
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
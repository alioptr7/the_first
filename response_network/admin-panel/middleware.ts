import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function middleware(request: NextRequest) {
  // 1. Get the access token cookie
  const accessToken = request.cookies.get("access_token");

  // 2. Define public and protected paths
  const { pathname } = request.nextUrl;
  const isAuthPage = pathname.startsWith("/login") || pathname.startsWith("/register");

  // 3. Redirect logic
  if (isAuthPage) {
    // If the user is on an auth page but is already authenticated,
    // redirect them to the dashboard.
    if (accessToken) {
      return NextResponse.redirect(new URL("/", request.url));
    }
  } else {
    // If the user is trying to access a protected page without being authenticated,
    // redirect them to the login page, preserving the intended destination.
    if (!accessToken) {
      const loginUrl = new URL("/login", request.url);
      return NextResponse.redirect(loginUrl);
    }
  }

  // If the request is valid, allow it to proceed.
  return NextResponse.next();
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // مسیرهای عمومی که نیاز به authentication ندارند
  const publicPaths = ['/login', '/forgot-password'];
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path));

  // بررسی وجود توکن در cookie
  const token = request.cookies.get('access_token');

  // اگر کاربر لاگین نیست و در مسیر محافظت‌شده است، به login منتقل می‌شود
  if (!token && !isPublicPath) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // اگر کاربر لاگین است و در صفحه login است، به dashboard منتقل می‌شود
  if (token && isPublicPath) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

// تنظیم مسیرهایی که middleware روی آن‌ها اجرا می‌شود
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};

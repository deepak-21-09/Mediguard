import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Route protection middleware.
 *
 * Protected routes: /dashboard and everything under it.
 * Auth signal: the presence of an "auth_token" cookie set by the sign-in flow.
 *
 * If an unauthenticated request hits a protected route it is redirected to
 * /sign-in with a `?redirect=<original-path>` param so the user lands back
 * where they intended after signing in.
 */
const PROTECTED_PREFIX = "/dashboard";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Only apply to dashboard routes
  if (!pathname.startsWith(PROTECTED_PREFIX)) {
    return NextResponse.next();
  }

  const token = request.cookies.get("auth_token")?.value;

  if (!token) {
    const signIn = new URL("/sign-in", request.url);
    signIn.searchParams.set("redirect", pathname);
    return NextResponse.redirect(signIn);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*"],
};

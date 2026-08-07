/** @type {import('next').NextConfig} */
const nextConfig = {
  // Required for the Docker standalone build (copies only the minimal runtime
  // output into .next/standalone so the production image stays small).
  output: 'standalone',
  images: {
    domains: ["img.clerk.com", "images.clerk.dev"],
  },
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  agentRules: false,
  webpack(config) {
    config.watchOptions = {
      ...config.watchOptions,
      ignored: [
        "**/.venv/**",
        "**/outputs/**",
        "**/work/**",
        "**/.runtime/**",
        "**/node_modules/**",
      ],
      poll: 1500,
    };
    return config;
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.BACKEND_URL ?? "http://127.0.0.1:8000"}/api/:path*`,
      },
    ];
  },
};
export default nextConfig;

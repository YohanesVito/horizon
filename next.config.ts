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
};
export default nextConfig;

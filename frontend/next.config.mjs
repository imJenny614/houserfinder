/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.propertyguru.com.sg" },
      { protocol: "https", hostname: "**.99.co" },
      { protocol: "https", hostname: "**.edgeprop.sg" },
    ],
  },
};

export default nextConfig;

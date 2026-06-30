/** @type {import('next').NextConfig} */
const repoName = 'Jan-Hit';
const isGithubActions = process.env.GITHUB_ACTIONS === 'true';

const nextConfig = {
  output: 'export',
  basePath: isGithubActions ? `/${repoName}` : '',
  assetPrefix: isGithubActions ? `/${repoName}/` : '',
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: { unoptimized: true },
};

module.exports = nextConfig;

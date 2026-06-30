import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'JanHit — Welfare Delivery for Frontline Workers',
  description: 'Helping Gram Sevaks, CSC Operators, and NGO field workers deliver welfare benefits to citizens.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-janhit-gray text-gray-900">{children}</body>
    </html>
  );
}

import './globals.css';
import Navbar from '@/components/Navbar';
import DegradedModeBanner from '@/components/DegradedModeBanner';

export const metadata = {
  title: 'GigBid - Autonomous Freelance Bidding Platform',
  description: 'AI-4016 R&D Assignment Multi-Agent System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col">
        <DegradedModeBanner />
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">{children}</main>
      </body>
    </html>
  );
}


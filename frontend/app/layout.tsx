import '@/app/global.css'; 
export const metadata = {
  title: 'RecruiteIQ AI',
  description: 'AI Resume Reviewer & Matcher',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
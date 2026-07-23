import "./globals.css";

export const metadata = {
  title: "Climb",
  description: "Your career's right hand",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

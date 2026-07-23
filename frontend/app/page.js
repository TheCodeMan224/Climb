import Link from "next/link";

export default function Home() {
  return (
    <main className="center">
      <h1 className="logo">Climb</h1>
      <p className="tag">Your career&apos;s right hand</p>
      <div className="row">
        <Link className="btn" href="/register" style={{ marginTop: 0 }}>
          Get started
        </Link>
        <Link className="link" href="/login">
          I already have an account
        </Link>
      </div>
    </main>
  );
}

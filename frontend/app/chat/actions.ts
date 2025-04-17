"use server";
import { cookies } from "next/headers";

export async function sendMessage(message: string) {
  const session = cookies().get("session_id")?.value
    ?? crypto.randomUUID();

  cookies().set("session_id", session);

  const res = await fetch(`${process.env.NEXT_PUBLIC_API}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: session, message }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("API Error");
  return res.json() as Promise<{answer:string}>;
}

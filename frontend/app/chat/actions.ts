"use server";
import { cookies } from "next/headers";

export async function sendMessage(message: string) {
  const session = cookies().get("session_id")?.value
    ?? crypto.randomUUID();

  cookies().set("session_id", session);

  console.log(`Attempting API request to: ${process.env.NEXT_PUBLIC_API}/chat`);
  
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: session, message }),
      cache: "no-store",
    });
    
    if (!res.ok) {
      const errorText = await res.text().catch(() => "Failed to get error details");
      console.error(`API Error: Status ${res.status} - ${errorText}`);
      throw new Error(`API Error: Status ${res.status} - ${errorText}`);
    }
    
    return res.json() as Promise<{answer:string}>;
  } catch (error) {
    console.error("API Call failed:", error);
    throw error;
  }
}

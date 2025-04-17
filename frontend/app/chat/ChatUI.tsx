"use client";
import { useState } from "react";
import { sendMessage } from "./actions";

export default function ChatUI() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{role:"user"|"bot";text:string}[]>([]);

  async function handleSend() {
    if (!input.trim()) return;
    setMessages([...messages, {role:"user", text:input}]);
    const res = await sendMessage(input);
    setMessages((m)=>[...m, {role:"bot", text:res.answer}]);
    setInput("");
  }

  return (
    <div className="w-full max-w-xl mx-auto">
      <ul className="mb-4 space-y-2">
        {messages.map((m, i)=>(
          <li key={i} className={m.role==="user"?"text-blue-600":"text-gray-900"}>
            <b>{m.role==="user"?"나":"AI"}:</b> {m.text}
          </li>
        ))}
      </ul>
      <textarea
        className="w-full border p-2 rounded"
        rows={2}
        value={input}
        onChange={e=>setInput(e.target.value)}
      />
      <button
        className="mt-2 px-4 py-2 bg-black text-white rounded"
        onClick={handleSend}
      >
        전송
      </button>
    </div>
  );
}

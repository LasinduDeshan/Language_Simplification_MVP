import React, { useState } from "react";
import { X, Volume2, Sparkles, Heart, CheckCircle2, Star, Smile } from "lucide-react";

export default function ChildPreviewModal({ childView, adaptation, task, onClose }) {
  const [selectedChoice, setSelectedChoice] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const instruction = childView?.presented_instruction || adaptation?.child_instruction || task?.child_friendly_instruction || "Look at the picture and let's have fun!";
  const supportiveMessage = childView?.supportive_message || adaptation?.supportive_message || "You are doing wonderful!";
  const retryCue = childView?.retry_cue;
  const adultSupportMessage = childView?.adult_support_message;
  const options = childView?.options || task?.options || [];
  const stimulus = childView?.stimulus || task?.stimulus;

  const handleSpeak = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(instruction);
      utter.rate = 0.85;
      utter.pitch = 1.1;
      utter.onstart = () => setIsSpeaking(true);
      utter.onend = () => setIsSpeaking(false);
      utter.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utter);
    }
  };

  const getOptionEmoji = (opt) => {
    const o = String(opt).toLowerCase();
    if (o.includes("cat")) return "🐱";
    if (o.includes("dog")) return "🐶";
    if (o.includes("rabbit")) return "🐰";
    if (o.includes("pencil")) return "✏️";
    if (o.includes("book")) return "📖";
    if (o.includes("apple")) return "🍎";
    if (o.includes("banana")) return "🍌";
    if (o.includes("car")) return "🚗";
    if (o.includes("fish") || o.includes("water")) return "🐟";
    if (o.includes("tree")) return "🌳";
    if (o.includes("in")) return "📥";
    if (o.includes("on")) return "📦";
    if (o.includes("under")) return "🪑";
    if (o.includes("red")) return "🔴";
    if (o.includes("blue")) return "🔵";
    if (o.includes("yellow")) return "🟡";
    if (o.includes("yes")) return "👍";
    if (o.includes("no")) return "👎";
    if (o.includes("she") || o.includes("girl")) return "👧";
    if (o.includes("he") || o.includes("boy")) return "👦";
    return "✨";
  };

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(15, 23, 42, 0.85)",
      backdropFilter: "blur(12px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
      padding: "1.5rem"
    }}>
      <div style={{
        position: "relative",
        maxWidth: "760px",
        width: "100%",
        background: "linear-gradient(135deg, #fff7ed 0%, #ffedd5 50%, #fef3c7 100%)",
        borderRadius: "28px",
        padding: "2.5rem 2rem",
        boxShadow: "0 25px 50px -12px rgba(249, 115, 22, 0.25), 0 0 0 4px #fb923c",
        border: "3px solid #ffffff",
        textAlign: "center"
      }}>
        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            position: "absolute",
            top: "-16px",
            right: "-16px",
            background: "#ffffff",
            border: "3px solid #fb923c",
            borderRadius: "50%",
            width: "44px",
            height: "44px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            color: "#ea580c"
          }}
          title="Close Preview"
        >
          <X size={24} />
        </button>

        {/* Top Supportive Pill */}
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "0.5rem",
          background: "rgba(255, 255, 255, 0.9)",
          padding: "0.5rem 1.25rem",
          borderRadius: "9999px",
          color: "#c2410c",
          fontWeight: 700,
          fontSize: "0.95rem",
          boxShadow: "0 2px 8px rgba(249, 115, 22, 0.15)",
          marginBottom: "1.25rem"
        }}>
          <Sparkles size={18} color="#f97316" />
          <span>{supportiveMessage}</span>
          <Heart size={16} color="#ef4444" fill="#ef4444" />
        </div>

        {/* Stimulus / Picture if available */}
        {stimulus && stimulus.alt_text && (
          <div style={{
            background: "#ffffff",
            borderRadius: "20px",
            padding: "1.25rem",
            marginBottom: "1.5rem",
            boxShadow: "0 4px 14px rgba(0,0,0,0.06)",
            border: "2px dashed #fdba74"
          }}>
            <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>
              {getOptionEmoji(stimulus.alt_text)}
            </div>
            <p style={{ margin: 0, color: "#7c2d12", fontSize: "0.95rem", fontWeight: 600 }}>
              {stimulus.alt_text}
            </p>
          </div>
        )}

        {/* Main Instruction */}
        <div style={{
          background: "#ffffff",
          borderRadius: "24px",
          padding: "2rem",
          boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.08)",
          marginBottom: "1.5rem",
          border: "2px solid #fed7aa"
        }}>
          <h2 style={{
            fontSize: "2rem",
            fontWeight: 800,
            color: "#1e293b",
            lineHeight: 1.35,
            margin: "0 0 1rem 0"
          }}>
            {instruction}
          </h2>

          {/* Audio Replay Button */}
          <button
            onClick={handleSpeak}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.5rem",
              background: isSpeaking ? "#ea580c" : "#f97316",
              color: "#ffffff",
              border: "none",
              padding: "0.75rem 1.5rem",
              borderRadius: "9999px",
              fontSize: "1.05rem",
              fontWeight: 700,
              cursor: "pointer",
              boxShadow: "0 4px 14px rgba(249, 115, 22, 0.4)",
              transition: "all 0.2s"
            }}
          >
            <Volume2 size={22} className={isSpeaking ? "animate-pulse" : ""} />
            <span>{isSpeaking ? "Listening..." : "Hear Instruction"}</span>
          </button>
        </div>

        {/* Retry or Adult Support message */}
        {retryCue && !adultSupportMessage && (
          <div style={{
            background: "#dbeafe",
            color: "#1e40af",
            padding: "0.75rem 1.25rem",
            borderRadius: "14px",
            fontWeight: 700,
            marginBottom: "1.25rem",
            display: "inline-block"
          }}>
            {retryCue}
          </div>
        )}

        {adultSupportMessage && (
          <div style={{
            background: "#ecfdf5",
            color: "#065f46",
            padding: "1rem 1.5rem",
            borderRadius: "16px",
            fontWeight: 700,
            fontSize: "1.1rem",
            marginBottom: "1.25rem",
            border: "2px solid #a7f3d0"
          }}>
            <Smile size={24} style={{ display: "inline", verticalAlign: "middle", marginRight: "0.5rem" }} />
            {adultSupportMessage}
          </div>
        )}

        {/* Interactive Response Options (If available) */}
        {options && options.length > 0 && (
          <div style={{
            display: "grid",
            gridTemplateColumns: options.length <= 2 ? "repeat(2, 1fr)" : "repeat(3, 1fr)",
            gap: "1rem",
            marginTop: "1rem"
          }}>
            {options.map((opt, idx) => {
              const isSelected = selectedChoice === opt;
              return (
                <button
                  key={idx}
                  onClick={() => setSelectedChoice(opt)}
                  style={{
                    background: isSelected ? "#f97316" : "#ffffff",
                    color: isSelected ? "#ffffff" : "#1e293b",
                    border: isSelected ? "3px solid #ea580c" : "2px solid #e2e8f0",
                    borderRadius: "20px",
                    padding: "1.25rem 1rem",
                    cursor: "pointer",
                    fontSize: "1.2rem",
                    fontWeight: 800,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "0.5rem",
                    boxShadow: isSelected ? "0 8px 20px rgba(249, 115, 22, 0.35)" : "0 4px 10px rgba(0,0,0,0.04)",
                    transition: "all 0.15s ease-in-out"
                  }}
                >
                  <span style={{ fontSize: "2rem" }}>{getOptionEmoji(opt)}</span>
                  <span>{opt}</span>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

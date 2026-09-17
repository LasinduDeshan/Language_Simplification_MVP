import React from "react";
import { X, Volume2, Sparkles } from "lucide-react";

export default function ChildPreviewModal({ adaptation, onClose }) {
  if (!adaptation) return null;

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: "rgba(15, 23, 42, 0.85)",
      backdropFilter: "blur(10px)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 100,
      padding: "1.5rem"
    }}>
      <div style={{ position: "relative", maxWidth: "750px", width: "100%" }}>
        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            position: "absolute",
            top: "-15px",
            right: "-15px",
            background: "#ffffff",
            border: "2px solid #fdba74",
            borderRadius: "50%",
            width: "36px",
            height: "36px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            zIndex: 10,
            boxShadow: "0 4px 10px rgba(0,0,0,0.15)"
          }}
        >
          <X size={20} color="#ea580c" />
        </button>

        {/* Child preview container */}
        <div className="child-preview-container">
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            background: "#ffedd5",
            color: "#c2410c",
            padding: "6px 16px",
            borderRadius: "999px",
            fontWeight: 700,
            fontSize: "0.9rem",
            marginBottom: "1.25rem"
          }}>
            <Sparkles size={16} />
            <span>Child Learning View</span>
          </div>

          <div className="child-instruction-bubble">
            "{adaptation.child_instruction}"
          </div>

          {adaptation.supportive_message && (
            <div className="child-support-message">
              {adaptation.supportive_message}
            </div>
          )}

          {adaptation.visual_cues && adaptation.visual_cues.length > 0 && (
            <div>
              <p style={{ fontSize: "0.95rem", color: "#64748b", fontWeight: 600, marginBottom: "0.75rem" }}>
                HELPFUL HINTS:
              </p>
              <div className="child-cue-cards">
                {adaptation.visual_cues.map((cue, idx) => (
                  <div key={idx} className="child-cue-card">
                    {cue.replace(/_/g, " ")}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{ marginTop: "2rem" }}>
            <button
              onClick={() => {
                if ('speechSynthesis' in window) {
                  const utter = new SpeechSynthesisUtterance(adaptation.child_instruction);
                  utter.rate = 0.85;
                  window.speechSynthesis.speak(utter);
                }
              }}
              className="btn"
              style={{
                backgroundColor: "#ea580c",
                color: "#ffffff",
                borderRadius: "999px",
                padding: "0.75rem 1.75rem",
                fontSize: "1.05rem",
                fontWeight: 700,
                boxShadow: "0 6px 16px rgba(234, 88, 12, 0.35)"
              }}
            >
              <Volume2 size={20} />
              <span>Listen to Instruction</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

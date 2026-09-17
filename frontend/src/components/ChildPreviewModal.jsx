import React, { useState } from "react";
import { X, Volume2, Sparkles, Heart, CheckCircle2, Star } from "lucide-react";

export default function ChildPreviewModal({ adaptation, onClose }) {
  const [selectedChoice, setSelectedChoice] = useState(null);

  if (!adaptation) return null;

  // Icon mapping for visual cues
  const getCueIcon = (cue) => {
    const c = cue.toLowerCase();
    if (c.includes("fish")) return "🐟";
    if (c.includes("water")) return "🌊";
    if (c.includes("tree")) return "🌳";
    if (c.includes("crayon")) return "🖍️";
    if (c.includes("bin")) return "♻️";
    if (c.includes("ball")) return "🔵";
    if (c.includes("broccoli")) return "🥦";
    if (c.includes("apple")) return "🍎";
    if (c.includes("teeth") || c.includes("toothbrush")) return "🪥";
    if (c.includes("wash") || c.includes("face")) return "🧼";
    if (c.includes("cat")) return "🐱";
    if (c.includes("desk")) return "🪑";
    if (c.includes("triangle")) return "🔺";
    if (c.includes("square")) return "🟨";
    if (c.includes("rabbit")) return "🐰";
    if (c.includes("bear")) return "🐻";
    if (c.includes("seed")) return "🌱";
    if (c.includes("watering") || c.includes("can")) return "🚿";
    if (c.includes("she") || c.includes("girl")) return "👧";
    if (c.includes("he") || c.includes("boy")) return "👦";
    return "⭐";
  };

  // Extract binary options if two_picture_choice
  const getBinaryChoices = () => {
    if (adaptation.answer_format !== "two_picture_choice") return null;
    const inst = adaptation.child_instruction.toLowerCase();
    if (inst.includes("water or tree") || inst.includes("water and tree")) {
      return [
        { label: "Water", icon: "🌊", hint: "In the water" },
        { label: "Tree", icon: "🌳", hint: "In the tree" }
      ];
    }
    if (inst.includes("he or she")) {
      return [
        { label: "He", icon: "👦", hint: "Boy" },
        { label: "She", icon: "👧", hint: "Girl" }
      ];
    }
    if (inst.includes("rabbit or bear")) {
      return [
        { label: "Rabbit", icon: "🐰", hint: "Little Rabbit" },
        { label: "Bear", icon: "🐻", hint: "Big Bear" }
      ];
    }
    if (inst.includes("on or under")) {
      return [
        { label: "Under Desk", icon: "🪑", hint: "Underneath" },
        { label: "On Top", icon: "📦", hint: "On top of desk" }
      ];
    }
    if (inst.includes("broccoli")) {
      return [
        { label: "Broccoli", icon: "🥦", hint: "Green Vegetable" },
        { label: "Apple", icon: "🍎", hint: "Sweet Fruit" }
      ];
    }
    return null;
  };

  const binaryChoices = getBinaryChoices();

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
      <div style={{ position: "relative", maxWidth: "780px", width: "100%" }}>
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
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            zIndex: 10,
            boxShadow: "0 4px 12px rgba(0,0,0,0.2)"
          }}
        >
          <X size={22} color="#ea580c" />
        </button>

        {/* Child preview card */}
        <div className="child-preview-container" style={{ textAlign: "center", position: "relative" }}>
          
          {/* Header pill */}
          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            background: "#ffedd5",
            color: "#c2410c",
            padding: "8px 20px",
            borderRadius: "999px",
            fontWeight: 800,
            fontSize: "0.95rem",
            marginBottom: "1.5rem"
          }}>
            <Sparkles size={18} />
            <span>Child Learning View • Attempt {adaptation.target_attempt_number || adaptation.attempt_number || 1}</span>
          </div>

          {/* Child instruction bubble */}
          <div className="child-instruction-bubble" style={{ fontSize: "1.75rem", lineHeight: 1.4, margin: "0 auto 1.25rem" }}>
            "{adaptation.child_instruction}"
          </div>

          {/* Supportive encouraging message */}
          {adaptation.supportive_message && (
            <div className="child-support-message" style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.5rem" }}>
              <Heart size={18} fill="#f97316" color="#f97316" />
              <span>{adaptation.supportive_message}</span>
            </div>
          )}

          {/* Interactive Binary Choice Cards (if two_picture_choice) */}
          {binaryChoices && (
            <div style={{ marginBottom: "1.75rem" }}>
              <p style={{ fontSize: "0.95rem", color: "#64748b", fontWeight: 700, marginBottom: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Touch or Say Your Choice:
              </p>
              <div style={{ display: "flex", gap: "1.25rem", justifyContent: "center" }}>
                {binaryChoices.map((choice, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setSelectedChoice(choice.label)}
                    style={{
                      flex: 1,
                      maxWidth: "240px",
                      background: selectedChoice === choice.label ? "#fed7aa" : "#ffffff",
                      border: selectedChoice === choice.label ? "3px solid #f97316" : "2px solid #e2e8f0",
                      borderRadius: "16px",
                      padding: "1.25rem 1rem",
                      cursor: "pointer",
                      boxShadow: selectedChoice === choice.label ? "0 8px 20px rgba(249, 115, 22, 0.25)" : "0 4px 10px rgba(0,0,0,0.06)",
                      transform: selectedChoice === choice.label ? "scale(1.04)" : "scale(1)",
                      transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)"
                    }}
                  >
                    <span style={{ fontSize: "3rem", display: "block", marginBottom: "0.5rem" }}>
                      {choice.icon}
                    </span>
                    <strong style={{ fontSize: "1.25rem", color: "#1e293b", display: "block" }}>
                      {choice.label}
                    </strong>
                    <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                      {choice.hint}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Visual Cue Cards */}
          {adaptation.visual_cues && adaptation.visual_cues.length > 0 && (
            <div style={{ marginBottom: "1.5rem" }}>
              <p style={{ fontSize: "0.85rem", color: "#94a3b8", fontWeight: 700, marginBottom: "0.6rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Visual Cues for Young Learner:
              </p>
              <div className="child-cue-cards" style={{ justifyContent: "center" }}>
                {adaptation.visual_cues.map((cue, idx) => (
                  <div key={idx} className="child-cue-card" style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem", fontSize: "1rem" }}>
                    <span>{getCueIcon(cue)}</span>
                    <span style={{ textTransform: "capitalize" }}>{cue.replace(/_/g, " ")}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Audio speech synthesis replay */}
          <div style={{ marginTop: "1.75rem", display: "flex", justifyContent: "center", gap: "1rem" }}>
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
                padding: "0.85rem 2rem",
                fontSize: "1.1rem",
                fontWeight: 700,
                boxShadow: "0 6px 18px rgba(234, 88, 12, 0.4)"
              }}
            >
              <Volume2 size={22} />
              <span>Listen to Instruction</span>
            </button>
          </div>

          <p style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "1rem" }}>
            🔒 Strict Privacy: No scores, test percentages, or technical grammar labels are ever shown in this screen.
          </p>
        </div>
      </div>
    </div>
  );
}

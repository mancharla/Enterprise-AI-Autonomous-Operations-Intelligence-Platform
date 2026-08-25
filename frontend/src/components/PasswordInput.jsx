import { useState } from "react";

export default function PasswordInput({
    name,
    value,
    onChange,
    placeholder,
    required = true,
}) {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <div
            style={{
                position: "relative",
                width: "100%",
            }}
        >
            <input
                type={showPassword ? "text" : "password"}
                name={name}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                required={required}
                autoComplete={
                    name === "confirmPassword"
                        ? "new-password"
                        : "current-password"
                }
                style={{
                    width: "100%",
                    paddingRight: "45px",
                    boxSizing: "border-box",
                }}
            />

            <button
                type="button"
                onClick={() =>
                    setShowPassword(!showPassword)
                }
                aria-label={
                    showPassword
                        ? "Hide password"
                        : "Show password"
                }
                style={{
                    position: "absolute",
                    right: "10px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    border: "none",
                    background: "transparent",
                    cursor: "pointer",
                    fontSize: "18px",
                    padding: "4px",
                }}
            >
                {showPassword ? "🙈" : "👁️"}
            </button>
        </div>
    );
}
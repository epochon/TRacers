import React from "react";

const Button = React.forwardRef(({ className, variant, size, ...props }, ref) => {
    // Simple button implementation
    // variant and size are ignored for now, or could map to classes
    return (
        <button
            ref={ref}
            className={`btn ${variant ? `btn-${variant}` : ''} ${className || ""}`}
            {...props}
            style={{
                padding: '8px 16px',
                borderRadius: '4px',
                cursor: 'pointer',
                ...props.style
            }}
        >
            {props.children}
        </button>
    );
});
Button.displayName = "Button";

export { Button };

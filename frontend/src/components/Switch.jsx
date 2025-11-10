import React from 'react';
import './Switch.css';

const Switch = ({ checked, onChange, disabled = false }) => {
  return (
    <label className="custom-switch">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="custom-switch-input"
      />
      <span className="custom-switch-slider"></span>
    </label>
  );
};

export default Switch;

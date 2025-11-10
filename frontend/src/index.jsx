import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles-tailwind.css"; // tailwind base first
import "./styles.css"; // custom overrides

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

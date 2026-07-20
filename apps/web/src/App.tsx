import { useState } from "react";
import type { Playbook } from "./types";
import Home from "./pages/Home";
import Result from "./pages/Result";

export default function App() {
  const [playbook, setPlaybook] = useState<Playbook | null>(null);

  if (playbook) {
    return <Result playbook={playbook} onReset={() => setPlaybook(null)} />;
  }

  return <Home onPlaybook={setPlaybook} />;
}

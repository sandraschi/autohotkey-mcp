import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { Dashboard } from "@/pages/dashboard";
import { Help } from "@/pages/help";
import { Chat } from "@/pages/chat";
import { Running } from "@/pages/running";
import { Scriptlets } from "@/pages/scriptlets";
import { Status } from "@/pages/status";

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/help" element={<Help />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/scriptlets" element={<Scriptlets />} />
          <Route path="/running" element={<Running />} />
          <Route path="/status" element={<Status />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;

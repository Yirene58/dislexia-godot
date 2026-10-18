import Game from "./pages/Game";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import CreateCharacter from "./pages/CreateCharacter";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CharacterSelection from "./pages/CharacterSelection";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={<Navigate to="/login" replace />}
          />

          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<ProtectedRoute />}>
          <Route path="/game/:id" element={<Game />} />
            <Route
              path="/characters"
              element={<CharacterSelection />}
            />
          </Route>

          <Route
            path="*"
            element={<Navigate to="/login" replace />}
          />

          <Route
            path="/characters/create"
            element={<CreateCharacter />}
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

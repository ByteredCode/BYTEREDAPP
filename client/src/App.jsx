// Importaciones agrupadas por tipo: contexto > layout > guards > páginas
// Esto facilita localizar dependencias de un vistazo
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import { ToastProvider } from "./context/ToastContext"
import Layout from "./components/Layout"
import ProtectedRoute from "./components/ProtectedRoute"
import AdminOnlyRoute from "./components/AdminOnlyRoute"
import Login from "./pages/Login"
import Dashboard from "./pages/Dashboard"
import AdminLayout from "./pages/admin/AdminLayout"
import AdminDashboard from "./pages/admin/AdminDashboard"
import Empresas from "./pages/admin/Empresas"
import EmpresaForm from "./pages/admin/EmpresaForm"
import EmpresaUsuarios from "./pages/admin/EmpresaUsuarios"
import Servicios from "./pages/admin/Servicios"
import Usuarios from "./pages/admin/Usuarios"
import UsuarioForm from "./pages/admin/UsuarioForm"
import ScrumLayout from "./pages/Scrum/ScrumLayout"
import Board from "./pages/Scrum/Board"
import Sprints from "./pages/Scrum/Sprints"
import NuevoTicket from "./pages/Tickets/NuevoTicket"
import TicketsAdmin from "./pages/admin/TicketsAdmin"
import DocumentosAdmin from "./pages/Documentos/DocumentosAdmin"
import Fichajes from "./pages/Fichajes"
import MiEmpresa from "./pages/MiEmpresa"
import NotFound from "./components/common/NotFound"

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
        <Routes>
          {/* Rutas publicas (sin layout ni autenticacion) */}
          <Route path="/login" element={<Login />} />
          {/* NuevoTicket es público porque clientes externos pueden reportar incidencias sin registrarse */}
          <Route path="/tickets/nuevo" element={<NuevoTicket />} />

          {/* Layout como ruta "padre" sin path: solo aporta el navbar y <Outlet /> para las hijas */}
          <Route element={<Layout />}>
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/mi-empresa"
              element={
                <ProtectedRoute>
                  <MiEmpresa />
                </ProtectedRoute>
              }
            />
            {/* Las rutas admin se anidan dentro de AdminLayout que renderiza la sidebar + <Outlet /> */}
            <Route
              path="/admin"
              element={
                <AdminOnlyRoute>
                  <AdminLayout />
                </AdminOnlyRoute>
              }
            >
              <Route index element={<AdminDashboard />} />
              <Route path="empresas" element={<Empresas />} />
              <Route path="empresas/nueva" element={<EmpresaForm />} />
              {/* :id es un parámetro dinámico; la misma ruta editar y el componente decide si crea o edita según si hay id */}
              <Route path="empresas/:id/editar" element={<EmpresaForm />} />
              <Route path="empresas/:id/usuarios" element={<EmpresaUsuarios />} />
              <Route path="empresas/:id/servicios" element={<Servicios />} />
              <Route path="usuarios" element={<Usuarios />} />
              <Route path="usuarios/nueva" element={<UsuarioForm />} />
              <Route path="usuarios/:id/editar" element={<UsuarioForm />} />
              <Route path="tickets" element={<TicketsAdmin />} />
              <Route path="documentos" element={<DocumentosAdmin />} />
            </Route>
            <Route
              path="/fichajes"
              element={
                <ProtectedRoute>
                  <Fichajes />
                </ProtectedRoute>
              }
            />
            {/* ScrumLayout renderiza tabs de navegación interna (Tablero / Sprints) y un <Outlet /> */}
            <Route
              path="/scrum"
              element={
                <ProtectedRoute>
                  <ScrumLayout />
                </ProtectedRoute>
              }
            >
              <Route path="tablero" element={<Board />} />
              <Route path="sprints" element={<Sprints />} />
            </Route>
          </Route>
          {/* Catch-all: cualquier ruta no definida muestra página 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

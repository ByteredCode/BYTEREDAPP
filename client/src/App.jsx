import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import { ToastProvider } from "./context/ToastContext"
import Layout from "./components/Layout"
import ProtectedRoute from "./components/ProtectedRoute"
import AdminOnlyRoute from "./components/AdminOnlyRoute"
import Login from "./pages/Login"
import Register from "./pages/Register"
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

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
        <Routes>
          {/* Rutas publicas (sin layout ni autenticacion) */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/tickets/nuevo" element={<NuevoTicket />} />

          {/* Rutas con layout principal (navbar) */}
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
            {/* Rutas de administracion (solo admins) */}
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
            {/* Rutas de Scrum con sub-layout (tabs) */}
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
          {/* Catch-all: redirige al login */}
          <Route path="*" element={<Login />} />
        </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

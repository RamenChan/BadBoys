import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';
import LoginRegister from './pages/LoginRegister';
import Dashboard from './pages/Dashboard';

function MainRouter() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/" element={<LoginRegister />} />

                    <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    );
}

export default MainRouter;
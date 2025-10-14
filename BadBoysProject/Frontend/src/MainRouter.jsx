import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginRegister from './pages/LoginRegister';
import Dashboard from './pages/Dashboard';

function MainRouter() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LoginRegister />} />
                <Route path="/dashboard" element={<Dashboard />} />
            </Routes>

        </BrowserRouter>
    );
}

export default MainRouter;
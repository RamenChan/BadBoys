// src/pages/LoginRegister.jsx
import '../App.css';
import Swal from 'sweetalert2';
import { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ResultCode from '../constants/resultcodes';

function LoginRegister() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const navigate = useNavigate();
    const { login, register, isAuthenticated } = useAuth();

    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    const handleLogin = async () => {
        const result = await login(username, password);

        if (result.success && result.data.code === ResultCode.SUCCESS) {
            Swal.fire({
                title: 'Başarılı',
                text: result.data.message,
                icon: 'success',
                timer: 1000,
                timerProgressBar: true,
                showConfirmButton: false
            }).then((result) => {
                if (result.dismiss === Swal.DismissReason.timer) {
                    navigate('/dashboard');
                }
            });
        } else if (result.data.code === ResultCode.INFO) {
            Swal.fire({
                title: 'Bilgilendirme',
                text: result.data.message,
                icon: 'info',
                confirmButtonText: 'Tamam'
            });
        } else {
            Swal.fire({
                title: 'Hata',
                text: result.data.message || 'Giriş başarısız!',
                icon: 'error',
                confirmButtonText: 'Tamam'
            });
        }
    };

    const handleRegister = async () => {
        const result = await register(username, password, confirmPassword, email);

        if (result.success && result.data.code === ResultCode.SUCCESS) {
            Swal.fire({
                title: 'Başarılı',
                text: result.data.message,
                icon: 'success',
                confirmButtonText: 'Tamam'
            });
        } else if (result.data.code === ResultCode.INFO) {
            let messageContent = "";

            if (Array.isArray(result.data.data)) {
                messageContent = result.data.data.join("<br>");
            } else {
                messageContent = result.data.message;
            }

            Swal.fire({
                title: 'Bilgilendirme',
                html: `<p>${messageContent}</p>`,
                icon: 'info',
                confirmButtonText: 'Tamam'
            });
        } else {
            Swal.fire({
                title: 'Hata',
                text: result.data.message || 'Kayıt başarısız!',
                icon: 'error',
                confirmButtonText: 'Tamam'
            });
        }
    };
    useEffect(() => {
        const container = document.getElementById('container');
        const registerBtn = document.getElementById('register');
        const loginBtn = document.getElementById('login');

        if (registerBtn && loginBtn && container) {
            registerBtn.addEventListener('click', () => {
                container.classList.add("active");
            });

            loginBtn.addEventListener('click', () => {
                container.classList.remove("active");
            });
        }

        return () => {
            if (registerBtn && loginBtn) {
                registerBtn.replaceWith(registerBtn.cloneNode(true));
                loginBtn.replaceWith(loginBtn.cloneNode(true));
            }
        };
    }, []);

    return (
        <div className="container" id="container">
            <div className="form-container sign-up">
                <form>
                    <h1>Kullanıcı Oluştur</h1>
                    <input
                        type="text"
                        placeholder="Kullanıcı Adı"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="email"
                        placeholder="E-Posta"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Şifre"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Tekrar Şifre"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                    <button type="button" onClick={handleRegister}>
                        Kayıt Ol
                    </button>
                </form>
            </div>

            <div className="form-container sign-in">
                <form>
                    <h1>Giriş Yap</h1>
                    <input
                        type="text"
                        placeholder="Kullanıcı Adı"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="Şifre"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <a href="#">Şifreni mi unuttun?</a>
                    <button type="button" onClick={handleLogin}>
                        Giriş Yap
                    </button>
                </form>
            </div>

            <div className="toggle-container">
                <div className="toggle">
                    <div className="toggle-panel toggle-left">
                        <h1>BadBoys</h1>
                        <p>Hesabın var mı?</p>
                        <button className="hidden" id="login" type="button" onClick={() => {
                            setPassword('');
                            setUsername('');
                        }}
                        >
                            Giriş Yap
                        </button>
                    </div>
                    <div className="toggle-panel toggle-right">
                        <h1>BadBoys</h1>
                        <p>Henüz hesabın yok mu?</p>
                        <button className="hidden" id="register" type="button" onClick={() => {
                            setPassword('');
                            setUsername('');
                            setConfirmPassword('');
                            setEmail('');
                        }}
                        >
                            Kayıt Ol
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginRegister;
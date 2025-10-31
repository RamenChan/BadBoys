import '../App.css';
import Swal from 'sweetalert2';
import { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import ResultCode from '../constants/resultcodes';

function LoginRegister() {

    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const navigate = useNavigate();


    const user_check = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/user_check", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            const data = await res.json();
            const result = data.result;

            if (result.code === ResultCode.SUCCESS) {
                Swal.fire({
                    title: 'Başarılı',
                    html: `<p>${result.message}</p>`,
                    icon: 'success',
                    timer: 1000,
                    timerProgressBar: true,
                    showConfirmButton: false
                }).then(() => {
                    navigate('/dashboard');
                });
            }
            else if (result.code === ResultCode.INFO) {
                Swal.fire({
                    title: 'Bilgilendirme',
                    html: `<p>${result.message}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Tamam'
                });
            }
            else if (result.code === ResultCode.ERROR) {
                Swal.fire({
                    title: 'Bilgilendirme',
                    html: `<p>${result.message}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Tamam'
                });
            }
        } catch (error) {
            Swal.fire({
                title: 'Hata',
                text: 'Backend ile iletişim kurulamadı!',
                icon: 'error',
                confirmButtonText: 'Tamam'
            });
            //console.log(error.message || error)
        }
    };


    const user_add = async () => {
        try {
            const res = await fetch("http://127.0.0.1:8000/user_add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password, confirmPassword, email }),
            });

            const data = await res.json();
            const result = data.result;

            if (result.code === ResultCode.SUCCESS) {
                Swal.fire({
                    title: 'Başarılı',
                    html: `<p>${result.message}</p>`,
                    icon: 'success',
                    confirmButtonText: 'Tamam'
                });
            } else if (result.code === ResultCode.INFO) {
                let messageContent = "";

                if (Array.isArray(result.data)) {
                    messageContent = result.data.join("<br>");
                } else if (typeof result.data === "string") {
                    messageContent = result.data;
                } else {
                    messageContent = result.message;
                }

                Swal.fire({
                    title: 'Bilgilendirme',
                    html: `<p>${messageContent}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Tamam'
                });
            } else if (result.code === ResultCode.ERROR) {
                Swal.fire({
                    title: 'Bilgilendirme',
                    html: `<p>${result.message}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Tamam'
                });
            }
        } catch (error) {
            Swal.fire({
                title: 'Hata',
                text: 'Backend ile iletişim kurulamadı!',
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
                    <input type="text" placeholder="Kullanıcı Adı"
                        value={username} onChange={(e) => setUsername(e.target.value)} />
                    <input type="email" placeholder="E-Posta"
                        value={email} onChange={(e) => setEmail(e.target.value)} />
                    <input type="password" placeholder="Şifre"
                        value={password} onChange={(e) => setPassword(e.target.value)} />
                    <input type="password" placeholder="Tekrar Şifre"
                        value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
                    <button type="button" onClick={user_add}>Kayıt Ol</button>
                </form>
            </div>

            <div className="form-container sign-in">
                <form>
                    <h1>Giriş Yap</h1>
                    <input type="text" placeholder="Kullanıcı Adı"
                        value={username} onChange={(e) => setUsername(e.target.value)} />
                    <input type="password" placeholder="Şifre"
                        value={password} onChange={(e) => setPassword(e.target.value)} />
                    <a href="#">Şifreni mi unuttun?</a>
                    <button type="button" onClick={user_check}>Giriş Yap</button>
                </form>
            </div>

            <div className="toggle-container">
                <div className="toggle">
                    <div className="toggle-panel toggle-left">
                        <h1>BadBoys</h1>
                        <p>Hesabın var mı?</p>
                        <button className="hidden" id="login" type="button"
                            onClick={() => { setIsLogin(false); setPassword(''); setUsername(''); }}>Giriş Yap</button>
                    </div>
                    <div className="toggle-panel toggle-right">
                        <h1>BadBoys</h1>
                        <p>Henüz hesabın yok mu?</p>
                        <button className="hidden" id="register" type="button"
                            onClick={() => { setIsLogin(true); setPassword(''); setUsername(''); setConfirmPassword(''); setEmail('') }}>Kayıt Ol</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginRegister;

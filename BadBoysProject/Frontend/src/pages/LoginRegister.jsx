import '../App.css';
import Swal from 'sweetalert2';
import { useState } from "react";
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
                Swal.fire({
                    title: 'Bilgilendirme',
                    html: `<p>${result.message}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Tamam'
                });
            } else {
                Swal.fire({
                    title: 'Hata',
                    html: `<p>${result.message}</p>`,
                    icon: 'error',
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


    return (
        <div className="LoginRegister">
            <section className="overlay">
                <div className={`slide-container ${isLogin ? "show-login" : "show-register"}`}>

                    {/* LOGIN FORM */}
                    <form className="form form-login">
                        <h1 className="card__title">BadBoys</h1>
                        <div className="row">
                            <input type="text"
                                name="user"
                                id="user"
                                placeholder="Kullanıcı Adı"
                                value={username} onChange={(e) => setUsername(e.target.value)} />
                            <label>Kullanıcı Adı</label>
                        </div>
                        <div className="row">
                            <input type="password"
                                name="password"
                                id="password"
                                placeholder="Şifre"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)} />
                            <label>Şifre</label>
                        </div>
                        <button className="btn" type="button" onClick={user_check}> Gönder </button>
                        <div className="container">
                            <div id="hesabin-yok-mu" className="item1" onClick={() => { setIsLogin(false); setPassword(''); setUsername(''); }}>
                                Hesabın yok mu? Kayıt Ol
                            </div>
                            <div className="item2">Şifremi Unuttum</div>
                        </div>
                    </form>

                    {/* REGISTER FORM */}
                    <form className="form form-register">
                        <h1 className="card__title">Kayıt Ol</h1>
                        <div className="row">
                            <input type="text"
                                name="user"
                                id="user"
                                placeholder="Kullanıcı Adı"
                                value={username} onChange={(e) => setUsername(e.target.value)} />
                            <label>Kullanıcı Adı</label>
                        </div>
                        <div className="row">
                            <input type="text"
                                name="usermail"
                                id="usermail"
                                placeholder="E-Mail"
                                value={email} onChange={(e) => setEmail(e.target.value)} />
                            <label>E-Mail</label>
                        </div>
                        <div className="row">
                            <input type="password"
                                name="password"
                                id="password"
                                placeholder="Şifre"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)} />
                            <label>Şifre</label>
                        </div>
                        <div className="row">
                            <input type="password"
                                name="confirmPassword"
                                id="confirmPassword"
                                placeholder="Tekrar Şifre"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)} />
                            <label>Tekrar Şifre</label>
                        </div>
                        <button className="btn" type="button" onClick={user_add}>Kaydol</button>
                        <div className="container">
                            <div className="item1" onClick={() => { setIsLogin(true); setPassword(''); setUsername(''); setConfirmPassword(''); setEmail('') }}>
                                Hesabın var mı? Giriş Yap
                            </div>
                        </div>
                    </form>

                </div>
            </section>
        </div>
    );
}

export default LoginRegister;

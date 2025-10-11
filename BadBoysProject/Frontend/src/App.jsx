import './App.css';
import Swal from 'sweetalert2';
import { useState } from "react";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const sendToBackend = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/encrypt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();


      Swal.fire({
        title: 'Şifreleme Başarılı',
        html: `
        <p><strong>Cipher Text:</strong> ${data.cipher_text}</p>
        <p><strong>Salt:</strong> ${data.salt}</p>
      `,
        icon: 'success',
        confirmButtonText: 'Tamam'
      });
    } catch (error) {
      console.error("Hata:", error);
      Swal.fire({
        title: 'Hata',
        text: 'Backend ile iletişim kurulamadı!',
        icon: 'error',
        confirmButtonText: 'Tamam'
      });
    }
  };


  return (
    <div className="app">
      <section className="overlay card">
        <h1 className="card__title">Giriş Yap</h1>
        <form id="login" className="card__form">
          <div className="row">
            <input
              type="text"
              name="user"
              id="user"
              placeholder="Kullanıcı Adı"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <label htmlFor="user">Kullanıcı Adı</label>
          </div>
          <div className="row">
            <input
              type="password"
              name="password"
              id="password"
              placeholder="Şifre"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <label htmlFor="password">Şifre</label>
          </div>
          <button className="btn" type="button" onClick={sendToBackend}>
            Gönder
          </button>
        </form>
      </section>
    </div>
  );
}

export default App;

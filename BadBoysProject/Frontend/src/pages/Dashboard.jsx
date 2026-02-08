import Swal from 'sweetalert2';
import { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { storiesAPI } from '../services/api';
import ResultCode from '../constants/resultcodes';
import '../App.css';
import { io } from "socket.io-client";

function timestampToDate(ts) {
    if (!ts) return null;
    return new Date(ts * 1000).toLocaleString();
}

function Dashboard() {
    const [storiesApi, setStoriesApi] = useState([]);
    const [storiesFetchedAtApi, setStoriesFetchedAtApi] = useState(null);

    const [storiesHtml, setStoriesHtml] = useState([]);
    const [storiesFetchedAtHtml, setStoriesFetchedAtHtml] = useState(null);

    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        const result = await Swal.fire({
            title: 'Emin misin?',
            text: 'Çıkış yapmak istediğine emin misin?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Evet, çıkış yap',
            cancelButtonText: 'İptal'
        });

        if (result.isConfirmed) {
            await logout();
            navigate('/');
            Swal.fire({
                title: 'Çıkış Yapıldı',
                text: 'Başarıyla çıkış yaptınız',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false
            });
        }
    };

    useEffect(() => {
        const socket = io("http://127.0.0.1:8000", {
            withCredentials: true
        });

        socket.on("new_stories", (result) => {
            if (result.code === ResultCode.SUCCESS) {
                setStoriesApi(result.data.stories);
                setStoriesFetchedAtApi(result.data.fetched_at);
            } else if (result.code === ResultCode.ERROR) {
                console.error('Socket hatası:', result.message);
            }
        });

        socket.on("new_stories_html", (result) => {
            if (result.code === ResultCode.SUCCESS) {
                setStoriesHtml(result.data.stories);
                setStoriesFetchedAtHtml(result.data.fetched_at);
            } else if (result.code === ResultCode.ERROR) {
                console.error('Socket hatası:', result.message);
            }
        });

        const fetchStories = async () => {
            try {
                const apiData = await storiesAPI.getStories('api');
                if (apiData.result.code === ResultCode.SUCCESS) {
                    setStoriesApi(apiData.result.data.stories);
                    setStoriesFetchedAtApi(apiData.result.data.fetched_at);
                }

                const htmlData = await storiesAPI.getStories('html');
                if (htmlData.result.code === ResultCode.SUCCESS) {
                    setStoriesHtml(htmlData.result.data.stories);
                    setStoriesFetchedAtHtml(htmlData.result.data.fetched_at);
                }
            } catch (error) {
                console.error('fetchStories hatası:', error);
                Swal.fire({
                    title: 'Hata',
                    text: 'Veriler yüklenirken hata oluştu!',
                    icon: 'error',
                    confirmButtonText: 'Tamam'
                });
            }
        };

        fetchStories();

        return () => {
            socket.disconnect();
        };
    }, []);

    return (
        <div className="dashboard-page">
            <div className="dashboard-header">
                <h2>BadBoys Dashboard</h2>
                <div className="dashboard-user">
                    <span>Hoşgeldin, {user?.username}</span>
                    <button onClick={handleLogout}>Çıkış Yap</button>
                </div>
            </div>

            <div className="dashboard-container">
                <div className="dashboard-left">
                    <h2 style={{ textAlign: "center" }}>API İle Çekilen Datalar</h2>
                    <ul style={{ listStyleType: "disc", paddingLeft: "20px" }}>
                        {storiesApi.map(story => (
                            <li key={story.id}>
                                <a href={story.url || "#"} target="_blank" rel="noreferrer">
                                    {story.title}
                                </a>
                            </li>
                        ))}
                    </ul>
                    {storiesFetchedAtApi && (
                        <div className="fetched-at">
                            <p>Son Güncelleme: {timestampToDate(storiesFetchedAtApi)}</p>
                        </div>
                    )}
                </div>

                <div className="dashboard-right">
                    <h2 style={{ textAlign: "center" }}>HTML İle Çekilen Datalar</h2>
                    <ul style={{ listStyleType: "disc", paddingLeft: "20px" }}>
                        {storiesHtml.map(story => (
                            <li key={story.id}>
                                <a href={story.url || "#"} target="_blank" rel="noreferrer">
                                    {story.title}
                                </a>
                            </li>
                        ))}
                    </ul>
                    {storiesFetchedAtHtml && (
                        <div className="fetched-at">
                            <p>Son Güncelleme: {timestampToDate(storiesFetchedAtHtml)}</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
import Swal from 'sweetalert2';
import { useState, useEffect } from "react";
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

    useEffect(() => {
        const socket = io("http://127.0.0.1:8000");

        socket.on("new_stories", (result) => {
            if (result.code === ResultCode.SUCCESS) {
                setStoriesApi(result.data.stories);
                setStoriesFetchedAtApi(result.data.fetched_at);
            } else if (result.code === ResultCode.ERROR) {
                Swal.fire({
                    title: 'Bilgilendirme',
                    html: `<p>${result.message}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Tamam'
                });
            }
        });


        socket.on("new_stories_html", (result) => {
            if (result.code === ResultCode.SUCCESS) {
                setStoriesHtml(result.data.stories);
                setStoriesFetchedAtHtml(result.data.fetched_at);
            } else if (result.code === ResultCode.ERROR) {
                Swal.fire({
                    title: 'Bilgilendirme',
                    html: `<p>${result.message}</p>`,
                    icon: 'info',
                    confirmButtonText: 'Tamam'
                });
            }
        });


        const fetchStories = async () => {
            try {
                const resApi = await fetch("http://127.0.0.1:8000/api/stories?source=api");
                const incomeApi = await resApi.json();
                if (incomeApi.result.code === ResultCode.SUCCESS) {
                    setStoriesApi(incomeApi.result.data.stories);
                    setStoriesFetchedAtApi(incomeApi.result.data.fetched_at);
                }

                const resHtml = await fetch("http://127.0.0.1:8000/api/stories?source=html");
                const incomeHtml = await resHtml.json();
                if (incomeHtml.result.code === ResultCode.SUCCESS) {
                    setStoriesHtml(incomeHtml.result.data.stories);
                    setStoriesFetchedAtHtml(incomeHtml.result.data.fetched_at);
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

        fetchStories();

        return () => {
            socket.disconnect();
        };
    }, []);
    return (


        <div className="dashboard-container">
            <div className="dashboard-left">
                <h2 style={{ textAlign: "center" }}>API İle Çekilen Datalar</h2>
                <ul style={{ listStyleType: "disc", paddingLeft: "20px" }}>
                    {storiesApi.map(story => (
                        <li key={story.id}>
                            <a href={story.url || "#"} target="_blank" rel="noreferrer">{story.title}</a>
                        </li>
                    ))}
                </ul>
                {storiesFetchedAtApi && (
                    <div className="fetched-at">
                        <p>Son Güncelleme: {timestampToDate(storiesFetchedAtApi) || "Bilinmiyor"}</p>
                    </div>
                )}
            </div>
            <div className="dashboard-right">
                <h2 style={{ textAlign: "center" }}>HTML İle Çekilen Datalar</h2>
                <ul style={{ listStyleType: "disc", paddingLeft: "20px" }}>
                    {storiesHtml.map(story => (
                        <li key={story.id}>
                            <a href={story.url || "#"} target="_blank" rel="noreferrer">{story.title}</a>
                        </li>
                    ))}
                </ul>
                {storiesFetchedAtHtml && (
                    <div className="fetched-at">
                        <p>Son Güncelleme: {timestampToDate(storiesFetchedAtHtml) || "Bilinmiyor"}</p>
                    </div>
                )}
            </div>
        </div>



    );
}

export default Dashboard;

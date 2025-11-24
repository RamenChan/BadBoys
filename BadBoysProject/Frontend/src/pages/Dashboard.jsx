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
    const [stories, setStories] = useState([]);
    const [storiesFetchedAt, setStoriesFetchedAt] = useState(null);

    useEffect(() => {
        const socket = io("http://127.0.0.1:8000");

        socket.on("new_stories", (result) => {

            if (result.code === ResultCode.SUCCESS) {
                setStories(result.data.stories);
                setStoriesFetchedAt(result.data.fetched_at);
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
                const res = await fetch("http://127.0.0.1:8000/api/stories");
                const income = await res.json();

                if (income.result.code === ResultCode.SUCCESS) {
                    setStories(income.result.data.stories);
                    setStoriesFetchedAt(income.result.data.fetched_at);
                }
                //to-do else if error durumunu kontrol et
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
                    {stories.map(story => (
                        <li key={story.id}>
                            <a href={story.url || "#"} target="_blank" rel="noreferrer">{story.title}</a>
                        </li>
                    ))}
                </ul>
                {storiesFetchedAt && (
                    <div className="fetched-at">
                        <p>Son Güncelleme: {storiesFetchedAt ? new Date(storiesFetchedAt * 1000).toLocaleString() : "Bilinmiyor"}</p>
                    </div>
                )}
            </div>
            <div className="dashboard-right">
                <div className="dashboard-right-placeholder">
                    HTML ile çekilen veriler buraya gelecek
                </div>
            </div>
        </div>



    );
}

export default Dashboard;

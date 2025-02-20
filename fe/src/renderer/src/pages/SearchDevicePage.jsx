import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import bgDarkmode from '../assets/bg-darkmode.png';
import modalBackground from '../assets/border-box.svg';
import deviceImage from '../assets/device.svg';
import plusSign from '../assets/plus-sign.svg';

// Mengambil BASE_URL dari environment variables
const BASE_URL = import.meta.env.VITE_BASE_URL;
const ENDPOINT = "/v1/check-device-status/";

const SearchDevicePage = () => {
  const navigate = useNavigate();
  const isFetchingRef = useRef(false); 

  useEffect(() => {
    const fetchData = async () => {
      if (isFetchingRef.current) return; 

      isFetchingRef.current = true; // Set fetching menjadi true
      try {
        const response = await fetch(`${BASE_URL}${ENDPOINT}`);
        const result = await response.json();
        console.log('API Response:', result);
        
        const { is_cable_connected, is_adb_connected } = result.data;

        if (is_cable_connected && is_adb_connected) {
          navigate('/device-info');
        } else if (is_cable_connected && !is_adb_connected) {
          navigate('/adb-device');
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        isFetchingRef.current = false; // Reset fetching state
      }
    };

    fetchData(); // Panggilan pertama
    const intervalId = setInterval(fetchData, 500); // Atur interval untuk memanggil fetchData setiap 1 detik

    return () => {
      clearInterval(intervalId); // Bersihkan interval saat komponen unmounted
    };
  }, [navigate]); // Menggunakan navigate sebagai dependensi

  return (
    <div
      className="h-screen w-screen flex flex-col justify-center items-center relative text-white"
      style={{
        backgroundImage: `url(${bgDarkmode})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Main Container */}
      <div
        className="relative w-[801px] h-[422px] p-6 flex flex-col justify-center items-center text-center"
        style={{
          backgroundImage: `url(${modalBackground})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        {/* Plus Sign (Kiri Atas Tengah) */}
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-12px] left-[-12px] w-6 h-6" />

        {/* Plus Sign (Kanan Bawah Tengah) */}
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-12px] right-[-12px] w-6 h-6"
        />

        {/* Device Image */}
        <img src={deviceImage} alt="Device" className="w-[325px] h-[207px] mb-6" />

        {/* Text Content */}
        <h2 className="text-2xl font-bold font-aldrich">Checking connection...</h2>
        <p className="text-gray-300 mt-2 font-aldrich">Please wait...</p>
      </div>
      {/* OTA Button */}
      <button
        className="absolute bottom-[52px] right-[52px] flex items-center justify-center w-[143px] h-[50px] bg-[#091817] text-sm font-bold text-white border border-[#4FD1C5] hover:bg-teal-700 font-roboto"
        onClick={() => navigate('/ota')}
      >
        <span>OTA</span>
      </button>
    </div>
  );
};

export default SearchDevicePage;

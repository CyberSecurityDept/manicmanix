import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import modalBackground from '../../assets/border/after-complete-border.svg';
import plusSign from '../../assets/plus-sign.svg';

const CompleteModal = ({ onClose }) => {
    const navigate = useNavigate();
  
    useEffect(() => {
      // Set delay 3 detik
      const timer = setTimeout(() => {
        navigate('/'); // Ganti '/home' dengan path home yang sesuai
      }, 3000);
  
      // Bersihkan timer ketika komponen unmount    
      return () => clearTimeout(timer);
    }, [navigate]);
  
  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich backdrop-blur-md"
      style={{
        background: 'rgba(0, 0, 0, 0.8)' 
      }}
    >
      <div
        className="relative w-[1001px] h-[89px] flex flex-col items-center justify-center p-8"
        style={{
          backgroundImage: `url(${modalBackground})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      >
        {/* Plus Sign (Top Left) */}
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute top-[-12px] left-[-12px] w-6 h-6"
        />

        {/* Plus Sign (Bottom Right) */}
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-12px] right-[-12px] w-6 h-6"
        />

        {/* Complete Confirmation Text */}
        <h2 className="text-xl text-white text-center justify-center">Perangkat anda aman untuk di cabut</h2>

      </div>
    </div>
  )
}

export default CompleteModal

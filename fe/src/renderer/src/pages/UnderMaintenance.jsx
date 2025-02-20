import React, { useEffect } from 'react'
import bgDarkmode from '../assets/bg-darkmode.png'
import modalBackground from '../assets/border-box.svg'
import maintenanceImage from '../assets/under-maintenance.png'
import plusSign from '../assets/plus-sign.svg'
import backIcon from '../assets/back-Icon.svg'
import { useNavigate } from 'react-router-dom'

const UnderMaintenance = () => {
  const navigate = useNavigate()

  return (
    <div
      className="h-screen w-screen flex flex-col justify-center items-center relative text-white"
      style={{
        backgroundImage: `url(${bgDarkmode})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Tombol Back */}
      <button
        className="absolute top-6 left-6 flex items-center justify-center focus:outline-none group transition-all duration-300"
        onClick={() => navigate('/')}
        style={{
          width: '68px',
          height: '68px',
          backgroundColor: 'transparent'
        }}
      >
        <img src={backIcon} alt="Back Icon" className="w-10 h-10" />
      </button>

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

        {/* Image (Maintenance) */}
        <img src={maintenanceImage} alt="Under Maintenance" className="w-[325px] h-[207px] mb-6" />

        {/* Text Content */}
        <h2 className="text-2xl font-semibold mb-2 font-aldrich">Under Maintenance</h2>
      </div>
    </div>
  )
}

export default UnderMaintenance

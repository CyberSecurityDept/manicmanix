import React from 'react'
import { useNavigate } from 'react-router-dom'
import cancelImage from '../../assets/cancel.svg'
import modalBackground from '../../assets/border/bawah-scanning-process.svg'
import plusSign from '../../assets/plus-sign.svg'
import button from '../../assets/border/button.svg'

const CancelModal = ({ onClose, onConfirm }) => {
  const navigate = useNavigate()

  const handleConfirm = () => {
    // Pindah ke halaman device-info ketika Yes diklik
    navigate('/device-info')
  }

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich"
      style={{
        background: 'rgba(0, 0, 0, 0.8)' // Semi-transparent background
      }}
    >
      <div
        className="relative w-[822px] h-[456px] flex flex-col items-center justify-center p-8"
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
          className="absolute top-[0px] left-[-12px] w-6 h-6"
        />

        {/* Plus Sign (Bottom Right) */}
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[0px] right-[-12px] w-6 h-6"
        />

        {/* Cancel Image */}
        <img src={cancelImage} alt="Cancel" className="w-[325px] h-[207px] mb-6" />

        {/* Cancel Confirmation Text */}
        <h2 className="text-xl font-bold mb-4 text-white">Are you sure you want to cancel?</h2>

        {/* Buttons Container */}
        <div className="flex space-x-4">
          <button
            className="w-[146px] h-[43px] bg-transparent text-white font-bold shadow-lg flex items-center justify-center"
            onClick={handleConfirm} // Panggil handleConfirm saat Yes diklik
            style={{
              backgroundImage: `url(${button})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          >
            Yes
          </button>
          <button
            className="w-[146px] h-[43px] bg-transparent text-white font-bold shadow-lg flex items-center justify-center"
            onClick={onClose} // Menutup modal saat No diklik
            style={{
              backgroundImage: `url(${button})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          >
            No
          </button>
        </div>
      </div>
    </div>
  )
}

export default CancelModal

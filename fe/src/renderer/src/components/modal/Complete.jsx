import React from 'react'
import completeImage from '../../assets/complete.svg'
import modalBackground from '../../assets/border/bawah-scanning-process.svg'
import plusSign from '../../assets/plus-sign.svg'
import button from '../../assets/border/button.svg'

const CompleteModal = ({ onClose, onConfirm }) => {
  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich"
      style={{
        background: 'rgba(0, 0, 0, 0.5)' // Semi-transparent background
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

        {/* Complete Image */}
        <img src={completeImage} alt="Complete" className="w-[325px] h-[207px] mb-6" />

        {/* Complete Confirmation Text */}
        <h2 className="text-xl font-bold mb-4 text-white">Are you sure you to Complete?</h2>

        {/* Buttons Container */}
        <div className="flex space-x-4">
          <button
            className="w-[146px] h-[43px] bg-transparent text-white font-bold shadow-lg flex items-center justify-center"
            onClick={onConfirm}
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
            onClick={onClose}
            style={{
              backgroundImage:  `url(${button})`,
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

export default CompleteModal

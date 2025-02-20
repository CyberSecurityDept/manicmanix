import React from 'react';
import deleteImage from '../../assets/delete.svg';
import modalBackground from '../../assets/border/bawah-scanning-process.svg';
import plusSign from '../../assets/plus-sign.svg';
import button from '../../assets/border/button.svg';

const DeleteModal = ({ onClose, onConfirm }) => {
  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich backdrop-blur-md"
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
        {/* Plus Signs and Remove Image */}
        <img src={plusSign} alt="Plus Sign" className="absolute top-[0px] left-[-12px] w-6 h-6" />
        <img src={plusSign} alt="Plus Sign" className="absolute bottom-[0px] right-[-12px] w-6 h-6" />
        <img src={deleteImage} alt="Remove" className="w-[325px] h-[207px] mb-6" />

        {/* Confirmation Text */}
        <h2 className="text-xl font-bold mb-4 text-white">Are you sure you want to delete?</h2>

        {/* Buttons */}
        <div className="flex space-x-4">
          <button
            className="w-[146px] h-[43px] bg-transparent text-white font-bold shadow-lg flex items-center justify-center"
            onClick={onConfirm} // Handle confirmation
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
            onClick={onClose} // Close modal on 'No'
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
  );
};

export default DeleteModal;

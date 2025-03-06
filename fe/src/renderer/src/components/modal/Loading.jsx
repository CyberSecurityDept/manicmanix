import React, { useState, useEffect } from 'react';
import plusSign from '../../assets/plus-sign.svg';
import loadingGif from '../../assets/loading.gif';

const Loading = ({ onClose, onProgressComplete }) => {
  console.log('onProgressComplete:', onProgressComplete);

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich backdrop-blur-md"
      style={{
        background: 'rgba(0, 0, 0, 0.8)',
      }}
    >
      <div
        className="relative w-[801px] h-[422px] flex flex-col items-center border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] justify-center p-8">
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-13px] left-[-13px] w-6 h-6" />
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-13px] right-[-13px] w-6 h-6"
        />

        <h1 className="text-2xl font-bold text-[#00E6E6]">Waiting</h1>

        {/* Ganti progress bar dengan loading GIF dan set ukuran menjadi 150px */}
        <div className="w-[150px] h-[150px] flex items-center justify-center mb-4">
          <img src={loadingGif} alt="Loading" style={{ width: '100px', height: '100px' }} />
        </div>
      </div>
    </div>
  );
};

export default Loading;

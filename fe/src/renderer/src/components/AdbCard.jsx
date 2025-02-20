import React from "react";

const AdbCard = ({ plusSign, adbImage, isCableConnected, isAdbConnected }) => {
  return (
    <div className="flex-1 relative">
      {/* Plus Sign at the border */}
      <img
        src={plusSign}
        alt="Plus Sign"
        className="absolute top-[-12px] left-[-12px] w-6 h-6"
      />
      <img
        src={plusSign}
        alt="Plus Sign"
        className="absolute bottom-[-11px] right-[-11px] w-6 h-6"
      />

      <div className="w-full h-[540px] max-h-[540px] border border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] text-white flex flex-col items-center justify-center p-4">
        {/* Content for Left Section */}
        <div className="text-center">
          <span className="text-3xl">Serial Number</span>
          <div className="mt-2 text-2xl">-</div>
        </div>

        {/* Gambar Device */}
        <img
          src={adbImage}
          alt="Device"
          className="w-[250px] h-[160px] object-contain mb-4"
        />

        {/* Status Box */}
        <div className="w-[382px] mt-6 p-4 border border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] text-white text-center">
          <div className="text-xl mb-2">Status</div>
          <div className="mt-1 text-lg">Cable: {isCableConnected ? 'Connected' : 'Not Connected'}</div>
          <div className="mt-1 text-lg">ADB: {isAdbConnected ? 'Connected' : 'Not Connected'}</div>
          <div className="mt-4 text-lg">Please Connect ADB</div>
        </div>
      </div>
    </div>
  );
};

export default AdbCard;

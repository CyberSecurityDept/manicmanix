import React from 'react'
import plusSign from '../../assets/plus-sign.svg'
import updateButtonBackground from '../../assets/border/update.svg'

const NewVersionModal = ({ onClose, onUpdate, updateData }) => {
  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich backdrop-blur-md"
      style={{
        background: 'rgba(0, 0, 0, 0.8)',
      }}
    >
      <div className="relative w-[801px] h-[305px] border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] flex flex-col items-center justify-center p-8">
        {/* Plus Signs */}
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-13px] left-[-13px] w-6 h-6" />
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-13px] right-[-12px] w-6 h-6"
        />

        {/* Title Text */}
        <h2 className="text-[#00FFE7] text-[48px] text-center">New Version Detected</h2>
        {updateData && (
          <p className="text-[#00FFE7] text-2xl mt-4">
            Latest Version: {updateData.latest_remote_tag}
          </p>
        )}

        {/* Check Update Button */}
        <button
          onClick={onUpdate}
          className="absolute bottom-[40px] w-[227px] h-[37px] text-white"
          style={{
            backgroundImage: `url(${updateButtonBackground})`,
            backgroundSize: 'cover',
            backgroundRepeat: 'no-repeat',
            backgroundPosition: 'center',
          }}
        >
          UPDATE
        </button>
      </div>
    </div>
  );
};

export default NewVersionModal

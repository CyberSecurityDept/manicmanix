// const RiskModal = ({ isOpen, onClose, riskData }) => {
//   if (!isOpen) return null

//   return (
//     <div className="fixed inset-0 flex items-center justify-center z-50">
//       <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
//       <div className="relative bg-gray-900 text-white w-full max-w-2xl rounded-lg shadow-xl">
//         {/* Header */}
//         <div className="flex justify-between items-center p-4 border-b border-gray-700">
//           <h2 className="text-xl font-semibold">
//             Malware Probability: <span className="text-red-500">60%</span>
//           </h2>
//           <button onClick={onClose} className="text-teal-400 hover:text-teal-300 text-xl">
//             ×
//           </button>
//         </div>

//         {/* Content */}
//         <div className="p-4">
//           {/* Malicious Section */}
//           <div className="mb-6">
//             <div className="flex justify-between items-center mb-2">
//               <h3 className="text-lg font-medium">Malicious</h3>
//               <span className="text-red-500">5/19</span>
//             </div>
//           </div>

//           {/* Common Section */}
//           <div className="mb-6">
//             <div className="flex justify-between items-center mb-2">
//               <h3 className="text-lg font-medium">Common</h3>
//               <span className="text-gray-400">16/26</span>
//             </div>
//           </div>

//           {/* Risk Items */}
//           <div className="space-y-4">
//             {[1, 2, 3].map((index) => (
//               <div key={index} className="bg-teal-900/30 rounded p-4">
//                 <div className="text-teal-400 font-medium mb-2">Android.permission.INTERNET</div>
//                 <p className="text-gray-300 text-sm">
//                   Malware can send your personal data to external servers without your knowledge.
//                   Used for network communication that can potentially steal sensitive information.
//                 </p>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }

// export default RiskModal

import { useState } from 'react'
import ButtonImage from '../../assets/modal_risk_button_active.svg' // Pastikan path gambar benar

const RiskModal = ({ isOpen, onClose }) => {
  const [activeButton, setActiveButton] = useState('malicious') // State untuk mengelola button aktif

  if (!isOpen) return null

  return (
    <>
      {/* Dark Overlay */}
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40" onClick={onClose} />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50 font-aldrich">
        <div
          className="bg-gradient-to-b from-[#0C1612] to-[#091817] border-t-2 border-b border-[#0C9A8D] w-full max-w-6xl p-6 text-white shadow-lg relative"
          style={{ boxShadow: 'inset 0px -4px 13.9px 0px rgba(79, 209, 197, 0.5)' }}
        >
          {/* Header */}
          <div className="flex flex-col items-center">
            <h2 className="text-xl mb-2">
              Malware Probability: <span className="text-red-500">60%</span>
            </h2>
            <button
              onClick={onClose}
              className="text-[#00B3A2] hover:text-emerald-300 text-xl absolute top-5 right-6"
            >
              ✕
            </button>
          </div>

          {/* Divider Line */}
          <div className="w-full h-[1px] bg-[#00B3A2]/30 my-4" />

          {/* Main Content - Split Layout */}
          <div className="flex gap-4 mt-6">
            {/* Left Section */}
            <div className="w-1/5 relative flex flex-col gap-7">
              {/* Malicious Button */}
              <button
                onClick={() => setActiveButton('malicious')}
                className={`relative p-3 text-center transition-all duration-300 w-full ${
                  activeButton === 'malicious' ? '' : 'bg-[#0C1612]/50 backdrop-blur-sm opacity-75' // Non-active state
                }`}
                style={
                  activeButton === 'malicious'
                    ? {
                        backgroundImage: `url(${ButtonImage})`,
                        backgroundSize: 'contain',
                        backgroundRepeat: 'no-repeat',
                        backgroundPosition: 'center'
                      }
                    : {}
                }
              >
                {/* Gradient Background */}
                {activeButton === 'malicious' && (
                  <div className="h-24 absolute inset-0 gradient-custom -right-2 -top-1 z-0"></div>
                )}
                {/* Rectangle */}
                {activeButton === 'malicious' && (
                  <div className="w-2 h-24 bg-[#05C7B4] absolute -right-4 -top-1 bottom-0 z-20" />
                )}
                <div className="text-lg mb-2">Malicious</div>
                <div>
                  <span className="text-red-500">5</span>
                  <span className="text-white">/19</span>
                </div>
              </button>

              {/* Common Button */}
              <button
                onClick={() => setActiveButton('common')}
                className={`relative p-3 text-center transition-all duration-300 w-full ${
                  activeButton === 'common' ? '' : 'bg-[#0C1612]/50 backdrop-blur-sm opacity-75' // Non-active state
                }`}
                style={
                  activeButton === 'common'
                    ? {
                        backgroundImage: `url(${ButtonImage})`,
                        backgroundSize: 'contain',
                        backgroundRepeat: 'no-repeat',
                        backgroundPosition: 'center'
                      }
                    : {}
                }
              >
                {/* Gradient Background */}
                {activeButton === 'common' && (
                  <div className="h-24 absolute inset-0 gradient-custom -right-2 -top-1 z-0"></div>
                )}
                {/* Rectangle */}
                {activeButton === 'common' && (
                  <div className="w-2 h-24 bg-[#05C7B4] absolute -right-4 -top-1 bottom-0 z-20" />
                )}
                <div className="text-lg mb-2">Common</div>
                <div>
                  <span className="text-red-500">5</span>
                  <span className="text-white">/19</span>
                </div>
              </button>
            </div>

            {/* Right Section */}
            <div className="w-4/5 border-l-2 border-t-2 border-[#23635D] p-4">
              <div className="bg-[#00B3A2] grid grid-cols-2 p-2">
                <div className="text-[#0B180F] font-normal">Malicious Item</div>
                <div className="text-[#0B180F] font-normal">Description</div>
              </div>

              <div className="space-y-4 mt-2">
                {Array(5)
                  .fill(null)
                  .map((_, index) => (
                    <div key={index} className="grid grid-cols-2 gap-4 p-2">
                      <div>Android.permission.INTERNET</div>
                      <div className="text-sm">
                        Malware can send your personal data to external servers without your
                        knowledge. Used for network communication that can potentially steal
                        sensitive information.
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default RiskModal

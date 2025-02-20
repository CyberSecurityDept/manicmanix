import { useNavigate } from 'react-router-dom'
import bgDarkmode from '../assets/bg-darkmode.png'
import backIcon from '../assets/back-Icon.svg'
import securityLogo from '../assets/logo_security.png'

const InformationPage = () => {
  const navigate = useNavigate()
  return (
    <div
      className="w-full h-screen relative bg-cover flex flex-col items-center justify-center font-aldrich bg-[#000201]"
      style={{
        backgroundImage: `url(${bgDarkmode})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Tombol Back */}
      <button className="absolute top-6 left-6" onClick={() => navigate('/ota')}>
        <img src={backIcon} alt="Back Icon" className="w-[48px] h-[48px]" />
      </button>

      <div className="flex flex-col items-center mb-9">
        <img src={securityLogo} alt="Security Logo" className="w-[600px] mb-8" />
        <h1 className="text-[#029D8C] text-4xl tracking-wider mb-4">SECURITY SCANNING</h1>
        <p className="text-white text-lg tracking-wider">App Version 24.3.2</p>
      </div>

      <div className="flex justify-center gap-16">
        {/* Serial Number */}
        <div className="relative w-[400px] h-[120px] flex flex-col justify-center items-center">
          <div
            className="absolute inset-0 bg-gradient-to-b from-[#0C1612] to-[#091817] border-t border-b border-[#0C9A8D]"
            style={{ boxShadow: 'inset 0px -4px 13.9px 0px rgba(79, 209, 197, 0.5)' }}
          />
          <h2 className="relative text-[#4FD1C5] text-xl mb-2 tracking-wider">Serial Number</h2>
          <p className="relative text-white text-lg tracking-wider">XPLO-P23CY-J1QS-SCS1</p>
        </div>

        {/* License */}
        <div className="relative w-[400px] h-[120px] flex flex-col justify-center items-center">
          <div
            className="absolute inset-0 bg-gradient-to-b from-[#0C1612] to-[#091817] border-t border-b border-[#0C9A8D]"
            style={{ boxShadow: 'inset 0px -4px 13.9px 0px rgba(79, 209, 197, 0.5)' }}
          />
          <h2 className="relative text-[#4FD1C5] text-xl mb-2 tracking-wider">License</h2>
          <p className="relative text-white text-lg tracking-wider">XPLO-P23CY-J1QS-SCS1</p>
        </div>
      </div>
    </div>
  )
}

export default InformationPage

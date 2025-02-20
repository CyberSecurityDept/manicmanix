import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'
import backIcon from '../assets/chevronleft.svg';  
import settingsIcon from '../assets/settings.svg'; 
import ActiveButton from '../assets/button-aktif.svg'; 
import DeactiveButton from '../assets/navbar-nonaktif.svg'; 
import Spotlight from '../assets/dashboard-spotlight.png';  

const Navbar = () => {
  const navigate = useNavigate()
  
  // State untuk menentukan tombol yang aktif
  const [activeButton, setActiveButton] = useState('Dashboard');

  return (
    <div className="relative w-screen h-[10vh] flex items-center justify-between px-6 mt-[-180px] ">
      {/* Button Back */}
      <button className="text-white flex items-center" onClick={() => navigate('/')}>
        <img src={backIcon} alt="Back" className="w-16 h-16" />
      </button>

      {/* Navbar (Middle Section) */}
      <div className="flex space-x-14 relative mt-[100px]">
        {/* Tombol Dashboard */}
        <button
          onClick={() => setActiveButton('Dashboard')}
          className="text-white w-56 h-11 bg-cover bg-center flex items-center justify-center relative"
          style={{
            backgroundImage: activeButton === 'Dashboard' ? `url(${ActiveButton})` : `url(${DeactiveButton})`
          }}
        >
          Dashboard
          {/* Spotlight untuk Dashboard */}
          {activeButton === 'Dashboard' && (
            <img
              src={Spotlight}
              alt="Dashboard Spotlight"
              className="absolute -bottom-[26px] left-1/2 transform -translate-x-1/2"
              style={{ width: '200px' }}  
            />
          )}
        </button>

        {/* Tombol Case Management */}
        <button
          onClick={() => setActiveButton('Case Management')}
          className="text-white w-56 h-11 bg-cover bg-center flex items-center justify-center relative"
          style={{
            backgroundImage: activeButton === 'Case Management' ? `url(${ActiveButton})` : `url(${DeactiveButton})`
          }}
        >
          Case Management
          {/* Spotlight untuk Case Management */}
          {activeButton === 'Case Management' && (
            <img
              src={Spotlight}
              alt="Case Management Spotlight"
              className="absolute -bottom-[26px] left-1/2 transform -translate-x-1/2"
              style={{ width: '200px' }}  // Ubah ukuran sesuai kebutuhan
            />
          )}
        </button>

        {/* Tombol Device Management */}
        <button
          onClick={() => setActiveButton('Device Management')}
          className="text-white w-56 h-11 bg-cover bg-center flex items-center justify-center relative"
          style={{
            backgroundImage: activeButton === 'Device Management' ? `url(${ActiveButton})` : `url(${DeactiveButton})`
          }}
        >
          Device Management
          {/* Spotlight untuk Device Management */}
          {activeButton === 'Device Management' && (
            <img
              src={Spotlight}
              alt="Device Management Spotlight"
              className="absolute -bottom-[26px] left-1/2 transform -translate-x-1/2"
              style={{ width: '200px' }}  // Ubah ukuran sesuai kebutuhan
            />
          )}
        </button>
      </div>

      {/* Button Settings */}
      <button className="text-white">
        <img src={settingsIcon} alt="Settings" className="w-16 h-16" />
      </button>
    </div>
  );
};

export default Navbar;

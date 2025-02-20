import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DeviceCard from '../../components/DeviceCard';
import AdbCard from '../../components/AdbCard'
import DeviceInfoCard from '../../components/DeviceInfoCard'
import bgDarkmode from '../../assets/bg-darkmode.png'
import headerImage from '../../assets/Header.png'
import backIcon from '../../assets/chevronleft.svg'
import plusSign from '../../assets/plus-sign.svg'
import deviceImage from '../../assets/device.svg'
import adbImage from '../../assets/adb.svg';
import chevronDownIcon from '../../assets/chevron-down.svg'
import bgButton from '../../assets/scan.svg'

// Mengambil BASE_URL dari environment variables
const BASE_URL = import.meta.env.VITE_BASE_URL;

const AddDevicePage = () => {
  const navigate = useNavigate()

  const [deviceStatus, setDeviceStatus] = useState({
    is_cable_connected: false,
    is_adb_connected: false,
  });
  
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const [isDropdownCase, setIsDropdownCaseOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [selectedPerson, setSelectedPerson] = useState('Pick Person')
  const [selectedCase, setSelectedCase] = useState('Pick Case')

  const [people, setPeople] = useState([
    { name: 'Arlene McCoy', case: 'Pembobolan ATM BCA Simatupang' },
    { name: 'Albert Flores', case: 'Pembobolan ATM BCA Simatupang' },
    { name: 'Jane Cooper', case: 'Pembobolan ATM BCA Simatupang' },
    { name: 'Kristin Watson', case: 'Pembobolan ATM BCA Simatupang' },
    { name: 'Marvin McKinney', case: 'Pembobolan ATM BCA Simatupang' },
  ]);
  
  const caseName = [
    { case: 'Pembobolan ATM BCA Simatupang' },
    { case: 'Pembobolan ATM BCA Simatupang' },
    { case: 'Pembobolan ATM BCA Simatupang' },
    { case: 'Pembobolan ATM BCA Simatupang' },
    { case: 'Pembobolan ATM BCA Simatupang' }
  ]

  const handleSelectPerson = (personName) => {
    setSelectedPerson(personName)
    setIsDropdownOpen(false)
  }
  const handleSelectCase = (caseName) => {
    setSelectedCase(caseName)
    setIsDropdownCaseOpen(false)
  }
  
  const handleAddNewFromSearch = () => {
    // Periksa apakah input kosong atau sudah ada di daftar
    if (search.trim() === '') {
      alert('Please enter a value!');
      return;
    }
  
    if (people.some((person) => person.name.toLowerCase() === search.toLowerCase())) {
      alert('This name already exists in the list!');
      return;
    }
  
    // Tambahkan nama baru ke daftar
    const updatedPeople = [...people, { name: search, case: 'Unknown Case' }];
    setPeople(updatedPeople);
    setSearch(''); // Reset search field
  };

  // Check if both Add Person and Add Case have been filled
  const isNextButtonDisabled = selectedPerson === 'Pick Person' || selectedCase === 'Pick Case'

  // useEffect(() => {
  //   // Fetch device status
  //   const fetchDeviceStatus = async () => {
  //     try {
  //       const response = await fetch(`${BASE_URL}/v1/check-device-status/`);
  //       const result = await response.json();
  //       if (result.status === 200) {
  //         setDeviceStatus(result.data);
  //       }
  //     } catch (error) {
  //       console.error('Failed to fetch device status:', error);
  //     }
  //   };

  //   // Fetch device overview if cable and ADB are connected
  //   const fetchDeviceInfo = async () => {
  //     if (deviceStatus.is_cable_connected && deviceStatus.is_adb_connected) {
  //       try {
  //         const response = await fetch(`${BASE_URL}/v1/device-overview/`);
  //         const result = await response.json();
  //         if (result.status === 200) {
  //           setDeviceInfo(result.data);
  //           localStorage.setItem('serial_number', result.data.serial_number);
  //         }
  //       } catch (error) {
  //         console.error('Failed to fetch device info:', error);
  //       }
  //     }
  //   };

  //   fetchDeviceStatus();
  //   fetchDeviceInfo();
  // }, [deviceStatus]);

  // Function to render card at left section
  const renderLeftSection = () => {
    const { is_cable_connected, is_adb_connected } = deviceStatus;

    if (is_cable_connected && is_adb_connected && deviceInfo) {
      return (
        <DeviceInfoCard
          image={deviceInfo.image}
          model={deviceInfo.model}
          imei1={deviceInfo.imei1}
          imei2={deviceInfo.imei2}
          androidVersion={deviceInfo.android_version}
          lastScan={deviceInfo.last_scan}
          securityPatch={deviceInfo.security_patch}
          serialNumber={deviceInfo.serial_number}
        />
      );
    }

    if (is_cable_connected && !is_adb_connected) {
      return (
        <AdbCard
          plusSign={plusSign}
          deviceImage={adbImage}
          cableStatus="Connected"
          adbStatus="Not Connected"
        />
      );
    }

    return (
      <DeviceCard
        plusSign={plusSign}
        deviceImage={deviceImage}
        isCableConnected={is_cable_connected}
        isAdbConnected={is_adb_connected}
      />
    );
  };


  return (
    <div
      className="min-h-screen bg-cover bg-no-repeat bg-center font-aldrich"
      style={{ backgroundImage: `url(${bgDarkmode})` }}
    >
      {/* Header Section */}
      <div className="relative">
        <img src={headerImage} alt="Header" className="w-full h-[85px] object-cover" />
        <h1 className="absolute left-1/2 transform -translate-x-1/2 top-6 text-3xl text-white tracking-widest uppercase">
          Add Device
        </h1>
        <button className="absolute top-16 left-6 flex items-center" onClick={() => navigate('/dashboard')} >
          <img src={backIcon} alt="Back" className="w-16 h-16" />
        </button>
      </div>

      {/* Main Content Section */}
      <div className="flex items-center justify-center mt-36">
        <div className="flex gap-8 w-full max-w-6xl">
          {/* Left Section */}
          {/* <DeviceInfoCard plusSign={plusSign} deviceImage={deviceImage} isCableConnected={deviceStatus.is_cable_connected} isAdbConnected={deviceStatus.is_adb_connected}/> */}
          {renderLeftSection()}

          {/* Right Section */}
          <div className="flex flex-col flex-1 space-y-8">
            {/* Add Person Section */}
            <div className="flex-1 p-8 border border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] text-white flex flex-col items-center justify-center relative">
              <span className="text-2xl mb-2">Add Person</span>
              <button
                className="w-full px-4 py-2 bg-transparent border border-[#4FD1C5] text-white text-lg flex justify-between items-center"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              >
                {selectedPerson}
                <img
                  src={chevronDownIcon}
                  alt="Chevron Down"
                  className={`w-8 h-8 transition-transform duration-300 ${
                    isDropdownOpen ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>

              {isDropdownOpen && (
                <div className="absolute top-full mt-[-60px] w-11/12 p-8 bg-gradient-to-b from-[#091817] to-[#0C1612] shadow-lg z-10 border border-y-[#0C9A8D] border-x-[#05564F]">
                  <div className="relative flex items-center justify-between mb-4">
                    {/* Search Input */}
                    <div className="flex items-center w-full max-w-xs border border-[#4FD1C5] rounded px-3 py-2">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={2}
                        stroke="white"
                        className="w-5 h-5 mr-2"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M21 21l-4.35-4.35M11 18a7 7 0 100-14 7 7 0 000 14z"
                        />
                      </svg>
                      <input
                        type="text"
                        placeholder="Search..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="bg-transparent flex-1 text-white placeholder-gray-500 focus:outline-none"
                      />
                    </div>

                    {/* Add New Button */}
                    <button className="ml-4 text-[#4FD1C5] font-semibold hover:underline"
                    onClick={handleAddNewFromSearch}>
                      Add new
                    </button>
                  </div>

                  <div className="h-52 overflow-y-auto custom-scrollbar pr-4">
                    {people
                      .filter((person) => person.name.toLowerCase().includes(search.toLowerCase()))
                      .map((person, index) => (
                        <div
                          key={index}
                          className="py-2 border-b border-[#4FD1C5] cursor-pointer"
                          onClick={() => handleSelectPerson(person.name)}
                        >
                          <p className="text-white font-semibold">{person.name}</p>
                          <p className="text-[#4FD1C5] text-sm">Case: {person.case}</p>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>

            {/* Add Case Section */}
            <div className="flex-1 p-8 border border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] text-white flex flex-col items-center justify-center relative">
              <span className="text-2xl mb-2">Add Case</span>
              <button
                className="w-full px-4 py-2 bg-transparent border border-[#4FD1C5] text-white text-lg flex justify-between items-center"
                onClick={() => setIsDropdownCaseOpen(!isDropdownCase)}
              >
                {selectedCase}
                <img
                  src={chevronDownIcon}
                  alt="Chevron Down"
                  className={`w-8 h-8 transition-transform duration-300 ${
                    isDropdownCase ? 'rotate-180' : 'rotate-0'
                  }`}
                />
              </button>

              {isDropdownCase && (
                <div className="absolute top-full mt-[-60px] w-full p-8 bg-gradient-to-b from-[#091817] to-[#0C1612] shadow-lg z-10 border border-y-[#0C9A8D] border-x-[#05564F]">
                  <div className="relative flex items-center justify-between mb-4">
                    {/* Search Input */}
                    <div className="flex items-center w-full max-w-sm border border-[#4FD1C5] rounded px-3 py-2">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={2}
                        stroke="white"
                        className="w-5 h-5 mr-2"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M21 21l-4.35-4.35M11 18a7 7 0 100-14 7 7 0 000 14z"
                        />
                      </svg>
                      <input
                        type="text"
                        placeholder="Search..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="bg-transparent flex-1 text-white placeholder-gray-500 focus:outline-none"
                      />
                    </div>

                    {/* Add New Button */}
                    <button className="ml-4 text-[#4FD1C5] font-semibold hover:underline">
                      Add new
                    </button>
                  </div>

                  <div className="h-36 overflow-y-auto custom-scrollbar pr-4">
                    {caseName
                      .filter((caseName) =>
                        caseName.case.toLowerCase().includes(search.toLowerCase())
                      )
                      .map((caseName, index) => (
                        <div
                          key={index}
                          className="py-2 border-b border-[#4FD1C5] cursor-pointer"
                          onClick={() => handleSelectCase(caseName.case)}
                        >
                          <p className="text-[#4FD1C5] text-sm">Case: {caseName.case}</p>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      {/* Next Button */}
      <button
        className={`absolute bottom-6 right-8 w-[140px] h-[60px] bg-cover bg-center ${
          isNextButtonDisabled ? 'opacity-50 cursor-not-allowed' : ''
        }`}
        style={{ backgroundImage: `url(${bgButton})` }}
        onClick={() => {
          if (!isNextButtonDisabled) {
            console.log('Next button clicked')
          }
        }}
        disabled={isNextButtonDisabled}
      >
        {/* Optional: Add text inside the button */}
        <span className="text-white text-xl font-semibold">Next</span>
      </button>
    </div>
  )
}

export default AddDevicePage

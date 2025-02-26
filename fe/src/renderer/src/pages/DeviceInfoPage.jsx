/* eslint-disable no-unused-vars */
import React, { useState, useEffect, useRef } from 'react'
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'
import CreatableSelect from 'react-select/creatable'
import { useNavigate } from 'react-router-dom'
import bgDarkmode from '../assets/bg-darkmode.png'
import plusSign from '../assets/plus-sign.svg'
import backIcon from '../assets/back-Icon.svg'
import buttonScan from '../assets/Scan.svg'
import historyIcon from '../assets/history-icon.svg'

// Mengambil BASE_URL dari environment variables
const BASE_URL = import.meta.env.VITE_BASE_URL;

const DeviceInfoPage = () => {
  const navigate = useNavigate();

  // State untuk menyimpan data API
  const [deviceData, setDeviceData] = useState(null);
  const [nameOptions, setNameOptions] = useState([]);
  const [selectedName, setSelectedName] = useState(null); // State untuk menyimpan nama yang dipilih
  const [loading, setLoading] = useState(true);

  const hasFetchedData = useRef(false); // Melacak apakah data sudah di-fetch

  // Fungsi untuk memanggil API saat komponen dimuat
  useEffect(() => {
    const fetchData = async () => {
      if (hasFetchedData.current) return; // Cegah pemanggilan ulang
      hasFetchedData.current = true;

      try {
        const response = await fetch(`${BASE_URL}/v1/device-overview`);
        const data = await response.json();
        console.log('Device Data:', data);

        if (data.data) {
          setDeviceData(data.data); // Simpan data device ke state
          setNameOptions([{ value: data.data.name, label: data.data.name }]);
          // Simpan serial number ke local storage
          localStorage.setItem('serial_number', data.data.serial_number);
        } else {
          console.error('Data device tidak tersedia.');
        }
      } catch (error) {
        console.error('Error fetching device data:', error);
      } finally {
        setLoading(false); // Matikan loading setelah fetch selesai
      }
    };

    fetchData();
  }, []);

  // Tambahkan pengecekan: jika loading selesai dan deviceData masih null, tampilkan pesan error
  if (!loading && !deviceData) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-white">Gagal memuat data device. Silakan coba lagi.</p>
      </div>
    );
  }

  // Fungsi untuk menangani opsi baru yang dibuat
  const handleCreate = (inputValue) => {
    const newOption = { value: inputValue, label: inputValue };
    setNameOptions((prevOptions) => [...prevOptions, newOption]);
    setSelectedName(newOption);
  };

  // Fungsi untuk memanggil API saat tombol Fast Scan diklik
  const handleFastScan = () => {
    // Pastikan deviceData tidak null sebelum mengakses serial_number
    if (!selectedName || !selectedName.value || !deviceData || !deviceData.serial_number) {
      alert('Name atau Serial Number tidak tersedia');
      return;
    }

    const requestUrl = `${BASE_URL}/v1/fast-scan/${deviceData.serial_number}?name=${selectedName.value}`;
    console.log('Request URL:', requestUrl);

    fetch(requestUrl, {
      method: 'POST',
      headers: {
        accept: 'application/json'
      }
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log('Fast Scan Response:', data);
        if (data.status === 200 && data.message === 'Fast scan started successfully in the background') {
          navigate('/fast-scan');
        } else {
          console.error('Fast scan failed:', data);
          alert('Failed to start fast scan. Please try again.');
        }
      })
      .catch((error) => {
        console.error('Error during Fast Scan:', error);
      });
  };

  // Fungsi untuk memanggil API saat tombol Full Scan diklik
  const handleFullScan = () => {
    if (!selectedName || !selectedName.value || !deviceData || !deviceData.serial_number) {
      alert('Name atau Serial Number tidak tersedia');
      return;
    }

    const requestUrl = `${BASE_URL}/v1/full-scan/${deviceData.serial_number}?name=${selectedName.value}`;
    console.log('Request URL:', requestUrl);

    fetch(requestUrl, {
      method: 'POST',
      headers: {
        accept: 'application/json'
      }
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log('Full Scan Response:', data);
        if (data.status === 200 && data.message === 'Full scan started successfully in the background') {
          navigate('/full-scan');
        } else {
          console.error('Full scan failed:', data);
          alert('Failed to start full scan. Please try again.');
        }
      })
      .catch((error) => {
        console.error('Error during Full Scan:', error);
      });
  };

  return (
    <div
      className="h-screen w-screen flex flex-col justify-center items-center relative text-white font-aldrich"
      style={{
        backgroundImage: `url(${bgDarkmode})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Tombol Back */}
      <button
        className="absolute top-6 left-6 flex items-center justify-center focus:outline-none group transition-all duration-300"
        onClick={() => navigate('/')}
        style={{
          width: '68px',
          height: '68px',
          backgroundColor: 'transparent'
        }}
      >
        <img src={backIcon} alt="Back Icon" className="w-10 h-10" />
      </button>

      {/* Tombol History */}
      <button
        className="absolute top-6 right-6 flex items-center focus:outline-none group"
        onClick={() => navigate('/history')}
      >
        <div className="relative w-[53px] h-[53px] flex items-center justify-center rounded-full border-2 border-[#4FD1C5] bg-[#0B1E1E] shadow-lg -mr-4 z-10 group-hover:bg-teal-700 transition-all duration-300">
          <img src={historyIcon} alt="History Icon" className="w-6 h-6" />
        </div>
        <div className="w-[134px] h-[40px] bg-[#0B1E1E] rounded-r-lg border-t-2 border-b-2 border-r-2 border-[#4FD1C5] shadow-lg flex items-center justify-center group-hover:bg-teal-700 transition-all duration-300">
          <span className="text-lg tracking-wide text-white group-hover:text-black font-aldrich">
            HISTORY
          </span>
        </div>
      </button>

      {/* Main Container */}
      {loading ? (
        <Skeleton
          width={801}
          baseColor="#0B0C0B"
          highlightColor="#064039"
          className="w-[801px] h-[480px]"
        />
      ) : (
        <div
          className="relative w-[801px] h-[480px] p-6 shadow-lg bg-black bg-opacity-30 text-center"
          style={{
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            boxShadow: 'inset 0 0 15px 4px rgba(4, 209, 197, 0.5)',
            border: '1px solid transparent'
          }}
        >
          {/* Plus Sign (Kiri Atas Tengah) */}
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute top-[-12px] left-[-12px] w-6 h-6"
          />

          {/* Plus Sign (Kanan Bawah Tengah) */}
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute bottom-[-12px] right-[-12px] w-6 h-6"
          />

          <h2 className="text-2xl font-bold mb-4">Device Specification</h2>

          {/* Detail Device Section */}
          <div
            className="w-[740px] h-[300px] flex items-center justify-start mb-[21px] p-4 border border-y-[#0C9A8D] border-x-[#05564F]"
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
              boxShadow:
                '0px -9px 0px -7px rgba(4, 209, 197, 0.5), 0px 11px 0px -9px rgba(4, 209, 197, 0.5)'
            }}
          >
            {/* Gambar Device */}
            <div className="flex justify-center p-4">
              <div className="p-2 rounded-lg w-[200px] h-[200px]">
                {loading ? (
                  <Skeleton className="w-full h-full" />
                ) : (
                  <img
                    src={deviceData?.image}
                    alt="Device"
                    className="w-full h-full object-contain"
                  />
                )}
              </div>
            </div>

            {/* Informasi Device */}
            <div className="w-[432px] h-[187px] flex-auto justify-between">
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">Name</span>
                  <span className="mx-2">:</span>
                  {loading ? (
                    <Skeleton width={150} />
                  ) : (
                    <CreatableSelect
                      value={selectedName}
                      onChange={setSelectedName}
                      options={nameOptions}
                      placeholder="Input name"
                      onCreateOption={handleCreate}
                      className="text-black flex-1 text-right w-[150px]"
                      isClearable
                      styles={{
                        control: (base, state) => ({
                          ...base,
                          borderColor: state.isFocused ? '#0C9A8D' : '#0C9A8D',
                          boxShadow: state.isFocused ? '0 0 0 1px #0C9A8D' : null,
                          '&:hover': {
                            borderColor: '#0C9A8D'
                          }
                        })
                      }}
                    />
                  )}
                </div>
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">Model</span>
                  <span className="mx-2">:</span>
                  <span className="flex-1 text-right">
                    {loading ? <Skeleton width={100} /> : deviceData?.model}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">IMEI1</span>
                  <span className="mx-2">:</span>
                  <span className="flex-1 text-right">
                    {loading ? <Skeleton width={150} /> : deviceData?.imei1}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">IMEI2</span>
                  <span className="mx-2">:</span>
                  <span className="flex-1 text-right">
                    {loading ? <Skeleton width={150} /> : deviceData?.imei2}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">Android Version</span>
                  <span className="mx-2">:</span>
                  <span className="flex-1 text-right">
                    {loading ? <Skeleton width={50} /> : deviceData?.android_version}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">Last Scan</span>
                  <span className="mx-2">:</span>
                  <span className="flex-1 text-right">
                    {loading ? <Skeleton width={150} /> : deviceData?.last_scan}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">Security Patch</span>
                  <span className="mx-2">:</span>
                  <span className="flex-1 text-right">
                    {loading ? <Skeleton width={150} /> : deviceData?.security_patch}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="w-1/3 text-left">Serial Number</span>
                  <span className="mx-2">:</span>
                  <span className="flex-1 text-right">
                    {loading ? <Skeleton width={150} /> : deviceData?.serial_number}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tombol Scan */}
      <div className="flex space-x-8 mt-6 font-aldrich">
        <button
          className={`w-[389px] h-[120px] text-xl font-bold bg-transparent border border-teal-400 hover:bg-teal-700 rounded-md shadow-lg flex flex-col justify-center items-center relative ${
            !selectedName ? 'cursor-not-allowed opacity-50' : ''
          }`}
          style={{
            backgroundImage: `url(${buttonScan})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
          onClick={handleFastScan}
          disabled={!selectedName}
        >
          FAST SCAN
          <p className="text-sm mt-2">Quickly check installed apps and accessibility settings.</p>
          <div className="absolute inset-0 bg-teal-700 opacity-0 hover:opacity-30 transition-opacity"></div>
        </button>

        {/* Full Scan Button */}
        <button
          className={`w-[389px] h-[120px] text-xl font-bold bg-transparent border border-teal-400 hover:bg-teal-700 rounded-md shadow-lg flex flex-col justify-center items-center relative ${
            !selectedName ? 'cursor-not-allowed opacity-50' : ''
          }`}
          style={{
            backgroundImage: `url(${buttonScan})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
          onClick={handleFullScan}
          disabled={!selectedName}
        >
          FULL SCAN
          <p className="text-sm mt-2">Perform a comprehensive security check of your device.</p>
          <div className="absolute inset-0 bg-teal-700 opacity-0 hover:opacity-30 transition-opacity"></div>
        </button>
      </div>

      {/* OTA Button */}
      <button
        className="absolute bottom-[52px] right-[52px] flex items-center justify-center w-[143px] h-[50px] bg-[#091817] text-sm font-bold text-white border border-[#4FD1C5] hover:bg-teal-700 font-roboto"
        onClick={() => navigate('/ota')}
      >
        <span>OTA</span>
      </button>
    </div>
  );
};

export default DeviceInfoPage;

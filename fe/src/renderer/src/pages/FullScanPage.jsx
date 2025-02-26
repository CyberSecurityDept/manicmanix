/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import modalBackground from '../assets/border/bawah-scanning.svg'
import ArrowPattern from '../components/ArrowPattern'
import CancelModal from '../components/modal/Cancel'
import bgImage from '../assets/bg-darkmode.png'
import plusSign from '../assets/plus-sign.svg'
import buttonViewMore from '../assets/border/view-more.svg'
import buttonCancel from '../assets/border/cancel.svg'

// Mengambil BASE_URL dari environment variables
const BASE_URL = import.meta.env.VITE_BASE_URL

const FullScanPage = () => {
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [progress, setProgress] = useState(0)
  const [logData, setLogData] = useState([])
  const [scanComplete, setScanComplete] = useState(false)
  const [showAllLogs, setShowAllLogs] = useState(false)
  const [serialNumber, setSerialNumber] = useState(null)
  const [showReconnectModal, setShowReconnectModal] = useState(false)
  const [reconnectTriggered, setReconnectTriggered] = useState(false)

  const openModal = () => setIsModalOpen(true)
  const closeModal = () => setIsModalOpen(false)

  const handleCancelScanning = () => {
    setIsModalOpen(false)
    navigate('/')
  }

  const formatDate = (datetimeString) => {
    if (!datetimeString || !datetimeString.includes(' ')) {
      return 'Unknown'
    }
    const [datePart] = datetimeString.split(' ')
    const [year, month, day] = datePart.split('-')
    return `${day}/${month}/${year}`
  }

  const formatTime = (datetimeString) => {
    if (!datetimeString || !datetimeString.includes(' ')) {
      return 'Unknown'
    }
    const [, timePart] = datetimeString.split(' ')
    const [hours, minutes] = timePart.split(':')
    return `${hours}:${minutes}`
  }

  useEffect(() => {
    // Mengambil serial_number dari localStorage
    const savedSerialNumber = localStorage.getItem('serial_number')
    if (savedSerialNumber) {
      setSerialNumber(savedSerialNumber)
    } else {
      console.error('Serial number not found in localStorage.')
      navigate('/') // Pindah ke halaman lain jika serial_number tidak ada
    }
  }, [navigate])

  useEffect(() => {
    let interval // Declare interval variable

    const fetchScanProgress = async () => {
      if (!serialNumber) return // Tunggu sampai serialNumber tersedia
      try {
        const response = await fetch(`${BASE_URL}/v1/fullscan-progress/${serialNumber}`)
        const data = await response.json()

        if (data.status === 200) {
          setProgress(parseInt(data.data.scan_percentage))
          setScanComplete(data.data.scan_complete)
          setLogData(data.data.log_process)

          // Jika progress sudah mencapai 100%, hentikan interval
          if (data.data.scan_percentage === 100) {
            clearInterval(interval)
          }
        } else {
          console.error('Failed to fetch scan progress')
        }
      } catch (error) {
        console.error('Error fetching scan progress:', error)
      }
    }

    // Mulai interval jika serial_number sudah ada
    if (serialNumber) {
      const delay = setTimeout(() => {
        interval = setInterval(fetchScanProgress, 3000) // Panggil API setiap 3 detik
      }, 2000) // Delay sebelum memulai fetch API

      return () => {
        clearInterval(interval) // Clean up interval on component unmount
        clearTimeout(delay) // Clean up timeout on component unmount
      }
    }
  }, [serialNumber]) // Jalankan efek saat serialNumber tersedia

  useEffect(() => {
    if (progress === 100 && serialNumber) {
      let isMounted = true // Untuk mencegah update state jika komponen sudah unmount
      const pollInterval = 3000 // Interval polling dalam milidetik

      const fetchResult = async () => {
        try {
          const resultUrl = `${BASE_URL}/v1/result-fullscan?serial_number=${serialNumber}&scan_type=full-scan`
          const response = await fetch(resultUrl, {
            method: 'GET',
            headers: {
              accept: 'application/json'
            }
          })

          if (!response.ok) {
            // Jika response tidak ok (misalnya 404), ambil data error
            const errorData = await response.json()
            console.warn('Data belum siap, polling lagi:', errorData)
            // Coba polling lagi setelah delay
            if (isMounted) {
              setTimeout(fetchResult, pollInterval)
            }
            return
          }

          // Jika response ok, parse datanya
          const data = await response.json()

          if (data.message === 'Get result successfully' && data.status === 'success') {
            // Jika data hasil scan sudah siap, delay 1 detik sebelum navigasi
            setTimeout(() => {
              if (isMounted) {
                navigate('/result-full-scan')
              }
            }, 1000)
          } else {
            console.warn('Response tidak sesuai, polling lagi:', data)
            if (isMounted) {
              setTimeout(fetchResult, pollInterval)
            }
          }
        } catch (error) {
          console.error('Error fetching fullscan result:', error)
          if (isMounted) {
            setTimeout(fetchResult, pollInterval)
          }
        }
      }

      fetchResult()

      // Cleanup function untuk membatalkan polling jika komponen unmount
      return () => {
        isMounted = false
      }
    }
  }, [progress, navigate, serialNumber])

  return (
    <div
      className="h-screen w-screen flex flex-col justify-center items-center relative text-white font-aldrich"
      style={{
        backgroundColor: '#000',
        backgroundImage: `url(${bgImage})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      {/* Modal Reconnect */}
      {showReconnectModal && <ReconnectModel onClose={() => setShowReconnectModal(false)} />}

      <div className="text-center">
        <h1 className="text-2xl font-bold">
          Please do not unplug your device. This process will take a little time.
        </h1>
      </div>

      <div className="pt-4 flex flex-col items-center w-[1022px]">
        <h2 className="text-3xl font-bold mb-2" style={{ color: '#00FFE7' }}>
          {progress}% {scanComplete && ' - Scan Complete!'}
        </h2>
        <div className="border-2 border-teal-500 p-2 shadow-lg bg-black w-full">
          <ArrowPattern progress={progress} />
        </div>
      </div>

      <div className="w-[1022px]">
        <div
          className="relative mt-8 p-6"
          style={{
            backgroundImage: `url(${modalBackground})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            minHeight: '385px'
          }}
        >
          <img src={plusSign} alt="Plus Sign" className="absolute top-[0px] left-[-13px] w-6 h-6" />
          <img
            src={plusSign}
            alt="Plus Sign"
            className="absolute bottom-[0px] right-[-13px] w-6 h-6"
          />

          <div className="flex flex-col items-center justify-center">
            <div
              className={`relative text-center p-4 bg-[#091310] w-full min-h-[200px] ${
                showAllLogs ? 'max-h-96 overflow-y-auto' : 'max-h-60 overflow-hidden'
              }`}
              style={{
                transition: 'max-height 0.1s ease-in-out',
                overflowY: 'auto', // Allow vertical scrolling
                overflowX: 'hidden' // Prevent horizontal scrolling
              }}
            >
              {logData.length === 0 ? (
                <p className="text-center text-gray-500">No log data available</p>
              ) : (
                <div className="space-y-2 w-full">
                  {logData
                    .slice()
                    .reverse()
                    .map((log, i) => {
                      const dateFormatted = formatDate(log.datetime)
                      const timeFormatted = formatTime(log.datetime)

                      return (
                        <div key={i} className="flex justify-between py-2 px-4">
                          {/* Bagian Date */}
                          <span className="w-[120px] text-left">{dateFormatted}</span>

                          {/* Bagian Time */}
                          <span className="w-[60px] text-center">{timeFormatted}</span>

                          {/* Bagian Log */}
                          <span className="flex-1 text-right">{log.log}</span>
                        </div>
                      )
                    })}
                </div>
              )}
            </div>

            <div className="flex justify-center mt-5">
              <button
                className="w-[223px] h-[43px] text-xl font-bold bg-transparent shadow-lg flex items-center justify-center relative"
                style={{
                  backgroundImage: `url(${buttonViewMore})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
                onClick={() => setShowAllLogs(!showAllLogs)}
              >
                {showAllLogs ? 'VIEW LESS' : 'VIEW MORE'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-center mt-6">
        <button
          className="w-[389px] h-[51px] text-xl font-bold bg-transparent shadow-lg flex items-center justify-center relative"
          style={{
            backgroundImage: `url(${buttonCancel})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
          onClick={openModal}
        >
          CANCEL SCANNING
        </button>
      </div>

      {isModalOpen && <CancelModal onClose={closeModal} onConfirm={handleCancelScanning} />}
    </div>
  )
}

export default FullScanPage
